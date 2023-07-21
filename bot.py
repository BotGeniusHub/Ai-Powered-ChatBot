import httpx
from pymongo import MongoClient
import logging
import requests
from pyrogram import filters, Client
from io import BytesIO
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Replace these with your actual values
API_ID = 19099900
API_HASH = "2b445de78e5baf012a0793e60bd4fbf5"
BOT_TOKEN = "6377102011:AAHJJ7AUKZhQKcAnHPQtjg9put5mG8vSjEc"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dictionary to store the conversation history for each user
conversation_history = {}

@app.on_message(filters.command("start"))
async def start_command(_: Client, message: Message):
    # Create the inline keyboard with the help button
    inline_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Help", callback_data="help")]]
    )

    # Send the start message with the inline keyboard
    start_msg = await message.reply(
        "Welcome to MyBot! I am an AI-powered chatbot. Send /help for more information.",
        reply_markup=inline_keyboard
    )

@app.on_callback_query(filters.regex("help"))
async def help_callback(_, callback_query):
    # Answer the callback query to remove the "typing" status
    await callback_query.answer()

    # Get the start message that triggered the callback query
    start_msg = callback_query.message

    # Create the help text
    help_text = (
        "**Usage Guide**\n"
        "1. Use /chat followed by your message to chat with the AI chatbot.\n"
        "2. Use /imagine followed by your text to generate an image based on the text.\n"
    )

    # Send the help text as a new message
    await start_msg.reply(help_text)

    # Delete the start message
    await start_msg.delete()

@app.on_message(filters.command("chat"))
async def gpt(_: Client, message: Message):
    txt = await message.reply("```Typing....```")

    if len(message.command) < 2:
        return await txt.edit("**Please provide a message too.**")

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
            await txt.edit(f"**An HTTP error occurred:``` {str(e)}``` **")
        except Exception as e:
            await txt.edit(f"**An error occurred:``` {str(e)}``` **")

@app.on_message(filters.private)
async def process_dm(client: Client, message: Message):
    # Handle DM messages without a specific command
    txt = await message.reply("```Typing....```")

    query = message.text

    # Retrieve conversation history for this user
    chat_id = message.from_user.id
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
            await txt.edit(f"**An HTTP error occurred:``` {str(e)}``` **")
        except Exception as e:
            await txt.edit(f"**An error occurred:``` {str(e)}``` **")

# Set up logging
logging.basicConfig(level=logging.ERROR)

# Connect to MongoDB
mongo_client = MongoClient("mongodb+srv://sonu55:sonu55@cluster0.vqztrvk.mongodb.net/?retryWrites=true&w=majority")
db = mongo_client["my_bot_db"]
user_collection = db["users"]

@app.on_message(filters.command("broadcast") & filters.private)
async def broadcast_command(_: Client, message: Message):
    try:
        # Check if the user is the bot owner (You can change this based on your needs)
        if message.from_user.id != 6198858059:
            return

        # Get the message to be broadcasted
        broadcast_message = message.text.split(maxsplit=1)[1]

        # Get all users from MongoDB
        all_users = user_collection.find()

        # Broadcast the message to all users
        for user_doc in all_users:
            user_id = user_doc["_id"]
            try:
                await app.send_message(user_id, broadcast_message)
            except Exception as e:
                logging.error(f"Error broadcasting to user {user_id}: {e}")

        await message.reply("Broadcast sent to all users.")
    except Exception as e:
        logging.error(f"Error in broadcast command: {e}")

@app.on_message(filters.command("stats"))
async def stats_command(_: Client, message: Message):
    try:
        # Get the number of users from MongoDB
        num_users = user_collection.count_documents({})

        # Get the number of groups
        all_groups = await app.get_chat_members_count()

        stats_text = f"Number of Users: {num_users}\nNumber of Groups: {all_groups}"

        await message.reply(stats_text)
    except Exception as e:
        logging.error(f"Error in stats command: {e}")

@app.on_message(filters.command("imagine"))
async def imagine_command(_: Client, message: Message):
    await message.reply("Coming soon! I will be able to generate images from your text soon. Stay tuned!")


app.run()
