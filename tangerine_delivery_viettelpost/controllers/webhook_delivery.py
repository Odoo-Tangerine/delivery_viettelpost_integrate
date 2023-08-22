import functools
import logging
from typing import Dict, Any
from odoo import SUPERUSER_ID
from odoo.tools import ustr
from odoo.http import request, Controller, route
from odoo.addons.tangerine_delivery_viettelpost.dataclass.viettelpost_webhook import Webhook
_logger = logging.getLogger(__name__)


def response(message: str, status: int) -> Dict[str, Any]:
    return {'status': status, 'message': message}


def get_next_sequence() -> str:
    sequence = request.env.ref('tangerine_delivery_viettelpost.seq_viettelpost_webhook_history')
    next_document = sequence.get_next_char(sequence.number_next_actual)
    request.env.cr.execute('''SELECT name FROM viettelpost_webhook_history''')
    query_res = request.env.cr.fetchall()
    while next_document in [res[0] for res in query_res]:
        next_tmp = request.env['ir.sequence'].next_by_code(sequence.code)
        next_document = next_tmp
    return next_document


def validate_api_key(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        api_key = request.httprequest.headers.get('Authorization')
        WebhookHistory = request.env['viettelpost.webhook.history'].sudo()
        if not api_key:
            WebhookHistory.create(dict(body=request.dispatcher.jsonrequest,
                                       status=401,
                                       message=f'The header Authorization missing',
                                       name=get_next_sequence()))
            return response(message='The header Authorization missing', status=401)
        partner_id = request.env['res.partner'].sudo().search([('viettelpost_api_key', '=', api_key)])
        if not partner_id:
            WebhookHistory.create(dict(body=request.dispatcher.jsonrequest,
                                       status=404,
                                       message=f'The token {api_key} seems to have invalid',
                                       name=get_next_sequence()))
            return response(message=f'The API KEY {api_key} seems to have invalid.', status=404)
        request.update_env(SUPERUSER_ID)
        return func(self, *args, **kwargs)
    return wrap


class WebhookDeliController(Controller):

    @validate_api_key
    @route('/api/v1/webhook/viettelpost', type='json', auth='user')
    def viettelpost_callback(self):
        try:
            webhook = Webhook(*Webhook.parser_dict(request.dispatcher.jsonrequest.get('DATA')))
            picking_id = request.env['stock.picking'].search([('carrier_tracking_ref', '=', webhook.order_number)])
            WebhookHistory = request.env['viettelpost.webhook.history'].sudo()
            if not picking_id:
                WebhookHistory.create(dict(body=request.dispatcher.jsonrequest,
                                           status=404,
                                           message=f'The order reference {webhook.order_number} not found',
                                           name=get_next_sequence()))
                return response(message='The order number not found.', status=404)
            status_id = request.env['viettelpost.status'].search([('code', '=', str(webhook.order_status))])
            payload_do = {
                'viettelpost_shipping_weight': float(webhook.product_weight)
            }
            if picking_id.viettelpost_service_type.code != webhook.service:
                service_id = request.env['viettelpost.service'].search([('code', '=', webhook.service)])
                payload_do.update({
                    'viettelpost_service_type': service_id.id if service_id else False
                })
            picking_id.write(payload_do)
            picking_id.sale_id.write({
                'viettelpost_status': status_id.id if status_id else False,
                'viettelpost_person_in_charge': webhook.person_in_charge,
                'viettelpost_phone': webhook.phone_number,
                'viettelpost_note': webhook.note,
                'viettelpost_money_total': webhook.money_total,
                'viettelpost_money_total_fee': webhook.money_total_fee,
                'viettelpost_money_collection': webhook.money_collection,
                'viettelpost_money_collection_fee': webhook.money_feecod
            })
            WebhookHistory.create(dict(body=request.dispatcher.jsonrequest,
                                       status=200,
                                       message='Successfully',
                                       name=get_next_sequence()))
            return response(message='Successfully', status=200)
        except Exception as e:
            request.env['viettelpost.webhook.history'].sudo().create(dict(body=request.dispatcher.jsonrequest,
                                                                          status=500,
                                                                          message=ustr(e),
                                                                          name=get_next_sequence()))
            return response(message=ustr(e), status=500)
