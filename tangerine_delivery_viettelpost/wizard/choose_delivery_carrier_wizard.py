from odoo import fields, models
from ..settings.constants import settings


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    grab_service_type = fields.Selection(selection=settings.service_type, default='INSTANT', string='Service Type')
    grab_vehicle_type = fields.Selection(selection=settings.vehicle_type, default='BIKE', string='Vehicle Type')

    def _get_shipment_rate(self):
        if self.carrier_id.delivery_type == settings.grab_code:
            context = dict(self.env.context)
            context.update({
                'grab_service_type': self.grab_service_type,
                'grab_vehicle_type': self.grab_vehicle_type
            })
            self.env.context = context
        return super(ChooseDeliveryCarrier, self)._get_shipment_rate()
