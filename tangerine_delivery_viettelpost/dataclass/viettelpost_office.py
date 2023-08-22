from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Sequence, Tuple


class KEY(Enum):
    INPUT_PROVINCE_NAME: str = 'TEN_TINH'
    INPUT_DISTRICT_NAME: str = 'TEN_QUANHUYEN'
    INPUT_WARD_NAME: str = 'TEN_PHUONGXA'
    INPUT_OFFICE_CODE: str = 'MA_BUUCUC'
    INPUT_OFFICE_NAME: str = 'TEN_BUUCUC'
    INPUT_OFFICE_PHONE: str = 'DIEN_THOAI'
    INPUT_ADDRESS: str = 'DIA_CHI'
    INPUT_LATITUDE: str = 'LATITUDE'
    INPUT_LONGITUDE: str = 'LONGITUDE'
    INPUT_PERSON_IN_CHARGE: str = 'PHUTRACH'
    INPUT_PERSON_IN_CHARGE_PHONE: str = 'PHUTRACHPHONE'

    OUTPUT_OFFICE_NAME: str = 'name'
    OUTPUT_OFFICE_CODE: str = 'code'
    OUTPUT_PROVINCE_NAME: str = 'province_name'
    OUTPUT_DISTRICT_NAME: str = 'district_name'
    OUTPUT_WARD_NAME: str = 'ward_name'
    OUTPUT_ADDRESS: str = 'address'
    OUTPUT_LATITUDE: str = 'latitude'
    OUTPUT_LONGITUDE: str = 'longitude'
    OUTPUT_OFFICE_PHONE: str = 'phone'
    OUTPUT_PERSON_IN_CHARGE: str = 'person_in_charge'
    OUTPUT_PERSON_IN_CHARGE_PHONE: str = 'person_in_charge_phone'


@dataclass(frozen=True)
class PostOffice:
    name: str
    code: str
    province_name: str
    district_name: str
    ward_name: str
    address: str
    latitude: str
    longitude: str
    phone: str
    person_in_charge: str
    person_in_charge_phone: str

    @staticmethod
    def parser_dict(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY.INPUT_OFFICE_NAME.value),
            data.get(KEY.INPUT_OFFICE_CODE.value),
            data.get(KEY.INPUT_PROVINCE_NAME.value),
            data.get(KEY.INPUT_DISTRICT_NAME.value),
            data.get(KEY.INPUT_WARD_NAME.value),
            data.get(KEY.INPUT_ADDRESS.value),
            data.get(KEY.INPUT_LATITUDE.value),
            data.get(KEY.INPUT_LONGITUDE.value),
            data.get(KEY.INPUT_OFFICE_PHONE.value),
            data.get(KEY.INPUT_PERSON_IN_CHARGE.value),
            data.get(KEY.INPUT_PERSON_IN_CHARGE_PHONE.value)
        )
        return result

    @staticmethod
    def parser_class(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY.OUTPUT_OFFICE_NAME.value: cls.name,
            KEY.OUTPUT_OFFICE_CODE.value: cls.code,
            KEY.OUTPUT_OFFICE_PHONE.value: cls.phone,
            KEY.OUTPUT_PROVINCE_NAME.value: cls.province_name.title() if cls.province_name else False,
            KEY.OUTPUT_DISTRICT_NAME.value: cls.district_name.title() if cls.district_name else False,
            KEY.OUTPUT_WARD_NAME.value: cls.ward_name.title() if cls.ward_name else False,
            KEY.OUTPUT_LATITUDE.value: cls.latitude,
            KEY.OUTPUT_LONGITUDE.value: cls.longitude,
            KEY.OUTPUT_ADDRESS.value: cls.address.title() if cls.address else False,
            KEY.OUTPUT_PERSON_IN_CHARGE.value: cls.person_in_charge,
            KEY.OUTPUT_PERSON_IN_CHARGE_PHONE.value: cls.person_in_charge_phone
        }
        return payload
