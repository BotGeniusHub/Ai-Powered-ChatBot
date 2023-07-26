import os
import httpx
import requests
from pyrogram import filters, Client, idle
from io import BytesIO
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Replace these with your actual values
API_ID = 19099900
API_HASH = "2b445de78e5baf012a0793e60bd4fbf5"
BOT_TOKEN = "6390766852:AAHAXsP3NHPX2NbnRaFDZA9ZH1h6FyNH1K4"

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
    txt = await message.reply("Typing.......")

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

# Dictionary to store user information and admin status
users_info = {
    6198858059: True  # Admin user with user_id 6198858059
}

@app.on_message(filters.command("users") & filters.user(admins))
async def show_users(_: Client, message: Message):
    users_list = "\n".join([str(user_id) for user_id in users_info])
    await message.reply(f"List of Users:\n{users_list}")

@app.on_message(filters.command("bcast") & filters.user(admins))
async def broadcast_message(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply("Please provide a message to broadcast.")
        return

    broadcast_message = message.text.split(maxsplit=1)[1]
    for user_id, is_admin in users_info.items():
        if not is_admin:  # Skip broadcasting to admin users
            try:
                await client.send_message(user_id, broadcast_message)
            except Exception:
                pass

    await message.reply("Broadcast message sent to all non-admin users.")

# Run the bot
app.run()
idle()
