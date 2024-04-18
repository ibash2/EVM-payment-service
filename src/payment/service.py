from sqlalchemy import select, insert, update
from eth_account import Account

from src.constants import AddressStatus
from src.database import Payment, Address
from src.payment.schemas import PaymentModel, PaymentResponse
from src.database import fetch_one, execute


async def create_evm_wallet(network: str):
    # Включение неаудитируемых функций HD Wallet
    Account.enable_unaudited_hdwallet_features()

    # Теперь вы можете использовать мнемоническую фразу для создания кошелька
    mnemonic = Account.create_with_mnemonic()

    # Создание кошелька из мнемонической фразы
    wallet = Account.from_mnemonic(mnemonic[1])

    # Получение адреса и приватного ключа
    address = wallet.address
    private_key = wallet.key

    # Возвращение информации о кошельке
    # return mnemonic[1], private_key.hex(), address # TODO сохранить приватники
    await save_address(address, network)
    return address


async def save_address(address: str, network: int):
    insert_qeury = insert(Address).values(
        address=address, balance=0, status=AddressStatus.busy.value, network=network
    )

    await execute(insert_qeury)


async def get_free_address() -> str | None:
    # async with Session() as session:
    #     async with session.begin():
    #         # SELECT ... FOR UPDATE захватывает запись, чтобы другие транзакции не могли её изменять
    #         select_query = select(Address).where(
    #             Address.status == AddressStatus.free.value
    #         ).with_for_update()
    #         address = await session.execute(select_query)
    #         address = address.scalar_one_or_none()

    #         if address:
    #             # Обновление статуса после успешного захвата адреса
    #             address.status = AddressStatus.busy.value
    #             await session.commit()
    #             return address
    #         else:
    #             await session.rollback()
    #             return None

    select_query = (
        select(Address)
        .where(Address.status == AddressStatus.free.value)
        .with_for_update()
    )

    address = await fetch_one(select_query)

    if address:
        update_query = (
            update(Address)
            .where(Address.id == address.id)
            .values(status=AddressStatus.busy.value)
        )
        await execute(update_query)

        return address.address
    return None


async def create_payment(payment: PaymentModel) -> PaymentResponse:
    address = await get_free_address()

    if not address:
        address = await create_evm_wallet(payment.network)

    insert_qeury = (
        insert(Payment)
        .values(**payment.model_dump(), address=address)
        .returning(Payment)
    )

    r_payment: Payment = await fetch_one(insert_qeury)

    return PaymentResponse(**r_payment._asdict())


async def get_payment_by_id(id):
    select_query = select(Payment).where(Payment.id == id)
    payment = await fetch_one(select_query)

    return payment._asdict()
