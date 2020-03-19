from odoo import api, fields, models, _

class StockLocationInherit(models.Model):
    _inherit = 'stock.location'

    item_status = fields.Selection([('Good','Good'),('Slightly_Damaged','Slightly Damaged'),
        ('Damaged','Damaged'),('Scrapped','Scrapped')],string='Status',)

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    return_request_id = fields.Many2one('return.stock.request','Return Request Stock')