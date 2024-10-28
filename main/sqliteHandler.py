import sqlite3
from config import cards

for card in cards:
    with sqlite3.connect(f"{card}.db") as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serial TEXT,
            pin TEXT,
            user_id INTEGER,  -- NULL or 0 means the card is unassigned
            tag_name TEXT,
            email TEXT
            )
        """)
        conn.commit()
        
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    referrer_id INTEGER,
    has_made_purchase BOOLEAN DEFAULT 0,
    earned_money DECIMAL(10, 2) DEFAULT 0.00
)''')
#To store completed transactions via Paystack
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,  
    transaction_id TEXT, 
    type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS withdrawals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount DECIMAL(10, 2),
    status TEXT DEFAULT 'pending',  -- Status could be 'pending', 'approved', 'rejected'
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()


def assign_card(db_name, user_id, tag_name, email):
    try:
        with sqlite3.connect(f'{db_name}.db') as conn:
            cursor = conn.cursor()

            # Start a transaction
            conn.execute('BEGIN TRANSACTION')

            # Select the first unassigned card (where user_id is NULL or 0)
            cursor.execute("""
                SELECT id FROM cards
                WHERE user_id IS NULL OR user_id = 0
                LIMIT 1
            """)
            unassigned_card = cursor.fetchone()

            if unassigned_card:
                card_id = unassigned_card[0]

                # Assign the card (update the user_id, tag_name, and email)
                cursor.execute("""
                    UPDATE cards
                    SET user_id = ?, tag_name = ?, email = ?
                    WHERE id = ?
                """, (user_id, tag_name, email, card_id))

                # Commit the changes to make sure the assignment is saved
                conn.commit()

                print(f"Card assigned successfully: {card_id}")
                return card_id
            else:
                print("No unassigned cards available.")
                return None
    except sqlite3.Error as e:
        # Rollback in case of an error
        conn.rollback()
        print(f"An error occurred: {e}")
        return None


def get_cards(user_id, db_name):
    with sqlite3.connect(f'{db_name}.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT serial, pin, tag_name, email FROM cards WHERE user_id = ?', (user_id,))
        users = cursor.fetchall()  # Fetch all rows matching the user_id

        if users:
            # Return a list of dictionaries for each row
            return [
                {
                    "serial": user[0],
                    "pin": user[1],
                    "tag_name": user[2],
                    "email": user[3],
                }
                for user in users
            ]
        else:
            return None  # Return None if no records were found


def mark_purchase_complete(user_id):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET has_made_purchase = 1
            WHERE telegram_id = ?
        """, (user_id,))
        conn.commit()

def add_earnings(referrer_id, amount):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET earned_money = earned_money + ?
            WHERE telegram_id = ?
        """, (amount, referrer_id))
        conn.commit()

def get_user_by_telegram_id(telegram_id):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        return cursor.fetchone()

# Function to create a new user
def create_user(telegram_id, referrer_id=None):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (telegram_id, referrer_id)
            VALUES (?, ?)
        """, (telegram_id, referrer_id))
        conn.commit()


# Function to record a Paystack transaction
def record_transaction(user_id, transaction_id, type):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, transaction_id, type)
            VALUES (?, ?, ?)
        """, (user_id, transaction_id, type))
        conn.commit()

# Function to get the referrer ID of a user
def get_referrer_id(user_id):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT referrer_id FROM users WHERE telegram_id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return the referrer_id if found
        return None  # Return None if the user has no referrer


import sqlite3

def add_cards(serial_pin_str_list):
    # Connect to the SQLite database
    with sqlite3.connect("WASSCE.db") as conn:
        cursor = conn.cursor()

        # Iterate over each line (each line contains a serial and pin)
        for serial_pin_str in serial_pin_str_list.strip().splitlines():
            # Split the input string into serial and pin
            serial, pin = serial_pin_str.split()

            # Insert the card into the 'cards' table
            cursor.execute("""
            INSERT INTO cards (serial, pin, user_id, tag_name, email) 
            VALUES (?, ?, NULL, NULL, NULL)
            """, (serial, pin))

        # Commit the transaction after processing all lines
        conn.commit()

    
 
