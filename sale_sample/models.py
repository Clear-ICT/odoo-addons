# -*- coding:utf-8 -*-
##############################################################################
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
##############################################################################

from openerp import api, fields, models
from openerp.addons import decimal_precision as dp


class res_partner(models.Model):

    _inherit = 'res.partner'

    @api.multi
    @api.depends('sale_order_ids')
    def _sale_order_count(self):

        # The current user may not have access rights for sale orders
        try:
            for partner in self:
                sale_count = 0
                sample_count = 0
                for sale in partner.sale_order_ids:
                    if sale.is_sample:
                        sample_count += 1
                    else:
                        sale_count += 1

                partner.sale_order_count = sale_count
        except:
            pass

    # Fields
    #

    # redefined from module: sale
    sale_order_count = fields.Integer(compute=_sale_order_count,
                                      string='# of Sales Order')


class sale_order(models.Model):

    _inherit = 'sale.order'

    # Fields
    #
    is_sample = fields.Boolean(string="Sample Order", default=False)
    parent_id = fields.Many2one('sale.order', string="Parent Sales Order")
    sample_ids = fields.One2many('sale.order', 'parent_id',
                                 string="Sample Orders")

    # Methods
    #

    @api.model
    @api.returns('sale.order')
    def create(self, vals):

        if vals.get('is_sample', False) and vals.get('name', '/') == '/':
            IrSeq = self.env['ir.sequence']
            ref = IrSeq.next_by_code('sale.order.sample.ref') or '/'
            parent = self.search([('id', '=', vals.get('parent_id'))])
            vals['name'] = parent.name + ref
            vals['user_id'] = parent.user_id.id

        return super(sale_order, self).create(vals)


class sample_order_wizard(models.TransientModel):

    _name = 'sale.order.sample.wizard'
    _description = 'Sample Sale Order Wizard'

    # Field default values
    #

    def _get_parent(self):

        res = False
        if self.env.context \
                and 'active_id' in list(self.env.context.iterkeys()):
            res = self.env.context['active_id']

        return res

    def _get_new_sale_line(self, orig_sale, orig_sale_line, wizard_line):
        """Internal function to get the fields of the sale order line. Modules
        enhancing this one should add their own fields to the return value."""

        res = {
            'order_id': orig_sale.id,
            'product_id': orig_sale_line.product_id.id,
            'name': orig_sale_line.name,
            'sequence': orig_sale_line.sequence,
            'price_unit': orig_sale_line.price_unit,
            'product_uom': orig_sale_line.product_uom.id,
            'product_uom_qty': wizard_line and wizard_line.qty or 0,
            'product_uos_qty': wizard_line and wizard_line.qty or 0,
        }

        # Simple check for installation of sale_line_code module
        if hasattr(orig_sale_line, 'order_line_ref'):
            res.update({'order_line_ref': orig_sale_line.order_line_ref})

        return res

    def _get_order_lines(self, sale):

        res = []
        for line in sale.order_line:
            wizard_line = False
            for wzline in self.wizard_lines:
                if wzline.product == line.product_id:
                    wizard_line = wzline
                    break

            if wizard_line:
                res.append(
                    (0, 0, self._get_new_sale_line(sale, line, wizard_line))
                )

        return res

    def _get_wizard_lines(self):

        res = []
        if self._get_parent():
            SaleOrder = self.env['sale.order']
            parent = SaleOrder.search([('id', '=', self._get_parent())])
            for line in parent.order_line:
                res.append((0, 0,
                            {
                                'product': line.product_id,
                                'qty': 1,
                            }))
        return res

    # Fields
    #
    order = fields.Many2one('sale.order', default=_get_parent, readonly=True)
    wizard_lines = fields.One2many('sale.order.sample.wizard.line', 'wizard',
                                   default=_get_wizard_lines)
    order_date = fields.Datetime(default=fields.Datetime.now())

    # Methods
    #

    @api.one
    def create_order(self):

        sale_vals = {
            'user_id': self.order.user_id.id,
            'partner_id': self.order.partner_id.id,
            'parent_id': self.order.id,
            'date_order': self.order_date,
            'client_order_ref': self.order.client_order_ref,
            'company_id': self.order.company_id.id,
            'is_sample': True,
            'order_line': self._get_order_lines(self.order)
        }
        self.env['sale.order'].create(sale_vals)

        return {'type': 'ir.actions.act_window_close'}


class sample_order_wizard_line(models.TransientModel):

    _name = 'sale.order.sample.wizard.line'
    _description = 'Sample Order Wizard Line'

    wizard = fields.Many2one('sale.order.sample.wizard')
    product = fields.Many2one('product.product',
                              domain=[('sale_ok', '=', True)])
    qty = fields.Float(string="Quantity", default=1.0,
                       digits_compute=dp.get_precision('Product UoS'))
