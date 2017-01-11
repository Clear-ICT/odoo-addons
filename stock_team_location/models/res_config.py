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


class ResConfig(models.TransientModel):

    _inherit = 'stock.config.settings'

    # Fields
    team_inventory_location = fields.Many2one(
        'stock.location', string="Stock Teams' parent inventory location"
    )

    @api.model
    def get_default_team_inventory_location(self, fields):

        loc = self.env.ref('stock_team_location.location_team_inventory')
        res = {
            'team_inventory_location': loc.exists() and loc.id or False
        }
        for rec in self.env['stock.config.settings'].search([]):
            res['team_inventory_location'] = rec.team_inventory_location.id
            break
        return res
