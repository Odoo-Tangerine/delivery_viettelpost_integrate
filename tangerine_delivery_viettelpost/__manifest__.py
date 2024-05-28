# -*- coding: utf-8 -*-
{
    'name': 'Viettelpost Express Shipping',
    'summary': """Viettelpost express shipping module will allow shippers to easily place, cancel, get quotes, and track orders via simple integration for delivery in Odoo.""",
    'author': 'Long Duong Nhat',
    'category': 'Inventory/Delivery',
    'support': 'odoo.tangerine@gmail.com',
    'version': '17.0.1.0',
    'depends': ['tangerine_delivery_base'],
    'data': [
        'data/delivery_grab_data.xml',
        'data/grab_route_api_data.xml',
        'data/grab_status_data.xml',
        'data/ir_cron.xml',
        'data/res_partner_data.xml',
        'wizard/choose_delivery_carrier_wizard_views.xml',
        'views/delivery_grab_views.xml',
        'views/stock_picking_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'images': ['static/description/thumbnail.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
    'currency': 'USD',
    'price': 68.00
}