from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError


import logging

_logger = logging.getLogger(__name__)

class StockInventory(models.Model):
	_inherit = 'stock.inventory'

	def action_compute_theoretical_qty(self):
		for line in self.line_ids:
			# self._compute_theoretical_qty()
			if not line.product_id:
				line.theoretical_qty = 0
				return
			theoretical_qty = sum([x.quantity for x in line._get_quants()])
			if theoretical_qty and line.product_uom_id and line.product_id.uom_id != line.product_uom_id:
				theoretical_qty = line.product_id.uom_id._compute_quantity(theoretical_qty, line.product_uom_id)
			line.theoretical_qty = theoretical_qty