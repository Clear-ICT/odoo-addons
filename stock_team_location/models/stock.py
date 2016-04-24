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

from openerp import api, fields, models, exceptions
from openerp.tools.translate import _

WARN_STR_INVALID_CONF = _('Invalid Configuration')


class Inventory(models.Model):

    _inherit = 'stock.inventory'

    # Fields
    #
    inventory_location_id = fields.Many2one(
        'stock.location', string='Gain/Loss Location',
        readonly=True, states={'draft': [('readonly', False)]},
        help="Enter an alternate inventory gain/loss location here")


class InventoryLine(models.Model):

    _inherit = 'stock.inventory.line'

    @api.model
    def get_inventory_loss_location(self, inventory_line):

        if inventory_line.inventory_id.inventory_location_id:
            return inventory_line.inventory_id.inventory_location_id.id
        return super(InventoryLine, self).get_inventory_loss_location(
            inventory_line
        )


class StockTeam(models.Model):

    _name = 'stock.team'
    _description = 'Stock Team'

    # Fields
    #
    name = fields.Char(required=True)
    user = fields.Many2one('res.users', required=True, string='Cashier')
    more_users = fields.Many2many('res.users', string="Additional users")
    inventory_location = fields.Many2one('stock.location')
    active = fields.Boolean(default=True)

    @api.model
    def get_parent_inventory_location(self):

        env = self.env
        conf = env['stock.config.settings']
        res = conf.get_default_team_inventory_location(['acct_recv_cashiers'])
        return env['stock.location'].browse(res['team_inventory_location'])

    @api.one
    def create_inventory_location(self):

        Team = self
        env = self.env

        ParentLocation = self.get_parent_inventory_location()
        if not ParentLocation:
            raise exceptions.Warning(
                WARN_STR_INVALID_CONF,
                _("Stock teams' parent inventory location not configured!"))

        new_location = {
            'name': Team.name,
            'usage': 'inventory',
            'location_id': ParentLocation.id,
            'reconcile': True,
        }
        Team.inventory_location = env['stock.location'].create(new_location)
