# CraveCart – Implementation & Progress Log

## Project Summary
- **Project Title:** CraveCart – Online Food Ordering System
- **Stack:** Python Flask, SQLite, Flask-SQLAlchemy, Flask-Login, Flask-WTF, HTML5, CSS3, Vanilla JavaScript
- **Architecture:** Application Factory Pattern with Modular Blueprints
- **Design Identity:** Modern culinary theme with warm cream background (`#FAF6EE`), deep forest green elements (`#163829`), and terracotta accents (`#D9532F`).

---

## Phase Status Overview

| Phase | Description | Status | Target Completion |
| :---: | :--- | :---: | :---: |
| **Phase 0** | Requirements Analysis & Architecture Design | **COMPLETED** | Initial Phase |
| **Phase 1** | Application Foundation, Extensions & Database Models | **COMPLETED** | Phase 1 |
| **Phase 2** | Customer Authentication & Food Browsing Experience | **COMPLETED** | Phase 2 |
| **Phase 3** | Shopping Cart, Cash-on-Delivery Checkout & Order Management | **COMPLETED** | Phase 3 |
| **Phase 4** | Administrator Portal, Menu/Category CRUD & Stock Control | Pending | Phase 4 |
| **Phase 5** | Administrator Order Fulfillment & Status Lifecycle Management | Pending | Phase 5 |
| **Phase 6** | End-to-End Testing, Responsive Polish & Final Documentation | Pending | Phase 6 |

---

## Detailed Phase Progress Log

### Phase 0: Requirements Analysis & Architecture Design
- **Date Completed:** 2026-11-09
- **Deliverables Created:**
  - `PROJECT_SPEC.md`: Comprehensive technical specification including system overview, data dictionary, entity-relationship diagrams, security policies, endpoint catalog, cart lifecycle, UI/UX design tokens, and testing plan.
  - `IMPLEMENTATION_LOG.md`: Living progress and decision record.
  - Proposed modular directory architecture.
- **Key Architectural Decisions:**
  1. **Application Factory Pattern:** Using `create_app()` inside `app/__init__.py` to avoid circular imports and enable test fixtures.
  2. **Session-Based Cart:** Storing cart items in `flask.session` to keep database operations light while ensuring abandoned carts do not accumulate table bloat.
  3. **Strict Price Integrity:** Calculating all line item subtotals and grand totals exclusively on the backend using active database prices at the moment of checkout. Client prices are completely ignored.
  4. **Single-Restaurant Scope:** Streamlined data model focusing on customer-to-restaurant order workflow without multi-vendor or multi-tenant complexity.
  5. **Vanilla UI Stack:** Designing clean, responsive styling with pure CSS variables and vanilla JavaScript to avoid unnecessary framework bloat for a college mini-project.

---

### Phase 1: Application Foundation, Extensions & Database Models
- **Date Completed:** 2026-11-09
- **Deliverables Created & Implemented:**
  1. **Application Factory (`app/__init__.py`)**:
     - Configurable environment initialization (`DevelopmentConfig`, `TestingConfig`, `ProductionConfig`).
     - Global context processors injecting app branding and year.
     - Centralized HTTP error handlers for 403, 404, and 500 status codes.
  2. **Extensions Setup (`app/extensions.py`)**:
     - Initialized `SQLAlchemy` ORM, `LoginManager` session handler, and `CSRFProtect` token manager.
     - Configured default login view (`auth.login`) and user loader callback.
  3. **Configuration & Secrets (`config.py`, `.env.example`, `.env`)**:
     - Dynamic instance folder creation.
     - SQLite URI default with absolute resolution to `instance/cravecart.db`.
     - File upload boundaries and payload limits (`MAX_CONTENT_LENGTH = 5MB`).
  4. **Database Models (`app/models.py`)**:
     - `User`: `id`, `name`, `email` (unique index), `password_hash`, `role` (`customer`/`admin`), `created_at`, password hashing methods (`set_password`, `check_password`), role check properties (`is_admin`, `is_customer`).
     - `Category`: `id`, `name` (unique index), `description`, `created_at`, relationship to `FoodItem` with cascade delete-orphan.
     - `FoodItem`: `id`, `name` (index), `description`, `price` (`Numeric(10,2)` with Python `Decimal` representation), `image_url`, `category_id` (FK), `is_available` (index), `created_at`.
     - `Order`: `id`, `order_number` (unique index), `user_id` (FK), `total_amount` (`Numeric(10,2)`), `delivery_address`, `phone_number`, `payment_method`, `status` (index, defaults to 'Pending'), `created_at` (index), with `recalculate_total()` and `generate_order_number()`.
     - `OrderItem`: `id`, `order_id` (FK cascade), `food_item_id` (FK set null), historical `item_name`, historical `unit_price`, `quantity`, `subtotal` with `calculate_subtotal()`.
  5. **Modular Blueprints**:
     - `app/auth/`: routes for `/auth/login`, `/auth/register`, `/auth/logout`.
     - `app/customer/`: routes for `/` (landing page with categories & featured dishes), `/menu`.
     - `app/admin/`: route for `/admin/dashboard` protected by `@login_required`.
     - `app/services/`: service layer package initialized.
  6. **Interactive & Automated CLI Commands (`app/commands.py`)**:
     - `flask init-db [--drop]`: Initializes SQLite tables safely.
     - `flask seed-db`: Populates 5 culinary categories and 12 realistic demonstration dishes with `Decimal` pricing and photography.
     - `flask create-admin`: Interactive password prompt with hidden input, confirmation, length checks, and role assignment. No hardcoded credentials.
  7. **Frontend Design Foundation (`app/static/css/main.css`, `base.html`)**:
     - Full design system implemented: warm cream `#FAF6EE`, deep forest green `#163829`, terracotta `#D9532F`.
     - Fully responsive navbar, cards, food grid, badges, buttons, flash alert auto-dismissal, and semantic footer.
  8. **Comprehensive Automated Test Suite (`tests/`)**:
     - `tests/conftest.py`: pytest fixtures for in-memory SQLite testing app, test client, and CLI runner.
     - `tests/test_models.py`: 6 unit tests covering password hashing, role checks, email uniqueness, category-item relationships, order-item calculations, price snapshot preservation, and cascade deletion.
     - `tests/test_cli_and_routes.py`: 5 tests covering CLI commands (`init-db`, `seed-db`, `create-admin`) and HTTP route status codes.
     - **Test Results:** 11 passed in 2.61s (100% pass rate).
  9. **Documentation**:
     - `README.md`: Complete setup, virtual environment, dependencies, CLI commands, and run guide.

---

### Phase 2: Customer Authentication & Food Browsing Experience
- **Date Completed:** 2026-11-12
- **Deliverables Created & Implemented:**

  #### Part A: Authentication System
  1. **Flask-WTF Forms (`app/forms/auth_forms.py`)**:
     - `RegistrationForm`: Full Name (2-100 chars), Email (sanitized, validated format, unique check against DB), Password (minimum 8 characters), Confirm Password (equality match).
     - `LoginForm`: Email, Password, Remember Me boolean.
     - Field-level validation error rendering under each input field in templates.
  2. **Security & Role Enforcement (`app/auth/routes.py`, `app/utils/decorators.py`)**:
     - Public registration strictly enforces `role='customer'`, preventing privilege escalation.
     - Passwords hashed using PBKDF2-SHA256 via Werkzeug security.
     - Safe post-login redirection using `is_safe_url()`, avoiding open-redirect vulnerabilities.
     - Role-aware post-login redirects: Administrators to `/admin/dashboard`, Customers to `/`.
     - Protected administrative endpoints using `@admin_required`: Unauthenticated requests redirect to login; unauthorized customer requests receive HTTP 403 Forbidden.
  3. **Session Management (Flask-Login)**:
     - `login_user()`, `logout_user()`, and `current_user` integrated into templates and routes.
     - Flash messages for success and error conditions (account creation, invalid credentials, logout confirmation).

  #### Part B: Customer Food Experience
  1. **Homepage (`/` – `app/templates/customer/index.html`)**:
     - Artisanal hero banner with headline and CTA button to explore the full menu.
     - Restaurant story and 3 value pillars: Farm-to-Table, Master Chef Crafted, Cash on Delivery.
     - Food categories section with quick filter cards.
     - Chef's featured items grid with real-time stock badges and Add to Cart buttons.
  2. **Menu Catalog (`/menu` – `app/templates/customer/menu.html`)**:
     - Full catalog displaying food image, dish name, description, price, and stock status.
     - Search functionality querying dish names and descriptions via SQL ILIKE.
     - Category filter tabs with active states and filter reset.
     - Responsive grid layout with empty search state handling.
  3. **Food Details Page (`/food/<id>` – `app/templates/customer/food_detail.html`)**:
     - High-resolution dish presentation with automatic fallback on missing images.
     - Full culinary description, category badge, and stock indicator.
     - Add to Cart form with interactive quantity stepper `[-] [input] [+]`.
     - Complementary dishes recommendations from the same category.
  4. **Navigation & Cart Integration**:
     - Reusable Jinja2 macro (`app/templates/components/_food_card.html`) for consistent food card rendering.
     - Dynamic cart badge counter in the navbar (`#cartBadgeCount`), injected across all templates via context processor.
     - Functional session cart addition (`/cart/add/<id>`) and cart review page (`/cart` – `app/templates/customer/cart.html`).
     - SVG culinary placeholder fallback (`app/static/images/food-placeholder.svg`) ensuring zero broken image icons.

---

### Phase 3: Shopping Cart, Cash-on-Delivery Checkout & Order Management
- **Date Completed:** 2026-11-12
- **Deliverables Created & Implemented:**

  #### Part A: Shopping Cart Engine (`app/services/cart_service.py`)
  1. **Session Cart Storage**:
     - Cart stored directly in encrypted client-side session (`flask.session['cart']`).
     - Persistent cart count badge rendered in the navbar across all views.
  2. **Cart Mutations**:
     - Add food items (`/cart/add/<id>`) with stock check.
     - Increase / decrease quantity (`/cart/update/<id>`) with upper boundary limits (1–50) and auto-removal at zero.
     - Remove individual items (`/cart/remove/<id>`).
     - Clear entire cart (`/cart/clear`).
  3. **Server-Side Integrity & Reconciliations**:
     - All prices, subtotals, and totals are computed strictly from database records using Python `Decimal`.
     - Frontend price parameters or tampering attempts are completely ignored.
     - Real-time stock verification prevents checkout if items become unavailable.
     - Rich empty-cart state guiding users back to the dining menu.

  #### Part B: Cash-on-Delivery Checkout (`app/forms/order_forms.py`, `app/templates/customer/checkout.html`)
  1. **Checkout Form (Flask-WTF)**:
     - Recipient Full Name, Contact Phone Number (required for delivery coordination), Delivery Street Address, and optional cooking/delivery notes.
     - Pre-populated with customer's registered account name.
  2. **Order Summary Review**:
     - Itemized list with line subtotals and quantities.
     - Prominently styled "Cash on Delivery (COD)" payment modality box.
     - Duplicate submission protection on the frontend button.

  #### Part C: Atomic Order Processing (`app/services/order_service.py`, `app/templates/customer/order_confirmation.html`)
  1. **Atomic Transaction**:
     - Creates master `Order` record with human-readable tracking code (`CRV-YYYYMMDD-ID`).
     - Generates `OrderItem` records capturing immutable historical snapshots of dish title and unit price.
     - Database commit wrapped in safe exception handling with automated rollback on failure.
     - Active session cart is emptied only upon confirmed database commit.
  2. **Order Confirmation View**:
     - Instant visual confirmation with order ID, tracking code, recipient details, and itemized bill.

  #### Part D: Customer Order History & Timeline Tracking (`app/templates/customer/orders.html`, `app/templates/customer/order_detail.html`)
  1. **Order History View (`/orders`)**:
     - Lists previous dining orders with status pills, formatted timestamps, and delivery summaries.
  2. **Detailed Order View & Timeline (`/orders/<id>`)**:
     - Progressive linear status timeline supporting all six system statuses:
       `PLACED` &bull; `CONFIRMED` &bull; `PREPARING` &bull; `OUT FOR DELIVERY` &bull; `DELIVERED` &bull; `CANCELLED`
     - Active stage indicator with animated highlight.
     - Immutable itemized receipt.
  3. **Customer Self-Service Cancellation**:
     - Cancellation is strictly restricted to orders in `PLACED` status.
     - Once an order reaches `CONFIRMED` or subsequent stages, cancellation is locked.
  4. **Authorization Security**:
     - Customers can strictly access only their own order records; unauthorized access attempts to other customers' orders return HTTP 403 Forbidden.

  #### Automated Testing Suite (`tests/test_cart_and_orders.py`)
  Added 7 new integration tests covering the complete cart and order workflow:
  - Full cart operations (+ / - / remove / clear / add).
  - Quantity bounds and out-of-stock dish rejection.
  - Server-side price calculation integrity.
  - Checkout form validation and empty-cart prevention.
  - Order creation, price snapshots, and cart clearing.
  - Order history and customer authorization guards (customer A cannot view customer B's order).
  - Cancellation state transitions and restrictions.
  - **Overall Test Results:** 28 passed in 14.92s (100% pass rate).

---

### Phase 4: Administrator Dashboard, Food/Category Management & Order Fulfillment
- **Date Completed:** 2026-11-15
- **Status:** COMPLETED
- **Deliverables Created & Implemented:**

  #### Part A: Protected Administrator Dashboard (`app/admin/routes.py`, `app/templates/admin/dashboard.html`)
  1. **Role-Based Authorization Gatekeeper**:
     - Enforced via `@admin_required` decorator across all `/admin/*` endpoints.
     - Anonymous users are redirected to the login page with a warning message.
     - Authenticated customers attempting access are rejected with an explicit HTTP 403 Forbidden.
  2. **Real-Time Analytical KPIs**:
     - Total Orders count.
     - Total Registered Customers.
     - Total Active Menu Dishes.
     - Total Delivered Revenue (computed strictly from `DELIVERED` orders using `Decimal` aggregation).
  3. **Order Status Breakdown & Live Pipeline**:
     - Visual breakdown cards for each stage: `PLACED`, `CONFIRMED`, `PREPARING`, `OUT FOR DELIVERY`, `DELIVERED`, and `CANCELLED`.
     - Recent Orders table with customer identity, phone, timestamp, item count, total price, and direct link to detail/management views.

  #### Part B: Food Item & Category Catalog Management
  1. **Category Management (`/admin/categories`, `/admin/categories/<id>/edit`, `/admin/categories/<id>/delete`)**:
     - Add new food category with name and description validation via `CategoryForm`.
     - Edit existing category metadata.
     - **Safe Deletion Check**: Prevents deletion of categories that have active food items attached to them, returning an informative flash message to prevent foreign key or orphan catalog errors.
  2. **Food Item Management (`/admin/items`, `/admin/items/new`, `/admin/items/<id>/edit`, `/admin/items/<id>/delete`)**:
     - Create new food dishes with image URL, culinary description, category assignment, and unit price validation (between $0.01 and $999.99).
     - Edit existing dishes with pre-populated values and dynamic category dropdown.
     - Instant stock availability toggle (`/admin/items/<id>/toggle-stock`) allowing one-click switching between "In Stock" and "Out of Stock".
     - Delete food item with confirmation.

  #### Part C: Order Fulfillment & State Machine Transitions (`/admin/orders`, `/admin/orders/<id>`)
  1. **Order Search & Filter Pipeline**:
     - Filter orders by status pill (`ALL`, `PLACED`, `CONFIRMED`, `PREPARING`, `OUT FOR DELIVERY`, `DELIVERED`, `CANCELLED`).
     - Search orders by order ID number, tracking reference (`CRV-...`), or customer name.
  2. **Order Details & Customer Delivery Information**:
     - Displays full customer delivery profile: recipient name, telephone number, full street delivery address, payment method (`CASH ON DELIVERY`), and customer notes.
     - Complete itemized bill breakdown with historic price and title snapshots.
  3. **Strict State Machine Workflow**:
     - Implemented model-level validation (`Order.can_transition_to` and `Order.allowed_transitions`):
       - `PLACED` &rarr; `CONFIRMED` or `CANCELLED`
       - `CONFIRMED` &rarr; `PREPARING` or `CANCELLED`
       - `PREPARING` &rarr; `OUT FOR DELIVERY`
       - `OUT FOR DELIVERY` &rarr; `DELIVERED`
       - Terminal statuses (`DELIVERED`, `CANCELLED`) cannot transition further.
     - Invalid status transitions are rejected on the backend with an error flash message and no state change.

  #### Part D: User Interface & Security
  1. **Dedicated Admin Workspace UI (`app/templates/admin/base_admin.html`, `app/static/css/admin.css`)**:
     - Responsive sidebar layout with brand badge, quick links (Dashboard, Food Items, Categories, Orders), and "View Storefront" shortcut.
     - Consistent warm cream background, deep forest green primary accents, and terracotta highlights design tokens.
     - CSRF token protection on all admin POST forms and action buttons.
  2. **Automated Testing Suite (`tests/test_admin.py`)**:
     - Customer access rejection (HTTP 403).
     - Anonymous access redirection (HTTP 302 &rarr; `/auth/login`).
     - Admin access to dashboard and KPI statistics.
     - Category CRUD operations and safe deletion constraint verification.
     - Food item CRUD operations, price boundary validations ($0.00 rejection), and stock toggling.
     - Order status filtering and search by ID/customer.
     - Order state machine transitions (valid progression tested and invalid transitions rejected).
     - **Overall Test Results:** 35 passed in 18.72s (100% pass rate).

---

### Phase 5: Full UI Refinement, Quality Assurance & End-to-End Journey Testing
- **Date Completed:** 2026-11-20
- **Status:** COMPLETED
- **Deliverables Created & Implemented:**

  #### Part A: UI Polish & Design System Modernization
  1. **Typography & Brand Hierarchy**:
     - Modernized typography with Playfair Display for hero titles and Plus Jakarta Sans for UI copy.
     - Enforced brand palette tokens: Warm Cream canvas (`#FAF7F2`), Dark Forest Green (`#122B1E`), and Terracotta flame accent (`#E05332`).
     - Standardized accessible `:focus-visible` styling with 2px offset across all interactive links, buttons, and form inputs.
  2. **Food Cards & Catalogs**:
     - Added floating status badges on image wrappers (`Sold Out` vs `In Stock`).
     - Line-clamp consistency for card titles and culinary descriptions ensuring uniform grid heights across varying screen sizes.
     - Dynamic Add to Cart button with responsive mobile layout and disabled states for unavailable dishes.
  3. **Alerts & Toasts**:
     - Slide-in animation with smooth 6-second auto-dismiss and pause-on-hover logic in `main.js`.
     - Explicit close buttons with animated fade-and-collapse transitions.

  #### Part B: Responsiveness Across Breakpoints (Desktop, Tablet, Mobile)
  1. **Customer Navigation**:
     - Implemented accessible mobile menu toggle (`#mobileNavToggle`) with smooth dropdown drawer for screens under 768px.
     - Name truncation for customer accounts with long display names preventing navbar overflow.
  2. **Admin Sidebar Responsive Drawer**:
     - Added mobile hamburger menu (`#adminMobileToggle`) to allow toggling navigation and footer actions on tablet and mobile viewports.
  3. **Layout Adaptations**:
     - `.cart-layout`, `.checkout-layout`, `.order-detail-layout`, and `.admin-split-layout` convert from 2-column desktop layouts to single-column vertical flows on viewports <900px.
     - Cart tables wrapped in `.cart-table-wrapper` with horizontal smooth scrolling and minimum widths, eliminating horizontal page overflow on mobile devices.
     - Order status timeline steps wrap cleanly on small mobile viewports with centered step indicators.

  #### Part C: Complete 14-Step User Journey Verification (`tests/test_e2e_journey.py`)
  Automated end-to-end integration test validating the entire business workflow:
  1. Customer opens homepage (`/`) &rarr; Hero, featured items, and categories verified.
  2. Customer browses food (`/menu`) &rarr; Catalog items render properly.
  3. Customer registers (`/auth/register`) &rarr; Customer account created with hashed password.
  4. Customer logs in (`/auth/login`) &rarr; Session established with welcome greeting.
  5. Customer searches food (`/menu?q=Truffle`) &rarr; Filtered results returned via SQL matching.
  6. Customer adds items to cart (`/cart/add/<id>`) &rarr; Session cart updated with stock verification.
  7. Customer updates quantities (`/cart/update/<id>`) &rarr; Server-side price recalculation verified.
  8. Customer checks out (`/checkout`) &rarr; Delivery coordinate form rendered.
  9. Customer places an order (`POST /checkout`) &rarr; Order and snapshot line items committed, session cart emptied, confirmation generated with tracking reference.
  10. Customer views order history (`/orders` & `/orders/<id>`) &rarr; Verified order summary, receipt, and live status progress timeline in `PLACED` state.
  11. Administrator logs in (`/auth/login`) &rarr; Admin redirected to dashboard with live statistics.
  12. Administrator views the order (`/admin/orders` & `/admin/orders/<id>`) &rarr; Discovers order and verifies customer delivery notes.
  13. Administrator updates status (`/admin/orders/<id>/status` &rarr; `CONFIRMED`) &rarr; Transition validated by state machine.
  14. Customer sees updated status (`/orders/<id>`) &rarr; Customer inspects timeline reflecting `CONFIRMED`, with order cancellation locked.

  #### Part D: Code Quality & Test Suite Health
  - Zero dead code, unused debugging statements (`print`, `console.log`), or empty `#` links.
  - All forms protected with Flask-WTF CSRF tokens and server-side validation.
  - Role-based authorization enforced across all customer and administrator routes.
  - **Overall Test Results:** 36 passed in 18.38s (100% pass rate).

---

### Project Status Overview
- **Phase 0:** Project Specification & Architecture (Done)
- **Phase 1:** Core Foundation, Blueprints & Database Models (Done)
- **Phase 2:** Customer Authentication & Food Catalog Experience (Done)
- **Phase 3:** Shopping Cart & Cash-on-Delivery Order Processing (Done)
- **Phase 4:** Administrator Dashboard, Menu/Category CRUD & Order Fulfillment (Done)
- **Phase 5:** Full UI Refinement, Quality Assurance & End-to-End Verification (Done)
