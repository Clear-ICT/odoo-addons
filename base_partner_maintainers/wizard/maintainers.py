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

from openerp import api, fields, models


class PartnerMaintainers(models.TransientModel):

    _name = 'res.partner.maintainers.wizard'
    _description = 'Partner Maintainers Wizard'

    def _get_current_maintainers(self):

        grp_partner_mgr = self.env.ref('base.group_partner_manager')
        if len(grp_partner_mgr) > 0:
            return grp_partner_mgr.users

        return self.env['res.users']

    # Fields
    #
    name = fields.Char(string='Partner Maintainers Wizard')
    user_ids = fields.Many2many(comodel_name='res.users', string="Maintainers",
                                default=_get_current_maintainers)

    @api.multi
    def save_maintainers(self):

        root_user = self.env.ref('base.user_root')
        for wizard in self:
            # You can never remove the Administrator
            if root_user not in wizard.user_ids:
                wizard.user_ids = root_user + wizard.user_ids

            grp_partner_mgrs = self.env.ref('base.group_partner_manager')
            grp_partner_mgrs.users = [(6, 0, wizard.user_ids.ids)]

        return {'type': 'ir.actions.act_window_close'}
