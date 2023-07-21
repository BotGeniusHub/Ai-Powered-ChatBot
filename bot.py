import httpx
import requests
from pyrogram import filters, Client
from pyrogram.types import Message
from io import BytesIO

# Replace these with your actual values
API_ID = 19099900
API_HASH = "2b445de78e5baf012a0793e60bd4fbf5"
BOT_TOKEN = "6377102011:AAHJJ7AUKZhQKcAnHPQtjg9put5mG8vSjEc"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dictionary to store the conversation history for each user
conversation_history = {}

# Help menu text
help_text = (
    "**Usage Guide**\n"
    "1. Send /start to begin the chatbot.\n"
    "2. Send /help to display this help menu.\n"
    "3. Use /chat followed by your message to chat with the AI chatbot.\n"
    "4. Use /imagine followed by your text to generate an image based on the text.\n"
)

@app.on_message(filters.command("start"))
async def start_command(_: Client, message: Message):
    await message.reply("Welcome to MyBot! I am an AI-powered chatbot. Send /help for more information.")

@app.on_message(filters.command("help"))
async def help_command(_: Client, message: Message):
    await message.reply(help_text)

@app.on_message(filters.command("chat"))
async def gpt(_: Client, message: Message):
    txt = await message.reply("**writing....**")

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
            await txt.edit(f"**An HTTP error occurred: {str(e)}**")
        except Exception as e:
            await txt.edit(f"**An error occurred: {str(e)}**")

@app.on_message(filters.private)
async def process_dm(client: Client, message: Message):
    # Handle DM messages without a specific command
    txt = await message.reply("**writing....**")

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
            await txt.edit(f"**An HTTP error occurred: {str(e)}**")
        except Exception as e:
            await txt.edit(f"**An error occurred: {str(e)}**")

@app.on_message(~filters.command("chat") & filters.private)
async def process_dm(client: Client, message: Message):
    # Respond to DM messages without a specific command
    txt = await message.reply("No need to use this command in private chat. You can send massage me direct")

IMAGGA_API_KEY = "acc_9047984d96000f6"
IMAGGA_API_SECRET = "b40fb74f55c2f21e2f0e25cb0c67070c"

@app.on_message(filters.command(["caption", "cap"]))
async def image_captioning_command(_, message: Message):
    # Check if the command is replying to a photo message
    if message.reply_to_message and message.reply_to_message.photo:
        txt = await message.reply("**Generating caption...**")

        # Get the file ID of the largest image
        file_id = message.reply_to_message.photo[-1].file_id

        # Download the image using the file ID
        file_path = await app.download_media(file_id)

        # Perform image captioning using Imagga API
        url = "https://api.imagga.com/v2/tags"
        headers = {
            "Authorization": f"Basic {IMAGGA_API_KEY}:{IMAGGA_API_SECRET}"
        }
        with open(file_path, "rb") as image_file:
            image_data = image_file.read()

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, files={"image": image_data}, headers=headers)
                response.raise_for_status()
                tags = response.json()["result"]["tags"]
                caption = ", ".join(tag["tag"]["en"] for tag in tags)

                await txt.edit(f"**Caption:** {caption}")
            except httpx.HTTPError as e:
                await txt.edit(f"**An HTTP error occurred: {str(e)}**")
            except Exception as e:
                await txt.edit(f"**An error occurred: {str(e)}**")

        # Remove the downloaded image after processing
        import os
        os.remove(file_path)

        # Reply with the captioned photo
        await message.reply_photo(file_path, caption=f"**Caption:** {caption}")
    else:
        await message.reply("Please use this command by replying to a photo message.")


@app.on_message(filters.command("imagine"))
async def imagine_command(_: Client, message: Message):
    await message.reply("Coming soon! I will be able to generate images from your text soon. Stay tuned!")


app.run()

            
