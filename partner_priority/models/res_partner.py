# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Clear ICT Solutions <info@clearict.com>.
#    © 2004-2009 Tiny SPRL (<http://tiny.be>).
#    © 2013 initOS GmbH & Co. KG (<http://www.initos.com>).
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

PARTNER_PRIO = [('0', 'D'), ('1', 'C'), ('2', 'B'), ('3', 'A')]


class ResPartner(models.Model):

    _inherit = 'res.partner'

    # Fields
    #
    priority = fields.Selection(PARTNER_PRIO, select=True)

    @api.model
    def _needsPriority(self, partner_id=None, vals=None):
        """
        Checks whether a priority should be assigned to a partner.
        :param parnter_id: id of the partner object
        :param vals: known field values of the partner object
        :return: true iff a priority should be assigned to the partner
        """
        if not vals and not partner_id:
            raise Exception('Either field values or an id must be provided.')
        vals = vals or {}
        # only assign a priority to commercial partners
        if partner_id:
            partner = self.browse(partner_id)
            vals.setdefault('is_company',  partner.is_company)
            vals.setdefault('parent_id', partner.parent_id.id)
        return vals.get('is_company') or not vals.get('parent_id')

    @api.model
    def _commercial_fields(self):
        """
        Make the partner reference a field that is propagated
        to the partner's contacts
        """
        return super(ResPartner, self)._commercial_fields() + ['priority']

    @api.model
    def create(self, vals):
        if not vals.get('priority') and self._needsPriority(vals=vals):
            vals['priority'] = '0'
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        for partner in self:
            prio = vals.get('priority') \
                if 'priority' in vals else partner.priority
            if not prio and self._needsPriority(partner.id, vals):
                vals['priority'] = '0'
            super(ResPartner, partner).write(vals)
        return True

    @api.one
    def copy(self, default=None):
        default = default or {}
        if self._needsPriority(self.id):
            default.update({
                'priority': '0',
            })

        return super(ResPartner, self).copy(default)
