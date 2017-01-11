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

from openerp import api, fields, models
from openerp.addons.decimal_precision import decimal_precision as dp
from openerp.tools.translate import _


class IssueVoucherWizard(models.TransientModel):

    _name = 'account.pettycash.fund.voucher'
    _desc = 'Petty Cash Fund Issue Voucher Wizard'

    @api.model
    def _get_fund(self):

        fund_id = self.env.context.get('active_id', False)
        return fund_id

    # Field
    #
    fund = fields.Many2one('account.pettycash.fund', required=True,
                           default=_get_fund)
    date = fields.Date(required=True, default=datetime.today().date())
    partner = fields.Many2one('res.partner')
    lines = fields.One2many('account.pettycash.fund.voucher.line', 'wizard')
    voucher = fields.Many2one('account.voucher')

    @api.multi
    def create_voucher(self):

        Vouchers = self.env['account.voucher']
        for wiz in self:
            lines = []
            total_lines = 0.0
            for line in wiz.lines:
                line_vals = {
                    'name': line.memo,
                    'type': 'dr',
                    'account_id': line.expense_account.id,
                    'amount': line.amount,
                }
                lines.append((0, 0, line_vals))
                total_lines += line.amount
            voucher_vals = {
                'name': _('Petty Cash Expenditure %s' % (wiz.date)),
                'journal_id': wiz.fund.journal.id,
                'account_id': wiz.fund.journal.default_credit_account_id.id,
                'amount': total_lines,
                'petty_cash_fund': wiz.fund.id,
                'partner_id': wiz.partner.id,
                'date': wiz.date,
                'type': 'payment',
                'audit': True,
            }
            onchange_res = Vouchers.onchange_journal(
                wiz.fund.journal.id, [], False, wiz.partner.id, wiz.date,
                total_lines, 'payment', False)
            voucher_vals.update(onchange_res['value'])
            voucher_vals.update({'line_dr_ids': lines})

            wiz.voucher = Vouchers.create(voucher_vals)

        return


class IssueVoucherWizardLine(models.TransientModel):

    _name = 'account.pettycash.fund.voucher.line'
    _desc = 'Petty Cash Fund Issue Voucher Wizard Line'

    # Fields
    #
    wizard = fields.Many2one('account.pettycash.fund.voucher')
    expense_account = fields.Many2one(
        'account.account', required=True,
        domain=[('type', '=', 'other'), ('user_type.code', '=', 'expense')])
    amount = fields.Float(digits_compute=dp.get_precision('Product Price'),
                          required=True)
    memo = fields.Char()
