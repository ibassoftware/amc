from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class ReturnStockRequest(models.Model):
    _name = 'return.stock.request'
    _description = "Return Stock Request"

    @api.model
    def _get_ope_type_id(self):
        return self.env.ref('stock.stock_location_stock').id

    date_now = fields.Date('Date', default=fields.Datetime.now,)
    state  = fields.Selection([('Draft','Draft'),('Submitted','Submitted'),('Done','Done')],string="State",default="Draft")
    scheduled_pick_up_date = fields.Date('Scheduled Pick Up Date')
    source_location = fields.Many2one('stock.location','Source Location')
    operation_type_id = fields.Many2one('stock.picking.type','Picking Type', default=_get_ope_type_id)
    stock_request_line = fields.One2many('return.stock.request.line','reten_req_id','Line')
    picking_count = fields.Integer(
        string='Number of Picking',
        compute='_compute_picking_count',
    )
    origin = fields.Char(string='RS #')

    @api.multi
    def _compute_picking_count(self):
        for line in self:
            picking_ids=self.env['stock.picking'].search([('return_request_id','=',line.id)])
            line.picking_count = len(picking_ids)

    @api.multi
    def action_picking_count(self):
        model_object = self.env['ir.model.data']
        picking_ids=self.env['stock.picking'].search([('return_request_id','=',self.id)])
        dummy, action_id = tuple(model_object.get_object_reference('stock', 'action_picking_tree_all'))
        [action] = self.env['ir.actions.act_window'].browse(action_id).read()
        if len(picking_ids) > 0:
            action['domain'] = [('id', 'in', picking_ids.ids)]
        elif len(sales_meeting_ids) == 1:
            action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = picking_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action


    def submit(self):
        self.write({'state':'Submitted'})
        if self.stock_request_line:
            for line in self.stock_request_line:
                picking_id = self.env['stock.picking'].create({
                        'picking_type_id': self.operation_type_id.id,
                        'location_id': self.source_location.id,
                        'location_dest_id': line.dest_location.id,
                        'return_request_id':self.id
                    })
                self.env['stock.move'].create({
                            'product_id': line.product_id.id,
                            'name': line.product_id.name,
                            'product_uom': line.product_id.uom_id.id,
                            'product_uom_qty': line.qty,
                            'quantity_done': line.qty,
                            'picking_id': picking_id.id,
                            'location_id': self.source_location.id,
                            'location_dest_id': line.dest_location.id 
                        })
              

    def done(self):
        self.write({'state':'Done'})
        picking_ids = self.env['stock.picking'].search([('return_request_id','=',self.id)])
        for picking_id in picking_ids:
            picking_id.action_confirm()
            picking_id.action_assign()
            picking_id.button_validate()



class ReturnStockRequestLine(models.Model):
    _name = 'return.stock.request.line'
    _description = "Return Stock Request Line"

    product_id = fields.Many2one('product.product','Product')
    reten_req_id = fields.Many2one('return.stock.request','Retrn Req ID')
    item_status = fields.Selection([('Good','Good'),('Slightly_Damaged','Slightly Damaged'),
        ('Damaged','Damaged'),('Scrapped','Scrapped')],string='Status',default='Good')
    qty = fields.Float('Quantity')
    unit_price = fields.Float('Unit Price')
    amount = fields.Float('Amount')
    dest_location = fields.Many2one('stock.location','Destination Location')

    @api.onchange('product_id','item_status','qty')
    def product_onchange(self):
        if not self.reten_req_id.operation_type_id:
            raise UserError(_('Select first a Picking Type before adding an Item to Return.'))
        self.unit_price = self.product_id.list_price
        self.amount = self.qty * self.unit_price
        if self.item_status == 'Slightly_Damaged':
            self.dest_location = self.env['stock.location'].search([('item_status','=','Slightly_Damaged')]).id
        elif self.item_status == 'Damaged':
            self.dest_location = self.env['stock.location'].search([('item_status','=','Damaged')]).id 
        elif self.item_status == 'Scrapped':
            self.dest_location = self.env.ref('stock.stock_location_scrapped').id #self.env['stock.location'].search([('item_status','=','Scrapped')]).id
        else:
            location_id = self.env['stock.location'].search([('item_status','=','Good')]).id
            if self.reten_req_id.operation_type_id.default_location_dest_id:
                location_id = self.reten_req_id.operation_type_id.default_location_dest_id.id
            self.dest_location =  location_id #self.env['stock.location'].search([('item_status','=','Good')]).id