# Database design

## Entities and relationships
```
User 1───* Category 1───* Transaction *───1 User
User 1───* Budget   *───0..1 Category
```
- Category: user, name, type, created_at, updated_at
- Transaction: user, category (PROTECT), type, amount, date, description, timestamps
- Budget: user, category (nullable, CASCADE), amount, month, timestamps

Money is `DecimalField(max_digits=12, decimal_places=2)`, never float.

## Constraints
| Rule | Where enforced |
|---|---|
| Category unique per user + name + type | database `UniqueConstraint` |
| Amounts > 0 (Transaction, Budget) | database `CheckConstraint` + validator |
| One overall budget per user/month; one budget per user/category/month | database functional `UniqueConstraint` |
| Transaction category belongs to same user | `Transaction.clean()` |
| Transaction type equals category type | `Transaction.clean()` |
| Budget category belongs to same user | `Budget.clean()` |
| Budget category must be an expense category | `Budget.clean()` |
| Budget month is the 1st of a month | `Budget.clean()` |

Cross-row rules live in `clean()` because they compare against another table.
`clean()` runs in admin and ModelForms, but **not** on a plain `.save()`, so
later forms/serializers must validate (or call `full_clean()`) before saving.
Direct writes (shell, scripts) can bypass these rules until then.

## Why both Transaction.type and Category.type?
The category defines what kind of money it is (Salary = income). The transaction
stores its own type so reports can filter income vs expense without a join, and
so the rule "transaction type must match category type" is explicit and checkable.
The duplication is deliberate and guarded by `Transaction.clean()`.

## Budget uniqueness
A plain unique on `(user, category, month)` fails for overall budgets: `NULL`
values are treated as distinct, so duplicates would be allowed. The model uses
`UniqueConstraint(user, Coalesce(category, 0), month)`, mapping "no category" to
`0` (real ids start at 1). Chosen because conditional (partial) unique
constraints are ignored by MySQL, while functional unique indexes work.

Requirements: Django 5.2 supports expression-based unique constraints. On MySQL
this needs **MySQL 8.0.13+** (MariaDB does not support them in Django). SQLite
works. Verify on both when switching databases.

## SQLite → MySQL plan
1. Install MySQL 8.0.13+, create a `utf8mb4` database and a dedicated user.
2. `pip install mysqlclient` (uncomment it in `requirements.txt`).
3. In `.env`: `DB_ENGINE=mysql` plus `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
4. Run `python manage.py migrate` against the empty MySQL database.
5. Check `python manage.py check` for warnings (e.g. unsupported constraints).
6. No real data exists yet; if it does later, use `dumpdata`/`loaddata`.
