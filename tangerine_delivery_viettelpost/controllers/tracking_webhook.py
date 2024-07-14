import logging
from odoo.tools import ustr
from odoo.http import request, Controller, route
from odoo.addons.tangerine_delivery_base.settings.status import status
from odoo.addons.tangerine_delivery_base.settings.utils import authentication, response

_logger = logging.getLogger(__name__)


class DeliveriesController(Controller):

    @authentication
    @route('/webhook/v1/delivery/viettelpost', type='json', auth='public', methods=['POST'])
    def viettelpost_callback(self):
        try:
            body = request.dispatcher.jsonrequest
            _logger.info(f'WEBHOOK VIETTELPOST START - BODY: {body}')
            picking_id = request.env['stock.picking'].sudo().search([
                ('carrier_tracking_ref', '=', body.get('ORDER_NUMBER'))
            ])
            if not picking_id:
                _logger.error(f'WEBHOOK VIETTELPOST ERROR: The delivery id {body.get("ORDER_NUMBER")} not found.')
                return response(
                    status=status.HTTP_400_BAD_REQUEST.value,
                    message=f'The delivery id {body.get("ORDER_NUMBER")} not found.'
                )
            status_id = request.env['delivery.status'].sudo().search([
                ('code', '=', body.get('ORDER_STATUS')),
                ('provider_id', '=', picking_id.carrier_id.id)
            ])
            if not status_id:
                _logger.error(f'WEBHOOK VIETTELPOST ERROR: The status {body.get("ORDER_STATUS")} invalid.')
                return response(
                    status=status.HTTP_400_BAD_REQUEST.value,
                    message=f'The status {body.get("ORDER_STATUS")} invalid.'
                )
            picking_id.sudo().write({'delivery_status_id': status_id.id})
            _logger.info(f'WEBHOOK VIETTELPOST SUCCESS: Receive order callback {body.get("deliveryID")} successfully.')
            return response(
                status=status.HTTP_200_OK.value,
                message=f'Receive order callback {body.get("ORDER_NUMBER")} successfully.'
            )
        except Exception as e:
            _logger.exception(f'WEBHOOK VIETTELPOST EXCEPTION: {ustr(e)}')
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR.value, message=ustr(e))
