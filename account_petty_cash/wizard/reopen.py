# -*- coding: utf-8 -*-
#
#
#    Copyright (c) 2016 Sucros Clear Information Technologies PLC.
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

from openerp import api, fields, models
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.tools import float_compare
from openerp.tools.translate import _


class ReopenFundWizard(models.TransientModel):

    _name = 'account.pettycash.fund.reopen'
    _description = 'Petty Cash Fund Re-open Wizard'

    @api.model
    def _get_fund(self):

        fund_id = self.env.context.get('active_id', False)
        return fund_id

    @api.model
    def _get_fund_amount(self):

        amount = False
        fnd = self.env['account.pettycash.fund'].browse(self._get_fund())
        if fnd:
            amount = fnd.amount
        return amount

    @api.model
    def _get_custodian(self):

        _id = False
        fnd = self.env['account.pettycash.fund'].browse(self._get_fund())
        if fnd:
            _id = fnd.custodian.id
        return _id

    # Fields
    #
    fund = fields.Many2one(
        'account.pettycash.fund', default=_get_fund, required=True)
    fund_amount = fields.Float(
        digits_compute=dp.get_precision('Product Price'), required=True,
        default=_get_fund_amount)
    custodian = fields.Many2one(
        'res.users', required=True, default=_get_custodian)
    payable_account = fields.Many2one('account.account', required=True,
                                      domain=[('type', '=', 'payable')])
    effective_date = fields.Date(required=True)
    payable_move = fields.Many2one('account.move', string="Journal Entry")

    @api.multi
    def reopen_fund(self):

        # Create the petty cash fund
        #
        for wizard in self:
            fnd = wizard.fund

            desc = _("Re-open Petty Cash Fund (%s)" % (wizard.fund.name))

            # Make necessary changes to fund
            #
            update_vals = {}
            if fnd.custodian.id != wizard.custodian.id:
                update_vals.update({'custodian': wizard.custodian.id})
            if float_compare(
                    fnd.amount, wizard.fund_amount, precision_digits=2) != 0:
                update_vals.update({'amount': wizard.fund_amount})
            fnd.reopen_fund()
            fnd.write(update_vals)

            # Create payable account entry and post it
            #
            move = fnd.create_payable_journal_entry(
                fnd, wizard.payable_account.id, wizard.effective_date,
                wizard.fund_amount, desc)
            wizard.payable_move = move
