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

{
    'name': 'Fleet Department',
    'summary': 'Associate a vehicle with a department',
    'description': """
Fleet Department
================
This module allows the assignment of a vehicle to a department. For vehicles
that have been assigned to a department only a Manager who has an employee
record linked to that department can manage it.
    """,
    'author': 'Clear ICT Solutions <info@clearict.com>',
    'website': 'http://www.clearict.com',
    'version': '1.0',
    'category': 'Managing vehicles and contracts',
    'depends': [
        'fleet',
        'hr',
    ],
    'data': [
        'security/fleet.xml',
        'security/ir.model.access.csv',
        'views/fleet.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
