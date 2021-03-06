# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, tools, _
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    """
    Add sizetag property to product
    """
    _inherit = 'product.template'

    has_sizetag = fields.Boolean(related='categ_id.has_sizetag')
    sizetags_line_ids = fields.One2many('category.sizetag.line', 'product_id', string="Size Tag Lines", copy=True)

