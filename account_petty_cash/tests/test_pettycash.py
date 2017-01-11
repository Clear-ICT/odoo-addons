# -*- coding: utf-8 -*-
#
#
#    Copyright (c) 2016 Sucros Clear Information Technologies Plc.
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
#

from datetime import datetime

from openerp import exceptions
from openerp.tests import common
from openerp.tools.float_utils import float_compare, float_is_zero


class TestPettyCashFund(common.TransactionCase):

    def setUp(self):
        super(TestPettyCashFund, self).setUp()

        self.VoucherObj = self.env['account.voucher']
        self.pcf_model = self.env['account.pettycash.fund']
        self.ir_seq = self.env['ir.sequence']
        self.jrn_model = self.env['account.journal']
        self.user_model = self.env["res.users"]
        self.uidAccountant = self.user_model.create({
            'name': 'Test Accountant',
            'login': 'accountant',
            'email': 'accountant@localhost',
        })
        self.uidAccountant.write({
            'groups_id': [(4, self.ref('account.group_account_user'))]
        })

        self.uidOwner = self.user_model.create({
            'name': 'Test Petty Cash Fund Owner',
            'login': 'pcfowner',
            'email': 'pcfowner@localhost',
        })
        self.uidOwner.write({
            'groups_id': [(4, self.ref('account.group_pettycash_custodian'))]
        })

        self.uidFinMgr = self.user_model.create({
            'name': 'Test Finance Manager',
            'login': 'finmgr',
            'email': 'finmgr@localhost',
        })
        self.uidFinMgr.write({
            'groups_id': [(4, self.ref('account.group_account_manager'))]
        })

        self.uidInv = self.user_model.create({
            'name': 'Test invoice',
            'login': 'invoice',
            'email': 'invoice@localhost',
        })
        self.uidInv.write({
            'groups_id': [(4, self.ref('account.group_account_invoice'))]
        })

        self.bank_account = self.env['account.account'].create({
            'name': 'Test Bank Account',
            'code': 'BNKPTY',
            'type': 'other',
            'user_type': self.env.ref('account.data_account_type_bank').id,
        })

        self.expense_account = self.env['account.account'].create({
            'name': 'Test Expense Account',
            'code': 'EXPT',
            'type': 'other',
            'user_type': self.env.ref('account.data_account_type_expense').id,
        })

        self.payable_account = self.env['account.account'].search(
            [('type', '=', 'payable'), ('currency_id', '=', False)],
            limit=1)[0]

        self.receivable_account = self.env['account.account'].search(
            [('type', '=', 'receivable'), ('currency_id', '=', False)],
            limit=1)[0]

        self.account = self.env['account.account'].search(
            [('type', '=', 'other'), ('currency_id', '=', False)],
            limit=1)[0]

        self.writeoff_account = self.env['account.account'].search(
            [('type', '=', 'other'), ('currency_id', '=', False)],
            limit=1)[0]

        self.owner = self.env['res.partner'].create({
            'name': 'Petty-cash Fund Owner',
        })

    def create_journal(self, name, code):

        jrnl = self.jrn_model.sudo(self.uidFinMgr).create({
            'name': name,
            'code': code,
            'type': 'cash',
            'default_credit_account_id': self.account.id,
            'default_debit_account_id': self.account.id,
        })
        return jrnl

    def get_jrn_code(self):

        prefix = '00'
        count = 0
        code = False
        while count < 1000:
            code = prefix + str(count)
            jrnls = self.jrn_model.search([('code', '=', code)])
            if not jrnls or len(jrnls) == 0:
                break
            count += 1
        return code

    def create_fund(self, name, custodian=None):

        if custodian is None:
            custodian = self.uidOwner

        Wizard = self.env['account.pettycash.fund.create']
        wiz = Wizard.sudo(self.uidFinMgr).create({
            'fund_name': name,
            'fund_code': self.get_jrn_code(),
            'fund_amount': 500.00,
            'custodian': custodian.id,
            'account': self.account.id,
            'payable_account': self.payable_account.id,
            'effective_date': datetime.today().date(),
        })
        wiz.sudo(self.uidFinMgr).initialize_fund()
        return wiz.fund

    def testManagerOnlyCreate(self):
        """Test only manager can create petty-cash fund"""

        pcf = self.create_fund('Test Petty Cash Fund')

        self.assertTrue(pcf.active)
        self.assertEquals(pcf.state, 'open')

        fundName = "Petty Cash - Test01"
        code = self.get_jrn_code()
        with self.assertRaises(exceptions.AccessError):
            self.pcf_model.sudo(self.uidAccountant).create_fund(
                1000.00, fundName, code, self.uidOwner, self.account)

    def testCustodianReadOnly(self):
        """Test custodian can only read petty-cash fund"""

        jrnl = self.create_journal("Petty Cash Journal", self.get_jrn_code())
        with self.assertRaises(exceptions.AccessError):
            self.pcf_model.sudo(self.uidOwner).\
                create({
                    'name': 'Test Petty Cash Fund',
                    'amount': 500.00,
                    'custodian': self.uidOwner.id,
                    'journal': jrnl.id,
                })

        pcf = self.create_fund('My Petty Cash Fund')

        # Test read
        self.assertEqual(pcf.custodian.id, self.uidOwner.id)

    def testCustodianSeesOnlyHisOwn(self):
        """Test custodian can see only his/her petty-cash funds"""

        uidOtherOwner = self.user_model.create({
            'name': 'Other Petty Cash Fund Owner',
            'login': 'pcfowner2',
        })
        uidOtherOwner.write({
            'groups_id': [(4, self.ref('account.group_pettycash_custodian'))]
        })

        pcf1 = self.create_fund('Petty Cash Fund 01')
        self.create_fund('Petty Cash Fund 02', custodian=uidOtherOwner)
        pcfs = self.pcf_model.sudo(self.uidOwner).search([])
        self.assertEqual(len(pcfs), 1)
        self.assertEqual(pcfs[0].id, pcf1.id)

    def testCreateSequence(self):
        """Test creation of sequence for journal"""

        fundName = "Petty Cash - Test01"
        code = "PTY01"
        prefix = "%s/%%(y)s/" % (code)
        sequences = self.pcf_model.sudo(self.uidFinMgr).\
            create_journal_sequence(fundName, code)

        self.assertEqual(len(sequences), 1)
        seq = sequences[0]
        self.assertEqual(seq.code, 'pay_voucher')
        self.assertEqual(seq.prefix, prefix)

    def testOnlyManagerCreateSequence(self):
        """Test only the finance manager can create sequences"""

        fundName = "Petty Cash - Test01"
        code = "PTY01"

        # Test Accountant
        with self.assertRaises(exceptions.AccessError):
            self.pcf_model.sudo(self.uidAccountant).\
                create_journal_sequence(fundName, code)

        # Test Custodian
        with self.assertRaises(exceptions.AccessError):
            self.pcf_model.sudo(self.uidOwner).\
                create_journal_sequence(fundName, code)

    def testCreateJournal(self):
        """Test manager can create a journal for petty cash fund"""

        fundName = "Petty Cash - Test01"
        code = "PTY01"
        SeqObj = self.env['ir.sequence']
        seq = SeqObj.sudo().create({
            'name': fundName,
            'code': 'pay_voucher',
            'prefix': code + "/%(y)s/",
            'padding': 2,
        })
        jrnl = self.pcf_model.sudo(self.uidFinMgr).create_journal(
            fundName, code, self.uidOwner.id, seq.id,
            self.account.id, self.account.id)

        self.assertEqual(len(jrnl), 1)
        jrn = jrnl[0]
        self.assertEqual(jrn.code, code)
        self.assertEqual(jrn.type, 'cash')
        self.assertEqual(jrn.user_id.id, self.uidOwner.id)
        self.assertEqual(jrn.sequence_id.id, seq.id)
        self.assertTrue(jrn.update_posted)

    def testCreateFund(self):
        """Test creation of petty cash fund"""

        fundName = "Petty Cash - Test01"
        code = "PTY01"
        prefix = "%s/%%(y)s/" % (code)
        fnd = self.pcf_model.sudo(self.uidFinMgr).create_fund(
            1000.00, fundName, code, self.uidOwner, self.account)

        self.assertEqual(len(fnd), 1)
        self.assertEqual(fnd.journal.sequence_id.code, 'pay_voucher')
        self.assertEqual(fnd.journal.sequence_id.prefix, prefix)
        self.assertEqual(fnd.journal.code, code)
        self.assertEqual(fnd.journal.type, 'cash')
        self.assertEqual(fnd.journal.user_id.id, self.uidOwner.id)
        self.assertEqual(fnd.name, fundName)
        self.assertEqual(
            float_compare(fnd.amount, 1000.00, precision_digits=2),
            0)
        self.assertEqual(fnd.custodian.id, self.uidOwner.id)
        self.assertEqual(fnd.state, 'open')

    def testCreateFundWizard(self):
        """Test fund creation wizard"""

        fundName = "Petty Cash - Test01"
        code = "PTY01"
        fund_amount = 1000.00

        Wizard = self.env['account.pettycash.fund.create']
        wiz = Wizard.sudo(self.uidFinMgr).create({
            'fund_name': fundName,
            'fund_code': code,
            'fund_amount': fund_amount,
            'custodian': self.uidOwner.id,
            'account': self.account.id,
            'payable_account': self.payable_account.id,
            'effective_date': datetime.today().date(),
        })
        wiz.initialize_fund()

        self.assertEqual(wiz.payable_move.state, 'posted')

        # Check ledger accounts have been updated properly:
        # Accounts payable should have a credit for the fund amount.
        # The fund account should have a debit for same amount.
        move = wiz.payable_move
        ml1 = move.line_id[0]
        ml2 = move.line_id[1]
        self.assertEqual(
            float_compare(ml1.debit, fund_amount, precision_digits=2),
            0.00)
        self.assertTrue(float_is_zero(ml1.credit, precision_digits=2))
        self.assertEqual(ml1.account_id.id, self.account.id)
        self.assertEqual(
            float_compare(ml2.credit, fund_amount, precision_digits=2),
            0.00)
        self.assertTrue(float_is_zero(ml2.debit, precision_digits=2))
        self.assertEqual(ml2.account_id.id, self.payable_account.id)

    def testCustodianCanSeeOwnVouchers(self):
        """Test the custodian can see only own petty cash vouchers"""

        VoucherWizard = self.env['account.pettycash.fund.voucher']
        uidOtherOwner = self.user_model.create({
            'name': 'Other Petty Cash Fund Owner',
            'login': 'pcfowner2',
            'email': 'pcfowner2@localhost',
        })
        uidOtherOwner.write({
            'groups_id': [(4, self.ref('account.group_pettycash_custodian'))]
        })

        # Create first fund and voucher
        #
        pcf1 = self.create_fund('Petty Cash Fund 01')
        vwiz_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'partner': pcf1.custodian_partner.id,
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 100.00}),
            ]
        }
        vwiz1 = VoucherWizard.sudo(self.uidOwner).create(vwiz_vals)
        vwiz1.create_voucher()
        self.assertEqual(
            float_compare(vwiz1.voucher.amount, 100.00, precision_digits=2),
            0)

        # Create second fund and voucher (with different custodian)
        #
        pcf2 = self.create_fund('Petty Cash Fund 02', custodian=uidOtherOwner)
        vwiz2_vals = {
            'fund': pcf2.id,
            'date': datetime.today().date(),
            'partner': pcf1.custodian_partner.id,
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 200.00}),
            ]
        }
        vwiz2 = VoucherWizard.sudo(uidOtherOwner).create(vwiz2_vals)
        vwiz2.create_voucher()
        self.assertEqual(
            float_compare(vwiz2.voucher.amount, 200.00, precision_digits=2),
            0)

        # See that one user cannot see the other's vouchers
        #
        vchrs = self.VoucherObj.sudo(self.uidOwner).\
            search([('petty_cash_fund', '=', pcf2.id)])
        self.assertEqual(len(vchrs), 0)
        vchrs = self.VoucherObj.sudo(self.uidOwner).\
            search([('petty_cash_fund', '=', pcf1.id)])
        self.assertEqual(len(vchrs), 1)

        vchrs = self.VoucherObj.sudo(uidOtherOwner).\
            search([('petty_cash_fund', '=', pcf1.id)])
        self.assertEqual(len(vchrs), 0)
        vchrs = self.VoucherObj.sudo(uidOtherOwner).\
            search([('petty_cash_fund', '=', pcf2.id)])
        self.assertEqual(len(vchrs), 1)

    def testVoucherCreate(self):
        """Test the fields from the wizard are copied to the voucher"""

        VoucherWizard = self.env['account.pettycash.fund.voucher']

        # Create first fund and voucher
        #
        pcf1 = self.create_fund('Petty Cash Fund 01')
        vwiz_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'partner': pcf1.custodian_partner.id,
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 100.00}),
            ]
        }
        vwiz1 = VoucherWizard.sudo(self.uidOwner).create(vwiz_vals)
        vwiz1.sudo(self.uidOwner).create_voucher()
        self.assertEqual(vwiz1.voucher.type, 'payment')
        self.assertEqual(vwiz1.voucher.partner_id.id, vwiz1.partner.id)
        self.assertEqual(vwiz1.voucher.date, vwiz1.date)
        self.assertEqual(vwiz1.voucher.line_ids[0].name, vwiz1.lines[0].memo)

        total_amount = 0.0
        for l in vwiz1.lines:
            total_amount += l.amount
        self.assertEqual(vwiz1.voucher.amount, total_amount)

    def testFundBalance(self):
        """Test the fund balance is accurate"""

        VoucherWizard = self.env['account.pettycash.fund.voucher']

        # Create first fund and voucher
        #
        pcf1 = self.create_fund('Petty Cash Fund 01')
        vwiz_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'partner': pcf1.custodian_partner.id,
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 100.00}),
            ]
        }
        vwiz1 = VoucherWizard.sudo(self.uidOwner).create(vwiz_vals)
        vwiz1.sudo(self.uidOwner).create_voucher()

        vwiz2_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 150.16}),
            ]
        }
        vwiz2 = VoucherWizard.sudo(self.uidOwner).create(vwiz2_vals)
        vwiz2.create_voucher()

        mybalance = pcf1.amount
        for l in vwiz1.lines:
            mybalance -= l.amount
        for l in vwiz2.lines:
            mybalance -= l.amount

        self.assertEqual(
            float_compare(pcf1.balance, mybalance, precision_digits=2),
            0)

    def testVouchersHistory(self):
        """Test posted and unposted vouchers are show separately"""

        VoucherWizard = self.env['account.pettycash.fund.voucher']

        # Create fund
        #
        pcf1 = self.create_fund('Petty Cash Fund 01')

        # Create vouchers
        #
        vwiz_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'partner': pcf1.custodian_partner.id,
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 100.00}),
            ]
        }
        vwiz1 = VoucherWizard.sudo(self.uidOwner).create(vwiz_vals)
        vwiz1.sudo(self.uidOwner).create_voucher()

        vwiz2_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 150.16}),
            ]
        }
        vwiz2 = VoucherWizard.sudo(self.uidOwner).create(vwiz2_vals)
        vwiz2.create_voucher()

        # Post the second voucher
        vwiz2.voucher.sudo(self.uidAccountant).button_proforma_voucher()
        self.assertEqual(vwiz2.voucher.state, 'posted')

        self.assertEqual(len(pcf1.vouchers), 1)
        self.assertEqual(pcf1.vouchers[0].id, vwiz1.voucher.id)
        self.assertEqual(len(pcf1.vouchers_history), 1)
        self.assertEqual(pcf1.vouchers_history[0].id, vwiz2.voucher.id)

    def testReconcileNonVoucher(self):
        """Test reconciling a voucher not from the fund fails"""

        ReconcileWizard = self.env['account.pettycash.fund.reconcile']

        # Create fund
        pcf1 = self.create_fund('Petty Cash Fund 01')

        # Create a voucher
        jrnl = self.create_journal("Just a test", "XYZ")
        line_vals = {
            'name': "Test voucher line",
            'type': 'dr',
            'account_id': self.expense_account.id,
            'amount': 50.00,
        }
        voucher_vals = {
            'name': "Test voucher",
            'journal_id': jrnl.id,
            'account_id': jrnl.default_credit_account_id.id,
            'amount': 50.00,
            'date': datetime.today().date(),
            'type': 'payment',
        }
        onchange_res = self.VoucherObj.onchange_journal(
            jrnl.id, [], False, False, datetime.today().date(),
            50.00, 'payment', False)
        voucher_vals.update(onchange_res['value'])
        voucher_vals.update({'line_dr_ids': [(0, 0, line_vals)]})
        voucher = self.VoucherObj.create(voucher_vals)

        wiz = ReconcileWizard.create({
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'payable_account': self.payable_account.id,
            'vouchers': [(4, voucher.id, 0)],
        })
        with self.assertRaises(exceptions.ValidationError):
            wiz.sudo(self.uidAccountant).reconcile_vouchers()

    def testReconcileSuccess(self):
        """Test that all vouchers of a fund are reconciled successfully"""

        VoucherWiz = self.env['account.pettycash.fund.voucher']
        ReconcileWiz = self.env['account.pettycash.fund.reconcile']

        # Create first fund and voucher
        #
        pcf1 = self.create_fund('Petty Cash Fund 01')
        vwiz_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'partner': pcf1.custodian_partner.id,
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 100.00}),
            ]
        }
        vwiz1 = VoucherWiz.sudo(self.uidOwner).create(vwiz_vals)
        vwiz1.sudo(self.uidOwner).create_voucher()

        vwiz2_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 150.16}),
            ]
        }
        vwiz2 = VoucherWiz.sudo(self.uidOwner).create(vwiz2_vals)
        vwiz2.sudo(self.uidOwner).create_voucher()
        receipts_total = 100.00 + 150.16

        self.assertEqual(pcf1.vouchers[0].state, 'draft')
        self.assertEqual(pcf1.vouchers[1].state, 'draft')
        self.assertEqual(len(pcf1.vouchers_history), 0)

        ctx = self.env.context.copy()
        ctx.update({'active_id': pcf1.id})
        wiz = ReconcileWiz.sudo(self.uidAccountant).with_context(ctx).create({
            'payable_account': self.payable_account.id,
            'date': datetime.today().date(),
        })
        self.assertEqual(len(wiz.vouchers), 2)
        wiz.sudo(self.uidAccountant).reconcile_vouchers()

        self.assertEqual(pcf1.vouchers_history[0].state, 'posted')
        self.assertEqual(pcf1.vouchers_history[1].state, 'posted')
        self.assertEqual(len(pcf1.vouchers), 0)
        self.assertEqual(pcf1.balance, pcf1.amount)

        # Check journal entries
        #

        self.assertEqual(wiz.move.state, 'posted')

        # Check ledger accounts have been updated properly:
        # Accounts payable should have a credit for the fund amount.
        # The fund account should have a debit for same amount.
        move = wiz.move
        ml1 = move.line_id[0]
        ml2 = move.line_id[1]
        self.assertEqual(
            float_compare(ml1.debit, receipts_total, precision_digits=2),
            0.00)
        self.assertTrue(float_is_zero(ml1.credit, precision_digits=2))
        self.assertEqual(ml1.account_id.id, self.account.id)
        self.assertEqual(
            float_compare(ml2.credit, receipts_total, precision_digits=2),
            0.00)
        self.assertTrue(float_is_zero(ml2.debit, precision_digits=2))
        self.assertEqual(ml2.account_id.id, self.payable_account.id)

        self.assertEqual(
            float_compare(pcf1.balance, pcf1.amount, precision_digits=2),
            0.00)

    def testClose(self):
        """Test closing a petty cash fund works"""

        pcf1 = self.create_fund('Petty Cash Fund 01')
        self.assertEqual(pcf1.state, 'open')

        # Run the close wizard
        Wizard = self.env['account.pettycash.fund.close']
        ctx = self.env.context.copy()
        ctx.update({'active_id': pcf1.id})
        wiz = Wizard.sudo(self.uidFinMgr).with_context(ctx).create({
            'receivable_account': self.receivable_account.id,
            'effective_date': datetime.today().date(),
        })
        self.assertEqual(wiz.fund.id, pcf1.id)
        fund_amount = pcf1.amount
        wiz.sudo(self.uidFinMgr).close_fund()

        self.assertEqual(pcf1.state, 'closed')
        self.assertFalse(pcf1.active)
        self.assertTrue(float_is_zero(pcf1.amount, precision_digits=2))

        # Check ledger accounts have been updated properly:
        # Accounts receivable should have a debit for the fund amount.
        # The fund account should have a credit for same amount.
        move = None
        for m in pcf1.journal_entries:
            if move is None or m.id > move.id:
                move = m
        ml1 = move.line_id[0]
        ml2 = move.line_id[1]
        self.assertEqual(
            float_compare(ml1.debit, fund_amount, precision_digits=2),
            0)
        self.assertTrue(float_is_zero(ml1.credit, precision_digits=2))
        self.assertEqual(ml1.account_id.id, self.receivable_account.id)
        self.assertEqual(
            float_compare(ml2.credit, fund_amount, precision_digits=2),
            0)
        self.assertTrue(float_is_zero(ml2.debit, precision_digits=2))
        self.assertEqual(ml2.account_id.id, self.account.id)

    def testCloseManagerOnly(self):
        """Test closing a petty cash fund without Manager perms fails"""

        pcf1 = self.create_fund('Petty Cash Fund 01')
        self.assertEqual(pcf1.state, 'open')

        with self.assertRaises(exceptions.AccessError):
            pcf1.sudo(self.uidAccountant).close_fund(False, False)

    def testCloseWithUnreconciledVouchers(self):
        """Test closing a fund fails if vouchers aren't reconciled"""

        VoucherWiz = self.env['account.pettycash.fund.voucher']

        pcf1 = self.create_fund('Petty Cash Fund 01')
        self.assertEqual(pcf1.state, 'open')
        vwiz_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'partner': pcf1.custodian_partner.id,
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 100.00}),
            ]
        }
        vwiz1 = VoucherWiz.sudo(self.uidOwner).create(vwiz_vals)
        vwiz1.sudo(self.uidOwner).create_voucher()

        with self.assertRaises(exceptions.ValidationError):
            pcf1.sudo(self.uidFinMgr).close_fund(False, False)

    def testReopen(self):
        """Test re-opening a petty cash fund"""

        # Create a fund and close it
        #
        pcf1 = self.create_fund('Petty Cash Fund 01')
        self.assertEqual(pcf1.state, 'open')

        # Run the close wizard
        Wizard = self.env['account.pettycash.fund.close']
        ctx = self.env.context.copy()
        ctx.update({'active_id': pcf1.id})
        wiz = Wizard.sudo(self.uidFinMgr).with_context(ctx).create({
            'receivable_account': self.receivable_account.id,
            'effective_date': datetime.today().date(),
        })
        self.assertEqual(wiz.fund.id, pcf1.id)
        wiz.sudo(self.uidFinMgr).close_fund()
        self.assertEqual(pcf1.state, 'closed')
        self.assertFalse(pcf1.active)

        # Re-open the fund
        Wizard = self.env['account.pettycash.fund.reopen']
        ctx = self.env.context.copy()
        ctx.update({'active_id': pcf1.id})
        wiz = Wizard.sudo(self.uidFinMgr).with_context(ctx).create({
            'payable_account': self.payable_account.id,
            'effective_date': datetime.today().date(),
        })
        wiz.sudo(self.uidFinMgr).reopen_fund()

        self.assertEqual(pcf1.state, 'open')
        self.assertTrue(pcf1.active)

        self.assertEqual(wiz.payable_move.state, 'posted')

        # Check ledger accounts have been updated properly:
        # Accounts payable should have a credit for the fund amount.
        # The fund account should have a debit for same amount.
        move = wiz.payable_move
        ml1 = move.line_id[0]
        ml2 = move.line_id[1]
        self.assertEqual(
            float_compare(ml1.debit, wiz.fund_amount, precision_digits=2),
            0)
        self.assertTrue(float_is_zero(ml1.credit, precision_digits=2))
        self.assertEqual(ml1.account_id.id, self.account.id)
        self.assertEqual(
            float_compare(ml2.credit, wiz.fund_amount, precision_digits=2),
            0)
        self.assertTrue(float_is_zero(ml2.debit, precision_digits=2))
        self.assertEqual(ml2.account_id.id, self.payable_account.id)

    def testReopenManagerOnly(self):
        """Test re-opening a petty cash fund without Manager perms fails"""

        # Create a fund and then close it
        pcf1 = self.create_fund('Petty Cash Fund 01')
        self.assertEqual(pcf1.state, 'open')

        # Run the close wizard
        Wizard = self.env['account.pettycash.fund.close']
        ctx = self.env.context.copy()
        ctx.update({'active_id': pcf1.id})
        wiz = Wizard.sudo(self.uidFinMgr).with_context(ctx).create({
            'receivable_account': self.receivable_account.id,
            'effective_date': datetime.today().date(),
        })
        self.assertEqual(wiz.fund.id, pcf1.id)
        wiz.sudo(self.uidFinMgr).close_fund()
        self.assertEqual(pcf1.state, 'closed')
        self.assertFalse(pcf1.active)

        with self.assertRaises(exceptions.AccessError):
            # Re-open the fund
            Wizard = self.env['account.pettycash.fund.reopen']
            ctx = self.env.context.copy()
            ctx.update({'active_id': pcf1.id})
            wiz = Wizard.sudo(self.uidAccountant).with_context(ctx).create({
                'payable_account': self.payable_account.id,
                'effective_date': datetime.today().date(),
            })
            wiz.reopen_fund()

    def testReopenWithChanges(self):
        """Test re-opening a petty cash fund and changing some values"""

        # Create a fund and close it
        #
        pcf1 = self.create_fund('Petty Cash Fund 01')
        self.assertEqual(pcf1.state, 'open')

        # Run the close wizard
        Wizard = self.env['account.pettycash.fund.close']
        ctx = self.env.context.copy()
        ctx.update({'active_id': pcf1.id})
        wiz = Wizard.sudo(self.uidFinMgr).with_context(ctx).create({
            'receivable_account': self.receivable_account.id,
            'effective_date': datetime.today().date(),
        })
        self.assertEqual(wiz.fund.id, pcf1.id)
        wiz.sudo(self.uidFinMgr).close_fund()
        self.assertEqual(pcf1.state, 'closed')
        self.assertFalse(pcf1.active)

        # Re-open the fund
        #
        uidOtherOwner = self.user_model.create({
            'name': 'Other Petty Cash Fund Owner',
            'login': 'pcfowner2',
            'email': 'pcfowner2@localhost',
        })
        uidOtherOwner.write({
            'groups_id': [(4, self.ref('account.group_pettycash_custodian'))]
        })
        Wizard = self.env['account.pettycash.fund.reopen']
        ctx = self.env.context.copy()
        ctx.update({'active_id': pcf1.id})
        wiz = Wizard.sudo(self.uidFinMgr).with_context(ctx).create({
            'custodian': uidOtherOwner.id,
            'fund_amount': 5000.000,
            'payable_account': self.payable_account.id,
            'effective_date': datetime.today().date(),
        })
        wiz.sudo(self.uidFinMgr).reopen_fund()

        self.assertEqual(pcf1.state, 'open')
        self.assertTrue(pcf1.active)

        self.assertEqual(wiz.payable_move.state, 'posted')

        # Check ledger accounts have been updated properly:
        # Accounts payable should have a credit for the fund amount.
        # The fund account should have a debit for same amount.
        move = wiz.payable_move
        ml1 = move.line_id[0]
        ml2 = move.line_id[1]
        self.assertEqual(
            float_compare(ml1.debit, wiz.fund_amount, precision_digits=2),
            0)
        self.assertTrue(float_is_zero(ml1.credit, precision_digits=2))
        self.assertEqual(ml1.account_id.id, self.account.id)
        self.assertEqual(
            float_compare(ml2.credit, wiz.fund_amount, precision_digits=2),
            0)
        self.assertTrue(float_is_zero(ml2.debit, precision_digits=2))
        self.assertEqual(ml2.account_id.id, self.payable_account.id)

    def testIncreaseFundAmount(self):
        """Test increasing the fund amount"""

        # Create a fund
        pcf1 = self.create_fund('Petty Cash Fund 01')
        self.assertEqual(pcf1.state, 'open')

        # Increase the fund
        Wizard = self.env['account.pettycash.fund.change']
        ctx = self.env.context.copy()
        ctx.update({'active_id': pcf1.id})
        wiz = Wizard.sudo(self.uidFinMgr).with_context(ctx).create({
            'new_amount': 10000.00,
            'payable_account': self.payable_account.id,
            'effective_date': datetime.today().date(),
            'custodian': self.uidInv.id,
            'fund_name': 'Changed name',
        })
        self.assertEqual(wiz.fund.id, pcf1.id)
        self.assertEqual(
            float_compare(wiz.fund_amount, pcf1.amount, precision_digits=2),
            0)
        diff_amount = wiz.new_amount - wiz.fund_amount

        wiz.sudo(self.uidFinMgr).change_fund()

        self.assertEqual(pcf1.name, 'Changed name')
        self.assertEqual(pcf1.custodian.id, self.uidInv.id)
        self.assertEqual(
            float_compare(pcf1.amount, 10000.00, precision_digits=2),
            0)
        self.assertEqual(wiz.move.state, 'posted')

        # Check ledger accounts have been updated properly:
        # Accounts payable should have a credit for the fund amount.
        # The fund account should have a debit for same amount.
        move = wiz.move
        ml1 = move.line_id[0]
        ml2 = move.line_id[1]
        self.assertEqual(
            float_compare(ml1.debit, diff_amount, precision_digits=2),
            0)
        self.assertTrue(float_is_zero(ml1.credit, precision_digits=2))
        self.assertEqual(ml1.account_id.id, self.account.id)
        self.assertEqual(
            float_compare(ml2.credit, diff_amount, precision_digits=2),
            0)
        self.assertTrue(float_is_zero(ml2.debit, precision_digits=2))
        self.assertEqual(ml2.account_id.id, self.payable_account.id)

    def testIncreaseManagerOnly(self):
        """Test increasing a petty cash fund without Manager perms fails"""

        # Create a fund
        pcf1 = self.create_fund('Petty Cash Fund 01')
        self.assertEqual(pcf1.state, 'open')

        with self.assertRaises(exceptions.AccessError):
            Wizard = self.env['account.pettycash.fund.change']
            ctx = self.env.context.copy()
            ctx.update({'active_id': pcf1.id})
            wiz = Wizard.sudo(self.uidAccountant).with_context(ctx).create({
                'new_amount': 10000.00,
                'payable_account': self.payable_account.id,
                'effective_date': datetime.today().date(),
            })
            wiz.change_fund()

    def testIncreaseWithUnreconciledVouchers(self):
        """Test increasing a fund succeeds even with unreconciled vouchers"""

        VoucherWiz = self.env['account.pettycash.fund.voucher']

        pcf1 = self.create_fund('Petty Cash Fund 01')
        self.assertEqual(pcf1.state, 'open')
        vwiz_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'partner': pcf1.custodian_partner.id,
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 100.00}),
            ]
        }
        vwiz1 = VoucherWiz.sudo(self.uidOwner).create(vwiz_vals)
        vwiz1.sudo(self.uidOwner).create_voucher()

        # Increase the fund
        Wizard = self.env['account.pettycash.fund.change']
        ctx = self.env.context.copy()
        ctx.update({'active_id': pcf1.id})
        wiz = Wizard.sudo(self.uidFinMgr).with_context(ctx).create({
            'new_amount': 10000.00,
            'payable_account': self.receivable_account.id,
            'effective_date': datetime.today().date(),
        })
        wiz.sudo(self.uidFinMgr).change_fund()

        self.assertEqual(
            float_compare(pcf1.amount, 10000.00, precision_digits=2),
            0)

    def testDecreaseWithUnreconciledVouchers(self):
        """Test decreasing a fund fails if vouchers aren't reconciled"""

        VoucherWiz = self.env['account.pettycash.fund.voucher']

        pcf1 = self.create_fund('Petty Cash Fund 01')
        self.assertEqual(pcf1.state, 'open')
        vwiz_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'partner': pcf1.custodian_partner.id,
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 100.00}),
            ]
        }
        vwiz1 = VoucherWiz.sudo(self.uidOwner).create(vwiz_vals)
        vwiz1.sudo(self.uidOwner).create_voucher()

        with self.assertRaises(exceptions.ValidationError):
            # Decrease the fund
            Wizard = self.env['account.pettycash.fund.change']
            ctx = self.env.context.copy()
            ctx.update({'active_id': pcf1.id})
            wiz = Wizard.sudo(self.uidFinMgr).with_context(ctx).create({
                'new_amount': 100.00,
                'receivable_account': self.receivable_account.id,
                'effective_date': datetime.today().date(),
            })
            wiz.sudo(self.uidFinMgr).change_fund()

    def testDecreaseFundAmount(self):
        """Test decreasing the fund amount"""

        # Create a fund
        pcf1 = self.create_fund('Petty Cash Fund 01')
        self.assertEqual(pcf1.state, 'open')

        # Decrease the fund
        Wizard = self.env['account.pettycash.fund.change']
        ctx = self.env.context.copy()
        ctx.update({'active_id': pcf1.id})
        wiz = Wizard.sudo(self.uidFinMgr).with_context(ctx).create({
            'new_amount': 100.00,
            'receivable_account': self.receivable_account.id,
            'effective_date': datetime.today().date(),
        })
        self.assertEqual(wiz.fund.id, pcf1.id)
        self.assertEqual(
            float_compare(wiz.fund_amount, pcf1.amount, precision_digits=2),
            0)
        diff_amount = wiz.fund_amount - wiz.new_amount

        wiz.sudo(self.uidFinMgr).change_fund()

        self.assertEqual(
            float_compare(pcf1.amount, 100.00, precision_digits=2),
            0)
        self.assertEqual(wiz.move.state, 'posted')

        # Check ledger accounts have been updated properly:
        # Accounts receivable should have a debit for the difference amount.
        # The fund account should have a credit for same amount.
        move = wiz.move
        ml1 = move.line_id[0]
        ml2 = move.line_id[1]
        self.assertEqual(
            float_compare(ml1.debit, diff_amount, precision_digits=2),
            0)
        self.assertTrue(float_is_zero(ml1.credit, precision_digits=2))
        self.assertEqual(ml1.account_id.id, self.receivable_account.id)
        self.assertEqual(
            float_compare(ml2.credit, diff_amount, precision_digits=2),
            0)
        self.assertTrue(float_is_zero(ml2.debit, precision_digits=2))
        self.assertEqual(ml2.account_id.id, self.account.id)

    def testButtonCancelVoucher(self):
        """Test UI button for cancelling vouchers is cancelled successfully"""

        VoucherWizard = self.env['account.pettycash.fund.voucher']

        # Create fund and voucher
        #
        pcf1 = self.create_fund('Petty Cash Fund 01')
        vwiz_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'partner': pcf1.custodian_partner.id,
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 100.00}),
            ]
        }
        vwiz1 = VoucherWizard.sudo(self.uidOwner).create(vwiz_vals)
        vwiz1.sudo(self.uidOwner).create_voucher()
        self.assertEqual(vwiz1.voucher.state, 'draft')

        vwiz1.voucher.sudo(self.uidOwner).button_cancel_voucher()

        self.assertEqual(vwiz1.voucher.state, 'cancel')
        self.assertNotIn(vwiz1.voucher.id, pcf1.vouchers.ids)

    def testBalanceWithManyAccounts(self):
        """Test balance of multiple funds using one ledger account"""

        VoucherWizard = self.env['account.pettycash.fund.voucher']

        # Create first fund and voucher
        #
        pcf1 = self.create_fund('Petty Cash Fund 01')
        vwiz_vals = {
            'fund': pcf1.id,
            'date': datetime.today().date(),
            'partner': pcf1.custodian_partner.id,
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 100.00}),
            ]
        }
        vwiz1 = VoucherWizard.sudo(self.uidOwner).create(vwiz_vals)
        vwiz1.sudo(self.uidOwner).create_voucher()

        # Create second fund and voucher
        #
        pcf2 = self.create_fund('Petty Cash Fund 02')
        vwiz2_vals = {
            'fund': pcf2.id,
            'date': datetime.today().date(),
            'lines': [
                (0, 0, {
                    'expense_account': self.expense_account.id,
                    'amount': 150.16}),
            ]
        }
        vwiz2 = VoucherWizard.sudo(self.uidOwner).create(vwiz2_vals)
        vwiz2.create_voucher()

        balance1 = pcf1.amount
        for l in vwiz1.lines:
            balance1 -= l.amount
        balance2 = pcf2.amount
        for l in vwiz2.lines:
            balance2 -= l.amount

        self.assertEqual(
            float_compare(pcf1.balance, balance1, precision_digits=2),
            0)
        self.assertEqual(
            float_compare(pcf2.balance, balance2, precision_digits=2),
            0)
