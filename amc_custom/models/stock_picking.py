from odoo import models, fields, api, _
from datetime import datetime
import pytz

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	customer_po = fields.Char(string='Customer PO#', compute='_compute_so')
	assigned_odr = fields.Char(string='Assigned ODR#')

	def _compute_so(self):
		for record in self:
			if record.sale_id:
				record.customer_po = record.sale_id.customer_po
			else:
				if record.origin:
					sale_order = self.env['sale.order'].search([('name', '=', record.origin)])
					if sale_order:
						customer_po = ''
						for sale in sale_order:
							customer_po += ' '
							customer_po += sale.customer_po
						record.customer_po = customer_po

	# OVERRIDE
	@api.multi
	def do_print_picking(self):
		_logger.info('BALIWW')
		self.write({'printed': True})
		return self.env.ref('amc_custom.action_report_picklist').report_action(self)

	# @api.multi
	# def order_lines_layouted(self):
	# 	"""
	# 	Returns this order lines classified by sale_layout_category and separated in
	# 	pages according to the category pagebreaks. Used to render the report.
	# 	"""
	# 	self.ensure_one()
	# 	report_pages = [[]]
	# 	line_count = 0
	# 	for lines in self.move_lines:
	# 		line_count +=1
	# 		# If last added category induced a pagebreak, this one will be on a new page
	# 		if report_pages[-1] and report_pages[-1][-1]['pagebreak']:
	# 			report_pages.append([])
	# 		# Append category to current report page
	# 		if line_count == 16:
	# 			report_pages[-1].append({
	# 				'name': 'Uncategorized',
	# 				'pagebreak': True,
	# 				'lines': list(lines)
	# 			})
	# 			line_count = 0

	# 	return report_pages

	@api.multi
	def export_data(self, fields_to_export, raw_data=False):
		""" Override to convert virtual ids to ids """
		res = super(StockPicking, self).export_data(fields_to_export, raw_data)
		_logger.info('EXPORT HELLO 2')
		_logger.info(fields_to_export)
		_logger.info(raw_data)
		dataindex = None

		for index, fieldlabel in enumerate(fields_to_export):
			if fieldlabel == 'scheduled_date':
				dataindex = index

		if 'scheduled_date' in fields_to_export:
			user = self.env['res.users'].browse(self.env.uid)
			# converting time to users timezone
			if user.tz:
				for index, val in enumerate(res['datas']):
					default_scheduled_date = res['datas'][index][dataindex]
					if default_scheduled_date:
						default_scheduled_date = str(default_scheduled_date)
						scheduled_date = datetime.strptime(default_scheduled_date, "%Y-%m-%d %H:%M:%S")
						tz = pytz.timezone(user.tz) or pytz.utc
						time = pytz.utc.localize(scheduled_date).astimezone(tz)
						new_scheduled_date = time.strftime('%m/%d/%Y %H:%M:%S')
						res['datas'][index][dataindex] = new_scheduled_date
		return res