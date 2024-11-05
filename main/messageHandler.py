import telebot
from functions import *
from config import *
from MySQLHandler import *
from obfuscator import *
from paymentHandler import *
from flask import Flask, request, jsonify
import re
import inspect
from telebot import types

# Initialize bot with your token (assumed to be defined elsewhere)
bot = telebot.TeleBot(BOT_TOKEN)

router = []
temp = []
# Initialize user IDs
user_ids = load_users()

# Command Handlers
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)

    def reff_check(message):
        if 'user_ids' not in globals():
            global user_ids
            user_ids = load_users()

        if user_id not in user_ids:
            user_ids.append(user_id)
            save_users(user_ids)

            if len(user_ids) % 20 == 0:
                bot.send_message(OWNER_ID, f"A new user has started the bot. Total users: {len(user_ids)}")
        else:
            pass

        if len(message.text.split()) > 1:
            referral_code = message.text.split()[1]
            referrer_id = deobfuscate_chat_id(referral_code)
            return referrer_id
        else:
            return None

    referrer_id = reff_check(message)
    user = get_user_by_telegram_id(user_id)
    if not user:
        create_user(user_id, referrer_id)

    bot.send_message(user_id, f"Welcome {message.chat.first_name}!\nTo your No.1 Telegram Voucher Shop in Ghana\nNOTE: GES announces that CSSPS (SHS school placement) is free this year!\nNo need for a checker!")
    send_main_menu(user_id)

# Back with message
@bot.message_handler(func=lambda message: message.text == 'Back')
def Back(message):
    unroute(message)

# Inline keyboard to initiate card purchase
@bot.message_handler(func=lambda message: message.text == "Purchase Checker PIN")
def purchase(message):
    user_id = str(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('CSSPS (SHS Placement)\nIS FREE', callback_data=cards[0])
    button2 = types.InlineKeyboardButton('WASSCE\nGHS19.00', callback_data=cards[1])
    button3 = types.InlineKeyboardButton('Back', callback_data="Back")

    markup.add(button1)
    markup.add(button2)
    markup.add(button3)
    
    bot.send_message(user_id, "Kindly choose your PIN purchase type", reply_markup=markup)
    enroute()

@bot.message_handler(func=lambda message: message.text == 'Withdraw')
def function(message):
    user_id = str(message.chat.id)
    keyboard = list_create_keyboard(['Back'])
    bot.send_message(user_id, 'Enter amount to withdraw', reply_markup=keyboard)
    enroute()
    bot.register_next_step_handler(message, handle_withdrawal)

@bot.message_handler(func=lambda message: message.text == 'Portals')
def request_withdraw(message):
    user_id = str(message.chat.id)
    keyboard = list_create_keyboard(['Back'])
    bot.send_message(user_id, 'SHS Placement:  https://cssps.gov.gh/\n\nWASSCE Results:  https://ghana.waecdirect.org/', reply_markup=keyboard)
    enroute()

@bot.message_handler(func=lambda message: message.text == "View Purchased PINs")
def request_withdraw(message):
    user_id = str(message.chat.id)
    keys = cards.copy()
    keys.append('Back')
    keyboard = list_create_keyboard(keys)
    bot.send_message(user_id, 'Please Choose type', reply_markup=keyboard)
    enroute()
    bot.register_next_step_handler(message, collect_cards)

def collect_cards(message):
    user_id = str(message.chat.id)
    txt = message.text.strip()

    # Check if the text is valid
    if txt not in cards and txt != "Back":
        unroute(message)
        return

    try:
        # Get cards associated with the user ID and input text
        user_cards = get_cards(user_id, txt)
        if not user_cards:
            return bot.send_message(user_id, 'No purchase made.')

        # Send formatted card details to the user
        for card in user_cards:
            formatted_card = "\n".join([f"{k}: {v}" for k, v in card.items()])
            bot.send_message(user_id, f"{txt}\n{formatted_card}")

    except Exception as e:  # Catch specific exceptions if needed
        bot.send_message(user_id, 'An error occurred. Please use the provided Keyboard Buttons in the menu.')
        print(f"Error in collect_cards: {e}")  # Log the error for debugging

@bot.message_handler(func=lambda message: message.text == "Referral Benefits")
def request_withdraw(message):
    user_id = str(message.chat.id)
    keyboard = list_create_keyboard(['Referral Link', 'Withdraw', 'Back'])
    bot.send_message(user_id, 'Get GHS0.5 every time your referee makes a purchase', reply_markup=keyboard)
    enroute()

@bot.message_handler(func=lambda message: message.text == 'Referral Link')
def request_withdraw(message):
    user_id = str(message.chat.id)
    referral_code = obfuscate_chat_id(user_id)
    referral_link = f"You can share your referral link\n https://t.me/{BOT}?start={referral_code}"
    bot.send_message(user_id, referral_link)

@bot.message_handler(func=lambda message: message.text == "Contact Support /\nReport Issue")
def request_withdraw(message):
    user_id = str(message.chat.id)
    bot.send_message(user_id, f'In case of any enquiry / issue\nContact the moderator @ https://t.me/{OWNER}')
    enroute()

@bot.message_handler(func=lambda message: message.text == "Visit our Website")
def request_withdraw(message):
    user_id = str(message.chat.id)
    bot.send_message(user_id, 'Click on this <a href="https://rootbotsgh.github.io/">link here</a>\n to be redirected to our website \nOR\n https://rootbotsgh.github.io/ ', parse_mode='HTML')
    enroute()

def handle_withdrawal(message):
    user_id = str(message.chat.id)
    if message.text == 'Back':
        Back(message)
        return
    try:
        amount = float(message.text)
        if amount < minimum_for_withdrawal:
            bot.reply_to(message, "Withdrawal amounts must be at least GHS5.0")
            return

        if deduct_balance(user_id, amount):
            add_withdrawal_request(user_id, amount)
            bot.reply_to(message, f"Your withdrawal request of GHS{amount} has been submitted.")
            bot.send_message(OWNER_ID, f"User {message.chat.first_name} has requested a withdrawal of GHS {amount}.")
        else:
            bot.reply_to(message, "You don't have enough balance to withdraw that amount.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Please specify a valid amount, e.g., 50.")

# Callback query handler
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    db = call.data  # Get the callback data

    # Handle 'Back' first to avoid other matches
    if db == "Back":
        Back(call.message)  # Call the Back function
        return

    elif db == "reset":
        Back(call.message)
        if temp:
            temp.pop()  # Remove last item from temp
        return

    elif db == "confirm":
        
        # Ensure that temp has exactly one item, meaning the email was entered
        if len(temp) == 2:
            # Proceed to enter the name or tag
            enter_name(call.message)
        else:
            start(call.message)  # Start over if the condition isn't met
        return

    # Handle card selection after handling other commands
    if db in cards:
        if db == 'CSSPS':
            bot.send_message(call.message.chat.id, "CSSPS is free. Just head to the portal")
            return

        temp.clear()
        temp.append(db)  # Add selected card type to temp
        handle_email(call.message)  # Proceed to email input

def enter_name(message):
    keyboard = list_create_keyboard(['Back'])
    bot.send_message(message.chat.id, "Please enter Recipients name or tag", reply_markup=keyboard)
    bot.register_next_step_handler(message, add_tag)
    enroute()

def add_tag(message):
    txt = temp[0]
    if txt != "Back":
        price = cards_to_price[txt]
        temp.append(txt)
        start_payment(message, temp, price, temp[0])
    else:
        keyboard = list_create_keyboard(['Back'])
        bot.send_message(message.chat.id, "Please enter tag or name", reply_markup=keyboard)
    

def save_address(message):
    recipient_email = message.text.strip()

    # Handle 'Back' action
    if recipient_email.lower() == 'back':
        return Back(message)

    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", recipient_email):
        bot.send_message(message.chat.id, "Invalid email address format. Please try again.")
        return handle_email(message)
    
    # Create confirmation buttons
    markup = types.InlineKeyboardMarkup()
    confirm_button = types.InlineKeyboardButton('Confirm', callback_data="confirm")
    back_button = types.InlineKeyboardButton('Back', callback_data="reset")
    
    # Store the email and ask for confirmation
    temp.append(recipient_email)
    markup.add(confirm_button, back_button)
    bot.send_message(message.chat.id, f"Are you sure {recipient_email} is your email address?", reply_markup=markup)

def handle_email(message):
    keyboard = list_create_keyboard(['Back'])
    bot.send_message(message.chat.id, "Please enter your email address:", reply_markup=keyboard)
    bot.register_next_step_handler(message, save_address)
    enroute()


def unroute(message):
    # Navigate back to the previous function in the router stack
    try:
        if len(router) == 0:
            globals()['start'](message)
        else:
            router.pop()
            if router:
                globals()[router[-1]](message)
            else:
                globals()['start'](message)
    except Exception as e:
        bot.send_message(message.chat.id, "An error occurred, please try again later.")
        print(f"Error in unroute: {e}")

def enroute():
    # Add the calling function's name to the router stack if it's not already the last entry
    func = inspect.stack()[1].function
    if not router or router[-1] != func:
        router.append(func)

# ADMIN KEYS
@bot.message_handler(commands=['stock'])
def handle_stock(message):
    # Check if the sender is the owner
    if message.from_user.id == int(OWNER_ID):  # Convert OWNER_ID to integer for comparison
        # Extract the message after the command
        message_text = message.text[len('/stock '):].strip()
        
        # Send the message to all users
        for user_id in user_ids:
            try:
                bot.send_message(user_id, message_text)
            except Exception as e:
                print(f"Failed to send message to {user_id}: {e}")
        
        bot.reply_to(message, "Message sent to all users.")
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

# Command handler for /addcards
@bot.message_handler(commands=['addcards'])
def add_cards_command(message):
    # Check if the user is the owner
    if message.chat.id != int(OWNER_ID):  # Convert OWNER_ID to integer for comparison
        bot.reply_to(message, "Unauthorized access. Only the bot owner can use this command.")
        return

    # Get the message text without the command
    serial_pin_type = message.text[len("/addcards "):].strip()
    temp.clear()
    temp.append(serial_pin_type)
    bot.send_message(message, """Enter card seials and pin in the order
    qrkfkff difkg
    didfkkk rogkg
    (separated by newlines)""")
    bot.register_next_step_handler(message, serial_pin)

    if not serial_pin_str_list:
        bot.reply_to(message, "Please provide a list of serial and pin pairs separated by newlines.")
        return


def serial_pin(message):  
    txt = message.text.strip()
    try:
        # Call the function to add the cards to the database
        add_cards(txt, temp[0])
        bot.reply_to(message, f"{temp[0]} cards added successfully.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")
        
        
'''/addcards Card_name
then
123456789 ABCDEFGHIJKL
987654321 MNOPQRSTUV
555555555 ZYXWVUTSRQ
'''
