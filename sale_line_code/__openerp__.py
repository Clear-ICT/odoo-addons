#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Clear ICT Solutions <info@clearict.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
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
    'name': 'Sales Order Line Reference Codes',
    'summary': 'Add both internal and customer reference codes to sales line items',
    'description': """
Sales Order Line Reference Codes
================================
* Sale Order Line
    * Internal Company Reference Number
    * Customer Reference Number
    """,
    'author':'Clear ICT Solutions',
    'website':'http://clearict.com',
    'category': 'Sales',
    'version': '1.0',
    'depends': [
        'sale',
    ],
    'data': [
        'views/sale.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'active': False,
}
