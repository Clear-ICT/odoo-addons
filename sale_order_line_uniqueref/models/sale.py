# -*- coding:utf-8 -*-
#
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
#

import logging

from openerp import api, fields, models, SUPERUSER_ID

_logger = logging.getLogger(__name__)


class SaleLine(models.Model):

    _inherit = 'sale.order.line'

    # fields
    #
    unique_ref = fields.Char(string="Unique Ref.", copy=False)

    _sql_constraints = [
        ('uniqueref_uniq', 'unique(unique_ref)',
         'The sale order line unique reference # must be unique accross all \
          companies.'),
    ]

    @api.model
    def create(self, vals):

        if 'unique_ref' not in vals.keys() or not vals['unique_ref']:
            ref = self.env['ir.sequence'].\
                next_by_code('sale.order.line.unique.ref') or '/'
            vals.update({'unique_ref': ref})

        return super(SaleLine, self).create(vals)

    def _set_unique_refs(self, cr, ids):

        for _id in ids:
            ref = self.pool['ir.sequence'].\
                next_by_code(
                    cr, SUPERUSER_ID, 'sale.order.line.unique.ref'
            ) or '/'
            query = "UPDATE sale_order_line \
                     SET unique_ref=%s      \
                     WHERE id=%s"
            cr.execute(query, (ref, _id))
        return True

    def init(self, cr):
        """Set reference numbers (if not set) at module installation"""

        cr.execute("SELECT id             \
                    FROM sale_order_line  \
                    WHERE unique_ref is NULL",)
        to_set = cr.fetchall()
        if to_set:
            _logger.info(
                'Setting unique reference numbers for %s sale order lines',
                len(to_set)
            )
            self._set_unique_refs(cr, to_set)
        return True
