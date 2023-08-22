import calendar
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, NoReturn, List, Tuple, Sequence
from odoo import _, SUPERUSER_ID, models
from odoo.exceptions import UserError
from odoo.addons.tangerine_delivery_viettelpost.api.viettelpost_client import ViettelpostClient


class Action:
    @staticmethod
    def display_notification(title: str, msg: str, notify_type: Optional[str] = 'success') -> Dict[str, Any]:
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'type': notify_type,
                'message': msg,
                'sticky': False,
            }
        }


class Func:
    @staticmethod
    def get_client_viettelpost(self) -> ViettelpostClient:
        viettelpost_carrier = self.env.ref('tangerine_delivery_viettelpost.free_delivery_carrier_viettelpost')
        if not viettelpost_carrier:
            raise UserError(_('The Viettelpost Carrier does not exist.'))
        client = ViettelpostClient(viettelpost_carrier)
        return client
