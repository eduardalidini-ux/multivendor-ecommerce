# Database Requirements Checklist (Supabase Postgres)

Project: MultiVendorEcommerce (Django backend)

This checklist maps the project to the stated database requirements. It documents what exists today and what should be improved to fully comply.

---

## 1) Relational, logically designed schema (tables separated by app needs)

### Current status: Partially meets

### What exists in this project

- Django is using a relational model structure split across apps:
  - `userauths` (users/profiles)
  - `store` (products, carts, orders, coupons, etc.)
  - `vendor` (vendors)
  - `addon`, `customer`, `api`
- Proper relational links are used in many places:
  - Foreign Keys (e.g., `CartOrderItem.order`, `Cart.product`, `Product.vendor`)
  - Many-to-many (e.g., `CartOrder.vendor`, `CartOrder.coupons`)

### Gaps / risks

- Some fields are not normalized into relational tables:
  - `Product.tags` is stored as a string, even though a `Tag` model exists.
  - `Product.brand` is stored as a string, even though a `Brand` model exists.

### Recommendations

- Convert `Product.tags` into a proper M2M relationship with `Tag`.
- Convert `Product.brand` into a FK to `Brand` (or store `Brand` as its own table and reference it).
- Add DB constraints where possible (e.g., prevent negative totals/qty via `CheckConstraint`).

---

## 2) Transactions for critical operations (orders, sales, payments, shipping, warehousing)

### Current status: Partially meets

### What exists in this project

- Orders are created inside transactions:
  - `CreateOrderView.create()` uses `with transaction.atomic():`.
- Stripe payment finalization uses transactions and row locking:
  - Stripe webhook uses `transaction.atomic()` and `select_for_update()` to avoid double-processing.
  - `finalize_order_payment()` is `@transaction.atomic`.
- Some vendor operations use transactions (product create/update).

### Gaps / risks

- Coupon application updates multiple tables/rows without explicit `transaction.atomic()`.
- Shipping / delivery updates are not consistently guarded by atomic transactions.
- No dedicated “inventory/warehouse ledger” tables exist; inventory is a simple `stock_qty` field.

### Recommendations

- Wrap coupon application and multi-row status updates inside `transaction.atomic()`.
- Consider adding an inventory movement table (stock in/out/reservations) and updating it transactionally.

---

## 3) Triggers, stored procedures, functions (DB-level automation)

### Current status: Does not meet

### What exists in this project

- Automation happens at the application level:
  - Model `save()` overrides (slugs, computed fields)
  - Django signals (e.g., auto-create Profile)

### What is missing

- No database-level triggers/functions/procedures were found:
  - No migrations using `RunSQL(...)`
  - No `CREATE TRIGGER`, `CREATE FUNCTION`, `CREATE PROCEDURE` scripts

### Recommendations (Postgres)

- Use DB constraints + triggers only where it improves consistency beyond app code.
- Typical candidates:
  - Enforce invariant totals (or at least check constraints)
  - Audit tables (order status transitions)
  - Inventory movement consistency

---

## 4) Sensitive data encrypted (passwords, credit card, PIN, etc.)

### Current status: Partially meets

### What exists in this project

- Passwords are not stored in plaintext:
  - Registration calls `user.set_password(...)` so Django stores a password hash.
- Card data is not stored:
  - Stripe Checkout is used; only `stripe_session_id` and statuses are stored.

### Gaps / risks

- Non-password sensitive tokens exist as plain fields (e.g., OTP/reset token fields in `User`).
- No field-level encryption is implemented for “at rest” encryption in the DB.

### Recommendations

- Avoid storing raw OTP/reset tokens; store *hashed* versions (similar to password hashing) or use short-lived signed tokens.
- If you must store sensitive values, implement field encryption (application-level) and rotate keys.
- Keep secrets out of the repo:
  - Use env vars for `DATABASE_URL`, `STRIPE_SECRET_KEY`, etc. (already done).

---

## 5) Indexes created with technical reasoning (search optimization)

### Current status: Meets

### What exists in this project

- Many implicit indexes exist via Django:
  - Primary keys
  - `unique=True` fields (e.g., `User.email`, `Product.sku`, `Product.pid`)
  - Foreign keys commonly become indexed
- Explicit indexes were added for the most common query patterns in `store`:
  - Implemented in `backend/store/models.py` via `Meta.indexes`
  - Applied to the database via migration `store.0029_cart_store_cart_cartid_idx_and_more`
  - Covers common filters/lookups such as:
    - `Cart(cart_id)` and `Cart(cart_id, user)`
    - `CartOrder(oid)`, `CartOrder(stripe_session_id)`, and reporting filters like `CartOrder(payment_status, date)`
    - Vendor dashboards and shipping filters on `CartOrderItem` (e.g., `(vendor, date)`, `delivery_status`)
    - Notification queries (e.g., `(vendor, seen)`, `(user, seen)`)
    - Case-insensitive coupon lookup via an expression index on `Lower(code)`

### Gaps / risks

- Some indexes can be consolidated later (too many indexes can slow down writes).
- If search requirements grow (multi-field, ranking, language), trigram search may be insufficient.

### Recommendations (Postgres)

- Decide how users search:
  - Full text search (tsvector + GIN)
  - Trigram search (`pg_trgm` + GIN) for partial matches
- Keep reviewing index usage with real query patterns:
  - Use query logs / `EXPLAIN ANALYZE` on Supabase Postgres
  - Remove redundant indexes and add specialized ones only where needed

### Implemented (search optimization)

- Enabled Postgres extension `pg_trgm` and added a GIN trigram index for faster `icontains`-style searches:
  - Migration: `store.0030_pg_trgm_product_title_idx`
  - Index: `st_prod_title_trgm_gin` on `store_product(title gin_trgm_ops)`

---

## 6) Roles and least privilege (DB rights)

### Current status: Not implemented in this repo

### What exists in this project

- DB config supports Postgres using `DATABASE_URL` and SSL requirement.

### What is missing

- No scripted roles/grants exist (no `GRANT/REVOKE/CREATE ROLE`).
- No separation of “migration/admin” user vs “runtime app” user.

### Recommendations (Supabase Postgres)

- Use a dedicated DB user for the app with only required privileges:
  - `SELECT/INSERT/UPDATE/DELETE` on needed tables
  - Avoid `SUPERUSER`, avoid schema changes
- Keep a separate privileged role/user for migrations/maintenance.
- Document the policy and ensure secrets are stored only in environment variables.

---

## Notes about current DB configuration

- The project previously included a SQLite fallback, but the deployment is Supabase Postgres. (its already online)
- Ensure `DATABASE_URL` is always set in your environments.
