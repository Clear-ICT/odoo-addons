#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2015 Sucros Clear Information Technologies PLC.
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
#
{
    "name": "Sequence number by partner and product",
    "summary": "Implements sequence numbers per partner per product",
    "description": """
Sequence Number based on Partner and Product
============================================
This modules implements sequence numbers based on partner and product. A new
method is introduced on ir.sequence: get_next_by_partner_product(partner_id, product_id, code).
To use it:
    1. Create a sequence type for the type of sequence(s) you want
    2. Create a sequence record for every partner/product combination you want to track
    3. To get the next sequence call self.env['ir.sequence'].get_next_by_partner_product(partner_id, product_id, sequence_type_code)
    """,
    "author": "Sucros Clear Information Technologies PLC",
    "website": "http://clearict.com",
    "category": "Generic Modules/Base",
    "version": "1.1",
    "depends": [
        "base",
        "ir_sequence_by_partner",
    ],
    "update_xml": [
        'ir_sequence_view.xml',
    ],
    "active": False,
    "installable": True
}
