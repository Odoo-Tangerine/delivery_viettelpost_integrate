from odoo import fields, models, _, api
from odoo.exceptions import UserError
from odoo.tools import ustr
from odoo.addons.tangerine_delivery_viettelpost.common.func import Func


class ViettelpostRegisterWarehouse(models.Model):
    _name = 'viettelpost.register.warehouse'
    _description = 'Viettelpost Register Warehouse'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Short Name', required=True)
    phone = fields.Char(string='Phone', required=True)
    street = fields.Char(string='Street', required=True)
    viettelpost_province_id = fields.Many2one('viettelpost.province', string='Province', required=True)
    viettelpost_district_id = fields.Many2one('viettelpost.district', string='District', required=True)
    viettelpost_ward_id = fields.Many2one('viettelpost.ward', string='Ward', required=True)

    @api.onchange('viettelpost_ward_id')
    def _onchange_viettelpost_ward_id(self):
        for rec in self:
            if rec.viettelpost_ward_id:
                rec.viettelpost_district_id = rec.viettelpost_ward_id.district_id
                rec.viettelpost_province_id = rec.viettelpost_ward_id.district_id.province_id

    def register_warehouse(self):
        try:
            client = Func.get_client_viettelpost(self)
            dataset = client.register_warehouse({
                'NAME': self.name,
                'PHONE': self.phone,
                'ADDRESS': self.street,
                'WARDS_ID': self.viettelpost_ward_id.ward_id
            })
            for data in dataset:
                warehouse_id = self.env['stock.warehouse'].search([('viettelpost_group_address_id', '=', data['groupaddressId'])])
                if not warehouse_id:
                    partner_id = self.env['res.partner'].create({
                        'name': data['name'],
                        'phone': data['phone'],
                        'street': data['address'],
                        'viettelpost_province_id': self.viettelpost_province_id.id,
                        'viettelpost_district_id': self.viettelpost_district_id.id,
                        'viettelpost_ward_id': self.viettelpost_ward_id.id
                    })
                    self.env['stock.warehouse'].create({
                        'name': data['name'],
                        'code': self.code,
                        'viettelpost_group_address_id': data['groupaddressId'],
                        'viettelpost_customer_id': data['cusId'],
                        'partner_id': partner_id.id
                    })
                    return {'type': 'ir.actions.client', 'tag': 'reload'}
        except Exception as e:
            raise UserError(_(f'Register warehouse failed. Error: {ustr(e)}'))