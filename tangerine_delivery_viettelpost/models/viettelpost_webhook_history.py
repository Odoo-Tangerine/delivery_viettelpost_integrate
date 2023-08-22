from odoo import fields, models


class ViettelpostRequestAPIHistory(models.Model):
    _name = 'viettelpost.webhook.history'
    _description = 'Logging data webhook API From ViettelPost'
    _order = 'create_date desc'

    name = fields.Char(string='Request', required=True, readonly=True)
    status = fields.Integer(string='Status', required=True, readonly=True)
    message = fields.Char(string='Message', required=True, readonly=True)
    body = fields.Text(string='Body', readonly=True)
