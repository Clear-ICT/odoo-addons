# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2015 Clear ICT Solutions <info@clearict.com>.
#    All Rights Reserved.
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

from openerp import api, models, exceptions
from openerp.tools.translate import _


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        company = self.env['res.company']
        if vals.get('partner_id', False):
            partner = self.env['res.partner'].browse(vals['partner_id'])
            company = self.env['res.company']

            if not partner.country_id \
                    or partner.country_id == company.country_id:
                if not partner.vat:
                    raise exceptions.Warning(
                        _('Customer does not have a Tax ID Number'),
                        _('You cannot make a sale to a '
                          'customer without a Tax ID Number.')
                    )
        return super(SaleOrder, self).create(vals)
