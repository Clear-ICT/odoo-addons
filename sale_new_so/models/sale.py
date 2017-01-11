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

from openerp import api, models


class SaleOrder(models.Model):

    _inherit = 'sale.order.line'

    # Copied verbatim from a similar function in sale_sample module.
    #
    def _get_fields_from_line(self):
        """Internal function to get the fields of the sale order line. Modules
        enhancing this one should add their own fields to the return value."""

        res = {
            'product_id': self.product_id.id,
            'name': self.name,
            'price_unit': self.price_unit,
            'product_uom': self.product_uom.id,
            'product_uom_qty': self.product_uom_qty,
            'product_uos_qty': self.product_uos_qty,
        }

        # Simple check for installation of sale_line_code module
        if hasattr(self, 'order_line_ref'):
            res.update({'order_line_ref': self.order_line_ref})

        return res

    @api.multi
    def create_so_from_line(self):

        self.ensure_one()
        OrigSO = self.order_id
        new_name = OrigSO.get_so_create_name(OrigSO.partner_id.id, '/')

        new_so = {
            'origin': OrigSO.name,
            'name': new_name,
            'partner_id': OrigSO.partner_id.id,
            'date_order': OrigSO.date_order,
            'client_order_ref': OrigSO.client_order_ref,
            'pricelist_id':
                OrigSO.pricelist_id and OrigSO.pricelist_id.id or False,
            'currency_id':
                OrigSO.currency_id and OrigSO.currency_id.id or False,
            'user_id': OrigSO.user_id.id,
            'section_id': OrigSO.section_id and OrigSO.section_id.id or False,
            'payment_term':
                OrigSO.payment_term and OrigSO.payment_term.id or False,
            'fiscal_position':
                OrigSO.fiscal_position and OrigSO.fiscal_position.id or False,
            'company_id': OrigSO.company_id and OrigSO.company_id.id or False,
            'order_line': [(0, 0, self._get_fields_from_line())]
        }
        NewSO = OrigSO.create(new_so)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': NewSO.id,
            'view_mode': 'form,tree,calendar,graph',
            'view_type': 'form',
        }
