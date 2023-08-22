from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Sequence, Tuple


class KEY_PROVINCE(Enum):
    INPUT_ID: str = 'PROVINCE_ID'
    INPUT_CODE: str = 'PROVINCE_CODE'
    INPUT_NAME: str = 'PROVINCE_NAME'
    OUTPUT_ID: str = 'province_id'
    OUTPUT_CODE: str = 'province_code'
    OUTPUT_NAME: str = 'province_name'
    OUTPUT_CARRIER_ID: str = 'carrier_id'


class KEY_DISTRICT(Enum):
    INPUT_ID: str = 'DISTRICT_ID'
    INPUT_CODE: str = 'DISTRICT_VALUE'
    INPUT_NAME: str = 'DISTRICT_NAME'
    INPUT_PROVINCE_ID: str = 'PROVINCE_ID'
    OUTPUT_ID: str = 'district_id'
    OUTPUT_CODE: str = 'district_code'
    OUTPUT_NAME: str = 'district_name'
    OUTPUT_PROVINCE_ID: str = 'province_id'


class KEY_WARD(Enum):
    INPUT_ID: str = 'WARDS_ID'
    INPUT_NAME: str = 'WARDS_NAME'
    INPUT_DISTRICT_ID: str = 'DISTRICT_ID'
    OUTPUT_ID: str = 'ward_id'
    OUTPUT_NAME: str = 'ward_name'
    OUTPUT_DISTRICT_ID: str = 'district_id'


@dataclass(frozen=True)
class Province:
    id: int
    code: str
    name: str

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY_PROVINCE.INPUT_ID.value),
            data.get(KEY_PROVINCE.INPUT_CODE.value),
            data.get(KEY_PROVINCE.INPUT_NAME.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY_PROVINCE.OUTPUT_ID.value: cls.id,
            KEY_PROVINCE.OUTPUT_CODE.value: cls.code,
            KEY_PROVINCE.OUTPUT_NAME.value: cls.name.title(),
            KEY_PROVINCE.OUTPUT_CARRIER_ID.value: kwargs.get('carrier_id')
        }
        return payload


@dataclass(frozen=True)
class District:
    id: int
    code: str
    name: str
    province_id: int

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY_DISTRICT.INPUT_ID.value),
            data.get(KEY_DISTRICT.INPUT_CODE.value),
            data.get(KEY_DISTRICT.INPUT_NAME.value).title(),
            data.get(KEY_DISTRICT.INPUT_PROVINCE_ID.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY_DISTRICT.OUTPUT_ID.value: cls.id,
            KEY_DISTRICT.OUTPUT_CODE.value: cls.code,
            KEY_DISTRICT.OUTPUT_NAME.value: cls.name.title(),
            KEY_DISTRICT.OUTPUT_PROVINCE_ID.value: kwargs.get(KEY_DISTRICT.OUTPUT_PROVINCE_ID.value)
        }
        return payload


@dataclass(frozen=True)
class Ward:
    id: int
    name: str
    district_id: int

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY_WARD.INPUT_ID.value),
            data.get(KEY_WARD.INPUT_NAME.value).title(),
            data.get(KEY_WARD.INPUT_DISTRICT_ID.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY_WARD.OUTPUT_ID.value: cls.id,
            KEY_WARD.OUTPUT_NAME.value: cls.name.title(),
            KEY_WARD.OUTPUT_DISTRICT_ID.value: kwargs.get(KEY_WARD.OUTPUT_DISTRICT_ID.value)
        }
        return payload
