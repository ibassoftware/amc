# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import deque
import json

from odoo import http
from odoo.http import request
from odoo.tools import ustr
from odoo.tools.misc import xlwt

from datetime import datetime
from datetime import date

import logging
_logger = logging.getLogger(__name__)

class ExportReportXlsSalesSummary(http.Controller):

	@http.route('/web/export_xls/stock_operation_report', type='http', auth="user")
	def export_xls(self, filename, title, company_id, date_from, date_to, **kw):
	# company = request.env['res.company'].search([('id', '=', company_id)])

		stock_picking = request.env['stock.picking'].search([('company_id.id', '=', company_id),('picking_type_id.code','in',('incoming', 'outgoing')),('state','=','done'),('scheduled_date','>=',date_from),('scheduled_date','<=',date_to)], order='scheduled_date asc')
		
		from_report_month = datetime.strptime(date_from, '%Y-%m-%d')
		to_report_month = datetime.strptime(date_to, '%Y-%m-%d')

		workbook = xlwt.Workbook()
		worksheet = workbook.add_sheet(title)

		# STYLES
		style_header_bold = xlwt.easyxf("font: bold on;font: name Calibri;align: wrap no")
		style_header_right = xlwt.easyxf("font: name Calibri;align: horiz right, wrap no")
		style_table_header_bold = xlwt.easyxf("font: bold on;font: name Calibri;align: horiz centre, vert centre, wrap on;borders: top thin, bottom thin, right thin;")
		style_table_row = xlwt.easyxf("font: name Calibri;align: horiz left, wrap no;borders: top thin, bottom thin, right thin;")
		style_table_row_amount = xlwt.easyxf("font: name Calibri;align: horiz right, wrap no;borders: top thin, bottom thin, right thin;", num_format_str="#,##0.00")
		style_table_total = xlwt.easyxf("pattern: pattern solid, fore_colour pale_blue;font: bold on;font: name Calibri;align: horiz left, wrap no;borders: top thin, bottom medium, right thin;")
		style_table_total_value = xlwt.easyxf("pattern: pattern solid, fore_colour pale_blue;font: bold on;font: name Calibri;align: horiz right, wrap no;borders: top thin, bottom medium, right thin;", num_format_str="#,##0.00")
		worksheet.col(0).width = 500*12
		worksheet.col(1).width = 500*12
		worksheet.col(2).width = 500*12
		worksheet.col(3).width = 500*12
		worksheet.col(4).width = 500*12
		worksheet.col(5).width = 350*12
		worksheet.col(6).width = 350*12

		# TEMPLATE HEADERS
		worksheet.write(0, 0, "For the period: ", style_header_bold) # Company Name
		worksheet.write(0, 1, '%s - %s'%(from_report_month.strftime('%B %d, %Y'),to_report_month.strftime('%B %d, %Y')), style_header_bold) # Report Date

		# TABLE HEADER
		worksheet.write(3, 0, 'Customer Name', style_table_header_bold) # HEADER
		worksheet.write(3, 1, 'Scheduled Date', style_table_header_bold) # HEADER
		worksheet.write(3, 2, 'Reference', style_table_header_bold) # HEADER
		worksheet.write(3, 3, 'Source Document', style_table_header_bold) # HEADER
		worksheet.write(3, 4, 'Delivered', style_table_header_bold) # HEADER
		worksheet.write(3, 5, 'Returned', style_table_header_bold) # HEADER
		worksheet.write(3, 6, 'Balance', style_table_header_bold) # HEADER

		# TABLE ROW LINES
		# table_row_start = 9
		row_count = 4
		transaction_count = 0
		balance = 0
		for stock in stock_picking:
			_logger.info("TELUS")
			delivered = 0
			returned = 0
			generate = False
			scheduled_date_line = datetime.strptime(stock.scheduled_date, '%Y-%m-%d %H:%M:%S')

			if stock.picking_type_id.code == 'outgoing':
				generate = True
				for line in stock.move_lines:
					amount = line.sale_line_id.price_unit * line.quantity_done
					delivered += amount
					balance += delivered

			if stock.picking_type_id.code == 'incoming':
				for line in stock.move_lines:
					if line.origin_returned_move_id:
						generate = True
						amount = line.sale_line_id.price_unit * line.quantity_done
						returned += amount
						balance -= returned
						_logger.info("YUW")
						_logger.info(line.sale_line_id.price_unit)
						_logger.info(line.quantity_done)
						_logger.info(amount)
					else:
						generate = False

			worksheet.write(row_count, 0, stock.partner_id.name or '', style_table_row)
			worksheet.write(row_count, 1, scheduled_date_line.strftime('%Y-%m-%d'), style_table_row) 
			worksheet.write(row_count, 2, stock.name or '', style_table_row)
			worksheet.write(row_count, 3, stock.origin or '', style_table_row)
			worksheet.write(row_count, 4, delivered, style_table_row)
			worksheet.write(row_count, 5, returned, style_table_row)
			worksheet.write(row_count, 6, balance, style_table_row)


			row_count +=1
			transaction_count +=1

		response = request.make_response(None,
			headers=[('Content-Type', 'application/vnd.ms-excel'),
					('Content-Disposition', 'attachment; filename=%s;'%(filename)
					)])

		workbook.save(response.stream)

		return response
