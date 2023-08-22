from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.addons.tangerine_delivery_viettelpost.common.func import Func, Action
from odoo.addons.tangerine_delivery_viettelpost.common.constants import Constants


class PrintWaybillWizard(models.TransientModel):
    _name = 'viettelpost.print.waybill'
    _description = 'Viettelpost Print waybill'

    @api.model
    def default_get(self, fields_list):
        values = super(PrintWaybillWizard, self).default_get(fields_list)
        if not values.get('picking_id') and 'active_model' in self._context \
                and self._context['active_model'] == 'stock.picking':
            values['picking_id'] = self._context.get('active_id')
        return values

    picking_id = fields.Many2one('stock.picking', string='Order', readonly=1)
    waybill_code = fields.Char(related='picking_id.carrier_tracking_ref', string='Tracking Reference')

    def _get_url_print_waybill(self, token: str) -> (str, str):
        type_print = self.env.context.get('type_print')
        if type_print == 'a5':
            url = Constants.VIETTELPOST_PRINT_URL_A5.value.format(token)
        elif type_print == 'a6':
            url = Constants.VIETTELPOST_PRINT_URL_A6.value.format(token)
        elif type_print == 'a7':
            url = Constants.VIETTELPOST_PRINT_URL_A7.value.format(token)
        else:
            raise UserError(_('Print type not found.'))
        return url

    def action_print_waybill(self):
        try:
            if not self.picking_id.carrier_tracking_ref:
                raise UserError(_('The carrier tracking ref not found.'))
            client = Func.get_client_viettelpost(self)
            payload = self._prepare_data_print_waybill()
            token = client.get_link_print(payload)
            url = self._get_url_print_waybill(token)
            body = f'<a href="{url}" target="_blank" style="padding: 5px 10px; color: #FFFFFF; text-decoration: none; '\
                   f'background-color: #875A7B; border: 1px solid #875A7B; border-radius: 3px">View link waybill</a>'
            self.picking_id.message_post(body=body)
            return Action.display_notification(title='Print waybill code successfully.',
                                               msg='Please click button [View link waybill] in Chatter to view.')
        except Exception as e:
            raise UserError(_(f'Print waybill failed. {e}'))

    def _prepare_data_print_waybill(self) -> dict:
        payload: dict = {
            'ORDER_ARRAY': [self.picking_id.carrier_tracking_ref],
            # 'EXPIRY_TIME': int((datetime.utcnow() + timedelta(hours=1)).timestamp()) * 1000,
        }
        return payload
