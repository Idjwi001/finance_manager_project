"""Singleton class that keeps track of the user's balance."""

from transaction.transaction_category import TransactionCategory


class Balance:
    """Singleton to track the balance.

    Only one Balance should exist in the whole app, so always get it with
    ``Balance.get_instance()`` instead of calling ``Balance()`` directly.
    """

    _instance = None

    def __init__(self):
        """Initialize the balance. Prevent direct instantiation."""
        if Balance._instance is not None:
            raise RuntimeError(
                "Balance is a singleton. Use Balance.get_instance() instead."
            )
        self._balance = 0.0
        self._observers = []

    @classmethod
    def get_instance(cls):
        """Return the single shared Balance, creating it the first time."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ----- Observer management -------------------------------------------
    def register_observer(self, observer):
        """Add an observer that will be told about every new transaction."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer):
        """Stop sending updates to an observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def clear_observers(self):
        """Remove every registered observer."""
        self._observers.clear()

    def _notify_observers(self, transaction):
        for observer in self._observers:
            observer.update(self._balance, transaction)

    # ----- Balance operations --------------------------------------------
    def reset(self):
        """Reset the net balance to zero."""
        self._balance = 0.0

    def add_income(self, amount):
        """Add income to the balance."""
        self._balance += amount

    def add_expense(self, amount):
        """Subtract expense from the balance."""
        self._balance -= amount

    def apply_transaction(self, transaction):
        """
        Apply a Transaction object to update the balance.

        Args:
            transaction (Transaction): The transaction to apply.

        Raises:
            ValueError: If the transaction category is not supported.
        """
        if transaction.category == TransactionCategory.INCOME:
            self.add_income(transaction.amount)
        elif transaction.category == TransactionCategory.EXPENSE:
            self.add_expense(transaction.amount)
        else:
            raise ValueError(
                f"Unknown transaction category: {transaction.category!r}"
            )
        self._notify_observers(transaction)

    def get_balance(self):
        """Get the current net balance."""
        return self._balance

    def summary(self):
        """Return a summary string of the net balance."""
        return f"Net balance: ${self._balance:.2f}"
