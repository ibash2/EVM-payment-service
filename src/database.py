from sqlalchemy import (
    Float,
    Column,
    CursorResult,
    Insert,
    Integer,
    Select,
    String,
    Update,
    ForeignKey,
    Boolean,
)
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings

DATABASE_URL = str(settings.DATABASE_URL)

async_engine = create_async_engine(DATABASE_URL)

# Создание сессии для асинхронной работы с базой данных
Session = sessionmaker(bind=async_engine, class_=AsyncSession)


Base_a = declarative_base()


class Base(Base_a):
    __abstract__ = True

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


metadata = Base.metadata


class Payment(Base):
    __tablename__ = "payment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hook_url = Column(String, nullable=True)  # TODO
    network = Column(Integer, ForeignKey("network.id"))
    create_time = Column(Integer, nullable=False)
    expiration_time = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    payed = Column(Float, default=0)
    address = Column(String, nullable=False)
    block_number = Column(Integer, default=0)
    confirmations = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="CREATED")


class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, autoincrement=True)
    network = Column(Integer, ForeignKey("network.id"))
    balance = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    status = Column(String, nullable=False)


class Network(Base):
    __tablename__ = "network"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    rpc = Column(String, nullable=False)
    is_middleware = Column(Boolean, nullable=False)
    explorer = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    decimals = Column(Integer, nullable=False)
    confirmations = Column(Integer, nullable=False)


# Асинхронные запросы в базу
async def fetch_one(select_query: Select | Insert | Update):
    async with async_engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return cursor.first() if cursor.rowcount > 0 else None


async def fetch_all(select_query: Select | Insert | Update) -> list:
    async with async_engine.begin() as conn:
        cursor: CursorResult = await conn.execute(select_query)
        return [r for r in cursor.all()]


async def execute(select_query: Insert | Update) -> None:
    async with async_engine.begin() as conn:
        return await conn.execute(select_query)
