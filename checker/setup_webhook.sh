#!/bin/bash

# Replace these with your actual values
BOT_TOKEN="YOUR_BOT_TOKEN"
NGROK_AUTHTOKEN="YOUR_NGROK_AUTH_TOKEN"

# Install ngrok
wget https://bin.equinox.io/c/111111/ngrok-stable-linux-amd64.zip
unzip ngrok-stable-linux-amd64.zip
sudo mv ngrok /usr/local/bin
ngrok authtoken $NGROK_AUTHTOKEN

# Start ngrok in the background forwarding both Flask and FastAPI ports
ngrok http 5000 &   # For Flask
ngrok http 8000 &   # For FastAPI

# Wait for ngrok to establish connections and get the public URLs
sleep 5

# Get the ngrok public URLs
FLASK_NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')
FASTAPI_NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[1].public_url')

# Set the webhook for the Telegram bot to the FastAPI URL
curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook?url=$FASTAPI_NGROK_URL/telebot"

echo "Flask is accessible at $FLASK_NGROK_URL"
echo "FastAPI webhook set to $FASTAPI_NGROK_URL/telebot"
