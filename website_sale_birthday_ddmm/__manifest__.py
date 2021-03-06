# -*- coding: utf-8 -*-
# © 2015 AbAKUS IT-Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Partner fields birth Day and birth Month",
    "summary": "Allow Birth Day and Month Fields to Partner",
    "description": "Add birth day and month fields to a Partner",
    "version": "10.0.1.0.0",
    "category": "Website",
    "website": "http://www.abakusitsolutions.eu",
    "author": "AbAKUS IT Solutions, ",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        'website_sale',
        'website_portal',
    ],
    "data": [
        'views/res_partner.xml',
        'views/portal_template.xml',
    ],
    'demo': [
    ],
}