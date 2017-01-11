# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################

from datetime import datetime

from openerp import api, exceptions, fields, models
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.tools.translate import _


class IssueVoucherWizard(models.TransientModel):

    _name = 'account.pettycash.fund.reconcile'
    _desc = 'Petty Cash Fund Reconciliation Wizard'

    @api.model
    def _get_fund(self):

        fund_id = self.env.context.get('active_id', False)
        return fund_id

    @api.model
    def _get_vouchers(self):

        fund_id = self._get_fund()
        if not fund_id:
            return []

        f = self.env['account.pettycash.fund'].browse(fund_id)
        vouchers = [
            (6, 0,
             [v.id for v in f.vouchers if v.state not in ['cancel', 'posted']])
        ]

        return vouchers

    # Field
    #
    fund = fields.Many2one('account.pettycash.fund', required=True,
                           default=_get_fund)
    date = fields.Date(required=True, default=datetime.today().date())
    payable_account = fields.Many2one(
        'account.account', required=True, domain=[('type', '=', 'payable')],
        help="The account used to record the payable amount to the custodian.")
    reconciled_amount = fields.Float(
        digits_compute=dp.get_precision('Product Price'), readonly=True)
    move = fields.Many2one('account.move', readonly=True)
    vouchers = fields.Many2many('account.voucher',
                                default=_get_vouchers)

    @api.multi
    def reconcile_vouchers(self):

        PettyCash = self.env['account.pettycash.fund']

        for wiz in self:

            total = 0.0
            for voucher in wiz.vouchers:

                # Do not process if voucher does not belong to this fund.
                if not voucher.petty_cash_fund \
                  or voucher.petty_cash_fund.id != wiz.fund.id:
                    raise exceptions.ValidationError(
                        _("Voucher (%s) does not belong to this petty cash "
                          "fund." % (voucher.name)))

                voucher.proforma_voucher()
                total += voucher.amount

            # Create a payable journal entry to custodian for total amount.
            move = PettyCash.create_payable_journal_entry(
                wiz.fund, wiz.payable_account.id, wiz.date, total,
                _("Replenish petty cash (%s)" % (wiz.fund.name)))

            wiz.reconciled_amount = total
            wiz.move = move

        return
