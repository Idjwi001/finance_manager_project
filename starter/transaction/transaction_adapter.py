"""Adapter that turns outside income records into normal Transactions."""

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TransactionAdapter:
    """Wraps an ExternalFreelanceIncome so the app can treat it as a
    regular Transaction."""

    # Maps the outside platform's text type to our own enum.
    _CATEGORY_MAP = {
        "income": TransactionCategory.INCOME,
        "expense": TransactionCategory.EXPENSE,
    }

    def __init__(self, external_transaction):
        self.external_transaction = external_transaction

    def to_transaction(self):
        """Convert an external transaction to a standard Transaction."""
        external_type = self.external_transaction.typ.lower()
        if external_type not in self._CATEGORY_MAP:
            raise ValueError(f"Unknown external type: {external_type!r}")
        return Transaction(
            self.external_transaction.amount,
            self._CATEGORY_MAP[external_type],
        )
