from sqlalchemy import select, update

from src.constants import PaymentStatus, AddressStatus
from src.database import execute, fetch_all, fetch_one, Payment, Address, Network


async def get_all_created_and_pending_payments() -> list[Payment]:
    select_query = select(Payment).where(
        Payment.status.in_([PaymentStatus.created.value, PaymentStatus.pending.value]),
    )
    payments = await fetch_all(select_query)
    return payments


async def get_all_pending_payments() -> list[Payment]:
    select_query = select(Payment).where(Payment.status == PaymentStatus.pending.value)
    payments = await fetch_all(select_query)
    return payments


async def update_payment_status(
    payment_id: int, status: PaymentStatus, bloc: int | None = None
):
    values = {"status": status.value}

    if bloc:
        values["block_number"] = bloc

    update_query = update(Payment).where(Payment.id == payment_id).values(**values)
    await execute(update_query)


async def get_payment_by_id(payment_id: int) -> Payment:
    select_query = select(Payment).where(Payment.id == payment_id)
    payment = await fetch_one(select_query)
    return payment


async def update_payment_to_not_full(payment_id: int, value: float):
    update_query = (
        update(Payment)
        .where(Payment.id == payment_id)
        .values(status=PaymentStatus.notfull.value, payed=Payment.payed + value)
    )
    await execute(update_query)


async def increment_payment_confirmations(payment_id: int, bloc: int):
    update_query = (
        update(Payment)
        .where(Payment.id == payment_id)
        .values(confirmations=bloc - Payment.block_number)
        .returning(Payment)
    )

    result = await execute(update_query)

    return result.first().confirmations


async def confirm_payment(payment: Payment):
    update_query = (
        update(Payment)
        .where(Payment.id == payment.id)
        .values(status=PaymentStatus.success.value)
        .returning(Payment.confirmations)
    )
    confirmations = await execute(update_query)

    await release_address(payment.address)
    return confirmations


async def release_address(address: str):
    update_query = (
        update(Address)
        .where(Address.address == address)
        .values(status=AddressStatus.free.value)
    )
    return await execute(update_query)


async def get_network_by_id(network: int) -> Network | None:
    select_query = select(Network).where(Network.id == network)
    network = await fetch_one(select_query)
    return network


async def get_used_networks() -> list[Network]:
    select_query = select(Payment).where(
        Payment.status == PaymentStatus.pending.value,
    )
    payments = await fetch_all(select_query)

    select_query = select(Network).where(Network.id.in_([p.network for p in payments]))
    return await fetch_all(select_query)
