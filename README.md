# PerkCart — Corporate Employee Privilege Shopping Platform

[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/SQLite3-Local%20Dev-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Test Suite](https://img.shields.io/badge/Tests-27%20Passed%20(100%25)-success?style=flat)](#testing-and-verification)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> Inspired by the premium visual and functional architecture of Samsung's Corporate Shopping Portal ([Reference](https://www.samsung.com/in/multistore/in_corporate/prelogin/)).  
> Built for college-level evaluation, academic review, and comprehensive technical demonstration.

---

## 🌟 Project Overview

**PerkCart** is an end-to-end corporate employee shopping web platform developed using Python and Django. It connects enterprise employees with pre-negotiated corporate subsidies (20% to 45% off MSRP) on flagship workstations, foldable smartphones, ultra-wide productivity displays, ANC audio gear, and ergonomic workspace accessories.

### Key Architectural Highlights
- **Premium Design:** Clean white aesthetic, generous whitespace, modern typography (`Plus Jakarta Sans`), subtle elevation shadows, and responsive layout across desktop, tablet, and mobile.
- **Database-Backed FAQ Module:** 15 comprehensive Q&As across 8 domains with instant live search, category chips, expandable accordions, AJAX helpful/unhelpful voting, and an unanswered question reporting form.
- **Structured Error-Code & Diagnostic Module:** 9 realistic error codes (`AUTH-001`, `AUTH-002`, `CART-001`, `CART-002`, `DISC-001`, `ORDER-001`, `PAY-001`, `API-001`, `SEC-001`) with severity filters, step-by-step resolution guides, friendly error pages, and an evaluator safe error trigger simulator.
- **Grounded AI Shopping Assistant:** Retrieval-Augmented Generation (RAG) assistant connecting to Google Gemini API (if key configured) or an intelligent search-based fallback engine with zero hallucinations and verified database citations.
- **Simulated Corporate Procurement & Checkout:** Complete checkout with simulated corporate payroll deductions, corporate card billing, real-time cart recalculations, and strict order ownership isolation.

---

## 🚀 Quick Start Guide (Run in 3 Steps)

### Prerequisites
- Python 3.10+ (or Python Launcher `py`)
- Git

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```
*(Or with Python Launcher on Windows)*:
```powershell
py -m pip install -r requirements.txt
```

### Step 2: Apply Migrations & Seed Demonstration Data
```bash
py manage.py migrate
py manage.py seed_data
```
The `seed_data` command automatically provisions:
- 1 Superuser account (`admin` / `Admin@12345`)
- 1 Verified corporate employee account (`employee` / `PerkCart@2026`)
- 1 Pending verification intern account (`intern` / `PerkCart@2026`)
- 6 Product categories
- 14 High-end enterprise products with specs and high-res images
- 4 Active corporate discount coupons (`WELCOME10`, `PERKTECH20`, `CORPVIP`, `FREESHIP`)
- 15 Database FAQs across all required domains
- 9 Structured error codes with diagnostic resolution workflows
- Sample employee feedback and simulated error logs

### Step 3: Run Development Server
```bash
py manage.py runserver
```
Visit the live portal at: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Demonstration Accounts

| Role | Username | Password | Purpose / Permissions |
| :--- | :--- | :--- | :--- |
| **Master Administrator** | `masteradmin` | `MasterAdmin@2026` | Master Superuser with root administrative access across all Django subsystems |
| **Portal Administrator** | `admin` | `Admin@12345` | Superuser, Django Admin access, Employee Verification Console, Safe Error Simulator |
| **Verified Employee** | `employee` | `PerkCart@2026` | Verified corporate status (`Apex Global Technologies`), unlocked corporate checkout |
| **Pending Intern** | `intern` | `PerkCart@2026` | `PENDING` verification status, demonstrates verification request workflow |

---

## 📁 System Architecture & Directory Structure

```text
perkcart/
├── accounts/                  # UserProfile, EmployeeVerification, auth views & forms
│   ├── models.py              # UserProfile & EmployeeVerification models
│   ├── views.py               # Register, login, logout, profile, admin verification console
│   └── tests.py               # Auth & verification tests
├── assistant/                 # Grounded AI Shopping Assistant subsystem
│   ├── engine.py              # Multi-domain RAG retrieval & Gemini / Fallback engine
│   ├── models.py              # AIConversation & AIMessage models
│   └── views.py               # Assistant page & AJAX JSON API endpoints
├── cart/                      # Session-based cart & Database order processing
│   ├── cart.py                # Session Cart class with subtotal & coupon calculations
│   ├── models.py              # Order & OrderItem models
│   └── views.py               # Cart detail, checkout, order list, order tracking
├── core/                      # Core presentation & monitoring
│   ├── context_processors.py  # Global navbar data (cart count, wishlist count, categories)
│   ├── management/commands/   # seed_data management command
│   ├── models.py              # Feedback model
│   └── views.py               # Homepage, search, feedback, /health/, /status/
├── faq/                       # Database-backed FAQ module
│   ├── models.py              # FAQCategory, FAQ, FAQVote, UnansweredQuestion
│   └── views.py               # Searchable accordion, AJAX voting, question submission
├── perkcart/                  # Django project root configuration
│   ├── settings.py            # Security headers, DB switch, environment configs
│   ├── urls.py                # Main URL router
│   └── wsgi.py
├── products/                  # Product catalog, categories, offers & wishlist
│   ├── models.py              # ProductCategory, Product, Offer, Wishlist
│   └── views.py               # Product list, filters, product detail, offers, wishlist
├── static/                    # CSS, JS, and UI assets
│   ├── css/style.css          # Premium Samsung-inspired stylesheet
│   └── js/main.js             # Client interactivity, AJAX wishlist, floating AI chat
├── templates/                 # Responsive HTML5 templates
│   ├── accounts/
│   ├── assistant/
│   ├── cart/
│   ├── core/
│   ├── errors/                # Friendly 404 & 500 pages (no raw tracebacks)
│   ├── faq/
│   ├── products/
│   └── troubleshooting/
├── troubleshooting/           # Error code & diagnostic knowledgebase
│   ├── middleware.py          # AppErrorLoggingMiddleware
│   ├── models.py              # ErrorCode & AppErrorLog models
│   └── views.py               # Error list, search/filters, detail, safe simulator
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🛠️ Module Descriptions & Features

### 1. Premium Corporate Visual Design (10 Marks)
- Inspired by Samsung's corporate shopping visual language: `#ffffff` canvas, subtle borders (`#e2e8f0`), deep slate primary accents (`#0f172a`), vibrant corporate blue (`#0284c7`), and generous whitespace.
- Hero banner with enterprise subsidies ticker, product category grid, featured products with stock badges and savings tags, and floating AI assistant launcher.
- Micro-interactions: AJAX wishlist toggle with real-time badge count update without page reload.

### 2. FAQ Module (10 Marks)
- 15 real questions stored in `FAQ` table across 8 domains (Registration, Verification, Discounts, Products, Cart, Orders, Payments, Security).
- Category filter pills and live search bar.
- Smooth expandable accordion UI.
- AJAX helpful/unhelpful voting with live count updates and session-based duplicate vote prevention.
- Unanswered question report form storing submissions in `UnansweredQuestion` for admin review.

### 3. Error-Code & Troubleshooting Module (15 Marks)
- Structured database model `ErrorCode` storing `code`, `title`, `category`, `severity`, `possible_causes`, `troubleshooting_steps`, `preventive_recommendations`, and `action_url`.
- 9 realistic error records (`AUTH-001`, `AUTH-002`, `CART-001`, `CART-002`, `DISC-001`, `ORDER-001`, `PAY-001`, `API-001`, `SEC-001`).
- Multi-dimensional search and filters by Category and Severity (`Low`, `Medium`, `High`, `Critical`).
- Dedicated detail pages with bulleted root causes, step-by-step instructions, and direct in-app action buttons.
- `AppErrorLoggingMiddleware` catching unhandled exceptions and logging sanitized context to `AppErrorLog` without leaking secrets.
- Evaluator Safe Error Simulator (`/troubleshooting/simulate/`) allowing administrators to safely trigger errors and inspect log entries.

### 4. Grounded AI Shopping Assistant (25 Marks)
- Persistent floating widget and full dedicated view (`/ai-assistant/`).
- **Retrieval-Augmented Generation (RAG) Architecture**:
  1. User prompt is analyzed for price ceilings (e.g. `under 80000`, `under 1 lakh`), product names, comparison requests (`compare X and Y`), coupon queries, FAQs, error codes, and user orders.
  2. Grounded records are retrieved from the SQLite database.
  3. If `GEMINI_API_KEY` is configured in `.env`, Google's Gemini REST API is called with a strict zero-hallucination system prompt.
  4. If no API key is present or external network timeout occurs, the system automatically engages the **Search-Based Fallback Engine**, clearly labelled with citation cards and markdown comparisons.
- Database conversation persistence: `AIConversation` and `AIMessage` store user chat threads.

### 5. Backend, Database & Corporate Verification (15 Marks)
- 13 Django ORM models with foreign keys, constraints, and custom properties (e.g., `product.discount_percent`, `cart.get_total_savings`).
- **Simulated Employee Verification Workflow**:
  - `PENDING` &rarr; `APPROVED` &rarr; `REJECTED`
  - Unverified users can preview catalog and wishlist items; verified status unlocks full subsidized checkout.
  - Dedicated Admin Verification Console (`/accounts/admin/verifications/`) allows administrators to approve or reject requests with one click.
- **Simulated Corporate Checkout**:
  - Server recalculates all cart subtotals and coupon discounts.
  - Simulated payment options: Corporate Payroll Deduction, Corporate Card, Instant UPI.
  - Decreases database inventory count upon successful order authorization.
  - Strict order ownership verification: User A cannot view User B's orders (violators are blocked and logged with code `ORDER-001`).

### 6. Deployment & Security (15 Marks)
- CSRF tokens on all POST requests.
- Passwords hashed using PBKDF2 with SHA256.
- Production security headers: `SECURE_BROWSER_XSS_FILTER`, `X_FRAME_OPTIONS = 'DENY'`, `SECURE_CONTENT_TYPE_NOSNIFF`, secure cookies conditional on `not DEBUG`.
- PostgreSQL support via `DATABASE_URL` environment variable.
- `.env.example` and `.gitignore` preventing accidental secret commits.

### 7. Monitoring & Feedback (5 Marks)
- Star rating (1-5) feedback form stored in `Feedback` model.
- Health-check endpoint at `/health/` returning HTTP 200 JSON status without exposing infrastructure secrets.
- Operational status monitor at `/status/` showing database connectivity, AI engine mode, and item counts.

---

## 🧪 Testing and Verification

PerkCart includes an automated test suite verifying 27 distinct test cases across all evaluation requirements:

```powershell
py manage.py test
```

### Actual Execution Results:
```text
Creating test database for alias 'default'...
Found 27 test(s).
System check identified no issues (0 silenced).
...........................
----------------------------------------------------------------------
Ran 27 tests in 15.306s

OK
Destroying test database for alias 'default'...
```

### Verified Test Areas:
1. `accounts.tests`: Corporate registration, login/logout, profile access, admin verification permissions.
2. `products.tests`: Catalog listing, product detail rendering, category filtering, discount calculations, AJAX wishlist toggle.
3. `cart.tests`: Cart addition, stock bound clamping, coupon application, checkout order creation, inventory decrements, and strict order ownership isolation.
4. `faq.tests`: FAQ listing, keyword search, AJAX voting with duplicate vote prevention, unanswered question submission.
5. `troubleshooting.tests`: Error code search, severity filtering, diagnostic detail view, safe administrative simulator.
6. `assistant.tests`: Price ceiling regex parser, RAG database context retrieval, search-based fallback generation, conversation/message database persistence.
7. `core.tests`: Homepage rendering, global multi-domain search, feedback submission, operational status, and `/health/` endpoint.

---

## 🌐 Production Deployment Guide

### Deploying to Render / Railway / Heroku

1. **Set Environment Variables**:
   ```ini
   SECRET_KEY=your-production-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-app.onrender.com,yourdomain.com
   DATABASE_URL=postgresql://user:password@hostname:5432/perkcart_db
   GEMINI_API_KEY=your-gemini-key-optional
   ```

2. **Run Migrations & Seed**:
   ```bash
   python manage.py migrate
   python manage.py seed_data
   ```

3. **Collect Static Files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Start Web Process (Gunicorn)**:
   ```bash
   gunicorn perkcart.wsgi:application --bind 0.0.0.0:$PORT
   ```

---

## 📄 License

This project is developed for educational and college evaluation purposes under the MIT License.
