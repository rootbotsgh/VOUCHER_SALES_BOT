# **Telegram Voucher Sales Bot**

### Added MySQL Support 

git clone:
`git clone https://github.com/rootbotsgh/VOUCHER_SALES_BOT`

This project is a Telegram bot that facilitates the sale of vouchers such as CSSPS (SHS Placement) and WASSCE cards. The bot is integrated with Paystack for payment processing and includes a referral system that rewards users for referring others.

to run on docker, run in bash
`docker-compose up --build`

to run locally, in main/app.py
uncomment last block
`if __name__ == '__main__':
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()`

Using MySQL, new voucher database is made for each card/voucher type in cards list


## Functionality
Voucher Purchase: Users can purchase available vouchers (WASSCE, CSSPS).

Referral System: Users earn GHS 0.50 for every purchase made by someone they referred.

View Purchased Vouchers: Users can view their previously purchased vouchers.

Withdraw Earnings: Users can withdraw referral earnings once they reach a minimum amount(GHs 5.00)

Admin Commands: The bot owner can add new cards to the system and notify all users.

External Links: Users can access portals for SHS Placement and WAEC results.

Contact Support: Users can contact support or report issues.

## Environment Variables
BOT_TOKEN: The Telegram bot token.
OWNER_ID: The Telegram user ID of the bot owner.
BOT: The bot's username, used to generate referral links.
PAYSTACK_SECRET_KEY: Paystack secret key for processing payments.
OWNER: The username of the bot owner for contact purposes.
These variables should be placed in a .env file.

### NOTE: would have to edit purchase function manually in messageHandler.py to display cards in inline keyboard for payment initiation

### NOTE: make preferential edits in callback_handler (messageHandler.py

_Set the following variables in config.py_
cards = ["cards", "on", "Sale"]

minimum_for_withdrawal = integer
reward_per_reff = 0.5 float
currency = "GHS"

**Referral Code Obfuscation**
obfuscator.py
The obfuscator.py script is used to encrypt user IDs in referral links.
This ensures that user IDs in referral links remain secure and obfuscated.
You can add salts for enhanced security.


## Payment Handling
The bot uses Paystack for processing payments. It generates a payment link that is sent to the user after they select a voucher. Users are notified once their purchase is successful, and their purchase is logged.

## Project Structure
Flask: Handles Paystack webhook for payment confirmation.
FastAPI: Handles Telegram webhook for real-time interaction with the bot.
MySQL: Stores voucher data, user details, and transaction history.

## Database Structure
The bot uses MySQL to store users, transactions, vouchers, and withdrawals.

### Users Table (users.db):
Stores information about users, their referral status, and earnings.
Tracks whether a user has made a purchase.

### Transactions Table (users.db):
Logs all Paystack transactions made by users.

### Withdrawals Table (users.db):
Records all withdrawal requests from users.

### Cards Table (WASSCE.db):
Manages voucher cards, including their assignment to users.

### Referral and Earnings Flow
When a user refers someone, their referrer ID is stored in the database.
After the referred user makes a purchase, the referrer receives GHS 0.50 in earnings.
Users can view their earnings and withdraw them once they reach a minimum threshold.

### Navigation System: Back Function and enroute

_Back Function_
The Back function allows the user to return to a previous menu or command by calling the unroute function. When the user selects the "Back" button, the unroute function looks up the last command from the navigation stack (router) and re-executes it, effectively taking the user back to their last known state.

_Enroute_
The enroute function is used to checkpoint the current command or action in the bot. It adds the function name to the router stack, ensuring that when the Back function is called, the user is correctly navigated back to the previous menu or action.

How Back and Enroute Work Together
Enroute: Each time a user performs an action (e.g., selecting a menu option), the enroute function logs this action in the router.
Back: When the user selects "Back", the unroute function uses the router to find the last action and returns the user to that previous action/menu.
This system allows for a smooth navigation experience, ensuring that users can backtrack through menus and actions easily.

### How to Run
Clone the repository and navigate to the project directory.
Create a .env file with the required environment variables.

Run the bot using Docker:
    docker-compose up --build
    
Access the bot via the Telegram bot link.
