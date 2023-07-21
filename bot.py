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
    "3. Send /stop to stop the current conversation.\n"
    "4. Use /chat followed by your message to chat with the AI chatbot.\n"
    "5. Use /imagine followed by your text to generate an image based on the text.\n"
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

@app.on_message(filters.command("stop"))
async def stop_command(_: Client, message: Message):
    chat_id = message.from_user.id
    if chat_id in conversation_history:
        del conversation_history[chat_id]
    await message.reply("Conversation stopped. Send /start to begin a new chat.")

# Replace this with your actual API key
DEEPAI_API_KEY = "f12e85a7-0bd7-4641-bc6c-574623677cf7"

@app.on_message(filters.command("imagine"))
async def imagine(_: Client, message: Message):
    txt = await message.reply("**Generating image...**")

    if len(message.command) < 2:
        return await txt.edit("**Please provide a text to generate the image.**")

    text_to_imagine = message.text.split(maxsplit=1)[1]

    try:
        # Call DeepAI API to generate the image
        response = requests.post(
            "https://api.deepai.org/api/text2img",
            data={
                'text': text_to_imagine,
            },
            headers={'api-key': 'f12e85a7-0bd7-4641-bc6c-574623677cf7'}
        )
        response.raise_for_status()
        api_response = response.json()

        if "output_url" in api_response:
            image_url = api_response["output_url"]
            await app.send_photo(
                chat_id=message.chat.id,
                photo=image_url,
                caption=f"**Generated BY:** @{app.me.username}\nCredits: DeepAI"
            )
        else:
            await txt.edit("**An error occurred while generating the image.**")

    except requests.exceptions.RequestException as e:
        await txt.edit(f"**An error occurred: {str(e)}**")

app.run()

            
