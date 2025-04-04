import os
import asyncio
from pyrogram import Client, filters
from pymongo import MongoClient

# ✅ Load from Environment Variables
MONGO_URL = os.getenv("MONGO_URL")
BOT_TOKENS = os.getenv("BOT_TOKENS", "").split(",")

# ✅ MongoDB Setup
client = MongoClient(MONGO_URL)
db = client["TelegramBots"]
users_collection = db["users"]

# ✅ Store all clients
bots = []

# ✅ /start Handler
async def start_handler(client, message):
    user_id = message.from_user.id
    bot_username = (await client.get_me()).username

    # Save user if not exists
    if not users_collection.find_one({"user_id": user_id, "bot_username": bot_username}):
        users_collection.insert_one({"user_id": user_id, "bot_username": bot_username})

    await message.reply_text(f"👋 Hello {message.from_user.first_name}, this is @{bot_username}!")

# ✅ /broadcast Handler
async def broadcast_handler(client, message):
    admin_id = int(os.getenv("ADMIN_ID", "123456789"))  # Replace with your Telegram ID

    if message.from_user.id != admin_id:
        return await message.reply("🚫 Not Authorized")

    bot_username = (await client.get_me()).username
    users = users_collection.find({"bot_username": bot_username})
    text = message.text.replace("/broadcast ", "")
    sent = 0

    for user in users:
        try:
            await client.send_message(user["user_id"], text)
            sent += 1
        except:
            pass

    await message.reply(f"✅ Message sent to {sent} users.")

# ✅ Function to Start Each Bot
async def start_bot(token):
    bot = Client(name=token[:10], bot_token=token)
    
    @bot.on_message(filters.command("start"))
    async def start(client, message):
        await start_handler(client, message)

    @bot.on_message(filters.command("broadcast"))
    async def broadcast(client, message):
        await broadcast_handler(client, message)

    await bot.start()
    me = await bot.get_me()
    print(f"✅ Bot started: @{me.username}")
    bots.append(bot)

#
