# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

from odoo.exceptions import UserError, AccessError

class ReorderLocation(models.Model):
    _name = 'reorder.location'
    _description = "Reorder Location"

    location_id = fields.Many2one('stock.location','Location')
    product_id = fields.Many2one('product.product','Item')
    retail_price = fields.Float('Retail Price')
    min_qty = fields.Float('Minimum Quantity')
    actual_qty = fields.Float('Actual Quantity', compute='_compute_actual_qty', store=True)
    actual_inventory_value = fields.Float('Actual Inventory Value',compute='_compute_inv_val', store=True)
    reorder_qty = fields.Float('Reorder Quantity',compute='_compute_reorder_qty', store=True)
    reorder_qty_value = fields.Float('Reorder Quantity Value',compute='_compute_reorder_qty_value', store=True)

    @api.depends('location_id','product_id')
    def _compute_actual_qty(self):
        for rec in self:
            quant_id = self.env['stock.quant'].search([('product_id','=',rec.product_id.id),
            ('location_id','=',rec.location_id.id)])
            if quant_id:
                rec.actual_qty = quant_id.quantity

    @api.onchange('product_id')
    def product_onchange(self):
        if self.product_id:
            self.retail_price = self.product_id.list_price

    @api.depends('retail_price','actual_qty')
    def _compute_inv_val(self):
        for rec in self:
            rec.actual_inventory_value = rec.retail_price * rec.actual_qty

    @api.depends('reorder_qty','retail_price')
    def _compute_reorder_qty_value(self):
        for rec in self:
            rec.reorder_qty_value = rec.retail_price * rec.reorder_qty

    @api.depends('min_qty','actual_qty')
    def _compute_reorder_qty(self):
        for rec in self:
            if rec.actual_qty < rec.min_qty:
                rec.reorder_qty = rec.min_qty - rec.actual_qty
            else:
                rec.reorder_qty = 0.0