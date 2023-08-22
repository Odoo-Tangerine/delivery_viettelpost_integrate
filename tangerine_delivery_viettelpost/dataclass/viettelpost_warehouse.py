from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Sequence, Tuple


class KEY(Enum):
    INPUT_GROUP_ADDRESS_ID: str = 'groupaddressId'
    INPUT_CUS_ID: str = 'cusId'
    INPUT_NAME: str = 'name'
    INPUT_PHONE: str = 'phone'
    INPUT_ADDRESS: str = 'address'
    INPUT_PROVINCE_ID: str = 'provinceId'
    INPUT_DISTRICT_ID: str = 'districtId'
    INPUT_WARDS_ID: str = 'wardsId'

    OUTPUT_NAME: str = 'name'
    OUTPUT_CODE: str = 'code'
    OUTPUT_SOURCE: str = 'source'
    OUTPUT_PHONE: str = 'phone'
    OUTPUT_PARTNER_ID: str = 'partner_id'
    OUTPUT_GROUP_ADDRESS_ID: str = 'viettelpost_group_address_id'
    OUTPUT_CUSTOMER_ID: str = 'viettelpost_customer_id'
    OUTPUT_ADDRESS: str = 'street'
    OUTPUT_PROVINCE_ID: str = 'viettelpost_province_id'
    OUTPUT_DISTRICT_ID: str = 'viettelpost_district_id'
    OUTPUT_WARD_ID: str = 'viettelpost_ward_id'
    OUTPUT_IS_WAREHOUSE_VIETTELPOST: str = 'is_warehouse_viettelpost'


@dataclass(frozen=True)
class Warehouse:
    name: str
    phone: str
    group_address_id: int
    cus_id: int
    address: str
    province_id: int
    district_id: int
    ward_id: int

    @staticmethod
    def _build_code_warehouse(name):
        words = name.split()
        first_letters = [word[0].upper() for word in words]
        code = ''.join(first_letters)
        return code[:3]  # Just take 3 characters in the result

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY.INPUT_NAME.value),
            data.get(KEY.INPUT_PHONE.value),
            data.get(KEY.INPUT_GROUP_ADDRESS_ID.value),
            data.get(KEY.INPUT_CUS_ID.value),
            data.get(KEY.INPUT_ADDRESS.value),
            data.get(KEY.INPUT_PROVINCE_ID.value),
            data.get(KEY.INPUT_DISTRICT_ID.value),
            data.get(KEY.INPUT_WARDS_ID.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY.OUTPUT_NAME.value: cls.name,
            KEY.OUTPUT_CODE.value: Warehouse._build_code_warehouse(cls.name),
            KEY.OUTPUT_GROUP_ADDRESS_ID.value: cls.group_address_id,
            KEY.OUTPUT_CUSTOMER_ID.value: cls.cus_id,
            KEY.OUTPUT_PARTNER_ID.value: kwargs.get(KEY.OUTPUT_PARTNER_ID.value),
            KEY.OUTPUT_IS_WAREHOUSE_VIETTELPOST.value: True
        }
        return payload

    @staticmethod
    def parser_class_partner(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY.OUTPUT_NAME.value: cls.name,
            KEY.OUTPUT_PHONE.value: cls.phone,
            KEY.OUTPUT_ADDRESS.value: cls.address,
            KEY.OUTPUT_PROVINCE_ID.value: kwargs.get(KEY.OUTPUT_PROVINCE_ID.value),
            KEY.OUTPUT_DISTRICT_ID.value: kwargs.get(KEY.OUTPUT_DISTRICT_ID.value),
            KEY.OUTPUT_WARD_ID.value: kwargs.get(KEY.OUTPUT_WARD_ID.value),
        }
        return payload
