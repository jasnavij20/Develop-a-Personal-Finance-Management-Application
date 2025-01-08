import unittest
import sqlite3
from io import StringIO
import sys


from app import create_database, register_user, login_user, add_transaction, update_transaction, delete_transaction

class TestFinanceApp(unittest.TestCase):

    def setUp(self):
        """Setup a fresh database before each test"""
        create_database()
        conn = sqlite3.connect('finance_app.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users')
        cursor.execute('DELETE FROM transactions')
        conn.commit()
        conn.close()

    def test_register_user(self):
        """Test the user registration functionality"""
        register_user()

        conn = sqlite3.connect('finance_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        conn.close()

        self.assertEqual(len(users), 1, "User should be registered successfully")

    def test_login_user(self):
        """Test the user login functionality"""
        register_user()

        # Test valid login
        user_id = login_user()
        self.assertIsNotNone(user_id, "Login should be successful with correct credentials")

        # Test invalid login
        sys.stdin = StringIO('invalid_user\ninvalid_password\n')  # Mock invalid input
        user_id = login_user()
        self.assertIsNone(user_id, "Login should fail with incorrect credentials")

    def test_add_transaction(self):
        """Test adding a transaction"""
        register_user()
        user_id = login_user()

        add_transaction(user_id)

        conn = sqlite3.connect('finance_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE user_id = ?', (user_id,))
        transactions = cursor.fetchall()
        conn.close()

        self.assertEqual(len(transactions), 1, "Transaction should be added successfully")

    def test_update_transaction(self):
        """Test updating a transaction"""
        register_user()
        user_id = login_user()

        add_transaction(user_id)
        conn = sqlite3.connect('finance_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM transactions WHERE user_id = ?', (user_id,))
        transaction_id = cursor.fetchone()[0]
        conn.close()

        update_transaction(user_id)

        conn = sqlite3.connect('finance_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        transaction = cursor.fetchone()
        conn.close()

        self.assertEqual(transaction[2], 200.0, "Transaction amount should be updated correctly")

    def test_delete_transaction(self):
        """Test deleting a transaction"""
        register_user()
        user_id = login_user()

        add_transaction(user_id)
        conn = sqlite3.connect('finance_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM transactions WHERE user_id = ?', (user_id,))
        transaction_id = cursor.fetchone()[0]
        conn.close()

        delete_transaction(user_id)

        conn = sqlite3.connect('finance_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        transaction = cursor.fetchone()
        conn.close()

        self.assertIsNone(transaction, "Transaction should be deleted successfully")


if __name__ == '__main__':
    unittest.main()
