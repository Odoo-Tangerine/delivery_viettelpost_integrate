import json
from typing import Dict, Any
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.tangerine_delivery_viettelpost.common.constants import Constants
from odoo.addons.tangerine_delivery_viettelpost.common.func import Func


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'
    _description = 'Delivery Carrier Selection Wizard'

    @staticmethod
    def _compute_price_product(order):
        total = 0.0
        for line in order.order_line:
            total += line.price_subtotal
        return total

    def _prepare_get_matching_service(self) -> Dict[str, Any]:
        payload = {
            'SENDER_PROVINCE': self.order_id.warehouse_id.partner_id.viettelpost_province_id.province_id,
            'SENDER_DISTRICT': self.order_id.warehouse_id.partner_id.viettelpost_district_id.district_id,
            'RECEIVER_PROVINCE': self.order_id.partner_shipping_id.viettelpost_province_id.province_id,
            'RECEIVER_DISTRICT': self.order_id.partner_shipping_id.viettelpost_district_id.district_id,
            'PRODUCT_TYPE': self.viettelpost_product_type,
            'PRODUCT_WEIGHT': self.order_id._get_estimated_weight(),
            'PRODUCT_PRICE': self._compute_price_product(self.order_id),
            'TYPE': 1
        }
        return payload

    def get_matching_service(self):
        client = Func.get_client_viettelpost(self)
        payload = self._prepare_get_matching_service()
        result = client.get_matching_service(payload)
        lst_matching_service = [rec.get('MA_DV_CHINH') for rec in result]
        return {
            'name': _('Add a shipping method'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'context': {'lst_matching_service': lst_matching_service},
            'res_model': 'choose.delivery.carrier',
            'res_id': self.id,
            'target': 'new',
        }

    def _get_domain(self):
        lst_matching_service = self.env.context.get('lst_matching_service', [])
        if lst_matching_service:
            domain = [('code', 'in', lst_matching_service)]
            return domain

    viettelpost_product_type = fields.Selection(Constants.VIETTELPOST_PRODUCT_TYPES.value,
                                                string='Product Type', default='HH')
    viettelpost_national_type = fields.Selection(Constants.VIETTELPOST_NATIONAL_TYPES.value,
                                                 string='National Type', default='1')
    viettelpost_service_type = fields.Many2one('viettelpost.service', string='Service Type',
                                               domain=_get_domain)
    viettelpost_extend_service_type = fields.Many2one('viettelpost.extend.service', string='Extend Service Type')
    viettelpost_order_payment = fields.Selection(Constants.VIETTELPOST_ORDER_PAYMENT.value, string='Order Payment Type',
                                                 help='Viettelpost Order Payment Type', default='1')

    def _prepare_payload_get_rate(self) -> Dict[str, Any]:
        payload = {
            'PRODUCT_WEIGHT': self.order_id._get_estimated_weight(),
            'PRODUCT_PRICE': self._compute_price_product(self.order_id),
            'ORDER_SERVICE_ADD': self.viettelpost_extend_service_type.extend_code or '',
            'ORDER_SERVICE': self.viettelpost_service_type.code,
            'SENDER_PROVINCE': self.order_id.warehouse_id.partner_id.viettelpost_province_id.province_id,
            'SENDER_DISTRICT': self.order_id.warehouse_id.partner_id.viettelpost_district_id.district_id,
            'RECEIVER_PROVINCE': self.order_id.partner_shipping_id.viettelpost_province_id.province_id,
            'RECEIVER_DISTRICT': self.order_id.partner_shipping_id.viettelpost_district_id.district_id,
            'PRODUCT_TYPE': self.viettelpost_product_type,
            'NATIONAL_TYPE': self.viettelpost_national_type
        }
        return payload

    def update_price(self):
        context = dict(self.env.context)
        payload = self._prepare_payload_get_rate()
        if self.carrier_id.delivery_type == 'viettelpost' and not self.viettelpost_service_type:
            raise UserError(_('The field Viettelpost Service Type is required.'))
        context.update({'viettelpost_payload_get_rate': json.dumps(payload)})
        return super(ChooseDeliveryCarrier, self.with_context(context)).update_price()

    @api.onchange('viettelpost_service_type')
    def _onchange_viettelpost_service_type(self):
        for rec in self:
            if rec.viettelpost_service_type:
                return {
                    'domain': {
                        'viettelpost_extend_service_type': [('service_id', '=', rec.viettelpost_service_type.id)]
                    }
                }

    def button_confirm(self):
        self.order_id.with_context(
            viettelpost_servie_type=self.viettelpost_service_type,
            viettelpost_servie_extend_type=self.viettelpost_extend_service_type
        ).set_delivery_line(self.carrier_id, self.delivery_price)
        self.order_id.write({
            'recompute_delivery_price': False,
            'delivery_message': self.delivery_message
        })
