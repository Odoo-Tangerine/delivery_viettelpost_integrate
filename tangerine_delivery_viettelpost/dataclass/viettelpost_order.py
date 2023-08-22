from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Sequence, Tuple, Optional
from odoo import _
from odoo.exceptions import UserError
from odoo.addons.tangerine_delivery_viettelpost.common.func import Func

WAYBILL_TYPE_CODE_1 = '1'  # Không thu hộ
WAYBILL_TYPE_CODE_2 = '2'  # Thu hộ tiền hàng và tiền cước
WAYBILL_TYPE_CODE_3 = '3'  # Thu hộ tiền hàng
WAYBILL_TYPE_CODE_4 = '4'  # Thu hộ tiền cước


class KEY_INPUT_DICT_ORDER(Enum):
    ORDER_NUMBER: str = 'ORDER_NUMBER'
    MONEY_COLLECTION: str = 'MONEY_COLLECTION'
    EXCHANGE_WEIGHT: str = 'EXCHANGE_WEIGHT'
    MONEY_TOTAL: str = 'MONEY_TOTAL'
    MONEY_TOTAL_FEE: str = 'MONEY_TOTAL_FEE'
    MONEY_FEE: str = 'MONEY_FEE'
    MONEY_COLLECTION_FEE: str = 'MONEY_COLLECTION_FEE'
    MONEY_OTHER_FEE: str = 'MONEY_OTHER_FEE'
    FEE_VAT: str = 'MONEY_VAT'


class KEY_OUTPUT_DICT_ORDER(Enum):
    ORDER_NUMBER: str = 'carrier_tracking_ref'
    MONEY_COLLECTION: str = 'money_collection'
    EXCHANGE_WEIGHT: str = 'shipping_weight'
    MONEY_TOTAL: str = 'money_total'
    MONEY_TOTAL_FEE: str = 'money_total_fee'
    MONEY_FEE: str = 'money_fee'
    MONEY_COLLECTION_FEE: str = 'money_collection_fee'
    MONEY_OTHER_FEE: str = 'money_other_fee'
    FEE_VAT: str = 'fee_vat'
    BL_STATUS: str = 'bl_status'
    DELI_CARRIER_ID: str = 'carrier_id'


class KEY_OUTPUT_DICT_SENDER(Enum):
    GROUP_ADDRESS_ID: str = 'GROUPADDRESS_ID'
    CUS_ID: str = 'CUS_ID'
    SENDER_FULLNAME: str = 'SENDER_FULLNAME'
    SENDER_ADDRESS: str = 'SENDER_ADDRESS'
    SENDER_PHONE: str = 'SENDER_PHONE'
    SENDER_WARD: str = 'SENDER_WARD'
    SENDER_DISTRICT: str = 'SENDER_DISTRICT'
    SENDER_PROVINCE: str = 'SENDER_PROVINCE'
    SENDER_LATITUDE: str = 'SENDER_LATITUDE'
    SENDER_LONGITUDE: str = 'SENDER_LONGITUDE'


class KEY_OUTPUT_DICT_RECIPIENT(Enum):
    RECEIVER_FULLNAME: str = 'RECEIVER_FULLNAME'
    RECEIVER_ADDRESS: str = 'RECEIVER_ADDRESS'
    RECEIVER_PHONE: str = 'RECEIVER_PHONE'
    RECEIVER_EMAIL: str = 'RECEIVER_EMAIL'
    RECEIVER_WARD: str = 'RECEIVER_WARD'
    RECEIVER_DISTRICT: str = 'RECEIVER_DISTRICT'
    RECEIVER_PROVINCE: str = 'RECEIVER_PROVINCE'
    RECEIVER_LATITUDE: str = 'RECEIVER_LATITUDE'
    RECEIVER_LONGITUDE: str = 'RECEIVER_LONGITUDE'


class KEY_OUTPUT_DICT_ORDER_INFORMATION(Enum):
    ORDER_NUMBER: str = 'ORDER_NUMBER'
    DELIVERY_DATE: str = 'DELIVERY_DATE'
    PRODUCT_TYPE: str = 'PRODUCT_TYPE'
    NATIONAL_TYPE: str = 'NATIONAL_TYPE'
    ORDER_PAYMENT: str = 'ORDER_PAYMENT'
    ORDER_SERVICE: str = 'ORDER_SERVICE'
    ORDER_SERVICE_ADD: str = 'ORDER_SERVICE_ADD'
    ORDER_NOTE: str = 'ORDER_NOTE'
    MONEY_COLLECTION: str = 'MONEY_COLLECTION'
    MONEY_TOTAL: str = 'MONEY_TOTAL'
    PRODUCT_NAME: str = 'PRODUCT_NAME'
    PRODUCT_DESCRIPTION: str = 'PRODUCT_DESCRIPTION'
    PRODUCT_QUANTITY: str = 'PRODUCT_QUANTITY'
    PRODUCT_PRICE: str = 'PRODUCT_PRICE'
    PRODUCT_WEIGHT: str = 'PRODUCT_WEIGHT'
    LIST_ITEM: str = 'LIST_ITEM'
    TYPE: str = 'TYPE'


@dataclass(frozen=True)
class Order:
    order_number: str
    money_collection: int
    exchange_weight: int
    money_total: int
    money_total_fee: int
    money_fee: int
    money_collection_fee: int
    money_other_fee: int
    fee_vat: int

    @staticmethod
    def parser_response_order(data: Dict[str, Any]) -> Sequence[Tuple]:
        result: tuple = (
            data.get(KEY_INPUT_DICT_ORDER.ORDER_NUMBER.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_COLLECTION.value),
            data.get(KEY_INPUT_DICT_ORDER.EXCHANGE_WEIGHT.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_TOTAL.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_TOTAL_FEE.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_FEE.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_COLLECTION_FEE.value),
            data.get(KEY_INPUT_DICT_ORDER.MONEY_OTHER_FEE.value),
            data.get(KEY_INPUT_DICT_ORDER.FEE_VAT.value)
        )
        return result

    @staticmethod
    def build_dictionary_sender(cls, **kwargs) -> Dict[str, Any]:
        payload: dict = {
            KEY_OUTPUT_DICT_SENDER.SENDER_FULLNAME.value: cls.name,
            KEY_OUTPUT_DICT_SENDER.SENDER_PHONE.value: cls.phone,
            KEY_OUTPUT_DICT_SENDER.SENDER_ADDRESS.value: cls.street,
            KEY_OUTPUT_DICT_SENDER.SENDER_WARD.value: cls.viettelpost_ward_id.ward_id,
            KEY_OUTPUT_DICT_SENDER.SENDER_DISTRICT.value: cls.viettelpost_district_id.district_id,
            KEY_OUTPUT_DICT_SENDER.SENDER_PROVINCE.value: cls.viettelpost_province_id.province_id,
            KEY_OUTPUT_DICT_SENDER.GROUP_ADDRESS_ID.value: kwargs.get('group_address_id'),
            KEY_OUTPUT_DICT_SENDER.CUS_ID.value: kwargs.get('customer_id'),
            KEY_OUTPUT_DICT_SENDER.SENDER_LATITUDE.value: 0,
            KEY_OUTPUT_DICT_SENDER.SENDER_LONGITUDE.value: 0
        }
        return payload

    @staticmethod
    def build_dictionary_recipient(cls) -> Dict[str, Any]:
        payload: dict = {
            KEY_OUTPUT_DICT_RECIPIENT.RECEIVER_FULLNAME.value: cls.name,
            KEY_OUTPUT_DICT_RECIPIENT.RECEIVER_PHONE.value: cls.phone,
            KEY_OUTPUT_DICT_RECIPIENT.RECEIVER_ADDRESS.value: cls.street,
            KEY_OUTPUT_DICT_RECIPIENT.RECEIVER_WARD.value: cls.viettelpost_ward_id.ward_id,
            KEY_OUTPUT_DICT_RECIPIENT.RECEIVER_DISTRICT.value: cls.viettelpost_district_id.district_id,
            KEY_OUTPUT_DICT_RECIPIENT.RECEIVER_PROVINCE.value: cls.viettelpost_province_id.province_id,
            KEY_OUTPUT_DICT_RECIPIENT.RECEIVER_LATITUDE.value: 0,
            KEY_OUTPUT_DICT_RECIPIENT.RECEIVER_LONGITUDE.value: 0
        }
        return payload

    @staticmethod
    def _prepare_data_list_item(cls):
        list_item: list = []
        total_weight: float = 0.0
        total_qty: float = 0.0
        total_price: float = 0.0
        if not cls.sale_id.order_line:
            raise UserError(_('Please add products to order line.'))
        for line in cls.sale_id.order_line:
            if line.is_delivery:
                continue
            item: dict = {
                KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_NAME.value: line.name,
                KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_PRICE.value: line.price_subtotal,
                KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_WEIGHT.value: line.product_template_id.weight,
                KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_QUANTITY.value: line.product_uom_qty
            }
            total_price += line.price_subtotal
            total_weight += line.product_template_id.weight * line.product_uom_qty
            total_qty += line.product_uom_qty
            list_item.append(item)
        return list_item, total_weight, total_qty, total_price

    @staticmethod
    def prepare_get_matching_service(cls, sender, recipient, weight, price) -> Dict[str, Any]:
        payload: dict = {
            KEY_OUTPUT_DICT_SENDER.SENDER_PROVINCE.value: sender.viettelpost_province_id.province_id,
            KEY_OUTPUT_DICT_SENDER.SENDER_DISTRICT.value: sender.viettelpost_district_id.district_id,
            KEY_OUTPUT_DICT_RECIPIENT.RECEIVER_PROVINCE.value: recipient.viettelpost_province_id.province_id,
            KEY_OUTPUT_DICT_RECIPIENT.RECEIVER_DISTRICT.value: recipient.viettelpost_district_id.district_id,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_TYPE.value: cls.viettelpost_product_type,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_WEIGHT.value: weight,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_PRICE.value: price,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.TYPE.value: cls.viettelpost_order_payment
        }
        return payload

    @staticmethod
    def _compute_money_collection(cls, total_price) -> Sequence[float]:
        collection: float = 0.0
        fee: float = 0.0
        if cls.viettelpost_order_payment in [WAYBILL_TYPE_CODE_2, WAYBILL_TYPE_CODE_4]:
            collection = total_price
        elif cls.viettelpost_order_payment == WAYBILL_TYPE_CODE_3:
            collection = float(cls.sale_id.amount_untaxed)
        return collection, fee

    @staticmethod
    def build_dictionary_order(cls) -> Dict[str, Any]:
        list_item, total_weight, total_qty, total_price = Order._prepare_data_list_item(cls)
        money_collection, money_total = Order._compute_money_collection(cls, total_price)
        product_name = cls.sale_id.order_line[0].name
        payload: dict = {
            KEY_OUTPUT_DICT_ORDER_INFORMATION.ORDER_NUMBER.value: cls.sale_id.name,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.DELIVERY_DATE.value: datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_TYPE.value: cls.viettelpost_product_type,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.ORDER_PAYMENT.value: int(cls.viettelpost_order_payment),
            KEY_OUTPUT_DICT_ORDER_INFORMATION.ORDER_SERVICE.value: cls.viettelpost_service_type.code,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.ORDER_SERVICE_ADD.value: cls.viettelpost_extend_service_type.code or '',
            KEY_OUTPUT_DICT_ORDER_INFORMATION.MONEY_COLLECTION.value: money_collection,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.MONEY_TOTAL.value: money_total,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_NAME.value: product_name,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_DESCRIPTION.value: product_name,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_QUANTITY.value: total_qty,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_PRICE.value: total_price,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.PRODUCT_WEIGHT.value: total_weight,
            KEY_OUTPUT_DICT_ORDER_INFORMATION.ORDER_NOTE.value: cls.note or '',
            KEY_OUTPUT_DICT_ORDER_INFORMATION.LIST_ITEM.value: list_item
        }
        return payload
