"""Command pattern: each transaction becomes an object that can be
run (execute) and taken back (undo)."""

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class ICommand:
    """Interface for every command."""

    def execute(self):
        raise NotImplementedError("Subclasses must implement execute.")

    def undo(self):
        raise NotImplementedError("Subclasses must implement undo.")


class ApplyTransactionCommand(ICommand):
    """Applies one transaction to a balance, and can reverse it.

    The balance is passed in (dependency injection) instead of being looked
    up inside the class, so tests can give it any balance they like.
    """

    _OPPOSITE = {
        TransactionCategory.INCOME: TransactionCategory.EXPENSE,
        TransactionCategory.EXPENSE: TransactionCategory.INCOME,
    }

    def __init__(self, balance, transaction):
        self.balance = balance
        self.transaction = transaction

    def execute(self):
        self.balance.apply_transaction(self.transaction)

    def undo(self):
        # Undo = apply the same amount in the opposite direction, so the
        # observers are told about the correction too.
        reverse = Transaction(
            self.transaction.amount,
            self._OPPOSITE[self.transaction.category],
        )
        self.balance.apply_transaction(reverse)


class TransactionManager:
    """Runs commands and remembers them so the last ones can be undone."""

    def __init__(self):
        self._history = []

    def run(self, command):
        command.execute()
        self._history.append(command)

    def undo_last(self):
        """Undo the most recent command. Returns False if nothing to undo."""
        if not self._history:
            return False
        self._history.pop().undo()
        return True

    @property
    def history(self):
        return list(self._history)
