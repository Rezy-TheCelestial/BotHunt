import asyncio
import random
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded
from pymongo import MongoClient
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
import time, psutil
from datetime import datetime, timedelta, timezone
import threading
from telegram.ext import Application
from datetime import datetime

# ---------------- Config ---------------- #
BOT_TOKEN = "8275817464:AAHdHynr99dP1uiyb1UKHnQ6CwhHIdWN1yY"
OWNER_ID = 5621201759
NOTIFY_CHAT_ID = -1002526806268  # Replace with your notification group ID
MONGO_URI = "mongodb://Celestial_Guard:Rrahaman%400000@ac-2aplzlb-shard-00-00.zxzlbns.mongodb.net:27017,ac-2aplzlb-shard-00-01.zxzlbns.mongodb.net:27017,ac-2aplzlb-shard-00-02.zxzlbns.mongodb.net:27017/?ssl=true&replicaSet=atlas-gx9cm9-shard-0&authSource=admin&retryWrites=true&w=majority"

ACCOUNTS_PER_PAGE = 15
BOT_START_TIME = time.time()
API_ID = 24561470
API_HASH = "1e2d3c0c1fd09ae41a710d2daea8374b"

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["telegram_bot_db"]

# Dictionary to track hunting status for each account
hunting_status = {}

# ---------------- Utils ---------------- #
def is_owner(user_id):
    return user_id == OWNER_ID

def user_collection(user_id):
    return db[f"user_{user_id}"]

async def notify_owner(context, text):
    try:
        await context.bot.send_message(chat_id=OWNER_ID, text=text)
    except:
        pass

def check_authorized(user_id):
    return db["auth_users"].find_one({"user_id": user_id}) is not None
    
# Startup notifier
          # 🔧 replace with your Telegram ID
  # 🔧 replace with your group/channel ID

async def send_startup_message(app: Application):
    try:
        startup_msg = (
            "━━━━━━━━━━━━━━━━━\n"
            "🫧 **🚀 Bot Started Successfully** 🫧\n"
            "━━━━━━━━━━━━━━━━━\n"
            f"📅 Date: `{datetime.now().strftime('%Y-%m-%d')}`\n"
            f"⏰ Time: `{datetime.now().strftime('%H:%M:%S')}`\n"
            f"🫧 Owner ID: `{OWNER_ID}`\n"
            f"📢 Notify Chat: `{NOTIFY_CHAT_ID}`\n"
            "━━━━━━━━━━━━━━━━\n"
            "🤖 Status: **Online & Ready**\n"
            "🚀 All systems operational\n"
            "🔍 Monitoring started\n"
            "━━━━━━━━━━━━━━━━"
        )

        # Send to Owner
        await app.bot.send_message(
            chat_id=OWNER_ID,
            text=startup_msg,
            parse_mode="Markdown"
        )

        # Send to notify chat if it's different from Owner
        if NOTIFY_CHAT_ID != OWNER_ID:
            await app.bot.send_message(
                chat_id=NOTIFY_CHAT_ID,
                text=startup_msg,
                parse_mode="Markdown"
            )

        print("✅ Starter message sent successfully!")
    except Exception as e:
        print(f"❌ Error sending starter message: {e}")

# ---------------- Commands ---------------- 

# MongoDB collection for users
users_collection = db["users"]

def ensure_user(user_id, username, status="auth"):
    """
    Ensure the user exists in users collection with given status.
    If user doesn't exist, insert them.
    """
    users_collection.update_one(
        {"_id": user_id},
        {"$set": {"username": username, "status": status}},
        upsert=True
    )
    
from datetime import datetime, timezone

def banned_handler(handler):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_id = user.id

        # 🚫 Check if banned
        if db["banned_users"].find_one({"user_id": user_id}):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return

        # ✅ Ensure user exists in db["users"]
        ensure_user(
            user_id,
            user.username or user.first_name,
            status="auth"
        )

        # ✅ Log command usage
        log_collection = db["logs"]
        log_collection.insert_one({
            "user_id": user_id,
            "command": update.message.text.split()[0] if update.message else "unknown",
            "time": datetime.now(timezone.utc)
        })

        # Run actual handler
        await handler(update, context)

    return wrapper
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    if not check_authorized(user_id):
        msg_text = (
            f"❌ Unauthorized user tried to start bot!\n\n"
            f"Name: {user.full_name}\n"
            f"Username: @{user.username or 'N/A'}\n"
            f"User ID: `{user_id}`\n\n"
            f"Use `/auth {user_id}` to authorize."
        )

        sent_msg = await context.bot.send_message(
            chat_id=OWNER_ID,
            text=msg_text,
            parse_mode='Markdown'
        )

        try:
            await context.bot.pin_chat_message(chat_id=OWNER_ID, message_id=sent_msg.message_id)
        except:
            pass

        await update.message.reply_text(
            "❌ You are not authorized to use this bot yet.\n"
            "Your details have been sent to owner for authorisation 🫧"
        )
        return

    await update.message.reply_text(
        f"✅ Welcome {user.full_name}!\nYou are authorized to use this bot.\nUse /login <phone_number> to start."
    )

# ---------- Login / OTP / 2FA ---------- #
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Not authorized")
        return
    if not context.args:
        await update.message.reply_text("Usage: /login <phone_number>")
        return

    phone = context.args[0]
    session_name = f"user_{user_id}_{phone}"
    app = Client(session_name, api_id=API_ID, api_hash=API_HASH)
    await app.connect()
    try:
        sent_code = await app.send_code(phone)
        await update.message.reply_text("📲 Confirmation code sent! Reply with /otp <code>")
        context.user_data['temp_client'] = app
        context.user_data['phone'] = phone
        context.user_data['sent_code'] = sent_code
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send code: {e}")
        await app.stop()

# OTP handler
async def otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'temp_client' not in context.user_data or 'sent_code' not in context.user_data:
        await update.message.reply_text("❌ No login in progress. Use /login <phone>")
        return
    if not context.args:
        await update.message.reply_text("Usage: /otp <code>")
        return

    code = context.args[0]
    app: Client = context.user_data['temp_client']
    phone = context.user_data['phone']
    sent_code = context.user_data['sent_code']

    try:
        # Correct call: all as keyword arguments
        await app.sign_in(phone_number=phone,
                          phone_code=code,
                          phone_code_hash=sent_code.phone_code_hash)
    except SessionPasswordNeeded:
        await update.message.reply_text("2FA detected! Reply with /password <your password>")
        return
    except Exception as e:
        await update.message.reply_text(f"❌ OTP failed: {e}")
        await app.stop()
        context.user_data.clear()
        return

    # Save session string in MongoDB
    session_str = await app.export_session_string()
    # Generate sequential account name
    col = user_collection(update.effective_user.id)
    acc_num = f"acc{col.count_documents({}) + 1}"
    
    # Save in MongoDB
    col.insert_one({
        "account": acc_num,
        "account_name": acc_num,  # You can change this to a real name if available
        "phone": phone,
        "session": await app.export_session_string()
    })
    
    # Notify user and owner
    await update.message.reply_text(f"✅ Logged in {acc_num} successfully!")
    await notify_owner(context, f"User {update.effective_user.id} logged in {phone} as {acc_num}")
    
    # Clean up
    await app.stop()
    context.user_data.clear()

async def password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'temp_client' not in context.user_data:
        await update.message.reply_text("❌ No login in progress. Use /login <phone>")
        return
    if not context.args:
        await update.message.reply_text("Usage: /password <password>")
        return

    pw = context.args[0]
    app: Client = context.user_data['temp_client']
    phone = context.user_data['phone']

    try:
        await app.check_password(pw)
        session_str = await app.export_session_string()
        col = user_collection(update.effective_user.id)
        acc_num = f"acc{col.count_documents({}) + 1}"
        col.insert_one({"account": acc_num, "phone": phone, "session": session_str})
        await update.message.reply_text(f"✅ Logged in {acc_num} successfully!")
        await notify_owner(context, f"User {update.effective_user.id} logged in {phone} as {acc_num}")
    except Exception as e:
        await update.message.reply_text(f"❌ Password failed: {e}")
    await app.stop()
    context.user_data.clear()

# ---------- Account management ---------- #
async def accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    col = user_collection(user_id)
    accounts_list = list(col.find({}).sort("_order", 1))  # sort by the order we set in /order

    if not accounts_list:
        await update.message.reply_text("❌ You have no logged-in accounts.")
        return

    page = int(context.args[0]) if context.args else 0
    start = page * ACCOUNTS_PER_PAGE
    end = start + ACCOUNTS_PER_PAGE
    accounts_page = accounts_list[start:end]

    msg = "🫧 Your accounts:\n"
    for acc in accounts_page:
        account_name = acc.get('account_name', acc['account'])
        hunting = "✅" if hunting_status.get(f"{user_id}_{acc['account']}", {}).get('running', False) else "❌"
        msg += f"     • {account_name} - {acc['phone']} {hunting}\n"

    # Pagination buttons
    buttons = []
    if start > 0:
        buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"accounts_{page-1}"))
    if end < len(accounts_list):
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"accounts_{page+1}"))

    reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None
    
    # Check if this is a callback query or a regular message
    if update.callback_query:
        await update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
    else:
        await update.message.reply_text(msg, reply_markup=reply_markup)
    
async def accounts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("accounts_"):
        page = int(data.split("_")[1])
        # Create a fake context with the page argument
        context.args = [str(page)]
        
        # Call the accounts function with the callback query
        await accounts(update, context)
    
async def change_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Usage check
    if len(context.args) != 2:
        await update.message.reply_text("❌ Usage: /change_acc <account_number> <new_acc_number>")
        return

    acc_number = context.args[0]  # sequence number: 1, 2, 3...
    new_number = context.args[1]  # the X for accX

    # Validate new_number is numeric
    if not new_number.isdigit():
        await update.message.reply_text("❌ New account number must be a number.")
        return

    new_acc_name = f"acc{new_number}"  # construct accX

    col = user_collection(user_id)
    # Get accounts in order of insertion
    accounts_list = list(col.find({}).sort("_id", 1))
    index = int(acc_number) - 1  # zero-based index

    if index < 0 or index >= len(accounts_list):
        await update.message.reply_text("❌ Invalid account number.")
        return

    # Find the first occurrence of the original account
    acc_doc = accounts_list[index]
    old_acc = acc_doc["account"]

    # Update **only this specific document**
    col.update_one({"_id": acc_doc["_id"]}, {"$set": {"account": new_acc_name, "account_name": new_acc_name}})

    await update.message.reply_text(f"✅ Account {old_acc} changed to {new_acc_name} successfully!")
    
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    col = user_collection(user_id)
    accounts_list = list(col.find({}))

    if not accounts_list:
        await update.message.reply_text("❌ You have no accounts to order.")
        return

    # Sort accounts by numeric part of "accX"
    def acc_sort_key(acc):
        acc_num = acc["account"][3:]  # extract X from "accX"
        return int(acc_num)

    sorted_accounts = sorted(accounts_list, key=acc_sort_key)

    # Update "_order" field in DB to reflect ascending order
    for index, acc_doc in enumerate(sorted_accounts):
        col.update_one({"_id": acc_doc["_id"]}, {"$set": {"_order": index}})

    await update.message.reply_text("✅ Accounts have been set to ascending order.")
   
    
        
async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not check_authorized(user_id):
        await update.message.reply_text("❌ You are not authorized.")
        return

    col = user_collection(user_id)
    accounts_list = list(col.find({}))

    if not accounts_list:
        await update.message.reply_text("❌ You have no accounts logged in.")
        return

    # If no argument provided, show accounts usage
    if not context.args:
        msg = "📒 Your logged-in accounts:\n"
        for acc in accounts_list:
            msg += f"{acc['account']} - {acc['phone']}\n"
        msg += "\nUse /logout <acc_number_or_phone> to log out a specific account."
        await update.message.reply_text(msg)
        return

    # Argument provided: try to match by acc_number or phone
    target = context.args[0]
    acc_to_logout = None
    for acc in accounts_list:
        if acc["account"] == target or acc["phone"] == target:
            acc_to_logout = acc
            break

    if not acc_to_logout:
        await update.message.reply_text("❌ No matching account found.")
        return

    # Delete the account from DB
    col.delete_one({"_id": acc_to_logout["_id"]})
    await update.message.reply_text(f"✅ Logged out {acc_to_logout['account']} ({acc_to_logout['phone']}) successfully!")

# ---------- Admin commands ---------- #
async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only owner can authorize
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    # Check usage
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /auth <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    # Get username if exists, else unknown
    user_doc = db["users"].find_one({"_id": target_id})
    username = user_doc.get("username", f"Unknown_{target_id}") if user_doc else f"Unknown_{target_id}"

    # Update users collection
    ensure_user(target_id, username, status="auth")
    
    # ADD THIS: Add user to auth_users collection
    db["auth_users"].update_one(
        {"user_id": target_id},
        {"$set": {"user_id": target_id, "username": username}},
        upsert=True
    )

    await update.message.reply_text(
        f"✅ User `{target_id}` has been authorized.",
        parse_mode="Markdown"
    )
    
async def unauth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only owner can unauth
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    # Check usage
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /unauth <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    # Get username if exists, else unknown
    user_doc = db["users"].find_one({"_id": target_id})
    username = user_doc.get("username", f"Unknown_{target_id}") if user_doc else f"Unknown_{target_id}"

    # Update users collection
    ensure_user(target_id, username, status="unauth")
    
    # ADD THIS: Remove user from auth_users collection
    db["auth_users"].delete_one({"user_id": target_id})

    await update.message.reply_text(
        f"✅ User `{target_id}` has been removed from authorized list.",
        parse_mode="Markdown"
    )
    
async def authlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return
    users = db["auth_users"].find({})
    msg = "✅ Authorized Users:\n"
    for u in users:
        uid = u["user_id"]
        user_obj = await context.bot.get_chat(uid)
        username = user_obj.username or "N/A"
        msg += f"•`@{username} - {uid}`\n"  # mono code formatting
    await update.message.reply_text(msg, parse_mode="Markdown")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /ban <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    username = f"Unknown_{target_id}"  # default if user never started

    # Force insert into users collection as banned
    ensure_user(target_id, username, status="banned")

    # Insert/update in banned_users collection (optional, for log)
    db["banned_users"].update_one(
        {"user_id": target_id},
        {"$set": {"user_id": target_id, "username": username}},
        upsert=True
    )

    await update.message.reply_text(
        f"✅ User `{target_id}` has been banned. They can no longer use the bot.",
        parse_mode="Markdown"
    )
    
from telegram.helpers import escape_markdown

async def banlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    banned_users = list(db["users"].find({"status": "banned"}))

    if not banned_users:
        await update.message.reply_text("❌ There are no banned users.")
        return

    msg = "🚫 Banned Users:\n"
    for i, user in enumerate(banned_users, start=1):
        username = escape_markdown(user.get("username", "NoUsername"), version=2)
        user_id = user["_id"]
        msg += f"     {i}\. {username} \- `{user_id}`\n"

    await update.message.reply_text(msg, parse_mode="MarkdownV2")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /unban <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    # Get username if exists
    user_doc = db["users"].find_one({"_id": target_id})
    username = user_doc.get("username", f"Unknown_{target_id}") if user_doc else f"Unknown_{target_id}"

    # Update status to auth
    ensure_user(target_id, username, status="auth")

    # Remove from banned_users collection
    db["banned_users"].delete_one({"user_id": target_id})

    await update.message.reply_text(
        f"✅ User `{target_id}` has been unbanned.",
        parse_mode="Markdown"
    )

# Check banned before running any command
def is_banned(user_id):
    return db["banned_users"].find_one({"user_id": user_id}) is not None

async def board(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /board <message>")
        return

    text = " ".join(context.args)
    sent_count = 0

    # Iterate through all user collections
    for col_name in db.list_collection_names():
        if col_name.startswith("user_"):
            try:
                uid = int(col_name.split("_")[1])
                await context.bot.send_message(chat_id=uid, text=text)
                sent_count += 1
            except:
                continue

    await update.message.reply_text(f"✅ Broadcast sent to {sent_count} users")

async def msg_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /msg <user_id> <message>")
        return

    uid = int(context.args[0])
    text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=uid, text=text)
        await update.message.reply_text(f"✅ Message sent to {uid}")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send message: {e}")

  # replace with your Telegram user ID

async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    from datetime import datetime, timedelta, timezone
    import psutil, time

    process = psutil.Process()

    # ✅ Global users collection
    users_collection = db["users"]

    # Users
    total_users = users_collection.count_documents({})
    authorized_users = users_collection.count_documents({"status": "auth"})
    banned_users_count = db["banned_users"].count_documents({})

    # Accounts
    total_accounts = 0
    max_accounts = 0
    max_user = None
    for user in users_collection.find({}):
        col = user_collection(user["_id"])   # your helper function
        count = col.count_documents({})
        total_accounts += count
        if count > max_accounts:
            max_accounts = count
            max_user = user["_id"]

    avg_accounts = round(total_accounts / total_users, 2) if total_users else 0

    # Activity
    log_collection = db["logs"]
    now = datetime.now(timezone.utc)
    last_24h = log_collection.count_documents({"time": {"$gte": now - timedelta(hours=24)}})
    last_7d = log_collection.count_documents({"time": {"$gte": now - timedelta(days=7)}})

    # Uptime
    uptime_seconds = int(time.time() - BOT_START_TIME)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

    # System stats
    memory = process.memory_info().rss // (1024 * 1024)
    cpu = process.cpu_percent(interval=0.5)

    msg = f"""
📊 Bot Statistics:

👥 Users:
     • Total users: {total_users}
     • Authorized: {authorized_users}
     • Banned: {banned_users_count}

📂 Accounts:
     • Total accounts: {total_accounts}
     • Avg per user: {avg_accounts}
     • Max accounts: {max_accounts} (User {max_user})

⚡ Activity:
     • Commands used (24h): {last_24h}
     • Commands used (7d): {last_7d}

🖥 System:
     • Uptime: {uptime_str}
     • Memory usage: {memory} MB
     • CPU load: {cpu}%
"""
    await update.message.reply_text(msg)

# ---------- Individual Account Hunting Functions ---------- #
async def solo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start hunting for a specific account"""
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only the owner can use this command.")
        return
        
    if not context.args:
        await update.message.reply_text("❌ Usage: /solo_start <account_number_or_phone>")
        return
        
    target = context.args[0]
    col = user_collection(user_id)
    accounts_list = list(col.find({}))
    
    # Find the account by account name or phone number
    account_to_start = None
    for acc in accounts_list:
        if acc["account"] == target or acc["phone"] == target:
            account_to_start = acc
            break
            
    if not account_to_start:
        await update.message.reply_text("❌ No matching account found.")
        return
        
    # Start hunting for this account
    result = await start_hunting_for_account(user_id, account_to_start['account'], account_to_start['session'])
    await update.message.reply_text(result)

async def solo_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop hunting for a specific account"""
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only the owner can use this command.")
        return
        
    if not context.args:
        await update.message.reply_text("❌ Usage: /solo_stop <account_number_or_phone>")
        return
        
    target = context.args[0]
    col = user_collection(user_id)
    accounts_list = list(col.find({}))
    
    # Find the account by account name or phone number
    account_to_stop = None
    for acc in accounts_list:
        if acc["account"] == target or acc["phone"] == target:
            account_to_stop = acc
            break
            
    if not account_to_stop:
        await update.message.reply_text("❌ No matching account found.")
        return
        
    # Stop hunting for this account
    result = await stop_hunting_for_account(user_id, account_to_stop['account'])
    await update.message.reply_text(result)

async def start_hunting_for_account(user_id, account_name, session_string):
    """Start hunting for a specific account"""
    account_key = f"{user_id}_{account_name}"
    
    if account_key in hunting_status and hunting_status[account_key]['running']:
        return f"❌ {account_name} is already hunting!"
    
    # Initialize hunting status
    hunting_status[account_key] = {
        'running': True,
        'paused': False,
        'stop_requested': False
    }
    
    # Start hunting in a separate thread
    thread = threading.Thread(
        target=asyncio.run, 
        args=(hunt_account(user_id, account_name, session_string, account_key),)
    )
    thread.daemon = True
    thread.start()
    
    return f"✅ Started hunting for {account_name}!"

async def stop_hunting_for_account(user_id, account_name):
    """Stop hunting for a specific account"""
    account_key = f"{user_id}_{account_name}"
    
    if account_key in hunting_status and hunting_status[account_key]['running']:
        hunting_status[account_key]['stop_requested'] = True
        return f"🛑 Stopping hunting for {account_name}..."
    else:
        return f"❌ {account_name} is not currently hunting!"
        
# ---------- Hunting Functions ---------- #
async def start_hunting_for_account(user_id, account_name, session_string):
    """Start hunting for a specific account"""
    account_key = f"{user_id}_{account_name}"
    
    if account_key in hunting_status and hunting_status[account_key]['running']:
        return f"❌ {account_name} is already hunting!"
    
    # Initialize hunting status
    hunting_status[account_key] = {
        'running': True,
        'paused': False,
        'stop_requested': False
    }
    
    # Start hunting in a separate thread
    thread = threading.Thread(
        target=asyncio.run, 
        args=(hunt_account(user_id, account_name, session_string, account_key),)
    )
    thread.daemon = True
    thread.start()
    
    return f"✅ Started hunting for {account_name}!"

async def stop_hunting_for_account(user_id, account_name):
    """Stop hunting for a specific account"""
    account_key = f"{user_id}_{account_name}"
    
    if account_key in hunting_status:
        hunting_status[account_key]['stop_requested'] = True
        return f"🛑 Stopping hunting for {account_name}..."
    else:
        return f"❌ {account_name} is not currently hunting!"

async def hunt_account(user_id, account_name, session_string, account_key):
    """Main hunting function for an account"""
    app = Client(":memory:", api_id=API_ID, api_hash=API_HASH, session_string=session_string)
    
    try:
        await app.start()
        
        # Get the bot entity
        bot_entity = await app.get_users('HeXamonbot')
        
        # Initialize last message tracking
        last_messages = []
        
        # Main hunting loop
        while hunting_status[account_key]['running'] and not hunting_status[account_key]['stop_requested']:
            if hunting_status[account_key]['paused']:
                await asyncio.sleep(3)
                continue
                
            try:
                # Get recent messages
                async for message in app.get_chat_history(bot_entity.id, limit=5):
                    last_messages.append(message)
                
                # Check for shiny or limit reached
                shiny_found = any(
                    '✨ Shiny Pokémon found!' in message.text and message.from_user.id == bot_entity.id
                    for message in last_messages if hasattr(message, 'text') and message.text
                )

                if shiny_found:
                    hunting_status[account_key]['running'] = False
                    # Send notification to owner
                    try:
                        # Get the account-specific NOTIFY_CHAT_ID if set, otherwise use global
                        col = user_collection(user_id)
                        account_data = col.find_one({"account": account_name})
                        target_chat_id = account_data.get("NOTIFY_CHAT_ID", NOTIFY_CHAT_ID) if account_data else NOTIFY_CHAT_ID

                        # 1. Send plain text to NOTIFY_CHAT_ID from the account
                        await app.send_message(
                            chat_id=target_chat_id,
                            text="Shiny aaya h account dekho"
                        )

                        # 2. Send aesthetic message to owner's DM from the bot
                        owner_message = f"""
🎉 *SPECIAL ITEM FOUND!*
━━━━━━━━━━━━━━━━━━━━
💎 *Item:* Shiny Pokémon
• *Acc Number:* `{account_name}`
• *Name:* {account_data.get('account_name', account_name) if account_data else account_name}
• *Phone:* {account_data['phone'] if account_data else 'N/A'}
━━━━━━━━━━━━━━━━━━━━
⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔔 *Notify Chat:* `{target_chat_id}`
                        """

                        bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
                        await bot_app.bot.send_message(
                            chat_id=OWNER_ID,
                            text=owner_message,
                            parse_mode="Markdown"
                        )

                    except:
                        # If above fails, try simplified version with bot only
                        try:
                            bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
                            await bot_app.bot.send_message(chat_id=NOTIFY_CHAT_ID, text="Shiny aaya h account dekho")
                            await bot_app.bot.send_message(chat_id=OWNER_ID, text=f"Shiny found in {account_name}")
                        except:
                            pass
                    break
                
                limit_reached = any(
                    'Daily hunt limit reached' in message.text and message.from_user.id == bot_entity.id
                    for message in last_messages if hasattr(message, 'text') and message.text
                )

                if limit_reached:
                    hunting_status[account_key]['running'] = False
                    
                    try:
                        # Get the account-specific NOTIFY_CHAT_ID if set, otherwise use global
                        col = user_collection(user_id)
                        account_data = col.find_one({"account": account_name})
                        target_chat_id = account_data.get("NOTIFY_CHAT_ID", NOTIFY_CHAT_ID) if account_data else NOTIFY_CHAT_ID
                        
                        # 1. Send plain text to NOTIFY_CHAT_ID from the account
                        await app.send_message(
                            chat_id=target_chat_id,
                            text="🫧 Daily Hunt limit reached"
                        )
                        
                        # 2. Send simple formatted message to owner's DM from the bot
                        owner_message = f"""
🫧 *Daily Limit Reached*
• Account: `{account_name}`
• Time: {datetime.now().strftime('%H:%M:%S')}
                        """
                        
                        bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
                        await bot_app.bot.send_message(
                            chat_id=OWNER_ID,
                            text=owner_message,
                            parse_mode="Markdown"
                        )
                        
                    except:
                        # If above fails, try simplified version with bot only
                        try:
                            bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
                            await bot_app.bot.send_message(chat_id=NOTIFY_CHAT_ID, text="🫧 Daily Hunt limit reached")
                            await bot_app.bot.send_message(chat_id=OWNER_ID, text=f"Daily limit reached in {account_name}")
                        except:
                            pass
                    break
                
                # Send hunt command if not paused and still running
                if hunting_status[account_key]['running'] and not hunting_status[account_key]['paused']:
                    await app.send_message(bot_entity.id, '/hunt')
                
                # Clear messages for next iteration
                last_messages = []
                
                # Random delay between 2-5 seconds
                await asyncio.sleep(random.randint(2, 4))
                
            except Exception as e:
                print(f"Error in hunting for {account_name}: {e}")
                await asyncio.sleep(5)
                
    except Exception as e:
        print(f"Failed to start hunting for {account_name}: {e}")
    finally:
        hunting_status[account_key]['running'] = False
        try:
            await app.stop()
        except:
            pass

async def start_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start hunting for all accounts"""
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only the owner can use this command.")
        return
        
    col = user_collection(user_id)
    accounts_list = list(col.find({}))
    
    if not accounts_list:
        await update.message.reply_text("❌ You have no logged-in accounts.")
        return
        
    started_count = 0
    for account in accounts_list:
        result = await start_hunting_for_account(user_id, account['account'], account['session'])
        if "Started" in result:
            started_count += 1
            
    await update.message.reply_text(f"✅ Started hunting for {started_count} accounts!")

async def stop_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop hunting for all accounts"""
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only the owner can use this command.")
        return
        
    col = user_collection(user_id)
    accounts_list = list(col.find({}))
    
    if not accounts_list:
        await update.message.reply_text("❌ You have no logged-in accounts.")
        return
        
    stopped_count = 0
    for account in accounts_list:
        account_key = f"{user_id}_{account['account']}"
        if account_key in hunting_status and hunting_status[account_key]['running']:
            hunting_status[account_key]['stop_requested'] = True
            stopped_count += 1
            
    await update.message.reply_text(f"🛑 Stopping hunting for {stopped_count} accounts...")
    

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the NOTIFY_CHAT_ID value"""
    message = f"Current Notify Gc : `{NOTIFY_CHAT_ID}`"
    await update.message.reply_text(message, parse_mode="Markdown")
    

async def set_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set NOTIFY_CHAT_ID for a specific account"""
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only the owner can use this command.")
        return
        
    if len(context.args) != 2:
        await update.message.reply_text("❌ Usage: /setchat <chat_id> <acc_number>")
        return
        
    try:
        chat_id = int(context.args[0])
        acc_number = context.args[1]
    except ValueError:
        await update.message.reply_text("❌ Chat ID must be a number.")
        return

    col = user_collection(user_id)
    account = col.find_one({"account": acc_number})
    
    if not account:
        await update.message.reply_text(f"❌ Account {acc_number} not found.")
        return
        
    # Update the account with the new NOTIFY_CHAT_ID
    col.update_one(
        {"account": acc_number},
        {"$set": {"NOTIFY_CHAT_ID": chat_id}}
    )
    
    await update.message.reply_text(
        f"✅ Notify Gc set to `{chat_id}` for account {acc_number}",
        parse_mode="Markdown"
    )

async def show_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current NOTIFY_CHAT_ID for a specific account"""
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only the owner can use this command.")
        return
        
    if len(context.args) != 1:
        await update.message.reply_text("❌ Usage: /show_chat <acc_number>")
        return
        
    acc_number = context.args[0]
    col = user_collection(user_id)
    account = col.find_one({"account": acc_number})
    
    if not account:
        await update.message.reply_text(f"❌ Account {acc_number} not found.")
        return
        
    # Get the NOTIFY_CHAT_ID, default to global NOTIFY_CHAT_ID if not set
    notify_chat_id = account.get("NOTIFY_CHAT_ID", NOTIFY_CHAT_ID)
    
    await update.message.reply_text(
        f"🔔 Account {acc_number} uses notify gc: `{notify_chat_id}`",
        parse_mode="Markdown"
    )
# ---------------- Main ---------------- #
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(send_startup_message).build()

    # Account login
    # Core commands
app.add_handler(CommandHandler("start", banned_handler(start)))
app.add_handler(CommandHandler("login", banned_handler(login)))
app.add_handler(CommandHandler("otp", banned_handler(otp)))
app.add_handler(CommandHandler("password", banned_handler(password)))
app.add_handler(CommandHandler("solo_start", banned_handler(solo_start)))
app.add_handler(CommandHandler("solo_stop", banned_handler(solo_stop)))
app.add_handler(CommandHandler("accounts", banned_handler(accounts)))
app.add_handler(CommandHandler("change_acc", banned_handler(change_acc)))
app.add_handler(CommandHandler("order", banned_handler(order)))
app.add_handler(CommandHandler("banlist", banned_handler(banlist)))
app.add_handler(CommandHandler("logout", banned_handler(logout)))
app.add_handler(CommandHandler("bot_stats", banned_handler(bot_stats)))

# Callback query handler (cannot wrap with banned_handler, handle inside callback if needed)
app.add_handler(CallbackQueryHandler(accounts_callback, pattern="^accounts_"))

# Admin commands
app.add_handler(CommandHandler("auth", banned_handler(auth)))
app.add_handler(CommandHandler("unauth", banned_handler(unauth)))
app.add_handler(CommandHandler("authlist", banned_handler(authlist)))
app.add_handler(CommandHandler("ban", banned_handler(ban)))
app.add_handler(CommandHandler("unban", banned_handler(unban)))
app.add_handler(CommandHandler("board", banned_handler(board)))
app.add_handler(CommandHandler("msg", banned_handler(msg_user)))

# Hunting commands
app.add_handler(CommandHandler("start_all", banned_handler(start_all)))
app.add_handler(CommandHandler("stop_all", banned_handler(stop_all)))
app.add_handler(CommandHandler("get_chat_id", banned_handler(get_chat_id)))
app.add_handler(CommandHandler("set_chat", banned_handler(set_chat)))
app.add_handler(CommandHandler("show_chat", banned_handler(show_chat)))

print("🤖 Bot is running...")
app.run_polling()

if __name__ == "__main__":

    main()

