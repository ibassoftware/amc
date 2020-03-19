# -*- coding: utf-8 -*-
# Copyright YEAR(2019), AUTHOR(IBAS)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	# customer_group_ids = fields.Many2many('customer.group', string='Customer Group', related='product_variant_ids.customer_group_ids')

	def button_fix_available_zero(self):
		_logger.info("YOJKFLHN")
		# for product in self.product_variant_ids:
		move_lines = self.env['stock.move.line'].sudo().search([
			('product_id.type', '=', 'product'),
			('product_uom_qty', '=', 0),
			('state', '=', 'assigned'),
		])

		if move_lines:
			move_ids = move_lines.sudo().mapped('move_id').ids
			if len(move_ids) > 1:
				self.env.cr.execute(""" UPDATE stock_move SET state = 'confirmed' WHERE id in %s ;""" % (tuple(move_ids), ))
			elif len(move_ids) == 1:
				self.env.cr.execute(""" UPDATE stock_move SET state = 'confirmed' WHERE id = %s ;""" % (move_ids[0]))

	def button_fix_unreserved_qty(self):
		for product in self.product_variant_ids:
			# Available variables:
			#  - env: Odoo Environment on which the action is triggered
			#  - model: Odoo Model of the record on which the action is triggered; is a void recordset
			#  - record: record on which the action is triggered; may be void
			#  - records: recordset of all records on which the action is triggered in multi-mode; may be void
			#  - time, datetime, dateutil, timezone: useful Python libraries
			#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
			#  - Warning: Warning Exception to use with raise
			# To return an action, assign: action = {...}
			quants = self.env['stock.quant'].sudo().search([('product_id','=',product.id)])
			move_line_ids = []
			warning = ''
			for quant in quants:
				move_lines = self.env["stock.move.line"].sudo().search([
					('product_id', '=', quant.product_id.id),
					('location_id', '=', quant.location_id.id),
					('lot_id', '=', quant.lot_id.id),
					('package_id', '=', quant.package_id.id),
					('owner_id', '=', quant.owner_id.id),
					('product_qty', '!=', 0)
				])
				move_line_ids += move_lines.ids
				reserved_on_move_lines = sum(move_lines.mapped('product_qty'))
				move_line_str = str.join(', ', [str(move_line_id) for move_line_id in move_lines.ids])

				if quant.location_id.should_bypass_reservation():
					# If a quant is in a location that should bypass the reservation, its `reserved_quantity` field
					# should be 0.
					if quant.reserved_quantity != 0:
						quant.write({'reserved_quantity': 0})
				else:
					# If a quant is in a reservable location, its `reserved_quantity` should be exactly the sum
					# of the `product_qty` of all the partially_available / assigned move lines with the same
					# characteristics.
					if quant.reserved_quantity == 0:
						if move_lines:
							move_lines.with_context(bypass_reservation_update=True).write({'product_uom_qty': 0})
					elif quant.reserved_quantity < 0:
						quant.write({'reserved_quantity': 0})
						if move_lines:
							move_lines.with_context(bypass_reservation_update=True).write({'product_uom_qty': 0})
					else:
						if reserved_on_move_lines != quant.reserved_quantity:
							move_lines.with_context(bypass_reservation_update=True).write({'product_uom_qty': 0})
							quant.write({'reserved_quantity': 0})
						else:
							if any(move_line.product_qty < 0 for move_line in move_lines):
								move_lines.with_context(bypass_reservation_update=True).write({'product_uom_qty': 0})
								quant.write({'reserved_quantity': 0})
				
				# CHECK FOR MOVELINES WITH STATE AVAILABLE BUT 0 RESERVED QUANTITY
				move_lines_reserved_zero = self.env["stock.move.line"].sudo().search([
					('product_id', '=', quant.product_id.id),
					('location_id', '=', quant.location_id.id),
					('lot_id', '=', quant.lot_id.id),
					('package_id', '=', quant.package_id.id),
					('owner_id', '=', quant.owner_id.id),
					('product_qty', '=', 0),
					('state', '=', 'assigned')
				])
				if move_lines_reserved_zero:
					move_ids = move_lines_reserved_zero.sudo().mapped('move_id').ids
					if len(move_ids) > 1:
						self.env.cr.execute(""" UPDATE stock_move SET state = 'confirmed' WHERE id in %s ;""" % (tuple(move_ids), ))
					elif len(move_ids) == 1:
						self.env.cr.execute(""" UPDATE stock_move SET state = 'confirmed' WHERE id = %s ;""" % (move_ids[0]))

class ProductProduct(models.Model):
	_inherit = 'product.product'

	# customer_group_ids = fields.Many2many('customer.group', string='Customer Group')

	def button_fix_available_zero(self):
		_logger.info("YOJKFLHN")
		# for product in self.product_variant_ids:
		move_lines = self.env['stock.move.line'].sudo().search([
			('product_id.type', '=', 'product'),
			('product_uom_qty', '=', 0),
			('state', '=', 'assigned'),
		])

		if move_lines:
			move_ids = move_lines.sudo().mapped('move_id').ids
			if len(move_ids) > 1:
				self.env.cr.execute(""" UPDATE stock_move SET state = 'confirmed' WHERE id in %s ;""" % (tuple(move_ids), ))
			elif len(move_ids) == 1:
				self.env.cr.execute(""" UPDATE stock_move SET state = 'confirmed' WHERE id = %s ;""" % (move_ids[0]))

	def button_fix_unreserved_qty(self):
		for product in self.product_variant_ids:
			# Available variables:
			#  - env: Odoo Environment on which the action is triggered
			#  - model: Odoo Model of the record on which the action is triggered; is a void recordset
			#  - record: record on which the action is triggered; may be void
			#  - records: recordset of all records on which the action is triggered in multi-mode; may be void
			#  - time, datetime, dateutil, timezone: useful Python libraries
			#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
			#  - Warning: Warning Exception to use with raise
			# To return an action, assign: action = {...}
			quants = self.env['stock.quant'].sudo().search([('product_id','=',product.id)])
			move_line_ids = []
			warning = ''
			for quant in quants:
				move_lines = self.env["stock.move.line"].sudo().search([
					('product_id', '=', quant.product_id.id),
					('location_id', '=', quant.location_id.id),
					('lot_id', '=', quant.lot_id.id),
					('package_id', '=', quant.package_id.id),
					('owner_id', '=', quant.owner_id.id),
					('product_qty', '!=', 0)
				])
				move_line_ids += move_lines.ids
				reserved_on_move_lines = sum(move_lines.mapped('product_qty'))
				move_line_str = str.join(', ', [str(move_line_id) for move_line_id in move_lines.ids])

				if quant.location_id.should_bypass_reservation():
					# If a quant is in a location that should bypass the reservation, its `reserved_quantity` field
					# should be 0.
					if quant.reserved_quantity != 0:
						quant.write({'reserved_quantity': 0})
				else:
					# If a quant is in a reservable location, its `reserved_quantity` should be exactly the sum
					# of the `product_qty` of all the partially_available / assigned move lines with the same
					# characteristics.
					if quant.reserved_quantity == 0:
						if move_lines:
							move_lines.with_context(bypass_reservation_update=True).write({'product_uom_qty': 0})
					elif quant.reserved_quantity < 0:
						quant.write({'reserved_quantity': 0})
						if move_lines:
							move_lines.with_context(bypass_reservation_update=True).write({'product_uom_qty': 0})
					else:
						if reserved_on_move_lines != quant.reserved_quantity:
							move_lines.with_context(bypass_reservation_update=True).write({'product_uom_qty': 0})
							quant.write({'reserved_quantity': 0})
						else:
							if any(move_line.product_qty < 0 for move_line in move_lines):
								move_lines.with_context(bypass_reservation_update=True).write({'product_uom_qty': 0})
								quant.write({'reserved_quantity': 0})
				
				# CHECK FOR MOVELINES WITH STATE AVAILABLE BUT 0 RESERVED QUANTITY
				move_lines_reserved_zero = self.env["stock.move.line"].sudo().search([
					('product_id', '=', quant.product_id.id),
					('location_id', '=', quant.location_id.id),
					('lot_id', '=', quant.lot_id.id),
					('package_id', '=', quant.package_id.id),
					('owner_id', '=', quant.owner_id.id),
					('product_qty', '=', 0),
					('state', '=', 'assigned')
				])
				if move_lines_reserved_zero:
					move_ids = move_lines_reserved_zero.sudo().mapped('move_id').ids
					if len(move_ids) > 1:
						self.env.cr.execute(""" UPDATE stock_move SET state = 'confirmed' WHERE id in %s ;""" % (tuple(move_ids), ))
					elif len(move_ids) == 1:
						self.env.cr.execute(""" UPDATE stock_move SET state = 'confirmed' WHERE id = %s ;""" % (move_ids[0]))
