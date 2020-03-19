from odoo import models, fields, api

from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class PrintPicklist(models.TransientModel):
	_name = 'print.picklist'

	name = fields.Char()

	def print(self):
		context = dict(self._context or {})
		active_ids = context.get('active_ids', [])
		picking_ids = self.env['stock.picking'].browse(active_ids)
		# print picking_ids
		_logger.info('PAIN')
		_logger.info(picking_ids)
		for picking in picking_ids:
			picking.write({'printed': True})
		return self.env.ref('amc_custom.action_report_picklist').with_context(active_ids=picking_ids.ids, active_model='stock.picking').report_action([])