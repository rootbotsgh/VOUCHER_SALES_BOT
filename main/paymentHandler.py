import requests
from sqliteHandler import sqlite3
import uuid
from config import bot, PAYSTACK_SECRET_KEY, OWNER_ID, currency

#PAYSTACK FOR PAYMENTS

# Function to generate Paystack payment link
def generate_paystack_payment_link(amount, email, user_id):
    random_uuid = uuid.uuid4().hex  # Generates a random 32-character hex string
    url = "https://api.paystack.co/transaction/initialize"
    
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "amount": amount * 100,
        "reference": f"txn_{user_id}_{random_uuid}",  # Paystack expects amounts in kobo (Naira) or pesewas (Ghana)
        "currency": currency  # Change to "GHS" if you are in Ghana
    }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    if response_data['status']:
        return response_data['data']['authorization_url']
    else:
        print(f"Error generating payment link: {response_data['message']}")
        return None

# Command to start payment
def start_payment(message, temp, price, card):
    chat_id = message.chat.id
    user_email = temp[1] # You should gather this from the user dynamically
    amount = price  # Amount in Naira (₦1000), change to any amount you want
    
    # Generate Paystack payment link
    unassigned_cards = check_unassigned_cards(amount, card)
    if unassigned_cards:
        print("Unassigned cards found:")

        payment_url = generate_paystack_payment_link(amount, user_email, chat_id)

        if payment_url:
            # Send the payment link to the user
            bot.send_message(chat_id, f"Click the link to make payment: {payment_url}")
        else:
            bot.send_message(chat_id, "There was an error generating the payment link.")
    else:
        db = card
        bot.send_message(chat_id, f"Currently out of {db} voucher stock\nWe apologise for the inconvenience")
        bot.send_message(OWNER_ID, f"OUT OF {db} VOUCHER STOCK" )

# Assuming `cursor` is your SQLite cursor and `connection` is your SQLite connection

def check_unassigned_cards(amount, card):
    db = card
    with sqlite3.connect(f'{db}.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM cards
            WHERE user_id IS NULL OR user_id = 0
        """)

        unassigned_cards = cursor.fetchnone()
        return unassigned_cards

# Usage


