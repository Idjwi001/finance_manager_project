import unittest
from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction_adapter import TransactionAdapter
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestTransactionAdapter(unittest.TestCase):

    def test_adapter_converts_freelance_income(self):
        ext_txn = ExternalFreelanceIncome(500, "INV-12345", "Website development")
        adapter = TransactionAdapter(ext_txn)
        txn = adapter.to_transaction()
        self.assertEqual(txn, Transaction(500, TransactionCategory.INCOME))

    def test_result_is_a_transaction(self):
        ext_txn = ExternalFreelanceIncome(80, "INV-1", "Logo design")
        txn = TransactionAdapter(ext_txn).to_transaction()
        self.assertIsInstance(txn, Transaction)

    def test_unknown_external_type_raises(self):
        ext_txn = ExternalFreelanceIncome(80, "INV-1", "Logo design")
        ext_txn.typ = "refund"
        with self.assertRaises(ValueError):
            TransactionAdapter(ext_txn).to_transaction()


if __name__ == "__main__":
    unittest.main()
