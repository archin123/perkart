# Database Schema & Data Models Specification

## 1. Multi-App Relational Architecture

The database architecture is segregated into domain-focused Django applications:

| App Name | Primary Models | Purpose |
| :--- | :--- | :--- |
| **`accounts`** | `UserProfile`, `EmployeeVerification` | User identity, company affiliation, verification state |
| **`products`** | `ProductCategory`, `Product`, `Offer`, `Wishlist` | Catalog management, pricing, coupons, bookmarks |
| **`cart`** | `Cart`, `CartItem`, `Order`, `OrderItem` | Session cart persistence, order checkout, invoicing |
| **`faq`** | `FAQCategory`, `FAQ`, `FAQVote`, `UnansweredQuestion` | Self-service help knowledgebase, voting feedback |
| **`troubleshooting`** | `ErrorCode`, `AppErrorLog` | Error code taxonomy, automated audit logging |
| **`core`** | `Feedback` | Employee platform reviews and satisfaction scoring |
| **`assistant`** | `AIConversation`, `AIMessage` | RAG query tracking, conversation threads, citations |

---

## 2. Dual Database Configuration

In [`perkcart/settings.py`](../perkcart/settings.py):

* **Local Environment:** Defaults to SQLite (`BASE_DIR / 'db.sqlite3'`) for zero-configuration, rapid development.
* **Production Environment (Vercel / Cloud):** When `DATABASE_URL` is provided (e.g. Neon PostgreSQL), Django automatically connects via `dj-database-url` with:
  * `conn_max_age = 600` (Persistent connection pooling across serverless invocations)
  * `conn_health_checks = True` (Prevents stale connections from causing 500 errors)
  * `ssl_require = True` (Enforces TLS encryption for database transactions)

---

## 3. Data Seeder (`seed_data.py`)

The platform includes an automated enterprise data provisioning command:

```powershell
py manage.py seed_data
```

This seeds:
* Master Superuser: `admin` / `Admin@12345`
* Test Corporate User: `employee` / `PerkCart@2026`
* Pending Verification Intern: `intern` / `PerkCart@2026`
* 6 Product categories (Laptops & Workstations, Flagship Smartphones, Audio, Smart Displays, etc.)
* 14 Products with realistic technical specs and corporate discounts
* 4 Corporate discount coupons (`WELCOME10`, `PERKTECH20`, `CORPVIP`, `FREESHIP`)
* 15 Database FAQs with initial vote counts
* 9 Structured error codes with diagnostic guides
