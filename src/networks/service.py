from sqlalchemy import select

from src.database import Network
from src.database import fetch_all


async def get_all_networks():
    select_query = select(Network)
    return await fetch_all(select_query)
