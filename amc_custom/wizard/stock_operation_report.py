# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime


class StockOperation(models.TransientModel):
	_name = 'stock.operation.report'
	_description = 'Stock Operation Report'

	def _default_date_from(self):
		return datetime.date.today().replace(day=1)

	def _default_date_to(self):
		date_today = datetime.date.today()
		next_month = date_today.replace(day=28) + datetime.timedelta(days=4)
		return next_month - datetime.timedelta(days=next_month.day)

	company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
	date_from = fields.Date(string='Start Date', required=True, default=lambda self: self._default_date_from())
	date_to = fields.Date(string='End Date', required=True, default=lambda self: self._default_date_to())

	def _print_report(self, data):
		filename = 'stock_operation_report.xls'
		title = 'STOCK OPERATION REPORT'
		company_id = data['company_id']['company_id'][0]
		date_from = data['date_from']['date_from']
		date_to = data['date_to']['date_to']
		
		return {
			'type' : 'ir.actions.act_url',
			'url': '/web/export_xls/stock_operation_report?filename=%s&title=%s&company_id=%s&date_from=%s&date_to=%s'%(filename,title,company_id,date_from,date_to),
			'target': 'self',
		}                     

	@api.multi
	def check_report(self):
		self.ensure_one()
		data = {}
		data['company_id'] = self.read(['company_id'])[0]
		data['date_from'] = self.read(['date_from'])[0]
		data['date_to'] = self.read(['date_to'])[0]
		return self._print_report(data)