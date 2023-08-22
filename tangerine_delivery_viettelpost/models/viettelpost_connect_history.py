from odoo import fields, models


class ViettelpostRequestAPIHistory(models.Model):
    _name = 'viettelpost.connect.history'
    _description = 'Logging request api to ViettelPost'
    _order = 'create_date desc'

    name = fields.Char(string='Request', required=True, readonly=True)
    status = fields.Integer(string='Status', required=True, readonly=True)
    message = fields.Char(string='Message', required=True, readonly=True)
    url = fields.Char(string='Url', required=True, readonly=True)
    method = fields.Char(string='Method', required=True, readonly=True)
    body = fields.Text(string='Body', readonly=True)
    request_id = fields.Char(string='Request Id', required=True, readonly=True)