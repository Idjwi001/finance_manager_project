# Reflection: Design Patterns in the Personal Finance Manager

The app tracks income and expenses, keeps a running balance, and warns the
user when money gets low. Four design patterns hold it together.

## Project layout

```
starter/
├── main.py                          # runs the demo
├── balance/
│   ├── balance.py                   # Singleton + Observer "subject"
│   └── balance_observer.py          # PrintObserver, LowBalanceAlertObserver
├── transaction/
│   ├── transaction.py               # Transaction class
│   ├── transaction_category.py      # INCOME / EXPENSE enum
│   ├── external_income_transaction.py
│   └── transaction_adapter.py       # Adapter
└── command/
    └── transaction_command.py       # Command (my 4th pattern)
```

Each folder has its own `test_*.py` files. Run them from `starter/` with
`python -m unittest discover`.

---

## 1. Singleton — `Balance`

**What it does:** Makes sure there is only one balance in the whole app.
You get it with `Balance.get_instance()`. Calling `Balance()` a second
time raises an error.

**Why it fits:** A person has one balance. If two parts of the app each made
their own `Balance`, they would show different numbers. With a Singleton,
everyone reads and changes the same number.

**Trade-off:** A Singleton is shared by everything, *including tests*. If
one test adds $100, the next test still sees it. To fix this I added
`reset()` and `clear_observers()` and call them in every test's `setUp()`.
I also made other classes *receive* the balance instead of calling
`get_instance()` themselves (see "Dependency injection" below), so most
code does not need to know it's a Singleton at all.

## 2. Adapter — `TransactionAdapter`

**What it does:** A freelance platform sends us `ExternalFreelanceIncome`
objects. They have an invoice ID, a description, and a text field
`typ = "income"`. Our app only understands `Transaction` objects with a
`TransactionCategory` enum. The adapter takes the outside object and gives
back a normal `Transaction`.

**Why it fits:** We can't change the outside platform's format, and we don't
want `Balance` to deal with every new format either. The adapter keeps all
the "translation" code in one small place. If we later connect a bank or
PayPal, we just write another adapter. `Balance` stays the same.

**Trade-off:** It's an extra class, and some details (invoice ID,
description) are dropped because `Transaction` has no place for them. For
this project that's fine. A bigger app might add those fields to
`Transaction`.

## 3. Observer — `PrintObserver` and `LowBalanceAlertObserver`

**What it does:** `Balance` keeps a list of "observers". Each time a
transaction is applied, it calls `update(balance, transaction)` on every
observer.

- `PrintObserver` prints the new balance.
- `LowBalanceAlertObserver` shows an alert when the balance is below a
  threshold. It sets `alert_triggered` to `True` while the balance is low
  and back to `False` once it recovers.

**Why it fits:** `Balance` should only handle the math. It shouldn't know
how to print or send alerts. With observers, we can add new reactions
(email, a log file, a phone notification) by writing a new observer and
registering it. `Balance` doesn't change.

**Trade-off:** The order of observers depends on the order you register
them, and it can be harder to follow "what happens when I apply a
transaction" because the code is spread over several classes. Observers
also have to be removed (`remove_observer`), or they stay attached to the
Singleton for good.

## 4. Command — `ApplyTransactionCommand` and `TransactionManager` (my choice)

**What it does:** Each transaction is wrapped in a small command object
with two methods:

- `execute()` applies the transaction to the balance.
- `undo()` applies the same amount in the opposite direction.

`TransactionManager` runs commands and keeps a history list, so
`undo_last()` can reverse the latest one. `main.py` shows this by undoing
the freelance payment at the end.

**Why I chose it:** Undo is a very natural feature for a finance app.
People enter wrong amounts all the time. Without Command, undo would mean
extra code inside `Balance`. With Command, "an action" becomes an object we
can store, list, and reverse.

**Where it fits:** Between `main.py` and `Balance`. Instead of calling
`balance.apply_transaction(t)` directly, `main.py` hands a command to the
`TransactionManager`.

**How it helps:**
- *Flexibility:* New actions (transfers, scheduled payments) can be new
  command classes without touching `Balance`.
- *Testability:* The command receives its balance from outside, so the
  tests pass in a simple `FakeBalance` and check exactly what it was told.
- *Scalability:* The history list is a good starting point for redo,
  saving an audit log, or replaying transactions.

**Trade-off:** It adds two more classes for something that used to be one
line. Also, because undo works by applying an opposite transaction, the
observers see the undo as a new transaction (for example, an "expense" of
$1200). I think that's actually helpful, since the user is told the balance
changed, but it's a choice worth noting.

---

## Dependency injection

Dependency injection just means "give an object what it needs, instead of
letting it go find it." I used it in two places:

- `PrintObserver(output=print)` and `LowBalanceAlertObserver(threshold,
  output=print)` take the function used to show messages. In the app it's
  `print`. In tests it's `list.append`, so the test can check the messages
  without reading the terminal.
- `ApplyTransactionCommand(balance, transaction)` takes the balance as an
  argument. In the app it's the real Singleton. In tests it can be a fake.

This made the code easier to test and kept classes loosely connected.

## Challenges

- The starter observer test expects `alert_triggered` to go back to `False`
  when the balance recovers. So it shows the *current* state, not "has an
  alert ever happened". I had to read the test carefully to see this.
- `python -m unittest discover` found 0 tests at first. The folders needed
  empty `__init__.py` files so Python sees them as packages.
- Getting the Singleton and the tests to play nicely (see the Singleton
  trade-off above).
