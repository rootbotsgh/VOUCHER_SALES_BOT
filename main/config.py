# Token and Configuration
import telebot
from fastapi import FastAPI
from dotenv import load_dotenv
import os 
load_dotenv()

# MySQL database connection details
db_config = {
    'host': '',
    'user': '',
    'password': '',
    'database': '',
    'port': 3306
}

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
BOT = os.getenv("BOT")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
OWNER = os.getenv('OWNER')
app = FastAPI()
bot = telebot.TeleBot(BOT_TOKEN)

#VOUCHERS ON SALE
cards = ["CSSPS", "WASSCE"]
cards_to_price = {'CSSPS': 12, 'WASSCE':19}
minimum_for_withdrawal = 5
reward_per_reff = 0.5
currency = "GHS"
