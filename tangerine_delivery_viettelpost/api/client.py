# -*- coding: utf-8 -*-
import json
import math
from dataclasses import dataclass
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
from odoo.addons.tangerine_delivery_base.settings.utils import URLBuilder
from .connection import Connection
from ..settings.constants import settings


@dataclass
class Client:
    conn: Connection

    def _build_header(self, route_id, token):
        headers = json.loads(safe_eval(route_id.headers))
        if route_id.code == settings.get_long_term_token_route.value and token:
            headers.update({'Token': token})
        elif route_id.is_need_access_token:
            headers.update({'Token': self.conn.provider.access_token})
        return headers

    def _payload_get_token(self):
        return {
            'USERNAME': self.conn.provider.viettelpost_username,
            'PASSWORD': self.conn.provider.viettelpost_password
        }

    @staticmethod
    def _validate_response(response):
        if response.get('error'):
            raise UserError(response.get('message'))
        return response.get('data')

    def _execute(self, route_id, params=None, payload=None, token=None):
        return self.conn.execute_restful(
            url=URLBuilder.builder(
                host=self.conn.provider.domain,
                routes=[route_id.route],
                params=params
            ),
            headers=self._build_header(route_id, token),
            method=route_id.method,
            **payload or {}
        )

    def get_short_term_access_token(self, route_id):
        return self._validate_response(self._execute(route_id=route_id, payload=self._payload_get_token()))

    def get_long_term_access_token(self, route_id, token):
        return self._validate_response(self._execute(route_id=route_id, payload=self._payload_get_token(), token=token))

    def service_synchronous(self, route_id):
        return self._validate_response(self._execute(route_id=route_id, payload={'TYPE': 2}))

    def service_extend_synchronous(self, route_id, extend_code):
        return self._validate_response(self._execute(route_id=route_id, params={'serviceCode': extend_code}))

    def _payload_estimate_cost(self, order):
        return {
            'PRODUCT_WEIGHT': math.ceil(order.carrier_id.convert_weight(
                order._get_estimated_weight(),
                self.conn.provider.base_weight_unit
            )),
            'PRODUCT_PRICE': order.amount_total,
            'ORDER_SERVICE_ADD': order.env.context.get('viettelpost_service_extend_code'),
            'ORDER_SERVICE': order.env.context.get('viettelpost_service_code'),
            'PRODUCT_TYPE': order.env.context.get('viettelpost_product_type'),
            'NATIONAL_TYPE': order.env.context.get('viettelpost_national_type'),
            'SENDER_ADDRESS': f'{order.warehouse_id.partner_id.shipping_address}',
            'RECEIVER_ADDRESS': f'{order.partner_shipping_id.shipping_address}',
        }

    def estimate_cost(self, route_id, order):
        return self._validate_response(self._execute(route_id=route_id, payload=self._payload_estimate_cost(order)))

    @staticmethod
    def _compute_quantity(lines):
        quantity = 0
        for line in lines:
            quantity += line.quantity
        return quantity

    def _payload_create_order(self, picking):
        sender_id = picking.picking_type_id.warehouse_id.partner_id
        recipient_id = picking.partner_id
        payload = {
            'ORDER_NUMBER': picking.sale_id.name,
            'ORDER_PAYMENT': picking.viettelpost_order_payment,
            'ORDER_SERVICE_ADD': picking.viettelpost_service_extend_id.code or '',
            'ORDER_SERVICE': picking.viettelpost_service_id.code,
            'ORDER_VOUCHER': picking.promo_code or '',
            'ORDER_NOTE': picking.remarks or '',
            'NATIONAL_TYPE': picking.viettelpost_national_type,
            'SENDER_FULLNAME': sender_id.name,
            'SENDER_PHONE': sender_id.mobile or sender_id.phone,
            'SENDER_ADDRESS': f'{sender_id.shipping_address}',
            'RECEIVER_FULLNAME': recipient_id.name,
            'RECEIVER_PHONE': recipient_id.mobile or recipient_id.phone,
            'RECEIVER_ADDRESS': f'{recipient_id.shipping_address}',
            'PRODUCT_WEIGHT': math.ceil(self.conn.provider.convert_weight(
                picking._get_estimated_weight(),
                self.conn.provider.base_weight_unit
            )),
            'PRODUCT_QUANTITY': self._compute_quantity(picking.move_ids),
            'PRODUCT_PRICE': picking.sale_id.amount_total,
            'PRODUCT_TYPE': picking.viettelpost_product_type,
            'MONEY_COLLECTION': 0,
            'MONEY_TOTAL': picking.sale_id.amount_total,
            'LIST_ITEM': [{
                'PRODUCT_NAME': line.product_id.name,
                'PRODUCT_PRICE': line.product_id.list_price,
                'PRODUCT_WEIGHT': line.product_id.weight,
                'PRODUCT_QUANTITY': line.quantity
            } for line in picking.move_line_ids_without_package]
        }
        if picking.cash_on_delivery and picking.cash_on_delivery_amount > 0.0:
            payload['MONEY_COLLECTION'] = picking.cash_on_delivery_amount
        return payload

    def create_order(self, route_id, picking):
        return self._validate_response(self._execute(route_id=route_id, payload=self._payload_create_order(picking)))

    @staticmethod
    def _payload_cancel_order(order):
        return {'ORDER_NUMBER': order, 'TYPE': 4}

    def cancel_order(self, route_id, order):
        self._execute(route_id=route_id, payload=self._payload_cancel_order(order))
