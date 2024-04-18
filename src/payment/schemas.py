from src.models import CustomModel


class PaymentRequest(CustomModel):
    network: int
    amount: float


class PaymentModel(PaymentRequest):
    create_time: int
    expiration_time: int


class PaymentResponse(PaymentModel):
    id: int
    address: str
    status: str
    confirmations: int
