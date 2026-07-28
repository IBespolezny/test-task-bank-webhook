from enum import Enum

class PaymentStatusBank(str, Enum):
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    PENDING = "PENDING"

class PaymentStatusServer(str, Enum):
    PROCESSED = "processed"
    ALREADY_PROCESSED = "already_processed"