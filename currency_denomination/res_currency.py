# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
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
##############################################################################

import math

from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.osv import fields, orm
from openerp.tools.float_utils import float_compare

class res_currency_denomination(orm.Model):
    
    _name = 'res.currency.denomination'
    _description = 'Currency Denomination'
    
    _columns = {
        'currency_id': fields.many2one('res.currency', 'Currency', required=True),
        'ratio': fields.float('Ratio', help="Ratio of this denomination to the smallest integral denomination."),
        'value': fields.float('Value', digits_compute=dp.get_precision('Account')),
    }
    
    _rec_name = 'value'

class res_currency(orm.Model):
    
    _inherit = 'res.currency'
    
    _columns = {
        'denomination_ids': fields.one2many('res.currency.denomination', 'currency_id',
                                            'Denominations'),
    }
    
    def get_denominations_from_amount(self, cr, uid, currency_name, amount, context=None):
        
        # Get denominations for currency
        # Arrange in order from largest value to smallest.
        #
        denominations = []
        smallest_note = 1
        currency_obj = self.pool.get('res.currency')
        currency_id = currency_obj.search(cr, uid, [('name', '=', currency_name)], context=context)[0]
        currency = currency_obj.browse(cr, uid, currency_id, context=context)
        for denom in currency.denomination_ids:
            if float_compare(denom.ratio, 1.00, precision_digits=2) == 0:
                smallest_note = denom.value

            if len(denominations) == 0:
                denominations.append(denom.value)
                continue
            
            idx = 0
            last_idx = len(denominations) - 1
            for preexist_val in denominations:
                if denom.value > preexist_val:
                    denominations.insert(idx, denom.value)
                    break
                elif idx == last_idx:
                    denominations.append(denom.value)
                    break
                idx += 1
        
        denom_qty_list = dict.fromkeys(denominations, 0)
        cents_factor = float(smallest_note) / denominations[-1]
        cents, notes = math.modf(amount)
        
        notes = int(notes)
        # XXX - rounding to 4 decimal places should work for most currencies... I hope
        cents = int(round(cents,4) * cents_factor)
        for denom in denominations:
            if notes >= denom:
                denom_qty_list[denom] += int(notes / denom)
            elif float_compare(denom, smallest_note, precision_digits=4) == 0:
                denom_qty_list[denom] += int(notes / smallest_note)
                notes = 0
            notes = (notes > 0) and (notes % denom) or 0
            
            if notes == 0 and cents >= (denom * cents_factor):
                cooked_denom = int(denom * cents_factor)
                if cents >= cooked_denom:
                    denom_qty_list[denom] += (cents / cooked_denom)
                elif denom == denominations[-1]:
                    denom_qty_list[denom] += (cents / cents_factor)
                    cents = 0
                cents = cents % denom
        
        res = []
        for k,v in denom_qty_list.items():
            vals = {
                'name': k,
                'qty': v,
            }
            res.append(vals)
        
        return res
