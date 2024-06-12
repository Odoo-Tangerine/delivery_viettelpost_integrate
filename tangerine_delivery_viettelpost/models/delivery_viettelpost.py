# -*- coding: utf-8 -*-
from typing import Any
from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import ustr
from odoo.addons.tangerine_delivery_base.settings import utils
from ..settings.constants import settings
from ..api.connection import Connection
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

    def viettelpost_get_access_token(self):
        try:
            self.ensure_one()
            if not self.viettelpost_username:
                raise UserError(_('The field Username is required'))
            elif not self.viettelpost_password:
                raise UserError(_('The field Password is required'))
            client = Client(Connection(self))
            route_id = utils.get_route_api(self, settings.get_short_term_token_route.value)
            result = client.get_short_term_access_token(route_id)
            route_id = utils.get_route_api(self, settings.get_long_term_token_route.value)
            result = client.get_long_term_access_token(route_id, result.get('token'))
            self.write({'access_token': result.get('token')})
            return utils.notification('success', 'Get access token successfully')
        except Exception as e:
            raise UserError(ustr(e))

    def viettelpost_rate_shipment(self, order) -> dict[str, Any]:
        client = Client(Connection(self))
        route_id = utils.get_route_api(self, settings.estimate_cost_route.value)
        result = client.estimate_cost(route_id, order)
        return {
            'success': True,
            'price': result.get('MONEY_TOTAL'),
            'error_message': False,
            'warning_message': False
        }

    def viettelpost_send_shipping(self, pickings):
        client = Client(Connection(self))
        route_id = utils.get_route_api(self, settings.create_order_route.value)
        for picking in pickings:
            result = client.create_order(route_id, picking)
            return [{
                'exact_price': result.get('MONEY_TOTAL'),
                'tracking_number': result.get('ORDER_NUMBER')
            }]

    @staticmethod
    def viettelpost_get_tracking_link(picking):
        return f'{settings.tracking_url.value}'

    def viettelpost_cancel_shipment(self, picking):
        client = Client(Connection(self))
        route_id = utils.get_route_api(self, settings.update_order_route.value)
        client.cancel_order(route_id, picking.carrier_tracking_ref)
        picking.write({
            'carrier_tracking_ref': False,
            'carrier_price': 0.0
        })
        return utils.notification(
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
