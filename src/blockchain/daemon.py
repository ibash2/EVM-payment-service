import asyncio
from asyncio import AbstractEventLoop
from threading import Thread
import time
import aiohttp

from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

from src.database import Network
from src.logger import Logger

from src.constants import PaymentStatus
from src.blockchain import service
from src.database import Payment

logger = Logger.get_auth_logger()


class BlockchainDaemon(Thread):
    def __init__(self, network: Network, payments: list[Payment], loop) -> None:
        super().__init__()
        self.daemon = True
        self.loop: AbstractEventLoop = loop

        self.network = network
        # self.rpc = 'https://mainnet.infura.io/v3/583c43516f464b2aae02993372269742'

        self.w3 = Web3(HTTPProvider(self.network.rpc))

        # Inject the PoA middleware to the innermost layer
        if self.network.is_middleware:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        self.payments = payments
        self.checked_bloc = 6014297

    @classmethod
    async def create(cls, network: int, loop):
        network = await service.get_network_by_id(network)
        payments = await service.get_all_created_and_pending_payments()
        return cls(network, payments, loop)

    def run(self) -> None:
        self.loop.create_task(self._check_payments())

    def add_payment(self, payment: Payment):
        self.payments.append(payment)

    async def _check_payments(self):
        logger.info("Daemon started")
        while True:
            block_data = self._get_last_block()

            for transaction in block_data.transactions:
                logger.info(f"Transaction: {transaction}")
                await self._finde_payment(transaction)

            self.checked_bloc += 1
            await self._update_payments()
            await asyncio.sleep(12)

    async def _finde_payment(self, transaction: dict):
        address = transaction["to"]

        for payment in self.payments:
            if payment.address == address:
                logger.info(f"Payment found: {payment.address}")
                await service.update_payment_status(
                    payment.id,
                    status=PaymentStatus.pending,
                    bloc=self.checked_bloc,
                )
                self._valid_payment(payment, transaction)
        return None

    async def _valid_payment(self, payment: Payment, transaction: dict):
        logger.info(f"Start validate payment: {payment.address}")

        transaction_value = Web3.from_wei(transaction["value"], "ether")

        if transaction_value >= payment.amount:
            await service.increment_payment_confirmations(payment.id, self.checked_bloc)
        else:
            await service.update_payment_to_not_full(payment.id, transaction_value)

    async def _update_payments(self):
        payments = await service.get_all_pending_payments()
        for payment in payments:
            if (
                payment.confirmations == 0
                and payment.expiration_time < time.time()
                and payment.status == PaymentStatus.created.value
            ):
                logger.warning(f"Payment {payment.address} failed")
                await service.update_payment_status(payment.id, PaymentStatus.failed)
                await self._send_hook(payment)
                self.payments = payments.remove(payment)
            else:
                confirmations = await service.increment_payment_confirmations(
                    payment.id, self.checked_bloc
                )

                if confirmations >= self.network.confirmations:
                    logger.info(f"Payment {payment.address} confirmed")
                    await service.update_payment_status(
                        payment.id, PaymentStatus.success
                    )
                    await self._send_hook(payment)
                    self.payments = payments.remove(payment)

    async def _send_hook(self, payment: Payment):
        async with aiohttp.ClientSession() as session:
            if payment.hook_url:
                async with session.post(
                    payment.hook_url,
                    json={
                        "id": payment.id,
                        "create_time": payment.create_time,
                        "expiration_time": payment.expiration_time,
                        "network": self.network.name,
                        "amount": payment.amount,
                        "confirmations": payment.confirmations,
                        "status": payment.status,
                    },
                ) as response:
                    return response.status

    def _get_last_block(self):
        block = self.w3.eth.get_block(self.checked_bloc, True)
        return block
