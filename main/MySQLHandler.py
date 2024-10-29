import mysql.connector
from config import cards, db_config

# Function to create connection to MySQL database
def create_connection():
    return mysql.connector.connect(**db_config)

# Loop over cards and create card-specific tables
for card in cards:
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {card}_cards (
        id INT PRIMARY KEY AUTO_INCREMENT,
        serial VARCHAR(255),
        pin VARCHAR(255),
        user_id INT,  -- NULL or 0 means the card is unassigned
        tag_name VARCHAR(255),
        email VARCHAR(255)
    )
    """)
    conn.commit()
    conn.close()

# Create users and other related tables
conn = create_connection()
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    telegram_id BIGINT UNIQUE,
    referrer_id INT,
    has_made_purchase BOOLEAN DEFAULT 0,
    earned_money DECIMAL(10, 2) DEFAULT 0.00
)''')

# Create transactions table
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,  
    transaction_id VARCHAR(255), 
    type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Create withdrawals table
cursor.execute('''
CREATE TABLE IF NOT EXISTS withdrawals (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    amount DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'pending',  -- Status could be 'pending', 'approved', 'rejected'
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()


def assign_card(db_name, user_id, tag_name, email):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Start a transaction
        conn.start_transaction()

        # Select the first unassigned card (where user_id is NULL or 0)
        cursor.execute("""
            SELECT id FROM {}_cards
            WHERE user_id IS NULL OR user_id = 0
            LIMIT 1
        """.format(db_name))  # Use {}_cards to dynamically refer to the table
        unassigned_card = cursor.fetchone()

        if unassigned_card:
            card_id = unassigned_card[0]

            # Assign the card (update the user_id, tag_name, and email)
            cursor.execute("""
                UPDATE {}_cards
                SET user_id = %s, tag_name = %s, email = %s
                WHERE id = %s
            """.format(db_name), (user_id, tag_name, email, card_id))

            # Commit the changes to make sure the assignment is saved
            conn.commit()

            print(f"Card assigned successfully: {card_id}")
            return card_id
        else:
            print("No unassigned cards available.")
            return None
    except mysql.connector.Error as e:
        # Rollback in case of an error
        conn.rollback()
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.close()


def get_cards(user_id, db_name):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT serial, pin, tag_name, email FROM {}_cards WHERE user_id = %s'.format(db_name), (user_id,))
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
    finally:
        conn.close()


# Mark a purchase as complete for a user
def mark_purchase_complete(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET has_made_purchase = 1
        WHERE telegram_id = %s
    """, (user_id,))
    conn.commit()
    conn.close()

# Add earnings to a referrer's account
def add_earnings(referrer_id, amount):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET earned_money = earned_money + %s
        WHERE telegram_id = %s
    """, (amount, referrer_id))
    conn.commit()
    conn.close()

# Get a user by their Telegram ID
def get_user_by_telegram_id(telegram_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to create a new user
def create_user(telegram_id, referrer_id=None):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (telegram_id, referrer_id)
        VALUES (%s, %s)
    """, (telegram_id, referrer_id))
    conn.commit()
    conn.close()

# Function to record a Paystack transaction
def record_transaction(user_id, transaction_id, type):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, transaction_id, type)
        VALUES (%s, %s, %s)
    """, (user_id, transaction_id, type))
    conn.commit()
    conn.close()

# Function to get the referrer ID of a user
def get_referrer_id(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT referrer_id FROM users WHERE telegram_id = %s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]  # Return the referrer_id if found
    return None  # Return None if the user has no referrer

# Function to add cards to the database
def add_cards(serial_pin_str_list):
    conn = create_connection()
    cursor = conn.cursor()

    # Iterate over each line (each line contains a serial and pin)
    for serial_pin_str in serial_pin_str_list.strip().splitlines():
        # Split the input string into serial and pin
        serial, pin = serial_pin_str.split()

        # Insert the card into the 'cards' table
        cursor.execute("""
        INSERT INTO cards (serial, pin, user_id, tag_name, email) 
        VALUES (%s, %s, NULL, NULL, NULL)
        """, (serial, pin))

    # Commit the transaction after processing all lines
    conn.commit()
    conn.close()

 
