import asyncio

from src.blockchain.daemon import BlockchainDaemon
from src.blockchain import service


async def run_daemon(network: int):
    loop = asyncio.get_running_loop()
    daemon = await BlockchainDaemon.create(network, loop)
    daemon.start()
    daemon.join()


async def run_daemons():
    for network in await service.get_used_networks():
        await run_daemon(network.id)
