from src.models import CustomModel


class NetworksResponse(CustomModel):
    id: int
    name: str
    explorer: str
    symbol: str
    decimals: int
    confirmations: int
