from odoo import models, fields


class ViettelPostStatus(models.Model):
    _name = 'viettelpost.status'
    _description = 'ViettelPost Status'
    _order = 'code asc'

    name = fields.Char(string='Name', required=True, readonly=True)
    code = fields.Char(string='Code', required=True, readonly=True)
    description = fields.Char(string='Description', required=True, readonly=True)