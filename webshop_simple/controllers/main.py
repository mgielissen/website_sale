# -*- coding: utf-8 -*-
import logging

from pprint import pformat
from odoo import http, tools, _
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import PPR

_logger = logging.getLogger(__name__)


class WebsiteSale(http.Controller):

    def get_attribute_value_ids(self, product):
        """ list of selectable attributes of a product
        :return: list of product variant description
           (variant id, [visible attribute ids], variant price, variant sale price)
        """
        # product attributes with at least two choices
        quantity = product._context.get('quantity') or 1
        product = product.with_context(quantity=quantity)

        visible_attrs_ids = product.attribute_line_ids.filtered(lambda l: len(l.value_ids) > 1).mapped('attribute_id').ids
        to_currency = request.website.get_current_pricelist().currency_id
        attribute_value_ids = []
        for variant in product.product_variant_ids:
            if to_currency != product.currency_id:
                price = variant.currency_id.compute(variant.website_public_price, to_currency) / quantity
            else:
                price = variant.website_public_price / quantity
            visible_attribute_ids = [v.id for v in variant.attribute_value_ids if v.attribute_id.id in visible_attrs_ids]
            attribute_value_ids.append([variant.id, visible_attribute_ids, variant.website_price, price])
        return attribute_value_ids

    def _get_search_domain_simple(self, search, category, attrib_values):
        domain = request.website.sale_product_domain()
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                    ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]

        if category:
            domain += [('public_categ_ids', '=', int(category))]

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        return domain

    # ------------------------------------------------------
    # Simple Web Shop landing page
    # ------------------------------------------------------
    @http.route(['/shop/simple'], type='http', auth="public", website=True)
    def shop_simple(self, category=None, search='', **kwargs):
        simple_categories = ('sandwich', 'salad', 'meal', 'dessert')
        # Build the /shop/simple endpoint
        categories = request.env['product.public.category'].search([('name', 'in', simple_categories)])

        values = {
            'categories': categories,
            'rows': PPR,
            'post': kwargs,
            'escape': lambda x: x.replace("'", r"\'")
        }
        return request.render("webshop_simple.shop_simple", values)

    # ------------------------------------------------------
    # Simple Web Shop category page
    # ------------------------------------------------------
    @http.route(['/shop/simple/category/<model("product.public.category"):category>'],
                type='http', auth="public", website=True)
    def shop_simple_category(self, category=None, search='', **kwargs):
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        # Get all products from this category that are base_sides
        domain = self._get_search_domain_simple(search, category, attrib_values)
        domain += [('active', '=', True)]
        products = request.env['product.template'].search(domain)
        # set the default product to display
        product_count = len(products)
        if product_count == 0:
            return request.redirect('/shop/simple')

        pricelist_context = dict(request.env.context)
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])
        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency.compute(price, to_currency)
        company = request.env.user.sudo().company_id

        values = {
            'search': search,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'company': company,
            'main_object': category,
            'category': category,
            'product_count': product_count,
            'products': products,
            'compute_currency': compute_currency,
            'get_attribute_value_ids': self.get_attribute_value_ids,
        }
        if category.has_base_products:
            return request.render("webshop_simple.category", values)
        else:
            return request.render("webshop_simple.category_product", values)


    # ------------------------------------------------------
    # Simple Web Shop category product page
    # ------------------------------------------------------
    @http.route(['/shop/simple/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def shop_simple_category_product(self, product, category='', search='', **kwargs):
        # Build the /shop/simple/category/  endpoint
        product_context = dict(request.env.context,
                               active_id=product.id,
                               partner=request.env.user.partner_id)
        ProductCategory = request.env['product.public.category']
        if category:
            category = ProductCategory.browse(int(category)).exists()

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        # Get all products from this category that are base_sides
        domain = self._get_search_domain_simple(search, category, attrib_values)
        products = request.env['product.template'].search(domain)
        product_count = len(products)

        # Get all product sides if any
        sides = []
        for accessory in product.accessory_product_ids:
            sides.extend(request.env['product.template'].search([('id', '=', accessory.product_tmpl_id.id)]))
        sides_count = len(sides)

        keep = QueryURL('/shop/simple', category=category and category.id, search=search, attrib=attrib_list)
        pricelist_context = dict(request.env.context)
        if not pricelist_context.get('pricelist'):
            pricelist = request.website.get_current_pricelist()
            pricelist_context['pricelist'] = pricelist.id
        else:
            pricelist = request.env['product.pricelist'].browse(pricelist_context['pricelist'])

        from_currency = request.env.user.company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: from_currency.compute(price, to_currency)
        company = request.env.user.sudo().company_id

        values = {
            'search': search,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'keep': keep,
            'company': company,
            'main_object': category,
            'category': category,
            'product_count': product_count,
            'products': products,
            'product': product,
            'sides_count': sides_count,
            'sides': sides,
            'compute_currency': compute_currency,
            'get_attribute_value_ids': self.get_attribute_value_ids,
        }
        return request.render("webshop_simple.category_product", values)

    # ------------------------------------------------------
    # Handle cart
    # ------------------------------------------------------
    def _filter_attributes(self, **kw):
        return {k: v for k, v in kw.items() if "attribute" in k}

    @http.route([
        '/shop/cart/update'
    ], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        breadtype = None
        if 'breadtype_' + str(product_id) in kw:
            breadtype = kw['breadtype_' + str(product_id)]
        sizetag = None
        if 'sizetag_' + str(product_id) in kw:
            sizetag = kw['sizetag_' + str(product_id)]
        sides = []
        for key in kw:
            if key.startswith("sides-" + str(product_id) + '-'):
                sides.append(int(kw[key]))

        # check if it's a birthday gift
        has_birthday_gift = False
        company = request.env.user.sudo().company_id
        if int(product_id) == company.birthday_promotion_product_id.id:
            if request.env.user._is_portal():
                if request.env.user._has_birthday_gift():
                    has_birthday_gift = True
        _logger.debug("ABAKUS: Add to cart product_id={}".format(int(product_id)))
        request.website.sale_get_order(force_create=1)._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            attributes=self._filter_attributes(**kw),
            sizetag=sizetag,
            breadtype=breadtype,
            sides=sides,
            has_birthday_gift=has_birthday_gift,
        )
        return request.redirect("/shop/cart")

    @http.route(['/shop/cart/update_alias_json'],
                type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_alias_json(self, product_id, line_id, alias, **kw):
        """ Custom endpoint to update SOL label """
        order = request.website.sale_get_order()
        order_lines = order._cart_find_product_line(product_id, line_id, **kw)
        order_line = order_lines and order_lines[0]
        values = {
            'alias': alias
        }
        order_line.write(values)
        return {}
