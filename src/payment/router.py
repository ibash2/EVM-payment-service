import time

from fastapi import APIRouter

from src.payment import service
from src.payment.schemas import PaymentRequest, PaymentResponse, PaymentModel

router = APIRouter(prefix="/payment", tags=["payment"])


@router.get("/", response_model=PaymentResponse)
async def get_payment(id: int):
    payment = await service.get_payment_by_id(id)

    return PaymentResponse(**payment)


@router.post("/", response_model=PaymentResponse)
async def create_payment(payment: PaymentRequest):
    payment = PaymentModel(
        **payment.model_dump(),
        create_time=int(time.time()),
        expiration_time=int(time.time() + 1800),
    )

    return await service.create_payment(payment)
