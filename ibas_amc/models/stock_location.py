from odoo import api, fields, models, _

class StockLocationInherit(models.Model):
    _inherit = 'stock.location'

    item_status = fields.Selection([('Good','Good'),('Slightly_Damaged','Slightly Damaged'),
        ('Damaged','Damaged'),('Scrapped','Scrapped')],string='Status',)

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    return_request_id = fields.Many2one('return.stock.request','Return Request Stock')

    @api.one
    @api.depends('move_lines.date_expected')
    def _compute_scheduled_date(self):
        if self.return_request_id:
            self.scheduled_date = self.return_request_id.scheduled_pick_up_date
        else:
            if self.move_type == 'direct':
                self.scheduled_date = min(self.move_lines.mapped('date_expected') or [fields.Datetime.now()])
            else:
                self.scheduled_date = max(self.move_lines.mapped('date_expected') or [fields.Datetime.now()])
