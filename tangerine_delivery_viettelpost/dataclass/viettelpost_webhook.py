from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Sequence, Tuple


class KEY(Enum):
    ORDER_NUMBER: str = 'ORDER_NUMBER'
    ORDER_REFERENCE: str = 'ORDER_REFERENCE'
    ORDER_STATUS: str = 'ORDER_STATUS'
    MONEY_COLLECTION: str = 'MONEY_COLLECTION'
    MONEY_FEECOD: str = 'MONEY_FEECOD'
    MONEY_TOTAL: str = 'MONEY_TOTAL'
    MONEY_TOTAL_FEE: str = 'MONEY_TOTAL_FEE'
    PRODUCT_WEIGHT: str = 'PRODUCT_WEIGHT'
    PERSON_IN_CHARGE: str = 'EMPLOYEE_NAME'
    PHONE_NUMBER: str = 'EMPLOYEE_PHONE'
    ORDER_SERVICE: str = 'ORDER_SERVICE'
    NOTE: str = 'NOTE'


@dataclass(frozen=True)
class Webhook:
    order_number: str
    order_reference: str
    order_status: int
    money_collection: int
    money_total_fee: int
    money_feecod: int
    money_total: int
    product_weight: int
    person_in_charge: str
    phone_number: str
    service: str
    note: str

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY.ORDER_NUMBER.value),
            data.get(KEY.ORDER_REFERENCE.value),
            data.get(KEY.ORDER_STATUS.value),
            data.get(KEY.MONEY_COLLECTION.value),
            data.get(KEY.MONEY_TOTAL_FEE.value),
            data.get(KEY.MONEY_FEECOD.value),
            data.get(KEY.MONEY_TOTAL.value),
            data.get(KEY.PRODUCT_WEIGHT.value),
            data.get(KEY.PERSON_IN_CHARGE.value),
            data.get(KEY.PHONE_NUMBER.value),
            data.get(KEY.ORDER_SERVICE.value),
            data.get(KEY.NOTE.value)
        )
        return result
