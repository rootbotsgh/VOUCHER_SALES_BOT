from flask import Flask, request, jsonify  # Added missing imports
from messageHandler import *  # Assuming this handles your Telegram bot logic
from fastapi import FastAPI, Request
import threading

# Flask app for Paystack webhook
flask_app = Flask(__name__)

@flask_app.route('/paystack/webhook', methods=['POST'])
def paystack_webhook():
    data = request.get_json()  # Get the webhook data

    if data['event'] == 'charge.success':
        # Get payment details
        reference = data['data']['reference']  # The unique reference
        user_id = extract_between_underscores(reference)  # Extract the user_id from the reference
        print(user_id)
        # Your logic for processing cards and transactions
        data = get_cards(user_id, temp[0])
        assign_card(temp[0], user_id, temp[2], temp[1])
        record_transaction(user_id, reference, temp[0])

        # Mark the user as having made a purchase
        mark_purchase_complete(user_id)

        # Check if they were referred and award the referrer
        referrer_id = get_referrer_id(user_id)
        if referrer_id is not None:
            try:
                reward_amount = 0.50  # Example reward
                add_earnings(referrer_id, reward_amount)
                # Notify the referrer
                bot.send_message(referrer_id, f"You've earned a reward of GHS{reward_amount} for referring a user who made a purchase!")
            except Exception as e:
                print(f"Error awarding referrer: {e}")

        bot.send_message(user_id, f"Purchase Complete\n{temp[0]} Card\n{temp[2]}\nSerial: {data[-1]['serial']}\nPIN: {data[-1]['pin']}")
        return jsonify({"status": "success"}), 200

    return jsonify({"status": "ignored"}), 200

def run_flask():
    flask_app.run(host="0.0.0.0")


# FastAPI app for Telegram webhook
fastapi_app = FastAPI()

@fastapi_app.post("/telebot")
async def process_webhook(request: Request):
    try:
        json_str = await request.json()
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
    except Exception as e:
        print(f"Error handling webhook: {e}")
    return {"status": "OK"}

# Start bot
def run_telegram_bot():
    import uvicorn
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)


