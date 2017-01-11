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


class CloseFundWizard(models.TransientModel):

    _name = 'account.pettycash.fund.close'
    _description = 'Petty Cash Fund Closing Wizard'

    @api.model
    def _get_fund(self):

        fund_id = self.env.context.get('active_id', False)
        return fund_id

    # Fields
    #
    fund = fields.Many2one(
        'account.pettycash.fund', default=_get_fund, required=True)
    receivable_account = fields.Many2one(
        'account.account', domain=[('type', '=', 'receivable')])
    effective_date = fields.Date(required=True)

    @api.multi
    def close_fund(self):

        # Create the petty cash fund
        #
        for wizard in self:
            wizard.fund.close_fund(
                wizard.effective_date, wizard.receivable_account)
