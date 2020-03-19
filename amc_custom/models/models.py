# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class AMCStock(models.Model):
	_inherit = 'stock.picking'
	
	@api.onchange('location_dest_id')
	def _onchange_location_dest_id(self):
		# self.message = "Dear %s" % (self.partner_id.name or "")
		# return {
		# 	'warning': {'title': "Warning", 'message': self.message},
		# }

		for rec in self:
			for line_item in rec.move_line_ids:
				line_item.location_dest_id = rec.location_dest_id

	@api.multi
	def order_lines_layouted(self):
		"""
		Returns this order lines classified by sale_layout_category and separated in
		pages according to the category pagebreaks. Used to render the report.
		"""
		self.ensure_one()
		report_pages = [[]]
		line_total = 0
		line_count = 0
		lines_list = []
		line_group_count = 0

		for line in self.move_lines:
			if line.quantity_done > 0:
				line_total += 1

		for lines in self.move_lines:
			if lines.quantity_done > 0:
				line_count += 1
				lines_list.append(lines)

				# If last added category induced a pagebreak, this one will be on a new page
				if report_pages[-1] and report_pages[-1][-1]['pagebreak']:
					report_pages.append([])

				# Append category to current report page
				if line_count == 16:
					report_pages[-1].append({
						'name': 'Uncategorized',
						'pagebreak': True,
						'lines': list(lines_list)
					})
					line_group_count += 1
					line_count = 0
					lines_list = []

				# Check Group And Remaining Lines
				is_remain = line_total - (line_group_count*16)
				if int(line_total/16) == line_group_count and is_remain != 0 and is_remain == line_count:
					report_pages[-1].append({
						'name': 'Uncategorized',
						'pagebreak': True,
						'lines': list(lines_list)
					})
					line_group_count += 1
					line_count = 0
					lines_list = []

		return report_pages
					
		
			
# class amc_custom(models.Model):
#     _name = 'amc_custom.amc_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100