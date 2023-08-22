from typing import List
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.addons.tangerine_delivery_viettelpost.dataclass.viettelpost_warehouse import Warehouse
from odoo.addons.tangerine_delivery_viettelpost.common.func import Func


class ViettelpostWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    is_warehouse_viettelpost = fields.Boolean(default=False)
    viettelpost_group_address_id = fields.Integer(string='Group Address ID', readonly=True)
    viettelpost_customer_id = fields.Integer(string='Customer ID', readonly=True)

    @staticmethod
    def _validate_address(province_id, district_id, ward_id):
        if not province_id:
            raise UserError(_('The province not found.'))
        elif not district_id:
            raise UserError(_('The district not found'))
        elif not ward_id:
            raise UserError(_('The ward not found'))

    def _get_address(self, data: Warehouse):
        province_id = self.env['viettelpost.province'].search(
            [('province_id', '=', data.province_id)])
        district_id = province_id.district_ids.search(
            [('district_id', '=', data.district_id)])
        ward_id = district_id.ward_ids.search([('ward_id', '=', data.ward_id)])
        self._validate_address(province_id, district_id, ward_id)
        return province_id, district_id, ward_id

    @api.model
    def sync_warehouses(self):
        try:
            client = Func.get_client_viettelpost(self)
            data_warehouses: list = []
            result = client.sync_warehouses()
            if not result: return
            lst_dataclass_store: List[Warehouse] = [Warehouse(*Warehouse.parser_dict(res)) for res in result]
            grp_address_ids: List[int] = [rec.group_address_id for rec in lst_dataclass_store]
            lst_grp_address_ids = self.search([('viettelpost_group_address_id', 'in', grp_address_ids)])
            grp_address_ids: List[int] = [rec.viettelpost_group_address_id for rec in lst_grp_address_ids]
            for data in lst_dataclass_store:
                if data.group_address_id not in grp_address_ids:
                    province_id, district_id, ward_id = self._get_address(data)
                    partner_id = self.env['res.partner'].create(Warehouse.parser_class_partner(data,
                                                                viettelpost_province_id=province_id.id,
                                                                viettelpost_district_id=district_id.id,
                                                                viettelpost_ward_id=ward_id.id))
                    data_warehouses.append(Warehouse.parser_class(data, partner_id=partner_id.id))
            if data_warehouses:
                self.create(data_warehouses)
        except Exception as e:
            raise UserError(_(f'Sync Warehouse failed. Error: {str(e)}'))
