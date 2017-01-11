# -*- coding: utf-8 -*-
#
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Sucros Clear Information Technologies PLC.
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

{
    'name': 'Change Dates on Sale Order Lines',
    'summary': 'Change requested date on sale order lines',
    'description': """
Change the following dates on sale order lines
==============================================

    * Requested Date
""",
    'author': 'Sucros Clear Information Technologies PLC',
    'website': 'http://clearict.com',
    'version': '1.0',
    'category': 'Sales Management',
    'depends': [
        'sale_order_line_dates',
    ],
    'data': [
        'views/change_date_wizard.xml',
        'views/sale.xml',
    ],
    'installable': True,
    'auto_install': False,
}
