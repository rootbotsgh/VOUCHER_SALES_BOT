# Token and Configuration
import telebot
from fastapi import FastAPI
from dotenv import load_dotenv
import os 
load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
BOT = os.getenv("BOT")
PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
OWNER = os.getenv('OWNER')
app = FastAPI()
bot = telebot.TeleBot(BOT_TOKEN)

#VOUCHERS ON SALE
cards = ["CSSPS", "WASSCE"]