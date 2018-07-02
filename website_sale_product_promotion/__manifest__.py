# -*- coding: utf-8 -*-
{
    'name': "Production Promotion",
    'summary': "Allows ceating a promotion featuring two products",
    'author': "AbAKUS it-solutions SARL",
    'website': "http://www.abakusitsolutions.eu",
    'category': 'Sale',
    'version': '10.0.1.0',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'views/product_view.xml',
        'views/sale_order_views.xml',
        'data/promotion_mail.xml',

        'data/ir_cron.xml',

        'security/ir.model.access.csv',
    ],
    'installable': True
}