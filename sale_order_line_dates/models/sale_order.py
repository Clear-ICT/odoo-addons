# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Clear ICT Solutions <info@clearict.com>.
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from datetime import datetime, timedelta

from openerp import api, fields, models
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DTFORMAT


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.model
    def _get_date_planned(self, order, line, start_date):

        if line and line.requested_date:
            date_planned = datetime.strptime(line.requested_date, OE_DTFORMAT)
            date_planned -= timedelta(days=order.company_id.security_lead)
            return date_planned.strftime(OE_DTFORMAT)

        return super(SaleOrder, self).\
            _get_date_planned(order, line, start_date)


class SaleOrderLine(models.Model):

    """Add several date fields to Sale Order Lines"""

    _inherit = 'sale.order.line'

    @api.depends('state', 'order_id.picking_ids')
    def _get_shipped_date(self):
        """Read the shipping date from the related pickings"""

        for line in self:
            order = line.order_id
            dates_list = []
            for pick in order.picking_ids:
                for move in pick.move_lines:
                    if move.product_id.id == line.product_id.id \
                       and move.state == 'done':
                        dates_list.append(pick.date)
            if dates_list:
                line.shipped_date = max(dates_list)
            else:
                line.shipped_date = False

    @api.depends('product_id', 'delay')
    def _get_commitment_date(self):
        """Compute the commitment date"""

        for line in self:
            if line.state == 'cancel':
                continue
            dates_list = []
            order_datetime = datetime.strptime(line.order_id.date_order,
                                               OE_DTFORMAT)
            dt = order_datetime + timedelta(days=line.delay or 0.0)
            dates_list.append(dt.strftime(OE_DTFORMAT))
            if dates_list:
                line.commitment_date = min(dates_list)

    @api.onchange('requested_date')
    def onchange_requested_date(self):
        """Warn if the requested dates is sooner than the commitment date"""

        for line in self:
            if (line.requested_date and
                    line.commitment_date and
                    line.requested_date < line.commitment_date):
                return {'warning': {
                    'title': _('Requested date is too soon!'),
                    'message': _("The date requested by the customer is "
                                 "sooner than the commitment date. You may be "
                                 "unable to honor the customer's request.")
                }
                }
        return {}

    # Fields
    #
    commitment_date = fields.Datetime(
        compute=_get_commitment_date, store=True, string='Commitment Date',
        help="Date by which the products are sure to be delivered. This is "
             "a date that you can promise to the customer, based on the "
             "Product Lead Times.")
    requested_date = fields.Datetime(
        'Requested Date', readonly=False, copy=False,
        help="Date by which the customer has requested the items to be "
             "delivered.\n"
             "When this Order gets confirmed, the Delivery Order's "
             "expected date will be computed based on this date and the "
             "Company's Security Delay.\n"
             "Leave this field empty if you want the Delivery Order to be "
             "processed as soon as possible. In that case the expected "
             "date will be computed using the default method: based on "
             "the Product Lead Times and the Company's Security Delay.")
    shipped_date = fields.Date(
        compute=_get_shipped_date, store=False, string='Shipped Date',
        help="Date on which the last shipment was made.")
