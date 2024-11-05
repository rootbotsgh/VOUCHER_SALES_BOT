from functions import *
from config import *
from sqliteHandler import *
from obfuscator import *
from paymentHandler import *
from flask import Flask, request, jsonify
import re
import inspect

router = []
temp = []
# Initialize user IDs
user_ids = load_users()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)  # Move user_id definition to the top

    def reff_check(message):
        # Initialize user_ids if not defined
        if 'user_ids' not in globals():
            global user_ids
            user_ids = load_users()  # Load users from your JSON file if needed

        # Check if user is already in the list
        if user_id not in user_ids:
            user_ids.append(user_id)  # Add new user to the list
            save_users(user_ids)  # Save updated list to JSON

            # Check if the count of users is a multiple of 20
            if len(user_ids) % 20 == 0:
                bot.send_message(OWNER_ID, f"A new user has started the bot. Total users: {len(user_ids)}")
        else:
            # User already exists
            pass

        # Check if there's a referral code (start param)
        if len(message.text.split()) > 1:
            referral_code = message.text.split()[1]
            referrer_id = deobfuscate_chat_id(referral_code)
            return referrer_id
        else:
            return None  # Return None if no referral code

    # Check if user exists, if not create a new one
    referrer_id = reff_check(message)  # Get referrer ID
    user = get_user_by_telegram_id(user_id)  # Check if user exists
    if not user:
        create_user(user_id, referrer_id)  # Create new user

    # Send welcome message and main menu
    bot.send_message(user_id, f"Welcome {message.chat.first_name}!\nTo your No.1 Telegram Voucher Shop in Ghana\nNOTE: GES announces that CSSPS (SHS school placement) is free this year!\nNo need for a checker!")
    send_main_menu(user_id)


#Back with message
@bot.message_handler(func=lambda message: message.text == 'Back')
def Back(message):
    unroute(message)

# Inline keyboard to initiate card purchase
@bot.message_handler(func=lambda message: message.text == "Purchase Checker PIN")
def purchase(message):
    user_id = str(message.chat.id)
    # Create inline buttons with callback data
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
def withdr_(message):
    user_id = str(message.chat.id)
    keyboard = list_create_keyboard(['Back'])
    bot.send_message(user_id, 'Enter amount to withdraw', reply_markup=keyboard)
    enroute()
    bot.register_next_step_handler(message, handle_withdrawal)


@bot.message_handler(func=lambda message: message.text == 'Portals')
def portals(message):
    user_id = str(message.chat.id)
    keyboard = list_create_keyboard(['Back'])
    bot.send_message(user_id, 'SHS Placement:  https://cssps.gov.gh/\n\nWASSCE Results:  https://ghana.waecdirect.org/', reply_markup=keyboard)
    enroute()

@bot.message_handler(func=lambda message: message.text == "View Purchased PINs")
def view_pins(message):
    user_id = str(message.chat.id)
    keys = cards
    keys.append('Back')
    keyboard = list_create_keyboard(keys)
    bot.send_message(user_id, 'Please Choose type', reply_markup=keyboard)
    enroute()
    bot.register_next_step_handler(message, collect_cards)

def collect_cards(message):
    user_id = str(message.chat.id)
    txt = message.text
    text = txt.replace(" ", "")
    try:
     cards = get_cards(user_id, text)
     for card in cards:
         card = str(card).replace('{', '').replace('}', '').replace("'",'').replace(',','\n')
         bot.send_message(user_id,text + '\n' + card)
    except:
        bot.send_message(user_id, 'Please use provided Keyboard Buttons in menu')

@bot.message_handler(func=lambda message: message.text == "Referral Benefits")
def reff_benefits(message):
    user_id = str(message.chat.id)
    keyboard = list_create_keyboard(['Referral Link', 'Withdraw', 'Back'])
    bot.send_message(user_id, 'Get GHS0.5 everytime your referree makes a purchase', reply_markup=keyboard)
    enroute()

@bot.message_handler(func=lambda message: message.text == 'Referral Link')
def reff_link(message):
    user_id = str(message.chat.id)
    referral_code = obfuscate_chat_id(user_id)
    referral_link = f"You can share your referral link\n https://t.me/{BOT}?start={referral_code}"
    bot.send_message(user_id, referral_link)

@bot.message_handler(func=lambda message: message.text == "Contact Support /\nReport Issue")
def contact_sp(message):
    user_id = str(message.chat.id)
    bot.send_message(user_id, f'In case of any enquiry / issue\nContact the moderator @ https://t.me/{OWNER}')
    enroute()

@bot.message_handler(func=lambda message: message.text == "Visit our Website")
def our_ws(message):
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


# Callback query handler with improved logic
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
        if not temp or len(temp) > 1:  
            return start(call.message)
        enter_name(call.message)

    # Check cards only after handling other commands
    if db in cards:
        if db == 'CSSPS':
            bot.send_message(call.message.chat.id, "CSSPS is free. Just head to the portal")
            return

        temp.clear()
        temp.append(db)
        handle_email(call.message)

def enter_name(message):
    keyboard = list_create_keyboard(['Back'])
    bot.send_message(message.chat.id, "Please enter Recipient's name or tag", reply_markup=keyboard)
    bot.register_next_step_handler(message, add_tag)
    enroute()

def add_tag(message):
    txt = message.text
    if txt in cards or txt != "Back":
        price = cards_to_price[txt]
        txt = txt.strip()
        temp.append(txt)
        start_payment(message, temp, price, temp[0])

    else:
        keyboard = list_create_keyboard(['Back'])
        bot.send_message(message.chat.id, "Please enter a tag or name", reply_markup=keyboard)
    enroute()


def save_address(message):
    recipient_email = message.text.strip()

    if recipient_email == 'Back':
        return Back(message)

    if '@' not in recipient_email or '.' not in recipient_email:
        bot.send_message(message.chat.id, "Invalid email address format. Please try again.")
        return handle_email(message)
    else:
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton('Confirm', callback_data="confirm")
        button2 = types.InlineKeyboardButton('Back', callback_data="reset")
        temp.append(recipient_email)
        markup.add(button1)
        markup.add(button2)
        bot.send_message(message.chat.id, f"Are you sure {recipient_email} is your email", keyboard = markup)


def handle_email(message):
    keyboard = list_create_keyboard(['Back'])
    bot.send_message(message.chat.id, "Please enter your email address:", reply_markup=keyboard)
    bot.register_next_step_handler(message, save_address)
    enroute()


def unroute(message):
    # Use globals() to get the function by its name
    try:
        if len(router) == 0:
            globals()['start'](message)  # If no previous route, go to start
        else:
            router.pop()  # Remove the last route from the stack
            if len(router) > 0:
                globals()[router[-1]](message)  # Go to the previous route
            else:
                globals()['start'](message)
    except Exception as e:
        print(f"Error in unroute: {e}")
        globals()['start'](message)


def enroute():
    # Get the current call stack and return the name of the caller
    func = inspect.stack()[1].function
    if len(router) != 0 and func == router[-1]:
        return
    router.append(func)


# ADMIN KEYS

@bot.message_handler(commands=['stock'])
def bulk_message(message):
    # Check if the sender is the owner
    if message.from_user.id == OWNER_ID:
        # Extract the message after the command
        message_text = message.text[len('/stock '):]
        
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
