from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

HTML_INSTRUCTIONS = '<p><b><font style="font-size: 14px;">This form is for requesting pull-outs from branches. Please see further instructions below:</font></b><ol><li><p><font style="font-size: 14px;">For Source Location, choose the store/branch that is requesting the pull-out.&nbsp;</font></p></li><li><p><font style="font-size: 14px;">For Scheduled Pick Up Date, please make sure the products are ready for pull-out by then. This means the documents should be prepared and the products should be packed.&nbsp;</font></p></li><li><p><font style="font-size: 14px;">For Scheduled Pick Up Date, please make sure the products are ready for pull-out by then. This means the documents should be prepared and the products should be packed.&nbsp;</font></p></li></ol></p>'


class ReturnStockRequest(models.Model):
    _name = 'return.stock.request'
    _description = "Return Stock Request"

    @api.model
    def _get_ope_type_id(self):
        return self.env.ref('stock.picking_type_internal', False)

    @api.model
    def _get_instructions(self):
        return HTML_INSTRUCTIONS

    date_now = fields.Date('Date', default=fields.Datetime.now,)
    state = fields.Selection([('Draft', 'Draft'), ('Submitted', 'Submitted'),
                              ('Done', 'Done')], string="State", default="Draft")
    scheduled_pick_up_date = fields.Date('Scheduled Pick Up Date', required=True)
    source_location = fields.Many2one('stock.location', 'Source Location')
    operation_type_id = fields.Many2one(
        'stock.picking.type', string='Picking Type', default=_get_ope_type_id)
    stock_request_line = fields.One2many(
        'return.stock.request.line', 'reten_req_id', 'Line')
    picking_count = fields.Integer(
        string='Number of Picking',
        compute='_compute_picking_count',
    )
    origin = fields.Char(string='RS #', required=True)

    instructions = fields.Text(
        string='Instructions', compute='_compute_get_instructions', default=_get_instructions)

    view_record = fields.Boolean(
        string="Allow to View", compute='_compute_allow_to_view', search="_search_allow_to_view")

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
                    # Get the Employee ID of the Created User
                    hr_employee_obj = hr_employee_model.search(
                        [('user_id', '=', rec.create_uid.id)])
                    # Get the Employee ID of the Sales Manager
                    hr_man_employee_obj = hr_employee_model.search(
                        [('user_id', '=', self.env.user.id)])

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
                    # Get the Employee ID of the Created User
                    hr_employee_obj = hr_employee_model.search(
                        [('user_id', '=', rec.create_uid.id)])
                    # Get the Employee ID of the Sales Manager
                    hr_man_employee_obj = hr_employee_model.search(
                        [('user_id', '=', self.env.user.id)])

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

    @api.multi
    def _compute_get_instructions(self):
        for rec in self:
            rec.instructions = HTML_INSTRUCTIONS

    @api.multi
    def _compute_picking_count(self):
        for line in self:
            picking_ids = self.env['stock.picking'].search(
                [('return_request_id', '=', line.id)])
            line.picking_count = len(picking_ids)

    @api.multi
    def action_picking_count(self):
        model_object = self.env['ir.model.data']
        picking_ids = self.env['stock.picking'].search(
            [('return_request_id', '=', self.id)])
        dummy, action_id = tuple(model_object.get_object_reference(
            'stock', 'action_picking_tree_all'))
        [action] = self.env['ir.actions.act_window'].browse(action_id).read()
        if len(picking_ids) > 0:
            action['domain'] = [('id', 'in', picking_ids.ids)]
        elif len(sales_meeting_ids) == 1:
            action['views'] = [
                (self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = picking_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action



    def submit(self):

        for rec in self:

            rec.write({'state': 'Submitted'})

            if rec.stock_request_line:

                destlocsall = []
                for line in rec.stock_request_line:
                    destlocsall.append(line.dest_location)

                destlocs = set(destlocsall)
                for destloc in destlocs:

                    # mydest = self.env['stock.location'].search([('id', '=', destloc)])[0]

                    picking_id = self.env['stock.picking'].create({
                            'picking_type_id': rec.operation_type_id.id,
                            'location_id': rec.source_location.id,
                            'location_dest_id': destloc.id,
                            'return_request_id': rec.id,
                            'assigned_odr': rec.origin

                        })
                    
                    for line in rec.stock_request_line:

                        if line.dest_location == destloc:                       
                            picking_id.write({'scheduled_date': rec.scheduled_pick_up_date})
                            rec.env['stock.move'].create({
                                'product_id': line.product_id.id,
                                'name': line.product_id.name,
                                'product_uom': line.product_id.uom_id.id,
                                'product_uom_qty': line.qty,
                                'quantity_done': line.qty,
                                'picking_id': picking_id.id,
                                'location_id': rec.source_location.id,
                                'location_dest_id': destloc.id
                            })

    def done(self):
        self.write({'state': 'Done'})
        picking_ids = self.env['stock.picking'].search(
            [('return_request_id', '=', self.id)])
        for picking_id in picking_ids:
            picking_id.action_confirm()
            picking_id.action_assign()
            picking_id.button_validate()


class ReturnStockRequestLine(models.Model):
    _name = 'return.stock.request.line'
    _description = "Return Stock Request Line"

    # @api.model
    # def _filter_by_selLoc(self):
    #     OL_STOCK = self.env.ref('__export__.stock_location_10949_5cdad591').id
    #     WH_STOCK = self.env.ref('stock.stock_location_stock').id
    #     SLGHT_DMG = self.env.ref('__export__.stock_location_10901_8ec8f698').id
    #     return [('id', 'in', [OL_STOCK, WH_STOCK, SLGHT_DMG])]

    product_id = fields.Many2one('product.product', 'Product')
    reten_req_id = fields.Many2one('return.stock.request', 'Retrn Req ID')
    item_status = fields.Selection([('Good', 'Good'), ('Slightly_Damaged', 'Slightly Damaged'),
                                    ('Scrapped', 'Scrapped')], string='Status', default='Good')
    qty = fields.Float('Quantity')
    unit_price = fields.Float('Unit Price')
    amount = fields.Float('Amount')
    dest_location = fields.Many2one(
        'stock.location', 'Destination Location', domain=[('is_amc_return_stock_location','=',True)])

    @api.onchange('product_id', 'item_status', 'qty')
    def product_onchange(self):
        if not self.reten_req_id.operation_type_id:
            raise UserError(
                _('Select first a Picking Type before adding an Item to Return.'))
        self.unit_price = self.product_id.list_price
        self.amount = self.qty * self.unit_price
        if self.item_status == 'Slightly_Damaged':
            self.dest_location = self.env['stock.location'].search(
                [('item_status', '=', 'Slightly_Damaged')]).id
        elif self.item_status == 'Damaged':
            self.dest_location = self.env['stock.location'].search(
                [('item_status', '=', 'Damaged')]).id
        elif self.item_status == 'Scrapped':
            # self.env['stock.location'].search([('item_status','=','Scrapped')]).id
            self.dest_location = self.env.ref(
                'stock.stock_location_scrapped').id
        else:
            location_id = self.env['stock.location'].search(
                [('item_status', '=', 'Good')]).id
            if self.reten_req_id.operation_type_id.default_location_dest_id:
                location_id = self.reten_req_id.operation_type_id.default_location_dest_id.id
            # self.env['stock.location'].search([('item_status','=','Good')]).id
            self.dest_location = location_id
