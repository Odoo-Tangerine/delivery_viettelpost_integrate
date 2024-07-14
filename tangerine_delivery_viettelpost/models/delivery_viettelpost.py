# -*- coding: utf-8 -*-
import math
from typing import Any
from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import ustr
from odoo.addons.tangerine_delivery_base.settings.utils import (
    standardization_e164,
    get_route_api,
    notification
)
from odoo.addons.tangerine_delivery_base.api.connection import Connection
from ..settings.constants import settings
from ..api.client import Client


class ProviderViettelpost(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('viettelpost', 'Viettel Post')
    ], ondelete={'viettelpost': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})

    viettelpost_username = fields.Char(string='Username')
    viettelpost_password = fields.Char(string='Password')

    default_viettelpost_order_payment = fields.Selection(selection=settings.order_payment.value, string='Payment Type')
    default_viettelpost_product_type = fields.Selection(selection=settings.product_type.value, string='Product Type')
    default_viettelpost_national_type = fields.Selection(
        selection=settings.national_type.value,
        string='Types of Shipments'
    )
    viettelpost_service_request_domain = fields.Binary(default=[], store=False)
    default_viettelpost_service_id = fields.Many2one('viettelpost.service', string='Service')
    default_viettelpost_service_extend_id = fields.Many2one('viettelpost.service.extend', string='Service Extend')

    def _payload_get_token(self):
        return {
            'USERNAME': self.viettelpost_username,
            'PASSWORD': self.viettelpost_password
        }

    def viettelpost_get_access_token(self):
        try:
            self.ensure_one()
            if not self.viettelpost_username:
                raise UserError(_('The field Username is required'))
            elif not self.viettelpost_password:
                raise UserError(_('The field Password is required'))
            client = Client(Connection(self, get_route_api(self, settings.get_short_term_token_route.value)))
            result = client.get_short_term_access_token(self._payload_get_token())
            client = Client(Connection(self, get_route_api(self, settings.get_long_term_token_route.value)))
            result = client.get_long_term_access_token(self._payload_get_token(), result.get('token'))
            self.write({'access_token': result.get('token')})
            return notification('success', 'Get access token successfully')
        except Exception as e:
            raise UserError(ustr(e))

    def _viettelpost_payload_estimate_cost(self, order):
        return {
            'PRODUCT_WEIGHT': math.ceil(order.carrier_id.convert_weight(
                order._get_estimated_weight(),
                self.base_weight_unit
            )),
            'PRODUCT_PRICE': order.amount_total,
            'ORDER_SERVICE_ADD': order.env.context.get('viettelpost_service_extend_code'),
            'ORDER_SERVICE': order.env.context.get('viettelpost_service_code'),
            'PRODUCT_TYPE': order.env.context.get('viettelpost_product_type'),
            'NATIONAL_TYPE': order.env.context.get('viettelpost_national_type'),
            'SENDER_ADDRESS': f'{order.warehouse_id.partner_id.shipping_address}',
            'RECEIVER_ADDRESS': f'{order.partner_shipping_id.shipping_address}',
        }

    def viettelpost_rate_shipment(self, order) -> dict[str, Any]:
        client = Client(Connection(self, get_route_api(self, settings.estimate_cost_route.value)))
        result = client.estimate_cost(self._viettelpost_payload_estimate_cost(order))
        return {
            'success': True,
            'price': result.get('MONEY_TOTAL'),
            'error_message': False,
            'warning_message': False
        }

    @staticmethod
    def _compute_quantity(lines):
        quantity = 0
        for line in lines:
            quantity += line.quantity
        return quantity

    def _viettelpost_payload_create_order(self, picking):
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
            'PRODUCT_WEIGHT': math.ceil(self.convert_weight(
                picking._get_estimated_weight(),
                self.base_weight_unit
            )),
            'PRODUCT_QUANTITY': self._compute_quantity(picking.move_ids),
            'PRODUCT_PRICE': picking.sale_id.amount_total,
            'PRODUCT_TYPE': picking.viettelpost_product_type,
            'MONEY_COLLECTION': 0,
            'MONEY_TOTAL': picking.sale_id.amount_total,
            'LIST_ITEM': [{
                'PRODUCT_NAME': line.product_id.name,
                'PRODUCT_PRICE': line.product_id.list_price,
                'PRODUCT_WEIGHT': math.ceil(self.convert_weight(
                    line.product_id.weight,
                    self.base_weight_unit
                )),
                'PRODUCT_QUANTITY': line.quantity
            } for line in picking.move_ids_without_package]
        }
        if picking.cash_on_delivery and picking.cash_on_delivery_amount > 0.0:
            payload['MONEY_COLLECTION'] = picking.cash_on_delivery_amount
        return payload

    def viettelpost_send_shipping(self, pickings):
        client = Client(Connection(self, get_route_api(self, settings.create_order_route.value)))
        for picking in pickings:
            result = client.create_order(self._viettelpost_payload_create_order(picking))
            status_id = self.env.ref('tangerine_delivery_viettelpost.viettelpost_status_1')
            picking.write({'delivery_status_id': status_id.id if status_id else False})
            self.env['carrier.ref.order'].sudo().create({'picking_id': picking.id})
            return [{
                'exact_price': result.get('MONEY_TOTAL'),
                'tracking_number': result.get('ORDER_NUMBER')
            }]

    @staticmethod
    def viettelpost_get_tracking_link(picking):
        return f'{settings.tracking_url.value}'

    @staticmethod
    def _viettelpost_payload_cancel_order(order):
        return {'ORDER_NUMBER': order, 'TYPE': 4}

    def viettelpost_cancel_shipment(self, picking):
        client = Client(Connection(self, get_route_api(self, settings.update_order_route.value)))
        client.cancel_order(self._viettelpost_payload_cancel_order(picking.carrier_tracking_ref))
        picking.write({
            'carrier_tracking_ref': False,
            'carrier_price': 0.0
        })
        return notification(
            'success',
            f'Cancel tracking reference {settings.update_order_route.value} successfully'
        )

    def viettelpost_toggle_prod_environment(self):
        self.ensure_one()
        if self.prod_environment:
            self.domain = settings.domain_production.value
        else:
            self.domain = settings.domain_staging.value

    def _viettelpost_get_default_custom_package_code(self): ...
