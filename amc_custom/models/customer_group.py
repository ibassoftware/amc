# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

class CustomerGroup(models.Model):
	_name = 'customer.group'
	_description = 'Customer Group'

	name = fields.Char(string='Customer Group', required=True)
	partner_id = fields.Many2one('res.partner', string='Customer')
	line_ids = fields.One2many('customer.group.line', 'customer_group_id', string='Products')
	
class CustomerGroupLine(models.Model):
	_name = 'customer.group.line'

	customer_group_id = fields.Many2one('customer.group', string='Customer Group')
	product_id = fields.Many2one('product.product', string='Product')