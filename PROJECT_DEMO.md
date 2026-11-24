# CraveCart – Examiner Demonstration Walkthrough & Viva Presentation Script (PROJECT_DEMO.md)

This document provides a sequential, step-by-step demonstration script designed for presenting **CraveCart – Online Food Ordering System** to an academic examiner or evaluation panel.

---

### Phase 1: Environment Preparation (Before Presentation)

Ensure your development environment is set up and tested:
```bash
# 1. Activate virtual environment
source venv/bin/activate       # On macOS / Linux
# venv\Scripts\activate.bat    # On Windows

# 2. Reset and seed fresh database with demonstration data
flask init-db --drop
flask seed-db

# 3. Create administrator credentials
flask create-admin
# Name: Executive Chef
# Email: admin@cravecart.com
# Password: AdminMaster2026!

# 4. Run automated test suite to prove 100% test passing
pytest -v
```

---

### Phase 2: Live Demonstration Sequence

#### Step 1: Architecture & Codebase Introduction (1-2 Minutes)
- **What to show**: Open the project root folder in your editor.
- **Talking points**:
  - *"CraveCart is an artisanal single-restaurant food ordering system developed from scratch using Python Flask, SQLite, and vanilla HTML5, CSS3, and ES6 JavaScript."*
  - *"We followed the Flask Application Factory pattern (`create_app`) and modular Blueprints (`app/auth`, `app/customer`, `app/admin`)."*
  - *"All financial calculations use Python `Decimal` and database records to ensure zero client-side price tampering."*
- **Action**: Start the server:
  ```bash
  python run.py
  ```
  Open browser at `http://127.0.0.1:5000`.

---

#### Step 2: Storefront & Brand Identity (Homepage)
- **What to show**: Homepage (`/`).
- **Highlights**:
  - Show the warm cream (`#FAF7F2`), dark forest green (`#122B1E`), and terracotta (`#E05332`) visual identity.
  - Explain the 3 value pillars: *Farm-to-Table Fresh*, *Master Chef Crafted*, and *Cash on Delivery*.
  - Show the **Explore by Category** section and **Chef's Featured Dishes**.
  - Point out that every dish displays an artisanal vector SVG placeholder if no custom image is supplied.

---

#### Step 3: Menu Browsing, Category Filtering & Live Search
- **What to show**: Menu Catalog (`/menu`).
- **Demonstration**:
  1. Click through the category filter tabs: *Starters & Appetizers*, *Main Course*, *Artisan Pizzas & Burgers*, *Desserts & Sweets*, *Beverages & Mocktails*. Notice the URL query updates cleanly (`/menu?category=1`).
  2. Test text search: Type `Truffle` into the search box and press Enter. Point out that *Crispy Truffle Fries* is displayed while unrelated dishes are filtered out.
  3. Click **Reset** or **Clear Filters** to show all items again.

---

#### Step 4: Dish Details & Allergen Presentation
- **What to show**: Food Detail View (`/food/<id>`).
- **Demonstration**:
  1. Click on *Crispy Truffle Fries*.
  2. Point out the breadcrumb navigation (`Home / Menu / Starters / Crispy Truffle Fries`).
  3. Show the large photography, full culinary description, price tag, and real-time stock badge (`In Stock & Ready`).
  4. Test the interactive quantity stepper `[-] [ 1 ] [+]` (demonstrate that it bounds values between 1 and 20).
  5. Point out the related dishes section at the bottom (*"You Might Also Crave"*).

---

#### Step 5: Customer Registration & Session Authentication
- **What to show**: Customer Registration (`/auth/register`) and Login (`/auth/login`).
- **Demonstration**:
  1. Click **Register** in the top navigation bar.
  2. Fill in the form:
     - Name: `Jane Doe`
     - Email: `jane@example.com`
     - Password: `CustomerPass123!`
     - Confirm Password: `CustomerPass123!`
  3. Submit the form. Show the success notification: *"Your account has been created successfully! Please sign in."*
  4. Log in as `jane@example.com`.
  5. Point out the navbar changes:
     - The customer's name is displayed with an active green status dot.
     - A **My Orders** link appears in the main navigation.
     - Sign In and Register are replaced by a **Logout** button.

---

#### Step 6: Shopping Cart Manipulation & Server-Side Pricing
- **What to show**: Cart View (`/cart`).
- **Demonstration**:
  1. Add 2x *Crispy Truffle Fries* ($7.50 each) and 1x *Wild Mushroom Risotto* ($14.50).
  2. Point out the real-time **Cart Count Badge** in the top navigation bar (`3`).
  3. Click the Cart button to navigate to `/cart`.
  4. Show the responsive table with line item subtotals:
     - 2x Truffle Fries = \$15.00
     - 1x Wild Mushroom Risotto = \$14.50
     - Total = \$29.50.
  5. Click the `+` button on Truffle Fries to increase quantity to 3. Notice the subtotal automatically updates to \$22.50 and the grand total to \$37.00.
  6. **Viva point to emphasize**: *"Examiner, notice that prices are never accepted from the frontend. Even if someone inspects the HTML and modifies the price attribute, our backend `CartService` fetches the price from SQLite directly."*

---

#### Step 7: Cash on Delivery Checkout & Atomic Transaction
- **What to show**: Checkout Page (`/checkout`).
- **Demonstration**:
  1. Click **Proceed to Checkout &rarr;**.
  2. Show the pre-filled customer name (`Jane Doe`).
  3. Complete the delivery coordinates:
     - Contact Phone: `+1-555-0199`
     - Delivery Address: `Suite 404, Evergreen Heights, Downtown`
     - Delivery Notes: `Please call upon arrival at the gate`
  4. Highlight the **Cash on Delivery (COD)** payment modality box. Explain to the examiner that COD is an authentic, zero-commission payment flow for single-kitchen dining.
  5. Click **Place Order (Cash on Delivery)**.
  6. Notice the button shows a loading state to prevent accidental double-clicks.

---

#### Step 8: Order Confirmation & Live Timeline Tracking
- **What to show**: Order Confirmation (`/orders/confirmation/<id>`) and Order Detail (`/orders/<id>`).
- **Demonstration**:
  1. The browser redirects to the confirmation screen. Point out the tracking code format (`CRV-20261120-0001`).
  2. Click **Track Order Timeline &rarr;** to open the live customer order tracking view.
  3. Point out the 5-stage progress stepper:
     - `1: Placed` (Active, highlighted in terracotta)
     - `2: Confirmed`
     - `3: Preparing`
     - `4: Out For Delivery`
     - `5: Delivered`
  4. Show the itemized bill table. Explain the **Snapshot Architecture**: dish names and unit prices are permanently recorded in `order_items` so future menu updates never alter past receipts.

---

#### Step 9: Customer Cancellation Policy Test
- **What to show**: Customer Order View (`/orders/<id>`).
- **Demonstration**:
  1. Show that while the order is in `PLACED` status, a red **Cancel This Order** button is available.
  2. Explain the policy: *"Customers can only cancel self-service while the kitchen has not accepted the order. Once the status advances to CONFIRMED, cancellation is locked."*

---

#### Step 10: Security Test: Role-Based Authorization Gatekeeper
- **What to show**: Customer attempting admin access.
- **Demonstration**:
  1. While still logged in as customer `Jane Doe`, manually type `http://127.0.0.1:5000/admin` into the browser URL bar.
  2. Press Enter.
  3. **Result**: The custom **403 Forbidden** page is displayed: *"Access Denied – You do not have permission to view this restricted page."*
  4. Point out to the examiner that the `@admin_required` decorator verified the user's role and blocked access.

---

#### Step 11: Administrator Dashboard & Live Financial Analytics
- **What to show**: Administrator Login & Dashboard (`/admin/dashboard`).
- **Demonstration**:
  1. Click **Logout** from the customer account.
  2. Sign in using the administrator credentials (`admin@cravecart.com` / `AdminMaster2026!`).
  3. The system automatically redirects to the **Admin Operations Console**.
  4. Review the 4 analytical KPI cards:
     - **Total Orders**: Active count of orders.
     - **Delivered Revenue**: Revenue computed strictly from completed `DELIVERED` orders.
     - **Active Customers**: Count of registered users.
     - **Menu Dishes**: Total dishes in the catalog.
  5. Show the **Order Status Breakdown** pills showing counts for `Placed`, `Confirmed`, `Preparing`, `Out for Delivery`, `Delivered`, and `Cancelled`.
  6. Show the **Recent Customer Orders** table listing Jane Doe's new order.

---

#### Step 12: Menu Catalog Management & Instant Stock Toggle
- **What to show**: Food Inventory (`/admin/items`).
- **Demonstration**:
  1. Navigate to **Food Inventory**.
  2. Find *Crispy Truffle Fries*. Show the **In Stock** button.
  3. Click the stock button. It instantly flips to **Out of Stock**.
  4. Open an incognito browser or separate tab to `/menu`: show that the dish now displays an overlay badge `Sold Out` and the Add to Cart button is disabled!
  5. Click the button again in the admin tab to return it to **In Stock**.
  6. Click **Edit** on a dish. Show the price validation: change price to `-5.00` or `0.00` and submit; show that the backend rejects it with *"Price must be between $0.01 and $999.99"*.

---

#### Step 13: Category Management & Relational Safe-Delete Guard
- **What to show**: Category Management (`/admin/categories`).
- **Demonstration**:
  1. Show existing categories: *Starters & Appetizers*, *Main Course*, etc.
  2. Find *Starters & Appetizers* (which contains active dishes).
  3. Click **Delete**.
  4. **Result**: The system blocks deletion and displays an alert: *"Cannot delete category 'Starters & Appetizers' because it still contains 3 dishes."*
  5. Explain to the examiner that this application-level relational check protects against orphaned records.
  6. Now, create a dummy category: *Seasonal Mocktails* with 0 dishes.
  7. Delete *Seasonal Mocktails*: it deletes cleanly with a success notification.

---

#### Step 14: Order Fulfillment State Machine Enforcement
- **What to show**: Admin Order Inspection & Transition (`/admin/orders/<id>`).
- **Demonstration**:
  1. Navigate to **Orders** (`/admin/orders`).
  2. Filter orders by status pill (*Placed*).
  3. Click **Fulfill &rarr;** on Jane Doe's order.
  4. Show the fulfillment transition card. The dropdown only offers valid target transitions according to the state machine:
     - Target: `Advance to: CONFIRMED` or `Advance to: CANCELLED`.
  5. Select `Advance to: CONFIRMED` and submit.
  6. The order status updates to `CONFIRMED`.
  7. Notice the dropdown now dynamically updates to offer the next stage: `Advance to: PREPARING` or `Advance to: CANCELLED`.
  8. Advance it to `PREPARING`, then `OUT FOR DELIVERY`, and finally `DELIVERED`.
  9. Show that once it reaches `DELIVERED`, the transition selector is replaced with: *"Terminal State – No further transitions allowed."*
  10. Return to the dashboard: show that the **Delivered Revenue** KPI has now updated to reflect this order's total amount!

---

#### Step 15: Customer Real-Time Status Verification
- **What to show**: Customer Order History (`/orders`).
- **Demonstration**:
  1. Sign out of the admin console.
  2. Log back in as `jane@example.com`.
  3. Navigate to **My Orders**.
  4. Open the order details.
  5. Point out that the 5-stage timeline now shows the completed progression with the final celebration message: *"Bon Appétit! Your order has been delivered and payment collected."*
  6. Notice the self-service **Cancel** button is no longer present.

---

#### Step 16: Automated Testing Demonstration (Final Proof)
- **What to show**: Terminal running pytest.
- **Demonstration**:
  1. Open terminal in the project directory.
  2. Run:
     ```bash
     pytest -v
     ```
  3. Show the output:
     ```text
     ============================== 36 passed in 18.38s ==============================
     ```
  4. Point out that all 36 tests—including unit tests, route handlers, security guards, and the complete 14-step integration test—pass with a 100% pass rate.

---

### Phase 3: Summary of Key Achievements for Examiner

1. **Clean Code & Modular Architecture**: Application Factory pattern with 3 isolated Blueprints and no monolithic Python files.
2. **True Full-Stack**: 100% handcrafted HTML5, CSS3 variables, and vanilla JavaScript without relying on heavy third-party UI frameworks.
3. **Rock-Solid Security**: CSRF protection on all mutating requests, PBKDF2 password hashing, RBAC via `@admin_required`, and IDOR defense on customer receipts.
4. **Financial Accuracy**: Absolute avoidance of binary floating-point errors through Python's `Decimal` and database snapshotting.
5. **Enforced State Machine**: Order fulfillment transitions follow a strict directed acyclic graph preventing invalid status jumps.
