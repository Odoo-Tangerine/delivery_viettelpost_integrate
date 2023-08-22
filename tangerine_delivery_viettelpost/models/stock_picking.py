import calendar
from datetime import datetime, timedelta
from typing import Final, Sequence, List, Tuple, Dict, Any, NoReturn
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.tangerine_delivery_viettelpost.common.func import Func
from odoo.addons.tangerine_delivery_viettelpost.dataclass.viettelpost_order import Order

ORDER_PAYMENT_COLLECT_EXPRESS_FEE: Final[str] = '4'
ORDER_PAYMENT_COLLECT_FEE_AND_PRICE_OF_GOOD: Final[str] = '2'


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _default_service_lcod(self):
        lcod_service = self.env['viettelpost.service'].search([('code', '=', 'LCOD')])
        return lcod_service.id

    def _get_domain_service_type(self):
        lst_matching_service = self.env.context.get('lst_matching_service')
        if lst_matching_service:
            domain = [('code', 'in', lst_matching_service)]
            return domain

    def _get_domain_extend_service_type(self):
        service_id = self._default_service_lcod()
        return [('service_id', '=', service_id)]

    def _get_default_weight_uom_gram(self):
        return self.env.ref('uom.product_uom_gram').display_name

    weight_uom_name_gram = fields.Char(string='Weight unit of measure label', compute='_compute_weight_uom_name_gram',
                                  readonly=True, default=_get_default_weight_uom_gram)

    def _compute_weight_uom_name_gram(self):
        for picking_type in self:
            picking_type.weight_uom_name_gram = self.env.ref('uom.product_uom_gram').display_name

    viettelpost_shipping_weight = fields.Float(string='Weight of Viettelpost', readonly=True, tracking=True)
    viettelpost_product_type = fields.Selection([('TH', 'Envelope'), ('HH', 'Goods')], string='Product Type',
                                                default='HH', help='Viettelpost Product Type', tracking=True)
    viettelpost_national_type = fields.Selection([('1', 'Inland'), ('0', 'International')], string='National Type',
                                                 default='1', help='Viettelpost National Type', tracking=True)
    viettelpost_service_type = fields.Many2one('viettelpost.service', help='Viettelpost Service Type',
                                               string='Service Type',  default=_default_service_lcod, tracking=True,
                                               domain=_get_domain_service_type)
    viettelpost_extend_service_type = fields.Many2one('viettelpost.extend.service', string='Extend Service Type',
                                                      domain=_get_domain_extend_service_type,
                                                      help='Viettelpost Extend Service Type', tracking=True)
    viettelpost_order_payment = fields.Selection([
        ('1', 'Uncollect money'),
        ('2', 'Collect express fee and price of goods'),
        ('3', 'Collect price of goods'),
        ('4', 'Collect express fee')
    ], string='Order Payment Type', help='Viettelpost Order Payment Type', default='1', tracking=True)

    viettelpost_status = fields.Many2one(related='sale_id.viettelpost_status')
    viettelpost_person_in_charge = fields.Char(related='sale_id.viettelpost_person_in_charge')
    viettelpost_phone = fields.Char(related='sale_id.viettelpost_phone')
    viettelpost_note = fields.Text(related='sale_id.viettelpost_note')

    @api.onchange('viettelpost_service_type')
    def _onchange_viettelpost_service_type(self):
        for rec in self:
            if rec.viettelpost_service_type:
                return {
                    'domain': {
                        'viettelpost_extend_service_type': [('service_id', '=', rec.viettelpost_service_type.id)]
                    }
                }

    def _find_partner(self) -> models:
        vat = self.env['ir.config_parameter'].sudo().get_param('viettelpost_vat')
        partner = self.env['res.partner'].sudo().search([('vat', '=', vat)], order='id desc', limit=1)
        return partner

    @staticmethod
    def _get_datetime() -> Sequence[str]:
        current_month, current_year = datetime.now().month, datetime.now().year
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        start_datetime = f'{current_year:04d}-{current_month:02d}-01 00:00:00'
        end_datetime = f'{current_year:04d}-{current_month:02d}-{days_in_month} 23:59:59'
        return start_datetime, end_datetime

    def _get_purchase_order_line(self, order: Order) -> List[Tuple[int, int, Dict[str, Any]]]:
        return [(0, 0, {
            'product_id': self.carrier_id.product_id.id,
            'name': f'{self.carrier_tracking_ref}',
            'price_unit': order.money_total,
            'product_qty': 1.0,
            'order_id': self.sale_id.id,
            'taxes_id': [(6, 0, self.carrier_id.product_id.taxes_id.ids)]
        })]

    def _get_body_purchase_order(self, order: Order, partner: models, uid: int, end_datetime: str) -> Dict[str, Any]:
        body = {
            'company_id': self.sale_id.company_id.id,
            'user_id': uid,
            'picking_type_id': self.picking_type_id.warehouse_id.in_type_id.id,
            'partner_id': partner.id,
            'state': 'draft',
            'date_order': datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S') - timedelta(hours=7),
            'order_line': self._get_purchase_order_line(order)
        }
        return body

    def _handle_purchase_order(self, order: Order) -> NoReturn:
        PO = self.env['purchase.order'].sudo()
        partner = self._find_partner()
        if not partner:
            raise UserError(_('[Create Purchase Auto] - Partner Viettelpost Not Found'))
        start_datetime, end_datetime = self._get_datetime()
        purchase_order = PO.search([
            ('company_id', '=', self.sale_id.company_id.id),
            ('partner_id', '=', partner.id),
            ('create_date', '>=', start_datetime),
            ('create_date', '<=', end_datetime),
            ('state', '=', 'draft'),
            ('picking_type_id', '=', self.picking_type_id.warehouse_id.in_type_id.id)
        ])
        if not purchase_order:
            PO.create(self._get_body_purchase_order(order, partner, self.env.uid, end_datetime))
        else:
            purchase_order.write({'order_line': self._get_purchase_order_line(order)})

    def _update_sale_order(self, order: Order) -> NoReturn:
        self.sale_id.write({
            'viettelpost_waybill_order': order.order_number,
            'viettelpost_status': self.env.ref('tangerine_delivery_viettelpost.viettelpost_status_1').id,
            'viettelpost_money_collection': order.money_collection,
            'viettelpost_money_total': order.money_total,
            'viettelpost_money_total_fee': order.money_total_fee,
            'viettelpost_money_fee': order.money_fee,
            'viettelpost_money_collection_fee': order.money_collection_fee,
            'viettelpost_money_other_fee': order.money_other_fee,
            'viettelpost_fee_vat': order.fee_vat,
            'viettelpost_product_type': self.viettelpost_product_type,
            'viettelpost_national_type': self.viettelpost_national_type,
            'viettelpost_service_type': self.viettelpost_service_type.id,
            'viettelpost_extend_service_type': self.viettelpost_extend_service_type.id,
            'viettelpost_order_payment': self.viettelpost_order_payment
        })
        if self.viettelpost_order_payment in [ORDER_PAYMENT_COLLECT_FEE_AND_PRICE_OF_GOOD,
                                              ORDER_PAYMENT_COLLECT_EXPRESS_FEE]:
            self.sale_id.with_context(
                viettelpost_servie_type=self.viettelpost_service_type,
                viettelpost_servie_extend_type=self.viettelpost_extend_service_type
            ).set_delivery_line(self.carrier_id, order.money_total)

    def _validate_data_input(self):
        if not self.carrier_id and self.carrier_id.delivery_type != 'viettelpost':
            raise UserError(_('Shipping Method must be Viettelpost'))
        elif not self.viettelpost_product_type:
            raise UserError(_('The [Viettelpost Product Type] field is required'))
        elif not self.viettelpost_national_type:
            raise UserError(_('The [Viettelpost National Type] field is required'))
        elif not self.viettelpost_order_payment:
            raise UserError(_('The [Viettelpost Order Payment] field is required'))
        elif not self.viettelpost_service_type:
            raise UserError(_('The [Viettelpost Service Type] field is required'))
        elif not self.picking_type_id:
            raise UserError(_('The field [Picking Type] is required'))
        elif not self.picking_type_id.warehouse_id:
            raise UserError(_('The [Warehouse] field is required.\n'
                              'Go to check in Model: Stock Picking Type'))
        elif not self.picking_type_id.warehouse_id.viettelpost_group_address_id:
            raise UserError(_('The [Group Address ID] field is required.\n'
                              'Go to check in Model: Warehouses -> Page: Viettelpost Information'))
        elif not self.picking_type_id.warehouse_id.viettelpost_customer_id:
            raise UserError(_('The [Customer ID] field is required.\n'
                              'Go to check in Model: Warehouses -> Page: Viettelpost Information'))
        elif not self.picking_type_id.warehouse_id.partner_id:
            raise UserError(_('The [Address] field is required.\nGo to check in Model: Warehouses'))
        elif not self.picking_type_id.warehouse_id.partner_id.viettelpost_province_id:
            raise UserError(_('The [Province] field of [Warehouse Address] is required.\n'
                              'Go to check in Model: Contacts -> Page: Viettelpost Address'))
        elif not self.picking_type_id.warehouse_id.partner_id.viettelpost_district_id:
            raise UserError(_('The [District] field of [Warehouse Address] is required.\n'
                              'Go to check in Model: Contacts -> Page: Viettelpost Address'))
        elif not self.picking_type_id.warehouse_id.partner_id.viettelpost_ward_id:
            raise UserError(_('The [Ward] field of [Warehouse Address] is required.\n'
                              'Go to check in Model: Contacts -> Page: Viettelpost Address'))
        elif not self.partner_id:
            raise UserError(_('The [Delivery Address] field is required.'))
        elif not self.partner_id.phone:
            raise UserError(_('The [Phone] field of [Delivery Address] is required.\n'
                              'Go to check in Model: Contacts'))
        elif not self.partner_id.viettelpost_province_id:
            raise UserError(_('The [Province] field of [Delivery Address] is required.\n'
                              'Go to check in Model: Contacts -> Page: Viettelpost Address'))
        elif not self.partner_id.viettelpost_district_id:
            raise UserError(_('The [District] field of [Delivery Address] is required.\n'
                              'Go to check in Model: Contacts -> Page: Viettelpost Address'))
        elif not self.partner_id.viettelpost_ward_id:
            raise UserError(_('The [Ward] field of [Delivery Address] is required.\n'
                              'Go to check in Model: Contacts -> Page: Viettelpost Address'))

    def action_booking_viettelpost(self):
        self._validate_data_input()
        client = Func.get_client_viettelpost(self)
        sender_id = self.picking_type_id.warehouse_id
        payload = {
            **Order.build_dictionary_sender(sender_id.partner_id,
                                            group_address_id=sender_id.viettelpost_group_address_id,
                                            customer_id=sender_id.viettelpost_customer_id),
            **Order.build_dictionary_recipient(self.partner_id),
            **Order.build_dictionary_order(self)
        }
        if self.carrier_id.viettelpost_check_unique_order:
            payload.update({'CHECK_UNIQUE': True})
        data = client.create_bill(payload)
        order = Order(*Order.parser_response_order(data))
        self._update_sale_order(order)
        self.write({
            'carrier_tracking_ref': order.order_number,
            'viettelpost_shipping_weight': order.exchange_weight
        })
        self._handle_purchase_order(order)

    @staticmethod
    def _compute_price_product(order):
        total = 0.0
        for line in order.order_line:
            total += line.price_subtotal
        return total

    def _prepare_get_matching_service(self) -> Dict[str, Any]:
        payload = {
            'SENDER_PROVINCE': self.picking_type_id.warehouse_id.partner_id.viettelpost_province_id.province_id,
            'SENDER_DISTRICT': self.picking_type_id.warehouse_id.partner_id.viettelpost_district_id.district_id,
            'RECEIVER_PROVINCE': self.partner_id.viettelpost_province_id.province_id,
            'RECEIVER_DISTRICT': self.partner_id.viettelpost_district_id.district_id,
            'PRODUCT_TYPE': self.viettelpost_product_type,
            'PRODUCT_WEIGHT': self.sale_id._get_estimated_weight(),
            'PRODUCT_PRICE': self._compute_price_product(self.sale_id),
            'TYPE': 1
        }
        return payload

    def _validate_data_get_matching_service(self):
        if not self.picking_type_id.warehouse_id:
            raise UserError(_('The [Warehouse] field is required.\n'
                              'Go to check in Model: Stock Picking Type'))
        elif not self.picking_type_id.warehouse_id.partner_id:
            raise UserError(_('The [Address] field is required.\nGo to check in Model: Warehouses'))
        elif not self.picking_type_id.warehouse_id.partner_id.viettelpost_province_id:
            raise UserError(_('The [Province] field of [Warehouse Address] is required.\n'
                              'Go to check in Model: Contacts -> Page: Viettelpost Address'))
        elif not self.picking_type_id.warehouse_id.partner_id.viettelpost_district_id:
            raise UserError(_('The [District] field of [Warehouse Address] is required.\n'
                              'Go to check in Model: Contacts -> Page: Viettelpost Address'))
        elif not self.partner_id:
            raise UserError(_('The [Delivery Address] field is required.'))
        elif not self.partner_id.viettelpost_province_id:
            raise UserError(_('The [Province] field of [Delivery Address] is required.\n'
                              'Go to check in Model: Contacts -> Page: Viettelpost Address'))
        elif not self.partner_id.viettelpost_district_id:
            raise UserError(_('The [District] field of [Delivery Address] is required.\n'
                              'Go to check in Model: Contacts -> Page: Viettelpost Address'))
        elif not self.viettelpost_product_type:
            raise UserError(_('The [Product Type] field is required.'))

    def get_matching_service(self):
        client = Func.get_client_viettelpost(self)
        payload = self._prepare_get_matching_service()
        result = client.get_matching_service(payload)
        lst_matching_service = [rec.get('MA_DV_CHINH') for rec in result]
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'target': 'current',
            'context': {
                'lst_matching_service': lst_matching_service,
                'is_get_matching': True
            },
            'res_id': self.id
        }
