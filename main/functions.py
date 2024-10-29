import os
import json
from config import *
from MySQLHandler import *
from telebot import types
from telebot import types  

# Assuming you're using pyTelegramBotAPI (TeleBot)
# Function to load user IDs from the MySQL `users` table
def load_users():
    conn = create_connection()
    cursor = conn.cursor()
    
    # Select all user IDs from the users table
    cursor.execute("SELECT telegram_id FROM users")
    user_ids = [row[0] for row in cursor.fetchall()]  # Fetch all user IDs
    
    conn.close()
    return user_ids

# Function to save user IDs to the MySQL `users` table
# This assumes that you're inserting new users
def save_users(user_ids):
    conn = create_connection()
    cursor = conn.cursor()

    # Insert user IDs into the users table (you can adapt this based on your logic)
    for user_id in user_ids:
        cursor.execute("""
            INSERT INTO users (telegram_id) 
            VALUES (%s)
            ON DUPLICATE KEY UPDATE telegram_id = telegram_id
        """, (user_id,))

    conn.commit()
    conn.close()
    


def list_create_keyboard(options):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)  # Set row width to 2 for pairs of buttons
    buttons = []

    # Iterate through the options and create buttons
    for option in options:
        button = types.KeyboardButton(option)
        buttons.append(button)

    # Add buttons to the keyboard in pairs
    for i in range(0, len(buttons) - len(buttons) % 2, 2):
        keyboard.add(buttons[i], buttons[i + 1])  # Add pairs of buttons

    # If the number of buttons is odd, add the last one alone
    if len(buttons) % 2 != 0:
        keyboard.add(buttons[-1])

    return keyboard

def send_main_menu(user_id):
    keyboard = list_create_keyboard(["Purchase Checker PIN","View Purchased PINs","Portals", "Referral Benefits", "Visit our Website", "Contact Support /\nReport Issue"])
    bot.send_message(user_id, "Welcome! Please choose an option:",parse_mode="Markdown", reply_markup=keyboard)

def extract_between_underscores(text):
    # Find the index of the first underscore
    first_underscore = text.find('_')
    
    # Find the index of the second underscore, starting after the first one
    second_underscore = text.find('_', first_underscore + 1)
    
    # If both underscores are found, extract the substring between them
    if first_underscore != -1 and second_underscore != -1:
        return text[first_underscore + 1:second_underscore]
    else:
        return None  
    

# Function to deduct balance from a user
def deduct_balance(user_id, amount):
    conn = create_connection()
    cursor = conn.cursor()

    # Ensure sufficient balance before deducting
    cursor.execute("""
        UPDATE users
        SET earned_money = earned_money - %s
        WHERE telegram_id = %s AND earned_money >= %s
    """, (amount, user_id, amount))
    
    conn.commit()
    success = cursor.rowcount > 0  # Check if a row was updated (successful deduction)
    conn.close()
    return success

# Function to add a withdrawal request
def add_withdrawal_request(user_id, amount):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO withdrawals (user_id, amount)
        VALUES (%s, %s)
    """, (user_id, amount))

    conn.commit()
    conn.close()
    
