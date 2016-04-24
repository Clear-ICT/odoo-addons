# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Clear ICT Solutions <info@clearict.com>.
#    All Rights Reserved.
#       @author: Michael Telahun Makonnen <miket@clearict.com>
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

{
    'name': 'Sale Quantity Non-zero',
    'summary': 'Dissallow negative or zero quantity on sale order lines',
    'description': """
This module constrains the sale order line quantity to never be less than or
equal to zero.
    """,
    'author': 'Clear ICT Solutions <info@clearict.com>',
    'website': 'http://clearict.com',
    'category': 'Sales Management',
    'version': '1.0',
    'depends': [
        'sale',
    ],
    'data': [
    ],
    'demo': [
    ],
    'installable': True,
    'active': False,
}
