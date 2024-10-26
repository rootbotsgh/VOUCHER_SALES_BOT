import os
import json
from config import *
from sqliteHandler import *
from telebot import types
from telebot import types  # Assuming you're using pyTelegramBotAPI (TeleBot)

USER_JSON_FILE = 'users.json'

# Function to load user IDs from JSON file
def load_users():
    if os.path.exists(USER_JSON_FILE):
        with open(USER_JSON_FILE, 'r') as f:
            return json.load(f)
    return []

# Function to save user IDs to JSON file
def save_users(user_ids):
    with open(USER_JSON_FILE, 'w') as f:
        json.dump(user_ids, f)



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
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users
            SET earned_money = earned_money - ?
            WHERE telegram_id = ? AND earned_money >= ?
        """, (amount, user_id, amount))  # Ensures the balance is enough
        conn.commit()
        return cursor.rowcount > 0  # Returns True if balance was successfully deducted

# Function to add a withdrawal request
def add_withdrawal_request(user_id, amount):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO withdrawals (user_id, amount)
            VALUES (?, ?)
        """, (user_id, amount))
        conn.commit()
