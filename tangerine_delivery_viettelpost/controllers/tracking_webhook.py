import functools
from typing import Any
from odoo import SUPERUSER_ID
from odoo.tools import ustr
from odoo.http import request, Controller, route
from odoo.addons.tangerine_delivery_base.settings.status import status
from ..schemas.grab_schemas import TrackingWebhookRequest


def response(status: int, message: str, data: list[dict[str, Any]] | dict[str, Any] | None = None) -> dict[str, Any]:
    response = {'status': status, 'message': message}
    if data:
        response.update({'data': data})
    return response


def validate_api_key(func):
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        api_key = request.httprequest.headers.get('Authorization')
        if not api_key:
            return response(
                message='The header Authorization missing',
                status=status.HTTP_401_UNAUTHORIZED
            )
        api_key_config = request.env['ir.config_parameter'].sudo().get_param('tangerine_delivery_grab.grab_api_key')
        if api_key != api_key_config:
            return response(
                message=f'The Client Secret {api_key} seems to have invalid.',
                status=status.HTTP_403_FORBIDDEN
            )
        request.update_env(SUPERUSER_ID)
        return func(self, *args, **kwargs)

    return wrap


class DeliveriesController(Controller):

    @validate_api_key
    @route('/api/v1/grab/callback', type='json', auth='none', methods=['POST'])
    def grab_callback(self):
        try:
            body = TrackingWebhookRequest(**request.dispatcher.jsonrequest)
            picking_id = request.env['stock.picking'].sudo().search([
                ('carrier_tracking_ref', '=', body.deliveryID)
            ])
            if not picking_id:
                return response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=f'The delivery id {body.deliveryID} not found.'
                )

            status_id = request.env['grab.status'].sudo().search([('code', '=', body.status)])
            if not status_id:
                return response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=f'The status {body.status} does not match my system.'
                )
            payload = {'status_id': status_id.id}
            if body.driver:
                payload.update({
                    'grab_driver_name': body.driver.name,
                    'grab_driver_license_plate': body.driver.licensePlate,
                    'grab_driver_phone': body.driver.phone,
                    'grab_driver_photo_url': body.driver.photoURL,
                    'grab_driver_current_lat': body.driver.currentLat,
                    'grab_driver_current_lng': body.driver.currentLng,
                })
            picking_id.sudo().write(payload)
        except Exception as e:
            return response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, message=ustr(e))
