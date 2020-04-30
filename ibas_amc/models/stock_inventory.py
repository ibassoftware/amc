# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from odoo.exceptions import UserError, AccessError

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    view_record = fields.Boolean(string="Allow to View", compute='_compute_allow_to_view', search="_search_allow_to_view")

    @api.multi
    def _search_allow_to_view(self, operator, value):
        hr_employee_model = self.env['hr.employee']
        stock_user = self.env.ref('stock.group_stock_user').id
        stock_manager = self.env.ref('stock.group_stock_manager').id
        ids_need = []
        for rec in self.search([]):
            if self.env.ref('sales_team.group_sale_manager').id in self.env.user.groups_id.ids:
                if rec.create_uid.id == self.env.user.id:
                    ids_need.append(rec.id)
                else:
                    #Get the Employee ID of the Created User
                    hr_employee_obj = hr_employee_model.search([('user_id','=', rec.create_uid.id)])
                    #Get the Employee ID of the Sales Manager
                    hr_man_employee_obj = hr_employee_model.search([('user_id','=', self.env.user.id)])

                    if hr_employee_obj:
                        if hr_employee_obj.parent_id:
                            if hr_employee_obj.parent_id.id == hr_man_employee_obj.id:
                                ids_need.append(rec.id)

            elif self.env.ref('sales_team.group_sale_salesman').id in self.env.user.groups_id.ids:
                if rec.create_uid.id == self.env.user.id:
                    ids_need.append(rec.id)

            elif self.env.ref('sales_team.group_sale_salesman_all_leads').id in self.env.user.groups_id.ids:
                if rec.create_uid.id == self.env.user.id:
                    ids_need.append(rec.id)

            if stock_user in self.env.user.groups_id.ids or stock_manager in self.env.user.groups_id.ids:
                ids_need.append(rec.id)        
        return [('id', 'in', ids_need)]


    @api.multi
    def _compute_allow_to_view(self):
        hr_employee_model = self.env['hr.employee']
        stock_user = self.env.ref('stock.group_stock_user').id
        stock_manager = self.env.ref('stock.group_stock_manager').id

        for rec in self:
            rec.view_record = False
            if self.env.ref('sales_team.group_sale_manager').id in self.env.user.groups_id.ids:
                if rec.create_uid.id == self.env.user.id:
                    rec.view_record = True
                else:
                    #Get the Employee ID of the Created User
                    hr_employee_obj = hr_employee_model.search([('user_id','=', rec.create_uid.id)])
                    #Get the Employee ID of the Sales Manager
                    hr_man_employee_obj = hr_employee_model.search([('user_id','=', self.env.user.id)])

                    if hr_employee_obj:
                        if hr_employee_obj.parent_id:
                            if hr_employee_obj.parent_id.id == hr_man_employee_obj.id:
                                rec.view_record = True

            elif self.env.ref('sales_team.group_sale_salesman').id in self.env.user.groups_id.ids:
                if rec.create_uid.id == self.env.user.id:
                    rec.view_record = True
                else:
                    rec.view_record = False
            elif self.env.ref('sales_team.group_sale_salesman_all_leads').id in self.env.user.groups_id.ids:
                if rec.create_uid.id == self.env.user.id:
                    rec.view_record = True
                else:
                    rec.view_record = False
            
            if stock_user in self.env.user.groups_id.ids or stock_manager in self.env.user.groups_id.ids:
                rec.view_record = True



class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    theoretical_qty_cost = fields.Float(string='Total Cost', compute="_compute_theo_cost")

    @api.one
    @api.depends('theoretical_qty', 'product_id')
    def _compute_theo_cost(self):
        cost = 0.00
        if self.product_id:
            cost = self.product_id.standard_price
        self.theoretical_qty_cost = self.theoretical_qty * cost



