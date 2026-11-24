# CraveCart – Complete Setup & Installation Guide (SETUP_GUIDE.md)

---

### Prerequisites
Before starting, ensure your system has the following installed:
- **Python**: Version 3.9, 3.10, 3.11, or 3.12 (Verify by typing `python --version` or `python3 --version`).
- **pip**: Python package manager (bundled with standard Python).
- **Git** (optional, for cloning).

---

### Step-by-Step Installation Instructions

#### Step 1: Navigate to Project Directory
Open your terminal or command prompt and change into the project root folder:
```bash
cd "Online food ordering system"
```

---

#### Step 2: Create a Python Virtual Environment
Creating an isolated virtual environment prevents library conflicts with your system packages.

- **On macOS / Linux**:
  ```bash
  python3 -m venv venv
  ```

- **On Windows (Command Prompt or PowerShell)**:
  ```cmd
  python -m venv venv
  ```

---

#### Step 3: Activate the Virtual Environment

- **On macOS / Linux**:
  ```bash
  source venv/bin/activate
  ```

- **On Windows (Command Prompt)**:
  ```cmd
  venv\Scripts\activate.bat
  ```

- **On Windows (PowerShell)**:
  ```powershell
  venv\Scripts\Activate.ps1
  ```
  *(Note: If PowerShell displays an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` first).*

When activated, your terminal prompt will display `(venv)`.

---

#### Step 4: Install Dependencies
Install all required libraries specified in `requirements.txt`:
```bash
pip install -r requirements.txt
```

This installs:
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Object-Relational Mapper
- **Flask-Login**: Session authentication
- **Flask-WTF**: CSRF protection and form validation
- **email-validator**: RFC-compliant email verification
- **python-dotenv**: Environment file loading
- **pytest**: Automated testing suite

---

#### Step 5: Configure Environment Variables
Copy the template configuration file `.env.example` to create `.env`:

- **On macOS / Linux**:
  ```bash
  cp .env.example .env
  ```

- **On Windows (Command Prompt)**:
  ```cmd
  copy .env.example .env
  ```

- **On Windows (PowerShell)**:
  ```powershell
  Copy-Item .env.example .env
  ```

The default values inside `.env` are configured for local development:
```env
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=change-this-to-a-very-secure-random-secret-key-in-production
DATABASE_URL=sqlite:///cravecart.db
```

---

#### Step 6: Initialize Database Schema
Run the custom Flask CLI command to initialize SQLite database tables:
```bash
flask init-db
```
*Output:*
```text
✓ Database tables initialized successfully.
```
This generates the SQLite database file at `instance/cravecart.db`.

---

#### Step 7: Seed Demonstration Menu & Dishes
Populate the database with curated categories and artisanal dishes:
```bash
flask seed-db
```
*Output:*
```text
Seeding demonstration food categories and items...
  + Added category: Starters & Appetizers
  + Added category: Main Course
  + Added category: Artisan Pizzas & Burgers
  + Added category: Desserts & Sweets
  + Added category: Beverages & Mocktails
  + Added dish: Crispy Truffle Fries ($7.50)
  + Added dish: Wild Mushroom Risotto ($14.50)
  ...
✓ Demonstration menu seeding completed successfully.
```

---

#### Step 8: Create an Administrator Account
Create a secure administrator login using the interactive command:
```bash
flask create-admin
```

Follow the prompts:
```text
--- CraveCart: Create Administrator Account ---
Administrator Name: Chef Manager
Administrator Email: admin@cravecart.com
Administrator Password: [Type a password with >= 8 characters]
Repeat for confirmation: [Retype password]
✓ Administrator account 'admin@cravecart.com' created successfully.
```
*(Note: Passwords are not hardcoded and are securely hashed using PBKDF2-SHA256).*

---

#### Step 9: Launch the Application
Start the Flask development server:
```bash
python run.py
```
*(Or alternatively: `flask run`)*

*Output:*
```text
 * Serving Flask app 'run.py'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

#### Step 10: Run the Automated Test Suite
To verify that all 36 automated unit, integration, and E2E tests pass on your machine:
```bash
pytest -v
```
*Expected Output:*
```text
============================= test session starts ==============================
collected 36 items

tests/test_admin.py (7 tests) PASSED
tests/test_auth_and_browsing.py (10 tests) PASSED
tests/test_cart_and_orders.py (7 tests) PASSED
tests/test_cli_and_routes.py (5 tests) PASSED
tests/test_e2e_journey.py (1 comprehensive E2E test) PASSED
tests/test_models.py (6 tests) PASSED

============================= 36 passed in 18.38s ==============================
```

---

### Troubleshooting Common Issues

1. **Port 5000 is already in use (macOS AirPlay)**:
   - On macOS Monterey/Ventura/Sonoma, port 5000 is occasionally reserved by "AirPlay Receiver".
   - *Fix Option A*: Turn off AirPlay Receiver in `System Settings -> General -> AirDrop & AirPlay`.
   - *Fix Option B*: Run the server on another port:
     ```bash
     flask run --port 5001
     ```
     Then open `http://127.0.0.1:5001`.

2. **Database Locked / Access Denied**:
   - Ensure you have write permissions to the `instance/` folder.
   - If resetting the database is necessary, run `flask init-db --drop` and re-seed using `flask seed-db`.

3. **ModuleNotFoundError on Windows**:
   - Ensure the virtual environment is activated (`venv\Scripts\activate.bat`).
   - Run `pip install -r requirements.txt` again while the virtual environment is active.
