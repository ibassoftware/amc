# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.invoice'

    sales_cordinator = fields.Many2one('res.users','Sales Coordinator')
    sales_manager = fields.Many2one('res.users','Sales Manager')