from fastapi import APIRouter

from src.networks import service
from src.networks.schemas import NetworksResponse

router = APIRouter(prefix="/network", tags=["networks"])


@router.get("/", response_model=list[NetworksResponse])
def get_all_networks():
    networks = service.get_all_networks()

    return [NetworksResponse(**network._asdict()) for network in networks]
