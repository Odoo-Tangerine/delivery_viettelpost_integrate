# -*- coding: utf-8 -*-
{
    'name': 'Viettelpost Shipping',
    'summary': """The addon integrates ViettelPost's API for delivery in Odoo.""",
    'description': """
        The Delivery ViettelPost addon is an Odoo integration that connects seamlessly to ViettelPost's API, 
        enabling efficient domestic and international package delivery and courier management. It streamlines 
        shipping logistics, tracking, and improves overall delivery processes within the Odoo ERP system for a 
        smooth customer experience.
    """,
    'author': "Long Duong Nhat",
    'category': 'Inventory/Delivery',
    'version': '16.0.1.0',
    'depends': ['stock', 'mail', 'delivery', 'contacts', 'purchase', 'uom'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/ir_config_parameters.xml',
        'data/ir_cron.xml',
        'data/delivery_viettelpost_data.xml',
        'data/viettelpost_status_data.xml',
        'data/res_partner_data.xml',
        'wizard/choose_delivery_carrier_views.xml',
        'wizard/viettelpost_print_waybill_views.xml',
        'wizard/viettelpost_register_warehouse_views.xml',
        'views/viettelpost_province_views.xml',
        'views/viettelpost_district_views.xml',
        'views/viettelpost_ward_views.xml',
        'views/viettelpost_office_views.xml',
        'views/viettelpost_service_views.xml',
        'views/viettelpost_connect_history_views.xml',
        'views/viettelpost_webhook_history_views.xml',
        'views/viettelpost_status_views.xml',
        'views/delivery_viettelpost_views.xml',
        'views/res_partner_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_warehouse_views.xml',
        'views/sale_order_views.xml',
        'views/menus.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'tangerine_delivery_viettelpost/static/src/**/*.js',
            'tangerine_delivery_viettelpost/static/src/**/*.xml'
        ]
    },
    'images': ['static/description/thumbnail.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
    'currency': 'USD',
    'price': 42.00
}
