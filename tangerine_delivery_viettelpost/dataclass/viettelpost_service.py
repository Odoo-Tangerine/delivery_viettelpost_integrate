from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Sequence, Tuple


class KEY(Enum):
    INPUT_CODE: str = 'SERVICE_CODE'
    INPUT_NAME: str = 'SERVICE_NAME'
    OUTPUT_CODE: str = 'code'
    OUTPUT_NAME: str = 'name'
    OUTPUT_SERVICE_ID: str = 'service_id'


@dataclass(frozen=True)
class Service:
    code: str
    name: str

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY.INPUT_CODE.value),
            data.get(KEY.INPUT_NAME.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY.OUTPUT_CODE.value: cls.code,
            KEY.OUTPUT_NAME.value: cls.name
        }
        return payload


@dataclass(frozen=True)
class ServiceExtend:
    code: str
    name: str

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY.INPUT_CODE.value),
            data.get(KEY.INPUT_NAME.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY.OUTPUT_CODE.value: cls.code,
            KEY.OUTPUT_NAME.value: cls.name,
            KEY.OUTPUT_SERVICE_ID.value: kwargs.get(KEY.OUTPUT_SERVICE_ID.value)
        }
        return payload
