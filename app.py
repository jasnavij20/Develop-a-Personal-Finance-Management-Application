import sqlite3
import hashlib
from datetime import datetime

# Create the database and users table
def create_database():
    conn = sqlite3.connect('finance_app.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create transactions table (for income and expenses)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            type TEXT NOT NULL,        -- Income or Expense
            amount REAL NOT NULL,
            category TEXT NOT NULL,    -- E.g., Food, Rent, Salary
            description TEXT,
            date TEXT NOT NULL,        -- Date of transaction
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create budgets table (to store monthly budgets for different categories)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT NOT NULL,
            budget_amount REAL NOT NULL,
            month INTEGER NOT NULL,
            year INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()

# Function to hash passwords for secure storage
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Register a new user
def register_user():
    username = input("Enter a unique username: ")
    password = input("Enter a password: ")
    confirm_password = input("Confirm your password: ")

    if password != confirm_password:
        print("Passwords do not match. Please try again.")
        return

    hashed_password = hash_password(password)

    conn = sqlite3.connect('finance_app.db')
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Username already exists. Please choose a different username.")
    finally:
        conn.close()

# Login user
def login_user():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    hashed_password = hash_password(password)

    conn = sqlite3.connect('finance_app.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = cursor.fetchone()

    conn.close()

    if user:
        print(f"Welcome back, {username}!")
        return user[0]  # Return user_id
    else:
        print("Invalid username or password. Please try again.")
        return None

# Add transaction (Income/Expense)
def add_transaction(user_id):
    transaction_type = input("Enter transaction type (Income/Expense): ").strip().capitalize()
    if transaction_type not in ['Income', 'Expense']:
        print("Invalid transaction type. Please enter 'Income' or 'Expense'.")
        return

    amount = float(input("Enter the amount: "))
    category = input("Enter the category (e.g., Food, Rent, Salary): ").strip()
    description = input("Enter a brief description (optional): ")
    date = input("Enter the date of transaction (YYYY-MM-DD): ")

    conn = sqlite3.connect('finance_app.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO transactions (user_id, type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, transaction_type, amount, category, description, date))

    conn.commit()
    conn.close()
    print("Transaction added successfully!")

# Update transaction
def update_transaction(user_id):
    transaction_id = int(input("Enter the transaction ID to update: "))

    conn = sqlite3.connect('finance_app.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM transactions WHERE id = ? AND user_id = ?', (transaction_id, user_id))
    transaction = cursor.fetchone()

    if not transaction:
        print("Transaction not found or you don't have permission to update it.")
        conn.close()
        return

    # Prompt user for updates
    transaction_type = input(f"Enter new transaction type (Current: {transaction[2]}): ").strip() or transaction[2]
    amount = float(input(f"Enter new amount (Current: {transaction[3]}): ") or transaction[3])
    category = input(f"Enter new category (Current: {transaction[4]}): ").strip() or transaction[4]
    description = input(f"Enter new description (Current: {transaction[5]}): ").strip() or transaction[5]
    date = input(f"Enter new date (Current: {transaction[6]}): ").strip() or transaction[6]

    cursor.execute('''
        UPDATE transactions
        SET type = ?, amount = ?, category = ?, description = ?, date = ?
        WHERE id = ? AND user_id = ?
    ''', (transaction_type, amount, category, description, date, transaction_id, user_id))

    conn.commit()
    conn.close()
    print("Transaction updated successfully!")

# Delete transaction
def delete_transaction(user_id):
    transaction_id = int(input("Enter the transaction ID to delete: "))

    conn = sqlite3.connect('finance_app.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM transactions WHERE id = ? AND user_id = ?', (transaction_id, user_id))
    transaction = cursor.fetchone()

    if not transaction:
        print("Transaction not found or you don't have permission to delete it.")
        conn.close()
        return

    cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', (transaction_id, user_id))
    conn.commit()
    conn.close()
    print("Transaction deleted successfully!")

# View all transactions
def view_transactions(user_id):
    conn = sqlite3.connect('finance_app.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM transactions WHERE user_id = ?', (user_id,))
    transactions = cursor.fetchall()

    conn.close()

    if transactions:
        print("\n--- Your Transactions ---")
        for txn in transactions:
            print(f"ID: {txn[0]}, Type: {txn[2]}, Amount: {txn[3]}, Category: {txn[4]}, Description: {txn[5]}, Date: {txn[6]}")
    else:
        print("No transactions found.")

# Add budget for a category
def set_budget(user_id):
    category = input("Enter the category (e.g., Food, Rent, Salary): ").strip()
    budget_amount = float(input("Enter the monthly budget amount for this category: "))
    current_month = datetime.now().month
    current_year = datetime.now().year

    conn = sqlite3.connect('finance_app.db')
    cursor = conn.cursor()

    # Insert or update the budget for the given category and month
    cursor.execute('''
        INSERT OR REPLACE INTO budgets (user_id, category, budget_amount, month, year)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, category, budget_amount, current_month, current_year))

    conn.commit()
    conn.close()
    print("Budget set successfully!")

# Main application loop
def main():
    create_database()

    while True:
        print("\n--- Personal Finance Management Application ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            register_user()
        elif choice == '2':
            user_id = login_user()
            if user_id:
                while True:
                    print("\n--- Main Menu ---")
                    print("1. Add Transaction")
                    print("2. Update Transaction")
                    print("3. Delete Transaction")
                    print("4. View Transactions")
                    print("5. Set Monthly Budget")
                    print("6. Logout")

                    menu_choice = input("Enter your choice: ")

                    if menu_choice == '1':
                        add_transaction(user_id)
                    elif menu_choice == '2':
                        update_transaction(user_id)
                    elif menu_choice == '3':
                        delete_transaction(user_id)
                    elif menu_choice == '4':
                        view_transactions(user_id)
                    elif menu_choice == '5':
                        set_budget(user_id)
                    elif menu_choice == '6':
                        print("Logged out.")
                        break
                    else:
                        print("Invalid choice. Please try again.")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
