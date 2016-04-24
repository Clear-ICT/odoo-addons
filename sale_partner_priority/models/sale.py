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
from openerp.addons.partner_priority.models.res_partner import PARTNER_PRIO


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.multi
    @api.depends('partner_id', 'partner_id.priority')
    def _get_priority(self):

        for order in self:
            order.priority = order.partner_id.priority

    # Fields
    #
    priority = fields.Selection(
        selection=PARTNER_PRIO,
        compute=_get_priority, store=True, select=True, readonly=True)


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    @api.multi
    @api.depends('order_id.partner_id', 'order_id.partner_id.priority')
    def _get_priority(self):

        for line in self:
            line.priority = line.order_id.partner_id.priority

    # Fields
    #
    priority = fields.Selection(
        selection=PARTNER_PRIO,
        compute=_get_priority, store=True, select=True, readonly=True)
