#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Clear ICT Solutions <info@clearict.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
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

from openerp.osv import fields, orm

class ir_sequence(orm.Model):
    
    _inherit = 'ir.sequence'
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', ondelete='cascade', select=1),
    }

    def next_by_partner_product(self, cr, uid, partner_id, product_id, sequence_code, context=None):
        """ Draw an interpolated string using a sequence with the requested code
            and associated with the specified partner and product.
            If several sequences with the correct code are available to the user
            (multi-company cases), the one from the user's current company will
            be used.

            :param dict context: context dictionary may contain a
                ``force_company`` key with the ID of the company to
                use instead of the user's current company for the
                sequence selection. A matching sequence for that
                specific company will get higher priority. 
        """
        self.check_access_rights(cr, uid, 'read')
        company_ids = self.pool.get('res.company').search(cr, uid, [], context=context) + [False]
        ids = self.search(cr, uid, [('partner_id', '=', partner_id),
                                    ('product_id', '=', product_id),
                                    '&', ('code', '=', sequence_code),
                                         ('company_id', 'in', company_ids)])
        return self._next(cr, uid, ids, context)
