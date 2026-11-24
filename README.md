# CraveCart – Online Food Ordering System

> **College Mini-Project**: A single-restaurant online food ordering web application built with Python Flask, SQLite, and vanilla frontend technologies.

---

## 🍽️ Features & Overview

- **Customer Operations**:
  - Discover artisanal categories and seasonal dishes.
  - Interactive search and category filters.
  - Session-based cart with dynamic quantity adjustments.
  - Cash on Delivery (COD) checkout with delivery details.
  - Real-time visual order tracking through progressive statuses.
- **Administrator Portal**:
  - Secure role-based administrative control panel.
  - Operational metrics and revenue insights.
  - Menu catalog management (Create, Read, Update, Delete) with image uploads.
  - Instant stock availability toggle (In Stock / Out of Stock).
  - Customer order fulfillment and status transitions.

---

## 🛠️ Technology Stack

| Layer | Component | Notes |
| :--- | :--- | :--- |
| **Backend** | Python 3.9+ / Flask 3.x | Application Factory Pattern with Modular Blueprints |
| **Database** | SQLite 3 | Relational file-based database (`instance/cravecart.db`) |
| **ORM** | Flask-SQLAlchemy 3.x | Declarative ORM models with `Decimal` precision |
| **Authentication**| Flask-Login 0.6+ & Werkzeug | Password hashing (PBKDF2-SHA256) & session management |
| **Forms & CSRF** | Flask-WTF 1.2+ & WTForms | Server-side validation and CSRF token protection |
| **Frontend** | HTML5, CSS3, Vanilla JS (ES6+) | Warm Cream, Deep Green, and Terracotta design system |

---

## 📁 Project Structure

```text
Online food ordering system/
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation
├── PROJECT_SPEC.md           # Full technical specifications & ERD
├── IMPLEMENTATION_LOG.md     # Progress tracker across all phases
├── requirements.txt          # Python dependencies
├── config.py                 # Multi-environment configurations (Dev, Test, Prod)
├── run.py                    # Application launch entrypoint
├── instance/
│   └── cravecart.db          # SQLite database storage
├── app/
│   ├── __init__.py           # Application factory (create_app)
│   ├── extensions.py         # SQLAlchemy, LoginManager, CSRFProtect instances
│   ├── models.py             # Database models (User, Category, FoodItem, Order, OrderItem)
│   ├── commands.py           # CLI commands (init-db, seed-db, create-admin)
│   ├── auth/                 # Authentication blueprint (/auth)
│   ├── customer/             # Customer catalog blueprint (/, /menu)
│   ├── admin/                # Admin control blueprint (/admin)
│   ├── services/             # Business logic & cart calculations
│   ├── static/
│   │   ├── css/main.css      # Design system variables, responsive styles
│   │   ├── js/main.js        # Vanilla client behaviors & flash dismissals
│   │   └── images/           # Placeholder graphics & upload targets
│   └── templates/
│       ├── base.html         # Master layout
│       ├── auth/             # Login & registration views
│       ├── customer/         # Catalog & landing page views
│       ├── admin/            # Admin dashboard views
│       └── errors/           # Custom error pages (403, 404, 500)
└── tests/
    ├── conftest.py           # Pytest test fixtures
    ├── test_models.py        # Model & relationship verification
    └── test_cli_and_routes.py# CLI & route smoke tests
```

---

## 🚀 Setup & Installation Instructions

### 1. Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### 2. Clone / Open the Project
```bash
cd "Online food ordering system"
```

### 3. Create and Activate Virtual Environment
```bash
python3 -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 6. Initialize & Seed Database
```bash
# Initialize database tables
flask init-db

# Seed demonstration categories and food items
flask seed-db

# Create an administrator account interactively (secure prompt)
flask create-admin
```

### 7. Run the Development Server
```bash
python run.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## 🧪 Running Automated Tests

Run the complete test suite with `pytest`:
```bash
pytest -v
```

---

## 🛡️ Security Highlights

1. **No Client-Side Price Reliance**: All cart line items and order totals are calculated directly on the server against active database prices.
2. **Password Encryption**: Uses salted PBKDF2-SHA256 password hashes; plaintext passwords are never stored.
3. **Role-Based Guards**: Administrative endpoints are protected via strict role authorization checks (`role == 'admin'`).
4. **CSRF Tokens**: All form mutations and AJAX calls are verified using CSRF protection.
