import os
import httpx
import time
import requests
import platform
import pyrogram
import sys
from pyrogram import filters, Client, idle
from io import BytesIO
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Replace these with your actual values
API_ID = 19099900
API_HASH = "2b445de78e5baf012a0793e60bd4fbf5"
BOT_TOKEN = "6206599982:AAENkopxhCmzexPq9pZB_gFZcVpOmDXwiNU"
# List of admin users who can perform sensitive commands
ADMIN = [6198858059]  # Replace with actual user IDs of admins


app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dictionary to store the conversation history for each user
conversation_history = {}

@app.on_message(filters.command("start"))
async def start_command(_: Client, message: Message):
    await message.reply(
        "Welcome! I am an AI-Powered Chatbot. Type /chat followed by your message to chat with me!\nMade With : @BotGeniusHub"
    )

@app.on_message(filters.command("chat"))
async def gpt(_: Client, message: Message):
    txt = await message.reply("💬")

    if len(message.command) < 2:
        return await txt.edit("Please provide a message too.")

    query = message.text.split(maxsplit=1)[1]

    # Retrieve conversation history for this user
    chat_id = message.chat.id
    if chat_id in conversation_history:
        dialog_messages = conversation_history[chat_id]
    else:
        dialog_messages = []

    url = "https://api.safone.me/chatgpt"
    payload = {
        "message": query,
        "chat_mode": "assistant",
        "dialog_messages": dialog_messages,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        try:
            response = await client.post(
                url, json=payload, headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            results = response.json()

            # Check if the API response contains the 'message' key
            if "message" in results:
                bot_response = results["message"]

                # Update conversation history with the latest message
                dialog_messages.append({"bot": bot_response, "user": query})
                conversation_history[chat_id] = dialog_messages

                await txt.edit(bot_response)
            else:
                await txt.edit("**An error occurred. No response received from the API.**")
        except httpx.HTTPError as e:
            await txt.edit(f"**An HTTP error occurred: {str(e)}**")
        except Exception as e:
            await txt.edit(f"**An error occurred: {str(e)}**")


# ... Existing code ...

# Record the bot's start time
start_time = time.time()

@app.on_message(filters.command("ping"))
async def ping_pong(_: Client, message: Message):
    # Calculate the bot's ping
    start = time.time()
    message_text = "Pong!🏓"
    msg = await message.reply(message_text)
    end = time.time()
    ping_duration = (end - start) * 1000  # Convert to milliseconds

    # Calculate bot uptime
    uptime_seconds = int(time.time() - start_time)
    uptime_string = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))

    # Add the ping and uptime information to the reply
    await msg.edit(f"{message_text}\nPing: {ping_duration:.2f} ms\nUptime: {uptime_string}")


@app.on_message(filters.command("info"))
async def info_command(_: Client, message: Message):
    bot_info = (
        "I am an AI-powered Chatbot bot. Created using Python and Pyrogram. \n"
        "Version: 1.0.0\n"
        "Purpose: To provide assistance and chat with users.\n"
        "Creator: @SexyNano"
    )
    await message.reply(bot_info)


@app.on_message(filters.command("alive"))
async def alive_command(_: Client, message: Message):
    owner_username = "SexyNano"  # Replace with the bot owner's username
    python_version = platform.python_version()
    pyrogram_version = pyrogram.__version__

    bot_info = (
        f"🤖 **Bot Info**\n"
        f"**Owner:** [{owner_username}](https://t.me/{owner_username})\n"
        f"**Python Version:** {python_version}\n"
        f"**Pyrogram Version:** {pyrogram_version}\n"
        f"**Running on:** {platform.system()} {platform.release()}\n"
        f"**Uptime:** {get_uptime()}"
    )

    await message.reply_text(bot_info, parse_mode="markdown", disable_web_page_preview=True)

def get_uptime():
    uptime_seconds = int(time.time() - start_time)
    uptime_string = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
    return uptime_string


print("Bot deployed successfully!")  # Add a log message for successful deployment

# Run the bot
app.run()
idle()


