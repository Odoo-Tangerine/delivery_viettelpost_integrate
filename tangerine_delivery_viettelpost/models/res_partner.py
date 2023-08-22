import hashlib
import base64
import string
import secrets

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    viettelpost_province_id = fields.Many2one('viettelpost.province', string='Province')
    viettelpost_district_id = fields.Many2one('viettelpost.district', string='District')
    viettelpost_ward_id = fields.Many2one('viettelpost.ward', string='Ward')
    viettelpost_api_key = fields.Char(string='API Key', help='Authorization for webhook Viettelpost carrier')

    @api.onchange('viettelpost_ward_id')
    def _onchange_viettelpost_ward_id(self):
        for rec in self:
            if rec.viettelpost_ward_id:
                rec.viettelpost_district_id = rec.viettelpost_ward_id.district_id
                rec.viettelpost_province_id = rec.viettelpost_ward_id.district_id.province_id

    @staticmethod
    def generate_code_verifier(length=80):
        alphabet = string.ascii_letters + string.digits + "-._~"
        code_verifier = ''.join(secrets.choice(alphabet) for _ in range(length))
        return code_verifier

    @staticmethod
    def create_code_challenge(code_verifier):
        code_verifier_bytes = code_verifier.encode('utf-8')
        code_challenge = hashlib.sha256(code_verifier_bytes).digest()
        code_challenge_base64 = base64.urlsafe_b64encode(code_challenge).rstrip(b'=').decode('utf-8')
        return code_challenge_base64

    def generate_api_key(self):
        self.sudo().write({'viettelpost_api_key': f"_{self.create_code_challenge(self.generate_code_verifier())}"})
