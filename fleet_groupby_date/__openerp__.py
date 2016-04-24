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
    'name': 'Vehicle Fuel Log Group by Date',
    'summary': 'Allow grouping fuel log entries by date',
    'description': """
Group Fuel Log Entries by Date
==============================
    """,
    'author':'Clear ICT Solutions <info@clearict.com>',
    'website':'http://clearict.com',
    'version': '1.0',
    'category': 'Generic Modules',
    'depends': [
        'fleet',
    ],
    'data': [
        'views/fleet_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'active': False,
}
