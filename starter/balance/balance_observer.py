"""Observers that react when the balance changes."""


class IBalanceObserver:
    """Interface that every balance observer must follow."""

    def update(self, balance, transaction):
        """Handle balance updates."""
        raise NotImplementedError("Subclasses must implement update method.")


class PrintObserver(IBalanceObserver):
    """Prints the new balance every time a transaction is applied.

    Args:
        output: Function used to show the message. Defaults to ``print``.
            Passing a different function in (dependency injection) lets
            tests capture the message instead of printing it.
    """

    def __init__(self, output=print):
        self.output = output

    def update(self, balance, transaction):
        """Print balance update message."""
        self.output(f"Applied {transaction} -> balance is now ${balance:.2f}")


class LowBalanceAlertObserver(IBalanceObserver):
    """Raises an alert when the balance drops below a threshold.

    ``alert_triggered`` is True only while the latest balance is below the
    threshold, so it goes back to False once the balance recovers.
    """

    def __init__(self, threshold, output=print):
        self.threshold = threshold
        self.output = output
        self.alert_triggered = False

    def update(self, balance, transaction):
        """Alert if balance drops below threshold."""
        self.alert_triggered = balance < self.threshold
        if self.alert_triggered:
            self.output(
                f"ALERT: balance ${balance:.2f} is below "
                f"${self.threshold:.2f}!"
            )
