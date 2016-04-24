# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Clear ICT Solutions <info@clearict.com>.
#    All Rights Reserved.
#       @author: Michael Telahun Makonnen <miket@clearict.com>
#
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models


class ChangeDateWizard(models.TransientModel):

    _name = 'sale.order.line.wizard.change.date'
    _description = 'Wizard to Change Dates on Sale Order Line'

    # fields
    #
    order_line = fields.Many2one(
        'sale.order.line',
        default=lambda s: s.env.context.get('active_id', False))
    requested_date = fields.Datetime()

    @api.onchange('order_line')
    def onchange_order_line(self):

        for wizard in self:
            if wizard.order_line.requested_date:
                self.requested_date = wizard.order_line.requested_date

        return

    @api.multi
    def do_change(self):

        assert self.order_line, "Unable to get active_id of order line!"
        self.order_line.requested_date = self.requested_date

        return {'type': 'ir.actions.act_window_close'}
