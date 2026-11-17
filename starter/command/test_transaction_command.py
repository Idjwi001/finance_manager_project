import unittest
from balance.balance import Balance
from command.transaction_command import (
    ApplyTransactionCommand,
    ICommand,
    TransactionManager,
)
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class FakeBalance:
    """Stand-in balance that just records what it was asked to do.

    Because the command receives its balance from outside (dependency
    injection), we can test it without touching the real singleton.
    """

    def __init__(self):
        self.applied = []

    def apply_transaction(self, transaction):
        self.applied.append(transaction)


class TestApplyTransactionCommand(unittest.TestCase):

    def test_execute_applies_transaction(self):
        fake = FakeBalance()
        t = Transaction(40, TransactionCategory.INCOME)
        ApplyTransactionCommand(fake, t).execute()
        self.assertEqual(fake.applied, [t])

    def test_undo_applies_opposite(self):
        fake = FakeBalance()
        ApplyTransactionCommand(
            fake, Transaction(40, TransactionCategory.EXPENSE)
        ).undo()
        self.assertEqual(
            fake.applied, [Transaction(40, TransactionCategory.INCOME)]
        )

    def test_interface_requires_methods(self):
        with self.assertRaises(NotImplementedError):
            ICommand().execute()
        with self.assertRaises(NotImplementedError):
            ICommand().undo()


class TestTransactionManager(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()
        self.manager = TransactionManager()

    def test_run_and_undo_with_real_balance(self):
        self.manager.run(ApplyTransactionCommand(
            self.balance, Transaction(100, TransactionCategory.INCOME)))
        self.manager.run(ApplyTransactionCommand(
            self.balance, Transaction(30, TransactionCategory.EXPENSE)))
        self.assertEqual(self.balance.get_balance(), 70)

        self.assertTrue(self.manager.undo_last())
        self.assertEqual(self.balance.get_balance(), 100)
        self.assertTrue(self.manager.undo_last())
        self.assertEqual(self.balance.get_balance(), 0)

    def test_undo_with_empty_history(self):
        self.assertFalse(self.manager.undo_last())

    def test_history_is_recorded(self):
        command = ApplyTransactionCommand(
            self.balance, Transaction(5, TransactionCategory.INCOME))
        self.manager.run(command)
        self.assertEqual(self.manager.history, [command])


if __name__ == "__main__":
    unittest.main()
