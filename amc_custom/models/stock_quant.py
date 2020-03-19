# from odoo import models, fields, api, _ 

# class StockQuant(models.Model):
# 	_inherit = 'stock.quant'

# 	stock_value = fields.Float('Value', compute='_compute_stock_value')

# 	@api.multi
# 	@api.depends('quantity', 'product_id.standard_price')
# 	def _compute_stock_value(self):
# 		for stock in self:
# 			stock.stock_value = stock.product_id.standard_price * stock.quantity
# 			# if stock.product_id.cost_method in ['standard', 'average']:
# 			# 	stock.stock_value = stock.product_id.standard_price * stock.quantity
# 			# elif stock.product_id.cost_method == 'fifo':
# 			# 	stock.stock_value = product._sum_remaining_values()