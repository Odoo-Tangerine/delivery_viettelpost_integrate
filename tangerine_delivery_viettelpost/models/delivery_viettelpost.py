# -*- coding: utf-8 -*-
import json
import concurrent.futures
from typing import Dict, Any
from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools import ustr
from odoo.addons.tangerine_delivery_viettelpost.common.func import Func, Action
from odoo.addons.tangerine_delivery_viettelpost.dataclass.viettelpost_order import Order

LINK_TRACKING_VIETTELPOST = 'https://viettelpost.vn/thong-tin-don-hang?peopleTracking=sender&orderNumber={}'


class ProviderViettelPost(models.Model):
    _inherit = 'delivery.carrier'

    def _default_service_lcod(self):
        lcod_service = self.env['viettelpost.service'].search([('code', '=', 'LCOD')])
        return lcod_service.id

    def _get_domain_extend_service_type(self):
        service_id = self._default_service_lcod()
        return [('service_id', '=', service_id)]

    delivery_type = fields.Selection(selection_add=[
        ('viettelpost', 'ViettelPost')
    ], ondelete={'viettelpost': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})

    viettelpost_host = fields.Char(string='Host', readonly=True, default='https://partner.viettelpost.vn')
    viettelpost_token = fields.Char(string='Token', readonly=True)
    viettelpost_username = fields.Char(string='Username')
    viettelpost_password = fields.Char(string='Password')
    viettelpost_check_unique_order = fields.Boolean(default=False, string='Check Unique',
                                                    help='If set to True, The Viettelpost will check SO unique.')

    def _build_payload_get_token(self) -> Dict[str, Any]:
        payload = {
            'USERNAME': self.viettelpost_username,
            'PASSWORD': self.viettelpost_password
        }
        return payload

    def viettelpost_get_token(self):
        payload = self._build_payload_get_token()
        client = Func.get_client_viettelpost(self)
        data = client.get_token(payload)
        self.viettelpost_token = data.get('token')
        data = client.get_token_long_term(payload)
        self.viettelpost_token = data.get('token')

    def viettelpost_rate_shipment(self, order):
        client = Func.get_client_viettelpost(self)
        payload = self.env.context.get('viettelpost_payload_get_rate')
        if not payload:
            return {'success': True,
                    'price': 0.0,
                    'error_message': False,
                    'warning_message': False}
        result = client.get_rate(json.loads(payload))
        return {'success': True,
                'price': result.get('MONEY_TOTAL', 0.0),
                'error_message': False,
                'warning_message': False}

    @staticmethod
    def _compute_price_product(order):
        total = 0.0
        for line in order.order_line:
            total += line.price_subtotal
        return total

    def viettelpost_send_shipping(self, pickings):
        raise UserError(_('Viettel\'s process does not use the [Send to Shipper] feature'))

    def viettelpost_get_tracking_link(self, picking):
        return LINK_TRACKING_VIETTELPOST.format(picking.carrier_tracking_ref)

    def viettelpost_cancel_shipment(self, picking):
        client = Func.get_client_viettelpost(self)
        payload = {
            'TYPE': 4,  # TYPE FOR CANCEL ORDER
            'ORDER_NUMBER': picking.carrier_tracking_ref
        }
        client.update_bill(payload)
        picking.message_post(body=_(f'Shipment {picking.carrier_tracking_ref} has been cancelled'))
        picking.write({'carrier_tracking_ref': False, 'carrier_price': 0.0})
        viettelpost_service = [rec.id for rec in picking.sale_id.order_line if rec.is_delivery and rec.product_id.id ==
                               self.env.ref('tangerine_delivery_viettelpost.product_product_delivery_viettelpost').id]
        picking.sale_id.write({
            'viettelpost_waybill_order': False,
            'viettelpost_status': False,
            'viettelpost_money_collection': 0.0,
            'viettelpost_money_total': 0.0,
            'viettelpost_money_total_fee': 0.0,
            'viettelpost_money_fee': 0.0,
            'viettelpost_money_collection_fee': 0.0,
            'viettelpost_money_other_fee': 0.0,
            'viettelpost_fee_vat': 0.0,
            'viettelpost_product_type': False,
            'viettelpost_national_type': False,
            'viettelpost_service_type': False,
            'viettelpost_extend_service_type': False,
            'viettelpost_order_payment': False,
            'order_line': [(2, int(*viettelpost_service))]
        })

    def viettelpost_get_default_custom_package_code(self):
        raise (_('This feature is not available for Viettelpost carrier'))

    def synchronize_viettelpost_resources(self):
        try:
            self.env['viettelpost.province'].sync_provinces()
            self.env['viettelpost.district'].sync_districts()
            self.env['viettelpost.ward'].sync_wards()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(self.env['viettelpost.office'].sync_offices())
                executor.submit(self.env['viettelpost.service'].sync_services())
                executor.submit(self.env['stock.warehouse'].sync_warehouses())
            return Action.display_notification(title='Synchronize Resources Successfully',
                                               msg='All resources of viettelpost have been downloaded to the system')
        except Exception as e:
            raise UserError(ustr(e))
