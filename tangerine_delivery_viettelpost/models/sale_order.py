import json

from odoo import fields, models, _, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    viettelpost_money_collection = fields.Monetary(string='Money Collection',
                                                   help='Is the amount that the customer wants Viettelpost to collect for the recipient',
                                                   tracking=True, readonly=True,
                                                   currency_field='currency_id')
    viettelpost_money_total = fields.Monetary(string='Total Money', tracking=True, readonly=True,
                                              currency_field='currency_id')
    viettelpost_money_total_fee = fields.Monetary(string='Main Charge', tracking=True, readonly=True,
                                                  currency_field='currency_id')
    viettelpost_money_fee = fields.Monetary(string='Sub Fee', help='e.g Oil fee, connection fee,…', tracking=True,
                                            readonly=True, currency_field='currency_id')
    viettelpost_money_collection_fee = fields.Monetary(string='Money Collection Fee', tracking=True, readonly=True,
                                                       currency_field='currency_id')
    viettelpost_money_other_fee = fields.Monetary(string='Other fee', help='e.g Pack fee, ...', tracking=True,
                                                  readonly=True, currency_field='currency_id')
    viettelpost_fee_vat = fields.Monetary(string='Sum of VAT', tracking=True, readonly=True,
                                          currency_field='currency_id')

    viettelpost_status = fields.Many2one('viettelpost.status', string='Status', tracking=True, readonly=True)
    viettelpost_person_in_charge = fields.Char(string='Person In Charge', tracking=True, readonly=True)
    viettelpost_phone = fields.Char(string='Phone', tracking=True, readonly=True,
                                    help='The phone number of person in charge')
    viettelpost_note = fields.Text(string='Note', tracking=True, readonly=True)
    viettelpost_waybill_order = fields.Char(string='Waybill Order', tracking=True, readonly=True)
    viettelpost_product_type = fields.Selection([
        ('TH', 'Envelope'), ('HH', 'Goods')
    ], string='Product Type', help='Viettelpost Product Type', tracking=True, readonly=True)
    viettelpost_national_type = fields.Selection([
        ('1', 'Inland'), ('0', 'International')
    ], string='National Type', help='Viettelpost National Type', tracking=True, readonly=True)
    viettelpost_service_type = fields.Many2one('viettelpost.service',
                                               help='Viettelpost Service Type', string='Service Type',
                                               tracking=True, readonly=True)
    viettelpost_extend_service_type = fields.Many2one('viettelpost.extend.service',
                                                      string='Extend Service Type', tracking=True, readonly=True,
                                                      help='Viettelpost Extend Service Type')
    viettelpost_order_payment = fields.Selection([
        ('1', 'Uncollect money'),
        ('2', 'Collect express fee and price of goods'),
        ('3', 'Collect price of goods'),
        ('4', 'Collect express fee')
    ], string='Order Payment Type', help='Viettelpost Order Payment Type', tracking=True, readonly=True)

    def _create_delivery_line(self, carrier, price_unit):
        SaleOrderLine = self.env['sale.order.line']
        context = {}
        if self.partner_id:
            # set delivery detail in the customer language
            context['lang'] = self.partner_id.lang
            carrier = carrier.with_context(lang=self.partner_id.lang)

        # Apply fiscal position
        taxes = carrier.product_id.taxes_id.filtered(lambda t: t.company_id.id == self.company_id.id)
        taxes_ids = taxes.ids
        if self.partner_id and self.fiscal_position_id:
            taxes_ids = self.fiscal_position_id.map_tax(taxes).ids

        # Create the sales order line

        if carrier.product_id.description_sale:
            so_description = '%s: %s' % (carrier.name,
                                        carrier.product_id.description_sale)
        else:
            viettelpost_service = self.env.context.get('viettelpost_servie_type')
            viettelpost_servie_extend_type = self.env.context.get('viettelpost_servie_extend_type')
            if viettelpost_service:
                viettelpost_service_description = f'{viettelpost_service.display_name}\n{viettelpost_servie_extend_type.display_name if viettelpost_servie_extend_type else ""}'
                so_description = viettelpost_service_description
            else:
                so_description = carrier.name
        values = {
            'order_id': self.id,
            'name': so_description,
            'product_uom_qty': 1,
            'product_uom': carrier.product_id.uom_id.id,
            'product_id': carrier.product_id.id,
            'tax_id': [(6, 0, taxes_ids)],
            'is_delivery': True,
        }
        if carrier.invoice_policy == 'real':
            values['price_unit'] = 0
            values['name'] += _(' (Estimated Cost: %s )', self._format_currency_amount(price_unit))
        else:
            values['price_unit'] = price_unit
        if carrier.free_over and self.currency_id.is_zero(price_unit) :
            values['name'] += '\n' + _('Free Shipping')
        if self.order_line:
            values['sequence'] = self.order_line[-1].sequence + 1
        sol = SaleOrderLine.sudo().create(values)
        del context
        return sol
