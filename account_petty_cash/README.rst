.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============
Petty Cash Management
=============

* Create petty cash fund
* Increase/decrease fund
* Assign custodian
* Create petty cash vouchers from the fund
* Reconcile petty cash vouchers
* Keep track of the account balance
* Close the fund

Configuration
=============

Before using a petty cash fund it must be configured by the Finance Manager
from Accounting -> Configuration -> Miscellaneous

Usage
=====

* The module posts a journal entry to Accounts Payable to the custodian for the fund amount
* The normal vendor payment process should be followed for making the payment
* The custodian issues petty cash vouchers for making payments from the fund
* The accountant reconciles the petty cash vouchers against receipts presented by the custodian
* After the reconciliation process a journal entry will be posted to Accounts Payable 
* For fund closing all vouchers must be reconciled beforehand and a journal entry is posted to Accounts Receivable

For further information, please visit:

 * https://www.clearict.com

Credits
=======

Contributors
------------

* Michael Telahun <miket@clearict.com>

Maintainer
----------

.. image:: sucros-clear-it-plc_logo.png
   :alt: Sucros Clear Information Technologies PLC
   :target: http://www.clearict.com

This module is maintained by Sucros Clear Information Technologies PLC

We are the premier implementer of Odoo in Ethiopia. Our mission is to enable
organizations to use technology to meet their business goals.

To contribute to this module, please visit http://github.com/clearict/odoo-addons.
