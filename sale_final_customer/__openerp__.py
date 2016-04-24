# -*- coding:utf-8 -*-
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
    'name': 'Sale Final Customer',
    'summary': 'Set an intermediate partner to which products are shipped',
    'description': """
This module allows the salesperson to select intermediate customer to whom the
ordered products are shipped. The customer for whom this is done is now called
the 'Final Customer'.
    """,
    'author': 'Clear ICT Solutions <info@clearict.com>',
    'website': 'http://clearict.com',
    'category': 'Sales Management',
    'version': '1.0',
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'views/sale_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'active': False,
}
