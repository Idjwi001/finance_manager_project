"""This module serves as the entry point for the program."""
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from balance.balance_observer import PrintObserver
from command.transaction_command import (
    ApplyTransactionCommand,
    TransactionManager,
)
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_adapter import TransactionAdapter
from transaction.external_income_transaction import ExternalFreelanceIncome

LOW_BALANCE_THRESHOLD = 100


def build_balance():
    """Create the balance and register the observers."""
    balance = Balance.get_instance()
    balance.register_observer(PrintObserver())
    balance.register_observer(LowBalanceAlertObserver(LOW_BALANCE_THRESHOLD))
    return balance


def main():
    balance = build_balance()
    manager = TransactionManager()

    print("Adding transactions...")

    # Create standard transactions
    transactions = [
        Transaction(100, TransactionCategory.INCOME),
        Transaction(50, TransactionCategory.EXPENSE),
        Transaction(200, TransactionCategory.INCOME),
        Transaction(75, TransactionCategory.EXPENSE),
    ]

    # Create an external income transaction (via Adapter pattern)
    freelance_income = ExternalFreelanceIncome(
        1200, "INV-98765", "Mobile App Project"
    )
    adapter = TransactionAdapter(freelance_income)
    adapted_transaction = adapter.to_transaction()

    all_transactions = transactions + [adapted_transaction]

    # Apply all transactions to balance (via Command pattern)
    for transaction in all_transactions:
        manager.run(ApplyTransactionCommand(balance, transaction))

    print(balance.summary())

    # Show the undo feature of the Command pattern
    print("\nOops, the freelance payment was a mistake. Undoing it...")
    manager.undo_last()
    print(balance.summary())


if __name__ == "__main__":
    main()
