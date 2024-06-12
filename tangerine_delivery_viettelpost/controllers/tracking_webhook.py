from odoo.tools import ustr
from odoo.http import request, Controller, route
from odoo.addons.tangerine_delivery_base.settings.status import status
from odoo.addons.tangerine_delivery_base.settings.utils import validate_api_key, response


class DeliveriesController(Controller):

    @validate_api_key
    @route('/api/v1/webhook/viettelpost', type='json', auth='public', methods=['POST'])
    def viettelpost_callback(self):
        try:
            body = request.dispatcher.jsonrequest
            picking_id = request.env['stock.picking'].sudo().search([
                ('carrier_tracking_ref', '=', body.get('ORDER_NUMBER'))
            ])
            if not picking_id:
                return response(
                    status=status.HTTP_400_BAD_REQUEST.value,
                    message=f'The delivery id {body.get("ORDER_NUMBER")} not found.'
                )

            status_id = request.env['delivery.status'].sudo().search([('code', '=', body.get('ORDER_STATUS'))])
            if not status_id:
                return response(
                    status=status.HTTP_400_BAD_REQUEST.value,
                    message=f'The status {body.get("ORDER_STATUS")} does not match partner system.'
                )
            service_id = request.env['viettelpost.service'].search([('code', '=', body.get('ORDER_SERVICE'))])
            if not service_id:
                return response(
                    status=status.HTTP_400_BAD_REQUEST.value,
                    message=f'The order service {body.get("ORDER_SERVICE")} does not match partner system.'
                )

            picking_id.sudo().write({
                'status_id': status_id.id,
                'viettelpost_service_id': service_id.id,
                'shipping_weight': body.get("PRODUCT_WEIGHT")
            })
            return response(
                status=status.HTTP_200_OK.value,
                message=f'Receive order callback {body.get("ORDER_NUMBER")} successfully.'
            )
        except Exception as e:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR.value, message=ustr(e))
