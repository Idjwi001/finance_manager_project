import unittest
from balance.balance import Balance
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestBalance(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_initial_balance(self):
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_singleton_instance(self):
        balance1 = Balance.get_instance()
        balance2 = Balance.get_instance()
        self.assertIs(balance1, balance2)

    def test_add_income(self):
        self.balance.add_income(100)
        self.assertEqual(self.balance.get_balance(), 100)

    def test_add_expense(self):
        self.balance.add_expense(40)
        self.assertEqual(self.balance.get_balance(), -40)

    def test_apply_transaction_income(self):
        t = Transaction(150, TransactionCategory.INCOME)
        self.balance.apply_transaction(t)
        self.assertEqual(self.balance.get_balance(), 150)

    def test_apply_transaction_expense(self):
        t = Transaction(60, TransactionCategory.EXPENSE)
        self.balance.apply_transaction(t)
        self.assertEqual(self.balance.get_balance(), -60)

    def test_apply_transaction_invalid_category(self):
        class FakeCategory:
            pass
        t = Transaction(100, FakeCategory())
        with self.assertRaises(ValueError):
            self.balance.apply_transaction(t)

    def test_reset(self):
        self.balance.add_income(100)
        self.balance.add_expense(50)
        self.balance.reset()
        self.assertEqual(self.balance.get_balance(), 0.0)


class TestBalanceSingletonRules(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()

    def test_direct_instantiation_is_blocked(self):
        with self.assertRaises(RuntimeError):
            Balance()

    def test_state_is_shared_between_references(self):
        Balance.get_instance().add_income(30)
        self.assertEqual(self.balance.get_balance(), 30)

    def test_summary(self):
        self.balance.add_income(12.5)
        self.assertEqual(self.balance.summary(), "Net balance: $12.50")


class TestBalanceFreshStart(unittest.TestCase):
    """Checks the Singleton before get_instance() has ever been called."""

    def setUp(self):
        # Pretend this is a brand-new program with no balance yet, and put
        # the real one back afterwards so other tests are not affected.
        saved = Balance._instance
        Balance._instance = None
        self.addCleanup(setattr, Balance, "_instance", saved)

    def test_first_direct_call_reserves_the_instance(self):
        first = Balance()
        self.assertIs(Balance.get_instance(), first)

    def test_second_direct_call_is_blocked(self):
        Balance()
        with self.assertRaises(RuntimeError):
            Balance()

    def test_get_instance_first_then_direct_call_is_blocked(self):
        Balance.get_instance()
        with self.assertRaises(RuntimeError):
            Balance()


if __name__ == "__main__":
    unittest.main()
