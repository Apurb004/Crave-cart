# CraveCart: Beginner's Complete Runbook & Operating Guide

Welcome to the **CraveCart Online Food Ordering System**! This guide is written specifically for beginners in software development. It gives you the exact, step-by-step instructions to set up, initialize, run, test, and troubleshoot your project without any prior command-line experience.

---

## Table of Contents
1. [Understanding the System Requirements](#1-understanding-the-system-requirements)
2. [Step-by-Step Environment Setup](#2-step-by-step-environment-setup)
3. [Installing Project Dependencies](#3-installing-project-dependencies)
4. [Setting Up Environment Variables (.env)](#4-setting-up-environment-variables-env)
5. [Database Initialization & Seeding](#5-database-initialization--seeding)
6. [Creating an Administrator Account](#6-creating-an-administrator-account)
7. [Starting the Application](#7-starting-the-application)
8. [Accessing the Application in Your Browser](#8-accessing-the-application-in-your-browser)
9. [Running Automated Tests](#9-running-automated-tests)
10. [Common Errors and Solutions](#10-common-errors-and-solutions)
11. [Quick Reference Cheat Sheet](#11-quick-reference-cheat-sheet)

---

## 1. Understanding the System Requirements

Before running the application, make sure you have:
- **Python**: Version `3.9`, `3.10`, `3.11`, or `3.12`.
- **pip**: The standard Python package installer (installed automatically with Python).
- **A Terminal** (macOS / Linux) or **Command Prompt / PowerShell** (Windows).
- **A Modern Web Browser** (Chrome, Firefox, Safari, or Edge).

To verify that Python and pip are installed, open your terminal and run:

**macOS / Linux:**
```bash
python3 --version
pip3 --version
```

**Windows:**
```cmd
python --version
pip --version
```

If version numbers appear (e.g., `Python 3.9.6`), you are ready to proceed!

---

## 2. Step-by-Step Environment Setup

### What is a Virtual Environment?
In Python, a **virtual environment** (`venv`) is a private, isolated folder containing its own copy of Python and installed libraries. Using a virtual environment ensures that the libraries CraveCart requires do not conflict with other Python programs on your computer.

### Step 2.1: Open your project folder
Navigate to the root directory where your project files reside:

**macOS / Linux / Windows:**
```bash
cd "Online food ordering system"
```

### Step 2.2: Create the virtual environment
Run this command once to create a folder named `venv`:

**macOS / Linux:**
```bash
python3 -m venv venv
```

**Windows:**
```cmd
python -m venv venv
```

### Step 2.3: Activate the virtual environment
Every time you open a new terminal window to work on CraveCart, you must activate the virtual environment:

**macOS / Linux:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```
*(Note for Windows PowerShell: If you see an error about execution policies, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` and try again).*

> **How do you know it worked?**
> Your terminal prompt will now have `(venv)` at the beginning, like this:
> `(venv) user@computer Online food ordering system %`

---

## 3. Installing Project Dependencies

With your virtual environment activated, install all the packages required by CraveCart listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### What gets installed:
1. `Flask`: The core lightweight web framework that routes web requests to Python functions.
2. `Flask-SQLAlchemy`: Connects Python code to the SQLite database using Python objects instead of raw SQL strings.
3. `Flask-Login`: Manages user login sessions, remember-me cookies, and authentication states.
4. `Flask-WTF`: Handles secure HTML forms and protects against Cross-Site Request Forgery (CSRF) attacks.
5. `email-validator`: Validates that customer email addresses follow valid internet email standards.
6. `python-dotenv`: Automatically loads configuration settings from a local `.env` file.
7. `pytest`: The test runner used to execute automated unit, integration, and end-to-end tests.

---

## 4. Setting Up Environment Variables (.env)

The application uses an environment configuration file called `.env` to store settings like the secret security key and database path. 

A template file named `.env.example` is provided in the repository.

### Create your `.env` file:

**macOS / Linux:**
```bash
cp .env.example .env
```

**Windows (Command Prompt):**
```cmd
copy .env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

### What is inside `.env`?
Your `.env` file contains:
```env
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=cravecart-dev-secret-key-9f8a3c2b1e7d4a5b6c
DATABASE_URL=sqlite:///cravecart.db
MAX_CONTENT_LENGTH=5242880
UPLOAD_FOLDER=app/static/images/uploads
```
- `FLASK_APP=run.py`: Tells Flask which Python file starts the application.
- `FLASK_DEBUG=1`: Enables automatic code reloading and helpful error messages when files change.
- `SECRET_KEY`: A secret string used by Flask to encrypt session cookies and CSRF tokens.
- `DATABASE_URL=sqlite:///cravecart.db`: Sets the local database to SQLite inside the `instance/` folder.

---

## 5. Database Initialization & Seeding

CraveCart uses custom CLI commands defined in `app/commands.py` to create and populate the database.

### Step 5.1: Create database tables
To build the database tables (`users`, `categories`, `food_items`, `orders`, `order_items`):

```bash
flask init-db
```

**Expected terminal output:**
```text
✓ Database tables initialized successfully.
```
*(This creates the file `instance/cravecart.db`).*

> **Optional Reset:** If you ever want to completely wipe the database and start fresh:
> ```bash
> flask init-db --drop
> ```
> Type `y` when prompted to confirm table removal.

---

### Step 5.2: Seed demonstration dishes and categories
To load the restaurant's initial gourmet menu (Starters, Main Course, Artisan Pizzas & Burgers, Desserts, Beverages):

```bash
flask seed-db
```

**Expected terminal output:**
```text
Seeding demonstration food categories and items...
  + Added category: Starters & Appetizers
  + Added category: Main Course
  + Added category: Artisan Pizzas & Burgers
  + Added category: Desserts & Sweets
  + Added category: Beverages & Mocktails
  + Added food item: Crispy Truffle Fries ($7.50)
  + Added food item: Wild Mushroom Risotto ($14.50)
  ...
✓ Database seeding complete! Added 12 new items.
```

---

## 6. Creating an Administrator Account

To log into the Administrator Operations Dashboard, create an administrator account using the interactive CLI command:

```bash
flask create-admin
```

Follow the prompts directly in your terminal:
```text
--- CraveCart: Create Administrator Account ---
Administrator Name [Restaurant Manager]: Admin Manager
Administrator Email: admin@cravecart.com
Administrator Password: [Type your password - at least 8 characters]
Repeat for confirmation: [Type your password again]
✓ Administrator account 'admin@cravecart.com' created successfully.
```

> **Security Note:** Passwords are never stored as plain text. The application securely hashes your password using the industry-standard `PBKDF2-SHA256` algorithm before saving it to the database.

---

## 7. Starting the Application

Ensure your virtual environment is active `(venv)`, then run the application using either of the following commands:

### Method A (Recommended):
```bash
python run.py
```

### Method B (Flask CLI):
```bash
flask run
```

**Expected terminal output:**
```text
 * Serving Flask app 'run.py'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
```

---

## 8. Accessing the Application in Your Browser

With the server running, open your web browser and visit:

```text
http://127.0.0.1:5000
```
*(or `http://localhost:5000`)*

### Quick Exploration Pathways:

1. **Browse as a Guest:**
   - Visit `http://127.0.0.1:5000/menu` to view food categories, search for dishes, and add items to your cart.
   - Click the **Cart** icon in the navbar to adjust quantities or clear items.

2. **Customer Registration & Checkout:**
   - Click **Register** (`http://127.0.0.1:5000/register`) to create a customer account.
   - Proceed to **Checkout** (`http://127.0.0.1:5000/checkout`), enter your delivery address and phone number, and click **Place Order – Cash on Delivery**.
   - Review your live order status in **My Orders** (`http://127.0.0.1:5000/orders`).

3. **Administrator Portal:**
   - Log out of your customer account.
   - Click **Sign In** (`http://127.0.0.1:5000/login`) and enter the administrator credentials created in Step 6.
   - You will automatically be routed to `http://127.0.0.1:5000/admin/dashboard`.
   - Update order statuses (`PLACED` &rarr; `CONFIRMED` &rarr; `PREPARING` &rarr; `OUT FOR DELIVERY` &rarr; `DELIVERED`).
   - Add new food items, manage categories, or toggle dishes In Stock / Out of Stock.

To stop the web server at any time, press **`CTRL + C`** in your terminal.

---

## 9. Running Automated Tests

CraveCart includes a comprehensive automated test suite consisting of **36 automated tests** covering:
- Database models and relationships (`tests/test_models.py`)
- User registration, login, and browsing (`tests/test_auth_and_browsing.py`)
- Shopping cart arithmetic and order lifecycle (`tests/test_cart_and_orders.py`)
- Admin dashboard metrics and access controls (`tests/test_admin.py`)
- CLI commands (`flask init-db`, `seed-db`, `create-admin`) (`tests/test_cli_and_routes.py`)
- Complete end-to-end customer purchase journey (`tests/test_e2e_journey.py`)

### Run all tests:
```bash
pytest -v
```

**Expected output:**
```text
============================= test session starts ==============================
collected 36 items

tests/test_admin.py .......                                              [ 19%]
tests/test_auth_and_browsing.py ..........                               [ 47%]
tests/test_cart_and_orders.py .......                                    [ 66%]
tests/test_cli_and_routes.py .....                                       [ 80%]
tests/test_e2e_journey.py .                                              [ 83%]
tests/test_models.py ......                                              [100%]

============================= 36 passed in 18.50s ==============================
```

### Run a specific test file:
```bash
pytest tests/test_cart_and_orders.py -v
```

---

## 10. Common Errors and Solutions

### Error 1: `Address already in use` or Port 5000 collision (macOS AirPlay)
- **Symptom:** Terminal says `OSError: [Errno 48] Address already in use` when starting `python run.py`.
- **Cause:** On macOS Monterey, Ventura, and Sonoma, Apple's built-in AirPlay Receiver often listens on port 5000 by default.
- **Solution Option A:** Turn off AirPlay Receiver in macOS:
  - Open `System Settings` &rarr; `General` &rarr; `AirDrop & AirPlay`.
  - Toggle off **AirPlay Receiver**.
- **Solution Option B:** Run Flask on an alternative port (e.g., 5001):
  ```bash
  flask run --port 5001
  ```
  Then open `http://127.0.0.1:5001` in your browser.

---

### Error 2: `ModuleNotFoundError: No module named 'flask'`
- **Symptom:** Running `python run.py` fails with `ModuleNotFoundError: No module named 'flask'`.
- **Cause:** Your virtual environment is not activated, or the dependencies were installed in a different Python environment.
- **Solution:**
  1. Activate your virtual environment:
     - macOS/Linux: `source venv/bin/activate`
     - Windows: `venv\Scripts\activate.bat`
  2. Verify your terminal shows `(venv)`.
  3. Re-run: `pip install -r requirements.txt`.

---

### Error 3: `OperationalError: no such table: users`
- **Symptom:** Visiting a webpage shows an error that a database table does not exist.
- **Cause:** The SQLite database has not yet been initialized with tables.
- **Solution:** Run the database initialization and seeding commands:
  ```bash
  flask init-db
  flask seed-db
  ```

---

### Error 4: `Error: Password must be at least 8 characters long`
- **Symptom:** During `flask create-admin` or registration, the form rejects the password.
- **Cause:** CraveCart enforces a minimum password length of 8 characters for security.
- **Solution:** Choose a password containing at least 8 characters (e.g., `AdminPass123!`).

---

### Error 5: Windows PowerShell Script Execution Error
- **Symptom:** Running `venv\Scripts\Activate.ps1` gives `Execution of scripts is disabled on this system`.
- **Cause:** Windows PowerShell prevents running downloaded scripts by default.
- **Solution:** Open PowerShell and run:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
  ```
  Then run `venv\Scripts\Activate.ps1` again. Alternatively, use standard Command Prompt (`cmd.exe`) and run `venv\Scripts\activate.bat`.

---

### Error 6: `CSRF session token missing or expired`
- **Symptom:** Submitting a form displays `The CSRF session token is missing` or `Bad Request (400)`.
- **Cause:** Browser cookies might be blocked, or your session timed out.
- **Solution:**
  1. Ensure cookies are enabled in your browser.
  2. Refresh the page to receive a fresh CSRF token.
  3. Ensure your `.env` file has a valid `SECRET_KEY` set.

---

## 11. Quick Reference Cheat Sheet

| Task | Command (macOS / Linux) | Command (Windows) |
|---|---|---|
| **Activate Virtual Environment** | `source venv/bin/activate` | `venv\Scripts\activate.bat` |
| **Install Packages** | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| **Copy Environment Settings** | `cp .env.example .env` | `copy .env.example .env` |
| **Initialize Database Tables** | `flask init-db` | `flask init-db` |
| **Seed Demo Menu & Dishes** | `flask seed-db` | `flask seed-db` |
| **Create Admin User** | `flask create-admin` | `flask create-admin` |
| **Start Application Server** | `python run.py` | `python run.py` |
| **Run All Automated Tests** | `pytest -v` | `pytest -v` |
| **Reset Database (Wipe Clean)** | `flask init-db --drop` | `flask init-db --drop` |
| **Stop Server** | `CTRL + C` | `CTRL + C` |
