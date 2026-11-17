import unittest
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from balance.balance import Balance
from balance.balance_observer import (
    IBalanceObserver,
    LowBalanceAlertObserver,
    PrintObserver,
)


class ObserverTestCase(unittest.TestCase):
    """Gives every test a clean balance with no observers."""

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()
        self.messages = []  # fake "screen" passed into the observers


class TestLowBalanceAlertObserver(ObserverTestCase):

    def test_alert_triggers_on_low_balance(self):
        observer = LowBalanceAlertObserver(threshold=50)
        self.balance.register_observer(observer)

        self.balance.apply_transaction(Transaction(100, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(60, TransactionCategory.EXPENSE))
        self.assertTrue(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(100, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(60, TransactionCategory.EXPENSE))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(60, TransactionCategory.EXPENSE))
        self.assertTrue(observer.alert_triggered)

    def test_alert_message_is_sent(self):
        observer = LowBalanceAlertObserver(50, output=self.messages.append)
        self.balance.register_observer(observer)
        self.balance.apply_transaction(Transaction(10, TransactionCategory.EXPENSE))
        self.assertEqual(len(self.messages), 1)
        self.assertIn("ALERT", self.messages[0])

    def test_no_alert_exactly_at_threshold(self):
        observer = LowBalanceAlertObserver(50, output=self.messages.append)
        self.balance.register_observer(observer)
        self.balance.apply_transaction(Transaction(50, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)
        self.assertEqual(self.messages, [])


class TestPrintObserver(ObserverTestCase):

    def test_prints_on_every_transaction(self):
        self.balance.register_observer(PrintObserver(output=self.messages.append))
        self.balance.apply_transaction(Transaction(100, TransactionCategory.INCOME))
        self.balance.apply_transaction(Transaction(30, TransactionCategory.EXPENSE))
        self.assertEqual(len(self.messages), 2)
        self.assertIn("$100.00", self.messages[0])
        self.assertIn("$70.00", self.messages[1])


class TestObserverRegistration(ObserverTestCase):

    def test_removed_observer_is_not_notified(self):
        observer = PrintObserver(output=self.messages.append)
        self.balance.register_observer(observer)
        self.balance.remove_observer(observer)
        self.balance.apply_transaction(Transaction(10, TransactionCategory.INCOME))
        self.assertEqual(self.messages, [])

    def test_same_observer_registered_once(self):
        observer = PrintObserver(output=self.messages.append)
        self.balance.register_observer(observer)
        self.balance.register_observer(observer)
        self.balance.apply_transaction(Transaction(10, TransactionCategory.INCOME))
        self.assertEqual(len(self.messages), 1)

    def test_interface_requires_update(self):
        with self.assertRaises(NotImplementedError):
            IBalanceObserver().update(0, None)


if __name__ == "__main__":
    unittest.main()
