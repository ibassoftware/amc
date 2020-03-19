from odoo import models, fields, api, _ 
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	inventory_location = fields.Many2one('stock.location', string='Inventory Location', help='Select a location to get latest inventory. If not set, system will use the default location of warehouse.')
	sales_rep_id = fields.Many2one('hr.employee', compute='_compute_sale_rep')
	sales_manager_id = fields.Many2one('hr.employee', compute='_compute_sale_manager')
	sales_national_manager_id = fields.Many2one('hr.employee', compute='_compute_sale_national_manager')
	is_allowed_sale_confirm = fields.Boolean(compute='_compute_group')
	customer_po = fields.Char(string='Customer PO#')
	total_delivered_amount = fields.Float(string="Total Delivered Amount", compute="compute_total_delivered_amount", store=True)
	customer_group_id = fields.Many2one('customer.group', string='Customer Group')

	@api.onchange('partner_id')
	def _get_default_customer_group(self):
		customer_group_id = self.env['customer.group'].search([('partner_id', '=', self.partner_id.id)], limit=1)
		self.customer_group_id = customer_group_id


	@api.onchange('warehouse_id')
	def _set_inventory_location(self):
		self.inventory_location = self.warehouse_id.lot_stock_id

	@api.depends('user_id')
	def _compute_sale_rep(self):
		for record in self:
			employee_id = self.env['hr.employee'].search([('user_id', '=', record.user_id.id)])
			if employee_id:
				if employee_id.parent_id.job_id.name == 'Sales Representative':
					record.sales_rep_id = employee_id.parent_id.id
				else:
					if employee_id.job_id.name == 'Sales Representative':
						record.sales_rep_id = employee_id.id

	@api.depends('sales_rep_id')
	def _compute_sale_manager(self):
		for record in self:
			if record.sales_rep_id:
				if record.sales_rep_id.parent_id.job_id.name == 'Sales Manager':
					record.sales_manager_id = record.sales_rep_id.parent_id.id
			else:
				employee_id = self.env['hr.employee'].search([('user_id', '=', record.user_id.id)])
				if employee_id:
					if employee_id.parent_id.job_id.name == 'Sales Manager':
						record.sales_manager_id = employee_id.parent_id.id
					else:
						if employee_id.job_id.name == 'Sales Manager':
							record.sales_manager_id = employee_id.id


	@api.depends('sales_manager_id')
	def _compute_sale_national_manager(self):
		for record in self:
			if record.sales_manager_id:
				if record.sales_manager_id.parent_id.job_id.name == 'National Sales Manager':
					record.sales_national_manager_id = record.sales_manager_id.parent_id.id
			else:
				employee_id = self.env['hr.employee'].search([('user_id', '=', record.user_id.id)])
				if employee_id:
					if employee_id.parent_id.job_id.name == 'National Sales Manager':
						record.sales_national_manager_id = employee_id.parent_id.id
					else:
						if employee_id.job_id.name == 'National Sales Manager':
							record.sales_national_manager_id = employee_id.id

	@api.depends('partner_id')
	def _compute_group(self):
		user = self.env['res.users'].browse(self.env.uid)
		for record in self:
			record.is_allowed_sale_confirm = False

			# USEr MUST BE A SALES MANAGER
			# if user.has_group('sales_team.group_sale_manager'):
			if user.has_group('sales_team.group_sale_salesman_all_leads'):

				# USER MUST BE A MANAGER OF SALESPERSON
				employee_id = self.env['hr.employee'].search([('user_id', '=', user.id)])
				salesperson_employee_id = self.env['hr.employee'].search([('user_id', '=', record.user_id.id)])

				if employee_id:
					if employee_id == record.sales_rep_id:
						if  salesperson_employee_id.parent_id == record.sales_rep_id:
							record.is_allowed_sale_confirm = True
						if record.sales_rep_id == salesperson_employee_id:
							record.is_allowed_sale_confirm = True

					if employee_id == record.sales_manager_id:
						if record.sales_rep_id:
							if record.sales_rep_id.parent_id == record.sales_manager_id:
								record.is_allowed_sale_confirm = True
						else:
							if salesperson_employee_id.parent_id == record.sales_manager_id:
								record.is_allowed_sale_confirm = True
						if record.sales_manager_id == salesperson_employee_id:
							record.is_allowed_sale_confirm = True


					if employee_id == record.sales_national_manager_id:
						if record.sales_manager_id:
							if record.sales_manager_id.parent_id == record.sales_national_manager_id:
								record.is_allowed_sale_confirm = True
						else:
							if salesperson_employee_id.parent_id == record.sales_national_manager_id:
								record.is_allowed_sale_confirm = True
							if record.sales_rep_id.parent_id == record.sales_national_manager_id:
								record.is_allowed_sale_confirm = True
						if record.sales_national_manager_id == salesperson_employee_id:
							record.is_allowed_sale_confirm = True

				# if employee_id and employee_id.parent_id.user_id == user:
				# 	record.is_allowed_sale_confirm = True

			# OVERRIDE RESTRICTIONS FOR ADMINISTRATOR
			if user.has_group('base.group_erp_manager'):
				record.is_allowed_sale_confirm = True

	@api.multi
	def action_confirm(self):
		for line in self.order_line:
			if line.product_id.type == 'product' and line.product_uom_qty > line.available_qty:
				raise UserError('Cannot validate order! Ordered quantity for product %s should not be greater than the available quantity.' % line.product_id.display_name)
		result = super(SaleOrder, self).action_confirm()

		return result

	@api.depends('order_line', 'order_line.qty_delivered', 'order_line.price_unit')
	@api.one
	def compute_total_delivered_amount(self):
		total_delivered_amount = 0
		for line in self.order_line:
			# total_delivered_amount += line.delivered_amount
			total_delivered_amount += (line.qty_delivered * line.price_unit)

		# self.total_delivered_amount = total_delivered_amount
		self.update({
			'total_delivered_amount': total_delivered_amount
		})

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	latest_inventory = fields.Float(string="Latest Inventory", compute="get_inventory", help="Quantity On Hand")
	available_qty = fields.Float(string="Available Qty", compute="get_inventory", help="Quantity on hand minus reserved qty.")
	# delivered_amount = fields.Float(string="Delivered Amount", compute="compute_delivered_amount", store=True)

	@api.onchange('product_id')
	def check_valid_product(self):
		if self.order_id.customer_group_id:
			product_ids = self.order_id.customer_group_id.mapped('line_ids').mapped('product_id').ids
			_logger.info("HELLO")
			_logger.info(product_ids)
			if self.product_id and self.product_id.id not in product_ids:
				raise UserError('Invalid! Product %s does not belong to customer group %s.' % (self.product_id.display_name,self.order_id.customer_group_id.name))

	@api.depends('product_id','order_id')
	def get_inventory(self):
		for line in self:
			inv_loc = line.order_id.inventory_location
			if not inv_loc:
				inv_loc = line.order_id.warehouse_id.lot_stock_id
			stock_quant = self.env['stock.quant'].search([('product_id','=',line.product_id.id),('location_id','=',inv_loc.id)])
			inv_qty = 0
			reserved_qty = 0
			for stock in stock_quant:
				inv_qty += stock.quantity
				reserved_qty += stock.reserved_quantity

			line.latest_inventory = inv_qty
			line.available_qty = inv_qty - reserved_qty

	# @api.one
	# def compute_delivered_amount(self):
	# 	delivered_amount = self.qty_delivered * self.price_unit
	# 	self.delivered_amount = delivered_amount
