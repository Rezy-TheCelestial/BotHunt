import asyncio
import random
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, FloodWait
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
import logging
from typing import Dict, Any, List, Optional
from telegram.ext import MessageHandler, filters
from telegram import InputMediaAnimation
import random
from telegram.ext import MessageHandler, filters
import os
from functools import wraps
from collections import defaultdict
from dotenv import load_dotenv
from telegram import Message
import queue
import threading
from concurrent.futures import ThreadPoolExecutor  # Add this import
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
# Global reference to the main bot application
main_bot_app = None
# Load environment variables
load_dotenv()

# ---------------- Enhanced Config with Environment Variables ---------------- #
BOT_TOKEN = os.getenv('BOT_TOKEN', '8275817464:AAGnjwnKXvJ9NrTNE4SEnsZAHs1gm1bLDP8')
OWNER_ID = int(os.getenv('OWNER_ID', 5621201759))
NOTIFY_CHAT_ID = int(os.getenv('NOTIFY_CHAT_ID', -1002526806268))
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://Celestial_Guard:Rrahaman%400000@ac-2aplzlb-shard-00-00.zxzlbns.mongodb.net:27017,ac-2aplzlb-shard-00-01.zxzlbns.mongodb.net:27017,ac-2aplzlb-shard-00-02.zxzlbns.mongodb.net:27017/?ssl=true&replicaSet=atlas-gx9cm9-shard-0&authSource=admin&retryWrites=true&w=majority')
API_ID = int(os.getenv('API_ID', 24561470))
API_HASH = os.getenv('API_HASH', '1e2d3c0c1fd09ae41a710d2daea8374b')

ACCOUNTS_PER_PAGE = 15
BOT_START_TIME = time.time()

# ---------------- Enhanced Logging Setup ---------------- #
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ---------------- Rate Limiting Setup ---------------- #
user_command_times = defaultdict(list)

def rate_limit(limit_per_minute=20):
    def decorator(handler):
        @wraps(handler)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user_id = update.effective_user.id
            now = time.time()
            
            # Clean old records (older than 1 minute)
            user_command_times[user_id] = [
                cmd_time for cmd_time in user_command_times[user_id] 
                if now - cmd_time < 60
            ]
            
            if len(user_command_times[user_id]) >= limit_per_minute:
                await update.message.reply_text(
                    "⚠️ Rate limit exceeded. Please wait a minute before sending more commands."
                )
                return
                
            user_command_times[user_id].append(now)
            return await handler(update, context)
        return wrapper
    return decorator

# ---------------- Database Setup with Error Handling ---------------- #
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.server_info()  # Test connection
    db = mongo_client["telegram_bot_db"]
    
    # FIX DUPLICATE KEY ERROR FIRST
    try:
        # Drop the problematic index if it exists
        db["users"].drop_index("user_id_1")
        print("✅ Fixed duplicate index issue")
    except Exception as e:
        print(f"ℹ️ Index cleanup: {e}")
    
    # Create indexes for better performance WITH FIX
    db["users"].create_index("user_id", unique=True, sparse=True)  # Added sparse=True
    db["auth_users"].create_index("user_id", unique=True)
    db["banned_users"].create_index("user_id", unique=True)
    db["logs"].create_index([("user_id", 1), ("time", -1)])
    
    logger.info("✅ MongoDB connected successfully")
except Exception as e:
    logger.error(f"❌ MongoDB connection failed: {e}")
    raise
# Dictionary to track hunting status for each account
# Add after existing globals around line 60-70
notification_queue = queue.Queue()
executor = ThreadPoolExecutor(max_workers=10)
hunting_status = {}
forward_tasks = {}




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
    
    
# Add this decorator function after your other decorators (after authorized_only)
def owner_only(handler):
    """Decorator to restrict commands to bot owner only"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        # Check if user is owner
        if user_id != OWNER_ID:
            await update.message.reply_text("❌ This command is restricted to bot owner only.")
            return
            
        # Owner is always authorized and can't be banned for these commands
        await handler(update, context)
        
    return wrapper


# ---------------- Enhanced Utils ---------------- #
def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

def user_collection(user_id: int):
    return db[f"user_{user_id}"]

async def notify_owner(context: ContextTypes.DEFAULT_TYPE, text: str):
    try:
        await context.bot.send_message(chat_id=OWNER_ID, text=text)
    except Exception as e:
        logger.error(f"Failed to notify owner: {e}")

def check_authorized(user_id: int) -> bool:
    """Single source of truth for authorization check"""
    try:
        return db["auth_users"].find_one({"user_id": user_id}) is not None
    except Exception as e:
        logger.error(f"Error checking authorization for user {user_id}: {e}")
        return False

def is_banned(user_id: int) -> bool:
    """Check if user is banned"""
    try:
        return db["banned_users"].find_one({"user_id": user_id}) is not None
    except Exception as e:
        logger.error(f"Error checking ban status for user {user_id}: {e}")
        return False

def ensure_user(user_id: int, username: str, status: str = "auth"):
    """Ensure the user exists in users collection with given status."""
    try:
        db["users"].update_one(
            {"_id": user_id},
            {"$set": {"username": username, "status": status, "last_seen": datetime.now(timezone.utc)}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error ensuring user {user_id}: {e}")

def authorized_only(handler):
    """Decorator to check if user is authorized and not banned"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        user_id = user.id
        
        # Check if banned
        if is_banned(user_id):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return

        # Check if authorized
        if not check_authorized(user_id):
            # Notify owner about unauthorized access attempt
            msg_text = (
                f"❌ Unauthorized user tried to use command!\n\n"
                f"Name: {user.full_name}\n"
                f"Username: @{user.username or 'N/A'}\n"
                f"User ID: `{user_id}`\n"
                f"Command: {update.message.text if update.message else 'Unknown'}\n\n"
                f"Use `/auth {user_id}` to authorize."
            )
            
            try:
                sent_msg = await context.bot.send_message(
                    chat_id=OWNER_ID,
                    text=msg_text,
                    parse_mode='Markdown'
                )
                await context.bot.pin_chat_message(chat_id=OWNER_ID, message_id=sent_msg.message_id)
            except Exception as e:
                logger.error(f"Failed to notify owner: {e}")
            
            await update.message.reply_text(
                "❌ You are not authorized to use this bot yet.\n"
                "Your details have been sent to owner for authorization 🫧"
            )
            return

        # Ensure user exists in database
        ensure_user(
            user_id,
            user.username or user.first_name or "Unknown",
            status="auth"
        )

        # Log command usage
        try:
            db["logs"].insert_one({
                "user_id": user_id,
                "command": update.message.text.split()[0] if update.message and update.message.text else "unknown",
                "time": datetime.now(timezone.utc),
                "username": user.username or "N/A"
            })
        except Exception as e:
            logger.error(f"Error logging command: {e}")

        # Run actual handler
        await handler(update, context)

    return wrapper

# ---------------- Login Session Management ---------------- #
async def cleanup_login_session(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Clean up login session resources"""
    try:
        if 'temp_client' in context.user_data:
            app = context.user_data['temp_client']
            if isinstance(app, Client):
                await app.disconnect()
            del context.user_data['temp_client']
        
        # Remove login-related data
        for key in ['phone', 'sent_code', 'login_start_time']:
            if key in context.user_data:
                del context.user_data[key]
                
    except Exception as e:
        logger.error(f"Error cleaning up login session for user {user_id}: {e}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel ongoing login/OTP/password process"""
    user_id = update.effective_user.id
    
    # Check if there's an active login session
    if 'temp_client' not in context.user_data:
        await update.message.reply_text("❌ No active login session to cancel.")
        return
    
    await cleanup_login_session(context, user_id)
    await update.message.reply_text("🎉  Login process cancelled successfully.")

# ---------------- Startup Notifier ---------------- #
async def send_startup_message(app: Application):
    try:
        startup_msg = (
            "━━━━━━━━━━━━━━━━━\n"
            "🐉 **Bot Started Successfully** 🐉\n"
            "━━━━━━━━━━━━━━━━━\n"
            f"🔸 Date: `{datetime.now().strftime('%Y-%m-%d')}`\n"
            f"🔰 Time: `{datetime.now().strftime('%H:%M:%S')}`\n"
            f"⚜️ Owner ID: `{OWNER_ID}`\n"
            f"✳️ Notify Chat: `{NOTIFY_CHAT_ID}`\n"
            "━━━━━━━━━━━━━━━━\n"
            "🔹 Status: **Online & Ready**\n"
            "⚕️ All systems operational\n"
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

        logger.info("✅ Starter message sent successfully!")
    except Exception as e:
        logger.error(f"❌ Error sending starter message: {e}")

# ---------------- Commands ---------------- #
@rate_limit(5)
@authorized_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🗽 Welcome {user.full_name}!\n"
        f"🐉 You are authorized to use this bot.\n"
        f"🔹 Use /help to know about BOT functionality "
        
    )

# ---------- Login / OTP / 2FA / Cancel ---------- #
@rate_limit(10)
@authorized_only
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check if already in login process
    if 'temp_client' in context.user_data:
        await update.message.reply_text(
            "❌ Login process already in progress.\n"
            "Complete it or use /cancel to start over."
        )
        return
        
    if not context.args:
        await update.message.reply_text("Usage: /login <phone_number>")
        return

    phone = context.args[0]
    session_name = f"user_{user_id}_{phone}"
    
    try:
        app = Client(session_name, api_id=API_ID, api_hash=API_HASH)
        await app.connect()
        
        # Store login start time for timeout handling
        context.user_data['login_start_time'] = time.time()
        context.user_data['temp_client'] = app
        context.user_data['phone'] = phone
        
        sent_code = await app.send_code(phone)
        context.user_data['sent_code'] = sent_code
        
        await update.message.reply_text(
            "🗝️ Confirmation code sent! Reply with /otp <code>\n"
            "Use /cancel to cancel this process."
        )
        
    except FloodWait as e:
        await update.message.reply_text(f"❌ Flood wait: Please wait {e.value} seconds before trying again.")
        await cleanup_login_session(context, user_id)
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send code: {e}")
        await cleanup_login_session(context, user_id)

@rate_limit(3)
@authorized_only
async def otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check login session timeout (10 minutes)
    if 'login_start_time' in context.user_data:
        if time.time() - context.user_data['login_start_time'] > 600:  # 10 minutes
            await update.message.reply_text("❌ Login session expired. Please start over with /login")
            await cleanup_login_session(context, user_id)
            return
    
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
        await app.sign_in(
            phone_number=phone,
            phone_code=code,
            phone_code_hash=sent_code.phone_code_hash
        )
    except SessionPasswordNeeded:
        await update.message.reply_text(
            "🔸 2FA detected! Reply with /password <your_password>\n"
            "Use /cancel to cancel this process."
        )
        return
    except Exception as e:
        await update.message.reply_text(f"❌ OTP failed: {e}")
        await cleanup_login_session(context, user_id)
        return

    # Login successful - save session
    session_str = await app.export_session_string()
    col = user_collection(user_id)
    
    # Get next account number
    acc_count = col.count_documents({})
    acc_num = f"acc{acc_count + 1}"
    
    # Save account with proper order
    col.insert_one({
        "account": acc_num,
        "account_name": acc_num,
        "phone": phone,
        "session": session_str,
        "tg_name": "",
        "NOTIFY_CHAT_ID": NOTIFY_CHAT_ID,
        "_order": acc_count,
        "created_at": datetime.now(timezone.utc),
        # Daily tracking fields
        "daily_hunts": 0,
        "today_shinies": 0,
        "last_hunt_reset": None
    })
    
    await update.message.reply_text(f"🎉 Logged in {acc_num} successfully!")
    await notify_owner(context, f"User {user_id} logged in {phone} as {acc_num}")
    await cleanup_login_session(context, user_id)

@rate_limit(3)
@authorized_only
async def password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check login session timeout
    if 'login_start_time' in context.user_data:
        if time.time() - context.user_data['login_start_time'] > 600:
            await update.message.reply_text("❌ Login session expired. Please start over with /login")
            await cleanup_login_session(context, user_id)
            return
    
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
        col = user_collection(user_id)
        
        acc_count = col.count_documents({})
        acc_num = f"acc{acc_count + 1}"
        
        col.insert_one({
            "account": acc_num,
            "account_name": acc_num,
            "phone": phone,
            "session": session_str,
            "tg_name": "",
            "NOTIFY_CHAT_ID": NOTIFY_CHAT_ID,
            "_order": acc_count,
            "created_at": datetime.now(timezone.utc),
            # Daily tracking fields
            "daily_hunts": 0,
            "today_shinies": 0,
            "last_hunt_reset": None
        })
        
        await update.message.reply_text(f"🎉 Logged in {acc_num} successfully!")
        await notify_owner(context, f"User {user_id} logged in {phone} as {acc_num}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Password failed: {e}")
    
    await cleanup_login_session(context, user_id)

# ---------- Account Management ---------- #
@rate_limit(10)
@authorized_only
async def accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    col = user_collection(user_id)
    
    try:
        accounts_list = list(col.find({}).sort("_order", 1))
    except Exception as e:
        logger.error(f"Error fetching accounts for user {user_id}: {e}")
        await update.message.reply_text("❌ Error fetching accounts.")
        return

    if not accounts_list:
        await update.message.reply_text("❌ You have no logged-in accounts.")
        return

    # Determine page number
    if update.callback_query:
        data = update.callback_query.data
        page = int(data.split("_")[1]) if "_" in data else 0
    else:
        page = int(context.args[0]) if context.args and context.args[0].isdigit() else 0

    start = page * ACCOUNTS_PER_PAGE
    end = start + ACCOUNTS_PER_PAGE
    accounts_page = accounts_list[start:end]

    msg = "🐉 Your accounts:\n\n"
    for idx, acc in enumerate(accounts_page, start=1):
        account_name = acc.get('account_name', acc['account'])
        
        # FIXED: Proper hunting status check
        account_key = f"{user_id}_{acc['account']}"
        if account_key in hunting_status and hunting_status[account_key].get('running', False):
            hunting = "✅" 
        else:
            hunting = "❌"
            
        msg += f"{start + idx}. {account_name} - {acc['phone']} {hunting}\n"

    # Pagination buttons
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"accounts_{page-1}"))
    if end < len(accounts_list):
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"accounts_{page+1}"))

    reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None
    
    if update.callback_query:
        await update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
    else:
        await update.message.reply_text(msg, reply_markup=reply_markup)

# Alternative simpler callback handler:
async def accounts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination callbacks for accounts"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    # Check authorization for callback
    if not check_authorized(user_id):
        await query.edit_message_text("❌ You are not authorized.")
        return
        
    if is_banned(user_id):
        await query.edit_message_text("❌ You are banned from using this bot.")
        return
    
    col = user_collection(user_id)
    
    try:
        accounts_list = list(col.find({}).sort("_order", 1))
    except Exception as e:
        logger.error(f"Error fetching accounts for user {user_id}: {e}")
        await query.edit_message_text("❌ Error fetching accounts.")
        return

    if not accounts_list:
        await query.edit_message_text("❌ You have no logged-in accounts.")
        return

    # Get page from callback data
    data = query.data
    page = int(data.split("_")[1]) if "_" in data else 0

    start = page * ACCOUNTS_PER_PAGE
    end = start + ACCOUNTS_PER_PAGE
    accounts_page = accounts_list[start:end]

    msg = "🐉 Your accounts:\n\n"
    for idx, acc in enumerate(accounts_page, start=1):
        account_name = acc.get('account_name', acc['account'])
        
        account_key = f"{user_id}_{acc['account']}"
        if account_key in hunting_status and hunting_status[account_key].get('running', False):
            hunting = "✅" 
        else:
            hunting = "❌"
            
        msg += f"{start + idx}. {account_name} - {acc['phone']} {hunting}\n"

    # Pagination buttons
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"accounts_{page-1}"))
    if end < len(accounts_list):
        buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"accounts_{page+1}"))

    reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None
    
    await query.edit_message_text(msg, reply_markup=reply_markup)

@rate_limit(5)
@authorized_only
async def change_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if len(context.args) != 2:
        await update.message.reply_text("❌ Usage: /change_acc <current_number> <new_number>")
        return

    current_num, new_num = context.args[0], context.args[1]

    if not new_num.isdigit() or not current_num.isdigit():
        await update.message.reply_text("❌ Both numbers must be numeric.")
        return

    new_acc_name = f"acc{new_num}"
    current_acc_name = f"acc{current_num}"

    col = user_collection(user_id)
    
    # Check if new account name already exists
    if col.find_one({"account": new_acc_name}):
        await update.message.reply_text("❌ Account with this number already exists.")
        return

    # Find and update the account
    result = col.update_one(
        {"account": current_acc_name},
        {"$set": {"account": new_acc_name, "account_name": new_acc_name}}
    )

    if result.modified_count > 0:
        await update.message.reply_text(f"🎉 Account {current_acc_name} changed to {new_acc_name} successfully!")
        
        # Update hunting status key if account was hunting
        old_key = f"{user_id}_{current_acc_name}"
        new_key = f"{user_id}_{new_acc_name}"
        if old_key in hunting_status:
            hunting_status[new_key] = hunting_status.pop(old_key)
    else:
        await update.message.reply_text("❌ Account not found.")

@rate_limit(5)
@authorized_only
async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    col = user_collection(user_id)
    
    try:
        accounts_list = list(col.find({}))
    except Exception as e:
        logger.error(f"Error fetching accounts for ordering: {e}")
        await update.message.reply_text("❌ Error fetching accounts.")
        return

    if not accounts_list:
        await update.message.reply_text("❌ You have no accounts to order.")
        return

    # Sort by numeric part of account name
    def get_account_number(acc):
        try:
            return int(acc["account"][3:])  # Extract number from "accX"
        except (ValueError, IndexError):
            return float('inf')  # Put invalid formats at the end

    sorted_accounts = sorted(accounts_list, key=get_account_number)

    # Update order in database
    try:
        for index, acc in enumerate(sorted_accounts):
            col.update_one({"_id": acc["_id"]}, {"$set": {"_order": index}})
        
        await update.message.reply_text("🎉 Accounts have been sorted in ascending order.")
    except Exception as e:
        logger.error(f"Error updating account order: {e}")
        await update.message.reply_text("❌ Error updating account order.")

@rate_limit(5)
@authorized_only
async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    col = user_collection(user_id)
    
    try:
        accounts_list = list(col.find({}))
    except Exception as e:
        logger.error(f"Error fetching accounts for logout: {e}")
        await update.message.reply_text("❌ Error fetching accounts.")
        return

    if not accounts_list:
        await update.message.reply_text("❌ You have no accounts logged in.")
        return

    if not context.args:
        # Show accounts list
        msg = "🐉 Your logged-in accounts:\n\n"
        for acc in accounts_list:
            msg += f"• {acc['account']} - {acc['phone']}\n"
        msg += "\nUse /logout <acc_number_or_phone> to log out a specific account."
        await update.message.reply_text(msg)
        return

    target = context.args[0]
    acc_to_logout = None
    
    for acc in accounts_list:
        if acc["account"] == target or acc["phone"] == target:
            acc_to_logout = acc
            break

    if not acc_to_logout:
        await update.message.reply_text("❌ No matching account found.")
        return

    # Stop hunting if this account is being hunted
    account_key = f"{user_id}_{acc_to_logout['account']}"
    if account_key in hunting_status:
        hunting_status[account_key]['stop_requested'] = True

    # Delete the account
    try:
        col.delete_one({"_id": acc_to_logout["_id"]})
        await update.message.reply_text(
            f"🐉 Logged out {acc_to_logout['account']} ({acc_to_logout['phone']}) successfully!"
        )
    except Exception as e:
        logger.error(f"Error logging out account: {e}")
        await update.message.reply_text("❌ Error logging out account.")

# ---------- Admin Commands (Owner Only) ---------- #
@rate_limit(5)
@owner_only
async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("🔸Usage: /auth <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    # Get user info
    try:
        user_obj = await context.bot.get_chat(target_id)
        username = user_obj.username or user_obj.first_name or f"Unknown_{target_id}"
    except:
        username = f"Unknown_{target_id}"

    # Update users collection
    ensure_user(target_id, username, status="auth")
    
    # Add to auth_users
    db["auth_users"].update_one(
        {"user_id": target_id},
        {"$set": {"user_id": target_id, "username": username, "authorized_at": datetime.now(timezone.utc)}},
        upsert=True
    )

    await update.message.reply_text(f"🎉 User `{target_id}` has been authorized.", parse_mode="Markdown")

@rate_limit(5)
@owner_only
async def unauth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("🔸Usage: /unauth <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    # Update users collection
    user_doc = db["users"].find_one({"_id": target_id})
    username = user_doc.get("username", f"Unknown_{target_id}") if user_doc else f"Unknown_{target_id}"
    ensure_user(target_id, username, status="unauth")
    
    # Remove from auth_users
    db["auth_users"].delete_one({"user_id": target_id})

    await update.message.reply_text(f"🎉 User `{target_id}` has been removed from authorized list.", parse_mode="Markdown")

@rate_limit(5)
@owner_only
async def authlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        users = list(db["auth_users"].find({}))
    except Exception as e:
        logger.error(f"Error fetching auth list: {e}")
        await update.message.reply_text("❌ Error fetching authorized users.")
        return

    if not users: 
        await update.message.reply_text("❌ No authorized users.") 
        return 
    
    msg = "🐉 Authorized Users:\n\n"
    for u in users:
        uid = u["user_id"]
        username = u.get("username", "N/A")
        # HTML escaping for safety
        escaped_username = username.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        msg += f"• @{escaped_username} - <code>{uid}</code>\n"
    
    await update.message.reply_text(msg, parse_mode="HTML")

@rate_limit(5)
@owner_only
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("🔸Usage: /ban <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    # Prevent owner from banning themselves
    if target_id == OWNER_ID:
        await update.message.reply_text("Bitch you cannot ban yourself (Owner)🤦🏻! ")
        return

    # Get user info
    try:
        user_obj = await context.bot.get_chat(target_id)
        username = user_obj.username or user_obj.first_name or f"Unknown_{target_id}"
    except:
        username = f"Unknown_{target_id}"

    # Update users collection
    ensure_user(target_id, username, status="banned")

    # Add to banned_users
    db["banned_users"].update_one(
        {"user_id": target_id},
        {"$set": {"user_id": target_id, "username": username, "banned_at": datetime.now(timezone.utc)}},
        upsert=True
    )

    await update.message.reply_text(f"🎉 User `{target_id}` has been banned.", parse_mode="Markdown")

# Remove the @owner_only decorator and add custom check for unban
@rate_limit(5)
@owner_only
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Allow only owner to use unban command, even if they are banned
    if user_id != OWNER_ID:
        # For non-owner users, check if they are banned
        if is_banned(user_id):
            await update.message.reply_text("❌ You are banned from using this bot.")
            return
        # For non-owner users, check if they are authorized
        if not check_authorized(user_id):
            await update.message.reply_text("❌ You are not authorized to use this command.")
            return

    if len(context.args) != 1:
        await update.message.reply_text("🔸Usage: /unban <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    # Get user info
    user_doc = db["users"].find_one({"_id": target_id})
    username = user_doc.get("username", f"Unknown_{target_id}") if user_doc else f"Unknown_{target_id}"

    # Update status to auth
    ensure_user(target_id, username, status="auth")

    # Remove from banned_users
    db["banned_users"].delete_one({"user_id": target_id})

    await update.message.reply_text(f"🎉 User `{target_id}` has been unbanned.", parse_mode="Markdown")

@rate_limit(5)
@owner_only
async def banlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        banned_users = list(db["banned_users"].find({}))
    except Exception as e:
        logger.error(f"Error fetching ban list: {e}")
        await update.message.reply_text("❌ Error fetching banned users.")
        return

    if not banned_users:
        await update.message.reply_text("❌ There are no banned users.")
        return

    msg = "🐉 Banned Users:\n\n"
    for i, user in enumerate(banned_users, start=1):
        username = user.get("username", "NoUsername")
        user_id = user["user_id"]
        msg += f"{i}. {username} - `{user_id}`\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

@rate_limit(5)
@owner_only
async def bot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Users statistics
        total_users = db["users"].count_documents({})
        authorized_users = db["auth_users"].count_documents({})
        banned_users_count = db["banned_users"].count_documents({})

        # Accounts statistics
        total_accounts = 0
        max_accounts = 0
        max_user = None
        
        for col_name in db.list_collection_names():
            if col_name.startswith("user_"):
                try:
                    user_id = int(col_name.split("_")[1])
                    col = db[col_name]
                    count = col.count_documents({})
                    total_accounts += count
                    if count > max_accounts:
                        max_accounts = count
                        max_user = user_id
                except:
                    continue

        avg_accounts = round(total_accounts / total_users, 2) if total_users else 0

        # Activity statistics
        now = datetime.now(timezone.utc)
        last_24h = db["logs"].count_documents({"time": {"$gte": now - timedelta(hours=24)}})
        last_7d = db["logs"].count_documents({"time": {"$gte": now - timedelta(days=7)}})

        # Uptime
        uptime_seconds = int(time.time() - BOT_START_TIME)
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

        # System stats
        process = psutil.Process()
        memory = process.memory_info().rss // (1024 * 1024)
        cpu = process.cpu_percent(interval=0.5)

        # Hunting stats
        active_hunts = sum(1 for status in hunting_status.values() if status.get('running', False))

        msg = f"""
🐉 Bot Statistics:

👥 Users:
     • Total users: {total_users}
     • Authorized: {authorized_users}
     • Banned: {banned_users_count}

💥 Accounts:
     • Total accounts: {total_accounts}
     • Avg per user: {avg_accounts}
     • Max accounts: {max_accounts} (User {max_user})

⚜️ Hunting:
     • Active hunts: {active_hunts}

⚡ Activity:
     • Commands used (24h): {last_24h}
     • Commands used (7d): {last_7d}

🖥 System:
     • Uptime: {uptime_str}
     • Memory usage: {memory} MB
     • CPU load: {cpu}%
"""
        await update.message.reply_text(msg)
        
    except Exception as e:
        logger.error(f"Error generating bot stats: {e}")
        await update.message.reply_text("❌ Error generating statistics.")

@rate_limit(3)
@owner_only
async def board(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /board <message>")
        return

    text = " ".join(context.args)
    sent_count = 0

    for col_name in db.list_collection_names():
        if col_name.startswith("user_"):
            try:
                uid = int(col_name.split("_")[1])
                # Check if user is authorized before sending
                if check_authorized(uid) and not is_banned(uid):
                    await context.bot.send_message(chat_id=uid, text=text)
                    sent_count += 1
            except Exception as e:
                logger.error(f"Error sending message to user {uid}: {e}")
                continue

    await update.message.reply_text(f"🎉 Broadcast sent to {sent_count} authorized users")

@rate_limit(5)
@owner_only
async def msg_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("❌ Usage: /msg <user_id> <message>")
        return

    try:
        uid = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")
        return

    text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=uid, text=text)
        await update.message.reply_text(f"🎉 Message sent to {uid}", parse_mode = "Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send message: {e}")

# ---------- Enhanced Name Function ---------- #
@rate_limit(7)
@authorized_only
async def names(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    col = user_collection(user_id)
    
    try:
        # Get accounts sorted by account number in ascending order
        accounts = list(col.find({}))
    except Exception as e:
        logger.error(f"Error fetching accounts for names: {e}")
        await update.message.reply_text("❌ Error fetching accounts.")
        return

    if not accounts:
        await update.message.reply_text("No accounts found ❌")
        return

    # Sort accounts by numeric part of account name (acc1, acc2, etc.)
    def get_account_number(acc):
        try:
            # Extract number from "accX" format
            return int(acc["account"][3:])  # Remove "acc" prefix and convert to int
        except (ValueError, IndexError):
            return float('inf')  # Put invalid formats at the end

    # Sort accounts by their numeric value
    sorted_accounts = sorted(accounts, key=get_account_number)

    async def fetch_name_live(acc):
        """Fetch name from Telegram and update cache"""
        session_string = acc.get("session")
        account_name = acc.get("account")
        
        if not session_string:
            return account_name, "No session"
            
        try:
            app = Client(":memory:", api_id=API_ID, api_hash=API_HASH, session_string=session_string)
            await app.start()
            me = await app.get_me()
            tg_name = f"{me.first_name or ''} {me.last_name or ''}".strip() or me.username or "No Name"
            await app.stop()
            
            # Update in DB
            col.update_one(
                {"_id": acc["_id"]}, 
                {"$set": {"tg_name": tg_name}}
            )
            
            return account_name, tg_name
        except Exception as e:
            logger.error(f"Failed to fetch name for {account_name}: {e}")
            return account_name, f"Error: {str(e)}"

    # Prepare cached names from sorted accounts
    msg_lines = []
    accounts_to_fetch = []
    
    for acc in sorted_accounts:
        tg_name = acc.get("tg_name")
        acc_name = acc.get("account", "Unknown")
        
        if tg_name:
            msg_lines.append(f"• {acc_name} - {tg_name}")
        else:
            accounts_to_fetch.append(acc)

    # Send cached names first (in correct order)
    if msg_lines:
        await update.message.reply_text(
            "🐉 Your accounts and Telegram names (sorted):\n\n" + "\n".join(msg_lines)
        )

    # Fetch missing names
    if accounts_to_fetch:
        await update.message.reply_text("🔄 Fetching updated names from Telegram...")
        
        updated_lines = []
        for acc in accounts_to_fetch:
            account_name, tg_name = await fetch_name_live(acc)
            updated_lines.append(f"• {account_name} - {tg_name}")
            await asyncio.sleep(1)  # Rate limiting

        if updated_lines:
            await update.message.reply_text(
                "📌 Updated names from Telegram:\n\n" + "\n".join(updated_lines)
            )

@rate_limit(3)
@authorized_only
async def order_names(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to reorder accounts by their numbers"""
    user_id = update.effective_user.id
    col = user_collection(user_id)
    
    try:
        accounts = list(col.find({}))
    except Exception as e:
        logger.error(f"Error fetching accounts for ordering: {e}")
        await update.message.reply_text("❌ Error fetching accounts.")
        return

    if not accounts:
        await update.message.reply_text("❌ You have no accounts to order.")
        return

    # Sort by numeric part of account name
    def get_account_number(acc):
        try:
            return int(acc["account"][3:])  # Extract number from "accX"
        except (ValueError, IndexError):
            return float('inf')  # Put invalid formats at the end

    sorted_accounts = sorted(accounts, key=get_account_number)

    # Update _order field in database to reflect the sorted order
    try:
        for index, acc in enumerate(sorted_accounts):
            col.update_one(
                {"_id": acc["_id"]}, 
                {"$set": {"_order": index}}
            )
        
        await update.message.reply_text("🎉 Accounts have been sorted in ascending order by account number!")
        
        # Show the new ordered list
        msg = "🐉 Accounts in new order:\n\n"
        for idx, acc in enumerate(sorted_accounts, start=1):
            account_name = acc.get('account_name', acc['account'])
            msg += f"{idx}. {account_name} - {acc['phone']}\n"
            
        await update.message.reply_text(msg)
        
    except Exception as e:
        logger.error(f"Error updating account order: {e}")
        await update.message.reply_text("❌ Error updating account order.")

@rate_limit(3)
@authorized_only
async def reorder_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recreate account numbers in proper sequential order"""
    user_id = update.effective_user.id
    col = user_collection(user_id)
    
    try:
        accounts = list(col.find({}))
    except Exception as e:
        logger.error(f"Error fetching accounts for reordering: {e}")
        await update.message.reply_text("❌ Error fetching accounts.")
        return

    if not accounts:
        await update.message.reply_text("❌ You have no accounts to reorder.")
        return

    # Sort by current account number
    def get_account_number(acc):
        try:
            return int(acc["account"][3:])
        except (ValueError, IndexError):
            return float('inf')

    sorted_accounts = sorted(accounts, key=get_account_number)

    # Recreate account numbers sequentially
    try:
        for index, acc in enumerate(sorted_accounts, start=1):
            new_acc_name = f"acc{index}"
            col.update_one(
                {"_id": acc["_id"]},
                {"$set": {
                    "account": new_acc_name,
                    "account_name": new_acc_name,
                    "_order": index - 1
                }}
            )

        await update.message.reply_text(f"🎉 Successfully reordered {len(sorted_accounts)} accounts sequentially!")
        
        # Show the new ordered list
        msg = "🐉 Accounts in new sequential order:\n\n"
        new_accounts = list(col.find({}).sort("_order", 1))
        for idx, acc in enumerate(new_accounts, start=1):
            msg += f"{idx}. {acc['account']} - {acc['phone']}\n"
            
        await update.message.reply_text(msg)
        
    except Exception as e:
        logger.error(f"Error reordering accounts: {e}")
        await update.message.reply_text("❌ Error reordering accounts.")









# ---------- Hunting Functions (Improved) ---------- #
# ---------- Hunting Functions (Improved) ---------- #

# ---------- HUNTING FUNCTIONS (WORKING VERSION) ---------- #
# ---------- HUNTING FUNCTIONS (FAST PARALLEL VERSION) ---------- #
@rate_limit(6)
@authorized_only
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

@rate_limit(6)
@authorized_only
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
    """Start hunting for a specific account - WORKING VERSION"""
    account_key = f"{user_id}_{account_name}"
    
    if account_key in hunting_status and hunting_status[account_key]['running']:
        return f"❌ {account_name} is already hunting!"
    
    # Initialize hunting status
    hunting_status[account_key] = {
        'running': True,
        'paused': False,
        'stop_requested': False,
        'hunt_count': 0
    }
    
    # Start hunting in a separate thread - SIMPLE APPROACH
    try:
        thread = threading.Thread(
            target=run_hunt_sync,  # Use sync wrapper
            args=(user_id, account_name, session_string, account_key),
            daemon=True,
            name=f"Hunter-{account_name}"
        )
        thread.start()
        
        return f"🎉 Successfully started hunting for {account_name}!"
    except Exception as e:
        hunting_status[account_key]['running'] = False
        return f"❌ Failed to start hunting: {e}"

async def stop_hunting_for_account(user_id, account_name):
    """Stop hunting for a specific account"""
    account_key = f"{user_id}_{account_name}"
    
    if account_key not in hunting_status:
        return f"❌ {account_name} is not currently hunting!"
    
    if not hunting_status[account_key]['running']:
        return f"❌ {account_name} is not currently hunting!"
    
    # Set stop requested flag
    hunting_status[account_key]['stop_requested'] = True
    
    # Wait a moment for the hunting loop to detect the stop request
    await asyncio.sleep(1)
    
    # Double check if it's still running
    if hunting_status[account_key]['running']:
        # Force stop if it didn't stop gracefully
        hunting_status[account_key]['running'] = False
    
    return f"🎉 Successfully stopped hunting for {account_name}!"

@rate_limit(6)
@authorized_only
async def start_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start hunting for all accounts - FAST PARALLEL VERSION"""
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ Only the owner can use this command.")
        return
        
    col = user_collection(user_id)
    accounts_list = list(col.find({}))
    
    if not accounts_list:
        await update.message.reply_text("❌ You have no logged-in accounts.")
        return
        
    # Send initial message
    progress_msg = await update.message.reply_text("💥 Starting all accounts in parallel...")
    
    # Filter out already running accounts and prepare tasks
    tasks = []
    accounts_to_start = []
    
    for account in accounts_list:
        account_key = f"{user_id}_{account['account']}"
        
        # Skip if already running
        if account_key in hunting_status and hunting_status[account_key].get('running', False):
            continue
            
        accounts_to_start.append(account)
        # Create task for each account
        task = asyncio.create_task(
            start_account_parallel(user_id, account['account'], account['session'], account_key)
        )
        tasks.append(task)
    
    if not tasks:
        await progress_msg.edit_text("All accounts are already running! 🤦🏻")
        return
    
    # Start ALL accounts simultaneously
    await asyncio.gather(*tasks, return_exceptions=True)
    
    # Wait a moment for threads to initialize
    await asyncio.sleep(2)
    
    # Count successfully started accounts
    successful_starts = sum(1 for account in accounts_to_start 
                           if hunting_status.get(f"{user_id}_{account['account']}", {}).get('running', False))
    
    message = f"⚡ **PARALLEL START COMPLETE**\n\n"
    message += f"🎉 Successfully started: `{successful_starts}` accounts\n"
    message += f"⚕️ Total accounts: `{len(accounts_list)}`\n"
    message += f"⚡ Speed: Instant parallel start"
    
    await progress_msg.edit_text(message, parse_mode="Markdown")
    
    # Force status refresh
    if successful_starts > 0:
        await context.bot.send_message(
            chat_id=user_id,
            text="💫 Use /hunting_status to check hunting status"
        )

async def start_account_parallel(user_id, account_name, session_string, account_key):
    """Start a single account in parallel - FAST VERSION"""
    if account_key in hunting_status and hunting_status[account_key]['running']:
        return f"❌ {account_name} is already hunting!"
    
    # Initialize hunting status
    hunting_status[account_key] = {
        'running': True,
        'paused': False,
        'stop_requested': False,
        'hunt_count': 0
    }
    
    # Start hunting in a separate thread - NO DELAY
    try:
        thread = threading.Thread(
            target=run_hunt_sync,
            args=(user_id, account_name, session_string, account_key),
            daemon=True,
            name=f"Hunter-{account_name}"
        )
        thread.start()
        return f"✅ Started {account_name}"
    except Exception as e:
        hunting_status[account_key]['running'] = False
        return f"❌ Failed to start {account_name}: {e}"

def run_hunt_sync(user_id, account_name, session_string, account_key):
    """Sync wrapper for hunting function"""
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(hunt_account_working(user_id, account_name, session_string, account_key))
    except Exception as e:
        logger.error(f"Hunting error for {account_name}: {e}")
        hunting_status[account_key]['running'] = False

async def hunt_account_working(user_id, account_name, session_string, account_key):
    """OPTIMIZED hunting function - FASTER START"""
    app = Client(f"hunter_{user_id}_{account_name}", api_id=API_ID, api_hash=API_HASH, session_string=session_string)
    
    try:
        await app.start()
        logger.info(f"🎯 Hunting STARTED for {account_name}")
        
        # Get the bot entity - FASTER
        bot_entity = await app.get_users('HeXamonbot')
        
        # Immediate first hunt - NO INITIAL DELAY
        await app.send_message(bot_entity.id, '/hunt')
        
        # UPDATE DAILY COUNT IN DATABASE (permanent)
        col = user_collection(user_id)
        col.update_one(
            {"account": account_name},
            {"$inc": {"daily_hunts": 1}}
        )
        
        # Update session counter (temporary)
        hunting_status[account_key]['hunt_count'] += 1
        
        # Main hunting loop
        while hunting_status[account_key]['running'] and not hunting_status[account_key]['stop_requested']:
            if hunting_status[account_key]['paused']:
                await asyncio.sleep(1)  # Reduced pause delay
                continue
                
            try:
                # Send hunt command
                await app.send_message(bot_entity.id, '/hunt')
                
                # UPDATE DAILY COUNT IN DATABASE (permanent)
                col.update_one(
                    {"account": account_name},
                    {"$inc": {"daily_hunts": 1}}
                )
                
                # Update session counter (temporary)
                hunting_status[account_key]['hunt_count'] += 1
                
                # Log every 10 hunts instead of 5 (reduce logging overhead)
                if hunting_status[account_key]['hunt_count'] % 10 == 0:
                    # Get current daily count from database
                    account_data = col.find_one({"account": account_name})
                    daily_count = account_data.get('daily_hunts', 0) if account_data else 0
                    logger.info(f"🔍 {account_name}: {hunting_status[account_key]['hunt_count']} session hunts, {daily_count} daily hunts")
                
                # Check for messages - OPTIMIZED
                async for message in app.get_chat_history(bot_entity.id, limit=2):  # Reduced from 3 to 2
                    if hasattr(message, 'text') and message.text:
                        # Check for shiny
                        if '✨ Shiny Pokémon found!' in message.text:
                            logger.info(f"🎉 SHINY FOUND in {account_name}!")
                            hunting_status[account_key]['running'] = False
                            await send_shiny_notification_working(user_id, account_name, account_key, app)
                            break
                            
                        # Check for daily limit
                        if 'Daily hunt limit reached' in message.text:
                            logger.info(f"🫧 Daily limit reached for {account_name}")
                            hunting_status[account_key]['running'] = False
                            await send_limit_notification_working(user_id, account_name, account_key, app)
                            break
                
                # Reduced random delay (2-4 seconds instead of 3-5)
                await asyncio.sleep(random.randint(2, 4))
                
            except Exception as e:
                logger.error(f"Error in hunting loop for {account_name}: {e}")
                await asyncio.sleep(3)  # Reduced error delay
                
    except Exception as e:
        logger.error(f"Failed to start hunting for {account_name}: {e}")
    finally:
        hunting_status[account_key]['running'] = False
        try:
            await app.stop()
        except:
            pass

@rate_limit(6)
@authorized_only
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
            
    await update.message.reply_text(f" 🎉 Successfully stopped hunting for {stopped_count} accounts...")

async def send_shiny_notification_working(user_id, account_name, account_key, app):
    """Send shiny notification - FIXED VERSION"""
    try:
        col = user_collection(user_id)
        account_data = col.find_one({"account": account_name})
        target_chat_id = account_data.get("NOTIFY_CHAT_ID", NOTIFY_CHAT_ID) if account_data else NOTIFY_CHAT_ID
        
        # Use the fixed notification function (NOT the hunting account's app)
        await send_hunt_notification(target_chat_id, f"🎉 SHINY FOUND in {account_name}!")  # Changed message
        try:
            # Send message from the hunting account
            await app.send_message(
                chat_id=target_chat_id,
                text=f"Shiny aaya h account dekho"
            )
            logger.info(f"✅ Account {account_name} sent limit message to notify GC")
        except Exception as e:
            logger.error(f"❌ Account failed to send message: {e}")
        
        # Send to owner
        owner_message = f"🎉 SHINY FOUND in {account_name}!"
        await send_owner_notification(owner_message)
        
        logger.info(f"✅ Shiny notification sent for {account_name}")
    except Exception as e:
        logger.error(f"❌ Shiny notification failed: {e}")

async def send_limit_notification_working(user_id, account_name, account_key, app):
    """Send limit notification - FIXED VERSION with account sending message"""
    try:
        col = user_collection(user_id)
        account_data = col.find_one({"account": account_name})
        target_chat_id = account_data.get("NOTIFY_CHAT_ID", NOTIFY_CHAT_ID) if account_data else NOTIFY_CHAT_ID
        
        # 1. Send notification using the bot (as before)
        await send_hunt_notification(target_chat_id, f"💥 Done Hunting -  {account_name}")
        
        # 2. ALSO send message from the hunting account itself to the notify GC
        try:
            # Send message from the hunting account
            await app.send_message(
                chat_id=target_chat_id,
                text=f"⚕️ Hunt limit reached  -  ({account_name}) "
            )
            logger.info(f"✅ Account {account_name} sent limit message to notify GC")
        except Exception as e:
            logger.error(f"❌ Account failed to send message: {e}")
        
        # 3. Send to owner
        owner_message = f"🫧 Daily limit reached for {account_name}"
        await send_owner_notification(owner_message)
        
        logger.info(f"✅ Limit notification sent for {account_name}")
    except Exception as e:
        logger.error(f"❌ Limit notification failed: {e}")


    
            
            
            
            
                
                




 
@rate_limit(5)   
@authorized_only   
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the NOTIFY_CHAT_ID value"""
    message = f"Current Notify Gc : `{NOTIFY_CHAT_ID}`"
    await update.message.reply_text(message, parse_mode="Markdown")
    
@rate_limit(3)
@authorized_only
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

@rate_limit(5)
@authorized_only
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
    
@rate_limit(7)
@owner_only
async def forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner-only. Reply to a message and run: /forward [count] or /forward <chat_id> [count]
       Default count = 1. If count>1 => ask confirmation."""
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ You are not authorized.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a message with /forward <count> or /forward <chat_id> <count>")
        return

    # parse args
    target_chat = NOTIFY_CHAT_ID
    count = 1
    try:
        if len(context.args) == 1:
            count = max(1, int(context.args[0]))
        elif len(context.args) >= 2:
            target_chat = int(context.args[0])
            count = max(1, int(context.args[1]))
    except Exception as e:
        await update.message.reply_text("❌ Invalid arguments. Usage: /forward OR reply with /forward <count> OR /forward <chat_id> <count>")
        return

    # If just one copy, do it immediately (no confirm)
    if count == 1:
        try:
            await update.message.reply_to_message.copy(chat_id=target_chat)
            await update.message.reply_text("🎉 Forwarded 1/1")
        except Exception as e:
            await update.message.reply_text(f"❌ Forward failed: {e}")
        return

    # count > 1 -> ask confirm
    keyboard = [
        [
            InlineKeyboardButton("✔️ Yes, Go ahead!", callback_data=f"confirm_forward:{target_chat}:{count}"),
            InlineKeyboardButton("❌ No, leave it!", callback_data="cancel_forward")
        ]
    ]
    # keep the replied message so the button handler can read it
    context.user_data["forward_message"] = update.message.reply_to_message
    context.user_data["forward_target_chat"] = target_chat
    context.user_data["forward_count"] = count

    await update.message.reply_text(
        f"☠️ You are about to forward this {count} times.\nProceed?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation buttons. Yes => wait 5s, delete confirm msg, start background forwarding.
       No => quick cancel and delete confirmation message after a short delay."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data.startswith("confirm_forward"):
        try:
            _, target_chat_s, count_s = query.data.split(":")
            target_chat = int(target_chat_s)
            count = int(count_s)
        except Exception:
            await query.edit_message_text("❌ Invalid confirmation data.")
            return

        message = context.user_data.get("forward_message")
        if not message:
            await query.edit_message_text("❌ No message stored to forward.")
            return

        # Edit to waiting text
        try:
            await query.edit_message_text("Sure! — starting in 5 seconds...")
        except:
            pass

        # small countdown (non-blocking visually, but we sleep)
        await asyncio.sleep(5)

        # attempt to delete the confirmation message (tidy up)
        try:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        except Exception:
            pass

        # start background forwarding (returns immediately)
        await start_forwarding_background(context, message, target_chat, count, user_id)

    elif query.data == "cancel_forward":
        try:
            await query.edit_message_text("❌ Forward cancelled.")
        except:
            pass
        await asyncio.sleep(2)
        try:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        except:
            pass


async def start_forwarding_background(context: ContextTypes.DEFAULT_TYPE,
                                      message: Message,
                                      target_chat: int,
                                      count: int,
                                      owner_user_id: int):
    """Start the forward loop in a background task and return immediately.
       The background task edits one progress message for updates. Stop instantly by cancelling the task."""
    # Cancel any previously running task for this owner
    existing = forward_tasks.get(owner_user_id)
    if existing and existing.get("task") and not existing["task"].done():
        try:
            existing["task"].cancel()
        except:
            pass

    # Reserve entry before starting task to avoid race
    forward_tasks[owner_user_id] = {"task": None, "progress_msg": None, "count": count, "current": 0}

    async def run():
        # send initial progress message to owner (so they can see edits)
        try:
            progress_msg = await context.bot.send_message(chat_id=owner_user_id, text=f"🔸 Forwarding 0/{count}")
            forward_tasks[owner_user_id]["progress_msg"] = progress_msg
        except Exception as e:
            logger.error(f"Failed to create progress message: {e}")
            forward_tasks.pop(owner_user_id, None)
            return

        try:
            for i in range(count):
                # copy the replied message to target chat
                await message.copy(chat_id=target_chat)

                # update counters
                forward_tasks[owner_user_id]["current"] = i + 1

                # edit the progress message (in-place)
                try:
                    await progress_msg.edit_text(f"🔸 Forwarding {i+1}/{count}")
                except Exception:
                    # ignore edit failures (message may be deleted)
                    pass

                # wait between forwards (2s)
                await asyncio.sleep(2)

            # finished normally
            try:
                await progress_msg.edit_text(f"🎉 Completed {count}/{count}")
            except Exception:
                pass

        except asyncio.CancelledError:
            # immediate cancellation path — edit progress (if exists)
            data = forward_tasks.get(owner_user_id, {})
            prog = data.get("progress_msg")
            current = data.get("current", 0)
            total = data.get("count", count)
            if prog:
                try:
                    await prog.edit_text(f"🔰 Cancelled at {current}/{total}")
                except Exception:
                    pass
            raise

        except Exception as e:
            logger.exception("Error during forwarding task: %s", e)
            prog = forward_tasks.get(owner_user_id, {}).get("progress_msg")
            if prog:
                try:
                    await prog.edit_text(f"❌ Error: {str(e)[:120]}")
                except Exception:
                    pass

        finally:
            # cleanup mapping (task done or cancelled)
            forward_tasks.pop(owner_user_id, None)

    # create and store background task (do NOT await it here)
    task = asyncio.create_task(run())
    forward_tasks[owner_user_id]["task"] = task
    # return immediately so handler doesn't block

@rate_limit(7)
@owner_only
async def stop_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner-only. Immediately stop ongoing forward task and edit the progress message."""
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("❌ You are not authorized.")
        return

    data = forward_tasks.get(user_id)
    if not data or not data.get("task"):
        await update.message.reply_text("⚠️ No active forwarding task.")
        return

    task = data["task"]
    if task.done():
        await update.message.reply_text("⚠️ No active forwarding task.")
        # cleanup if still present
        forward_tasks.pop(user_id, None)
        return

    # Cancel the task immediately
    task.cancel()

    # Wait a short moment to let the task catch CancelledError and edit the progress message
    # but do not block long — we return instantly to the owner
    await asyncio.sleep(0.05)
    await update.message.reply_text("🐉 Forwarding task stopped ")
    
    
async def handle_shiny_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Debug why messages aren't being detected"""
    
    print(f"🔍 MESSAGE RECEIVED!")
    print(f"📝 Text: {update.message.text if update.message else 'No message'}")
    print(f"🏠 Chat ID: {update.message.chat.id if update.message else 'No chat'}")
    print(f"🎯 Target Chat ID: {NOTIFY_CHAT_ID}")
    print(f"✅ Match: {update.message.chat.id == NOTIFY_CHAT_ID if update.message else 'No'}")
    
    if update.message and update.message.text:
        print(f"🔎 Checking for 'Shiny aaya h account dekho' in text...")
        print(f"📋 Contains phrase: {'Shiny aaya h account dekho' in update.message.text}")
    
    # Check if message exists and is in notify GC
    if (update.message and 
        update.message.chat.id == NOTIFY_CHAT_ID and 
        update.message.text and
        "Shiny aaya h account dekho" in update.message.text):
        
        print("🎉 CONDITION MET! Sending victory reply...")
        
        # Get sender info
        if update.message.from_user:
            sender_name = update.message.from_user.first_name or "Unknown"
        else:
            sender_name = "Someone"
        
        # Reply with victory GIF and message
        await send_victory_reply(update, context, sender_name)
    else:
        print("❌ Conditions not met")
        
async def send_victory_reply(update: Update, context: ContextTypes.DEFAULT_TYPE, account_name: str):
    """Reply with monospace professional victory message"""
    
    try:
        # 🔥 QUALITY GIFS 🔥
        victory_gifs = [
            "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
            "https://media.giphy.com/media/xULW8N9O5WD32Gc6e4/giphy.gif",
            "https://media.giphy.com/media/3o85xGocUH8RYoDKKs/giphy.gif",
            "https://media.giphy.com/media/l0HlG8fgsLuUog13a/giphy.gif",
        ]
        
        gif_url = random.choice(victory_gifs)
        
        # 🎯 MONOSPACE PROFESSIONAL MESSAGE
        victory_text = f"""
🫧 **WELL DONE SEXY BUDDY!** 🫧

`Account    : {account_name}`
`Discovery  : Shiny Pokémon` 
`Status     : Successful Hunt`
`Timestamp  : {datetime.now().strftime('%H:%M:%S')}`
`Hunter     : Elite Status`

⚕️ **Exceptional performance!** 🗽
        """
        
        print(f"🎁 Sending victory reply to {account_name}")
        
        await update.message.reply_animation(
            animation=gif_url,
            caption=victory_text,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        print(f"❌ Error: {e}")
        await update.message.reply_text(
            f"🫧 **WELL DONE SEXY BUDDY!** 🫧 \n\n"
            f"`Account    : {account_name}`\n"
            f"`Discovery  : Shiny Pokémon`\n"
            f"`Status     : Successful Hunt`\n"
            f"`Timestamp  : {datetime.now().strftime('%H:%M:%S')}`\n"
            f"`Hunter     : Elite Status`\n\n"
            f"⚕️ **Exceptional performance!** 🗽",
            parse_mode="Markdown"
        )


@rate_limit(3)
@owner_only
async def test_shiny_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test the shiny reply system"""
    try:
        account_name = "Test Account"
        
        # Curated list of victory GIFs
        victory_gifs = [
            "https://media.giphy.com/media/26tknCqiJrBQG6bxC/giphy.gif",
            "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif", 
            "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif",
            "https://media.giphy.com/media/xULW8N9O5WD32Gc6e4/giphy.gif",
        ]
        
        gif_url = random.choice(victory_gifs)
        
        victory_text = f"""
🎉 **WELL DONE SEXY BUDDY!** 🎉

🌟 *Congratulations {account_name}!* 🌟
✨ You found a shiny Pokémon! ✨
🏆 Absolute legend! 🏆

💖 Keep up the amazing work! 💖
        """
        
        # Send test GIF
        await update.message.reply_animation(
            animation=gif_url,
            caption=victory_text,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Test failed: {e}")   

@rate_limit(5)
@owner_only
async def debug_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if bot is receiving messages from notify GC"""
    await update.message.reply_text(
        f"🔍 **Debug Info:**\n"
        f"Notify GC ID: `{NOTIFY_CHAT_ID}`\n"
        f"Bot is listening for messages...\n\n"
        f"**Test:** Send 'Shiny aaya h account dekho' in the notify GC",
        parse_mode="Markdown"
    )    

@rate_limit(3)
@owner_only
async def test_permissions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test if bot can send messages in notify GC"""
    try:
        # Try to send a test message to notify GC
        await context.bot.send_message(
            chat_id=NOTIFY_CHAT_ID,
            text="🤖 Bot permission test - I can send messages here!"
        )
        await update.message.reply_text("✅ Bot can send messages to notify GC!")
    except Exception as e:
        await update.message.reply_text(f"❌ Bot cannot send messages: {e}") 
 
@rate_limit(1)
@owner_only
async def emergency_unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Emergency unban command that bypasses all checks"""
    user_id = 5621201759  # Your owner ID
    
    # Remove from banned_users
    db["banned_users"].delete_one({"user_id": user_id})
    
    # Update users collection
    db["users"].update_one(
        {"_id": user_id},
        {"$set": {"status": "auth"}}
    )
    
    await update.message.reply_text("✅ Owner has been unbanned!")

# ---------------- NEW IMPROVEMENTS ADDED ---------------- #

@rate_limit(5)
@authorized_only
async def backup_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Backup all accounts data for a user"""
    user_id = update.effective_user.id
    col = user_collection(user_id)
    
    try:
        accounts = list(col.find({}))
        if not accounts:
            await update.message.reply_text("❌ No accounts to backup.")
            return
            
        # Create backup collection
        backup_col = db[f"backup_user_{user_id}_{int(time.time())}"]
        backup_col.insert_many(accounts)
        
        await update.message.reply_text(f"✅ Backup created for {len(accounts)} accounts!")
        
    except Exception as e:
        logger.error(f"Backup error: {e}")
        await update.message.reply_text("❌ Backup failed.")

@rate_limit(10)
@authorized_only
async def hunting_status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check hunting status of all accounts with your format"""
    user_id = update.effective_user.id
    col = user_collection(user_id)
    
    try:
        accounts = list(col.find({}))
        if not accounts:
            await update.message.reply_text("❌ No accounts found.")
            return
        
        # Sort accounts by account number (acc1, acc2, acc3, etc.)
        def get_account_number(acc):
            try:
                return int(acc["account"][3:])  # Extract number from "accX"
            except (ValueError, IndexError):
                return float('inf')  # Put invalid formats at the end
        
        sorted_accounts = sorted(accounts, key=get_account_number)
            
        active_count = 0
        total_count = len(sorted_accounts)
        total_today_hunts = 0
        total_session_hunts = 0
        
        status_msg = """
╔══════════════════════════════╗
         🐉 HUNTING STATUS 🐉
╚══════════════════════════════╝

"""
        
        for acc in sorted_accounts:
            account_name = acc.get('account_name', acc['account'])
            daily_hunts = acc.get('daily_hunts', 0)
            total_today_hunts += daily_hunts
            
            account_key = f"{user_id}_{acc['account']}"
            if account_key in hunting_status and hunting_status[account_key].get('running', False):
                status = "✅"
                active_count += 1
                session_hunts = hunting_status[account_key].get('hunt_count', 0)
                total_session_hunts += session_hunts
                status_msg += f"🔹 {account_name}: {status} {daily_hunts} hunts (+{session_hunts})\n"
            else:
                status = "❌"
                status_msg += f"🔹 {account_name}: {status} {daily_hunts} hunts\n"
                
        # Calculate averages
        avg_today_hunts = round(total_today_hunts / total_count, 1) if total_count > 0 else 0
        avg_session_hunts = round(total_session_hunts / active_count, 1) if active_count > 0 else 0
        
        status_msg += f"""
╔══════════════════════════════╗
             🐉 SUMMARY 🐉
╚══════════════════════════════╝

✔️ Active Accounts : {active_count}/{total_count}
⚕️ Total Hunts Today : {total_today_hunts}
🫧 Average per Account : {avg_today_hunts} hunts
⚡ Average Active Session : {avg_session_hunts} hunts
"""
        
        await update.message.reply_text(f"```{status_msg}```", parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Hunting status error: {e}")
        await update.message.reply_text("❌ Error fetching hunting status.")
        
# Dictionary to track hunting status for each account
notification_queue = queue.Queue()
executor = ThreadPoolExecutor(max_workers=10)
hunting_status = {}
forward_tasks = {}

# ---------------- Daily Reset Scheduler ---------------- #
def reset_daily_counts():
    """Reset all daily hunt counts at 5:30 AM IST"""
    try:
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        today_date = now.date()
        
        logger.info(f"🔄 Checking daily reset - Current IST: {now}")
        
        # Only reset if it's after 5:30 AM
        if now.hour >= 5 and now.minute >= 30:
            reset_count = 0
            
            for col_name in db.list_collection_names():
                if col_name.startswith("user_"):
                    try:
                        col = db[col_name]
                        # Reset accounts that haven't been reset today
                        result = col.update_many(
                            {
                                "$or": [
                                    {"last_hunt_reset": {"$lt": today_date}},
                                    {"last_hunt_reset": None},
                                    {"last_hunt_reset": {"$exists": False}}
                                ]
                            },
                            {
                                "$set": {
                                    "daily_hunts": 0,
                                    "today_shinies": 0,
                                    "last_hunt_reset": today_date
                                }
                            }
                        )
                        reset_count += result.modified_count
                    except Exception as e:
                        logger.error(f"Reset error for {col_name}: {e}")
            
            if reset_count > 0:
                logger.info(f"✅ Reset daily counts for {reset_count} accounts at {now}")
            else:
                logger.info(f"ℹ️ No accounts needed reset at {now}")
                
    except Exception as e:
        logger.error(f"❌ Daily reset error: {e}")

def start_daily_reset_scheduler():
    """Start the scheduler for daily resets"""
    try:
        scheduler = BackgroundScheduler()
        # Run every minute to check if it's 5:30 AM IST
        scheduler.add_job(reset_daily_counts, 'cron', minute='*', timezone='Asia/Kolkata')
        scheduler.start()
        logger.info("✅ Daily reset scheduler started (checking every minute for 5:30 AM IST)")
        
        # Run immediate check on startup
        reset_daily_counts()
        
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")

@rate_limit(5)
@owner_only
async def system_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check system health and bot status"""
    try:
        # System info
        process = psutil.Process()
        memory_mb = process.memory_info().rss // (1024 * 1024)
        cpu_percent = process.cpu_percent(interval=1)
        
        # Database info
        total_users = db["users"].count_documents({})
        total_accounts = sum(1 for col_name in db.list_collection_names() if col_name.startswith("user_"))
        
        # Bot uptime
        uptime_seconds = int(time.time() - BOT_START_TIME)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        
        # Hunting stats
        active_hunts = sum(1 for status in hunting_status.values() if status.get('running', False))
        
        health_msg = f"""
🩺 System Health Report:

💻 System:
  • Memory Usage: {memory_mb} MB
  • CPU Load: {cpu_percent}%
  • Uptime: {hours}h {minutes}m

🗄️ Database:
  • Total Users: {total_users}
  • Total Accounts: {total_accounts}

🎯 Hunting:
  • Active Sessions: {active_hunts}

🔧 Status: {'✅ Healthy' if cpu_percent < 80 and memory_mb < 500 else '⚠️ High Load'}
"""
        await update.message.reply_text(health_msg)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        await update.message.reply_text("❌ Error checking system health.")

@rate_limit(20)
@authorized_only
async def dash_boob(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clean, professional dashboard in boxed format"""
    try:
        # Fetch all statistics
        # Users statistics
        total_users = db["users"].count_documents({})
        authorized_users = db["auth_users"].count_documents({})
        banned_users_count = db["banned_users"].count_documents({})
        
        # Calculate active users (last 24 hours)
        now = datetime.now(timezone.utc)
        active_users_24h = len(db["logs"].distinct("user_id", {
            "time": {"$gte": now - timedelta(hours=24)}
        })) if db["logs"].count_documents({"time": {"$gte": now - timedelta(hours=24)}}) > 0 else 0
        
        # Accounts statistics
        total_accounts = 0
        max_accounts = 0
        max_user = None
        user_accounts = {}
        
        for col_name in db.list_collection_names():
            if col_name.startswith("user_"):
                try:
                    user_id = int(col_name.split("_")[1])
                    col = db[col_name]
                    count = col.count_documents({})
                    total_accounts += count
                    user_accounts[user_id] = count
                    if count > max_accounts:
                        max_accounts = count
                        max_user = user_id
                except:
                    continue
        
        avg_accounts = round(total_accounts / total_users, 2) if total_users else 0
        
        # Activity statistics
        last_24h = db["logs"].count_documents({"time": {"$gte": now - timedelta(hours=24)}})
        last_7d = db["logs"].count_documents({"time": {"$gte": now - timedelta(days=7)}})
        
        # Calculate week-over-week growth
        previous_week = db["logs"].count_documents({
            "time": {"$gte": now - timedelta(days=14), "$lt": now - timedelta(days=7)}
        })
        weekly_growth = round(((last_7d - previous_week) / previous_week * 100), 1) if previous_week else 0
        
        # Uptime
        uptime_seconds = int(time.time() - BOT_START_TIME)
        days, remainder = divmod(uptime_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{days}d {hours}h {minutes}m"
        
        # System stats
        process = psutil.Process()
        memory_mb = process.memory_info().rss // (1024 * 1024)
        cpu_percent = process.cpu_percent(interval=0.5)
        
        # Hunting stats - USING DAILY COUNTS FROM DATABASE
        active_hunts = sum(1 for status in hunting_status.values() if status.get('running', False))
        
        # Calculate today's hunt statistics from database
        total_hunts_today = 0
        hunt_counts = {}
        
        for col_name in db.list_collection_names():
            if col_name.startswith("user_"):
                try:
                    col = db[col_name]
                    accounts = list(col.find({}))
                    for acc in accounts:
                        daily_hunts = acc.get('daily_hunts', 0)
                        total_hunts_today += daily_hunts
                        hunt_counts[acc['account']] = daily_hunts
                except:
                    continue
        
        # Calculate averages and top hunters
        avg_hunts_per_acc = round(total_hunts_today / len(hunt_counts), 1) if hunt_counts else 0
        top_hunters = sorted(hunt_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Calculate percentages for display
        active_hunts_pct = round((active_hunts / total_accounts * 100), 1) if total_accounts else 0
        uptime_pct = round((uptime_seconds / (7 * 86400)) * 100, 1)  # Percentage of week
        memory_pct = round((memory_mb / 512) * 100, 1)  # Assuming 512MB max
        auth_pct = round((authorized_users / total_users * 100), 1) if total_users else 0
        
        # Build the dashboard
        dashboard = f"""
╔════════════════════════════════════╗
             🐉 BOT DASHBOARD 🐉
╚════════════════════════════════════╝

🎉 HUNTING OPERATIONS
  • Active Hunts: {active_hunts}/{total_accounts} ({active_hunts_pct}%)
  • Hunts Today: {total_hunts_today} commands
  • Average per Account: {avg_hunts_per_acc} hunts
  • Top Hunter: {top_hunters[0][0] if top_hunters else 'N/A'} ({top_hunters[0][1] if top_hunters else 0} hunts)

👥 USER ANALYTICS
  • Total Users: {total_users}
  • Authorized: {authorized_users} ({auth_pct}%)
  • Banned: {banned_users_count}
  • Active (24h): {active_users_24h} users

💥 ACCOUNT MANAGEMENT
  • Total Accounts: {total_accounts}
  • Average per User: {avg_accounts}
  • Maximum Accounts: {max_accounts} (User {max_user})
  • Active Sessions: {active_hunts}/{total_accounts}

⚡ PERFORMANCE METRICS
  • Uptime: {uptime_str} ({uptime_pct}%)
  • Memory Usage: {memory_mb}MB ({memory_pct}%)
  • CPU Load: {cpu_percent}%
  • Commands (24h): {last_24h} ({weekly_growth:+}% weekly)

🏆 TOP HUNTER ACCOUNTS
"""
        
        # Add top hunters
        for i, (acc_name, hunt_count) in enumerate(top_hunters):
            rank = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}."
            dashboard += f"  {rank} {acc_name}: {hunt_count} hunts\n"
        
        # Add system status
        health_status = "✅ Stable" if cpu_percent < 80 and memory_pct < 90 else "⚠️ High Load"
        growth_status = "📈 Growing" if weekly_growth > 0 else "📉 Declining" if weekly_growth < 0 else "➡️ Stable"
        
        dashboard += f"""
🔧 SYSTEM STATUS
  • Hunt Activity: {'Active ✔️' if active_hunts > 0 else ' Inactive ❌'}
  • User Growth: {growth_status}
  • System Health: {health_status}
  • Database:  Connected ✓
"""
        
        await update.message.reply_text(f"```{dashboard}```", parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error generating dashboard: {e}")
        await update.message.reply_text("❌ Error generating dashboard statistics.")
        
def get_peer_type(peer_id: int) -> str:
    """Get the peer type from peer ID"""
    try:
        if peer_id > 0:
            return "user"
        elif peer_id < 0:
            # Check if it's a chat or channel
            if str(peer_id).startswith('-100'):
                return "channel"
            else:
                return "chat"
        else:
            return "user"  # Default fallback
    except (TypeError, ValueError):
        return "user"  # Safe fallback


@rate_limit(15)
@authorized_only
async def today_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's hunting statistics with average"""
    user_id = update.effective_user.id
    col = user_collection(user_id)
    
    accounts = list(col.find({}))
    total_today_hunts = sum(acc.get('daily_hunts', 0) for acc in accounts)
    total_today_shinies = sum(acc.get('today_shinies', 0) for acc in accounts)
    
    # Calculate averages
    total_accounts = len(accounts)
    avg_hunts_per_acc = round(total_today_hunts / total_accounts, 1) if total_accounts > 0 else 0
    
    # Most active today
    most_active_today = max(accounts, key=lambda x: x.get('daily_hunts', 0), default=None)
    
    # Active accounts count
    active_accounts = sum(1 for acc in accounts 
                         if hunting_status.get(f"{user_id}_{acc['account']}", {}).get('running', False))
    
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist)
    
    message = f"""
╔════════════════════════════╗
      🐉 TODAY'S STATISTICS 🐉
╚════════════════════════════╝

⚕️ Total Accounts    : -- {total_accounts}
✔️ Active Now        : -- {active_accounts}
🫧 Today's Hunts     : -- {total_today_hunts}
💥 Avg per Account   : -- {avg_hunts_per_acc} hunts
✨ Shinies Today     : -- {total_today_shinies}

🥇 Today's MVP       : -- {most_active_today['account'] if most_active_today else 'N/A'} ({most_active_today['daily_hunts'] if most_active_today else 0} hunts)

🔄 Next reset: 05:30 AM IST
"""
    
    await update.message.reply_text(f"```{message}```", parse_mode="Markdown")

@rate_limit(10)
@authorized_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all available commands with descriptions"""
    
    help_text = """
╔════════════════════════════════════╗
              🐉 BOT HELP MENU 🐉
╚════════════════════════════════════╝

🔰 ACCOUNT MANAGEMENT
  • /start - Start the bot and check authorization
  • /login <phone> - Login with phone number
  • /otp <code> - Enter OTP code
  • /password <pass> - Enter 2FA password
  • /cancel - Cancel ongoing login process
  • /accounts - List all your accounts
  • /logout <acc> - Logout specific account

⚜️ HUNTING COMMANDS
  • /start_all - Start hunting on all accounts
  • /stop_all - Stop hunting on all accounts
  • /solo_start <acc> - Start hunting on specific account
  • /solo_stop <acc> - Stop hunting on specific account
  • /hunting_status - Check current hunting status

💥 STATISTICS & MONITORING
  • /today_stats - Today's hunting statistics
  • /dash_boob - Complete bot dashboard
  • /system_health - System health check
  • /bot_stats - Detailed bot statistics

⚙️ ACCOUNT SETTINGS
  • /names - Show Telegram names of accounts
  • /order_names - Sort accounts by number
  • /reorder - Recreate sequential account numbers
  • /change_acc <old> <new> - Change account number
  • /set_chat <chat_id> <acc> - Set notify chat for account
  • /show_chat <acc> - Show notify chat for account

🗽 OWNER COMMANDS (Owner Only)
  • /auth <user_id> - Authorize user
  • /unauth <user_id> - Remove user authorization
  • /authlist - List authorized users
  • /ban <user_id> - Ban user
  • /unban <user_id> - Unban user
  • /banlist - List banned users
  • /board <msg> - Broadcast message to all users
  • /msg <user_id> <msg> - Send message to specific user
  • /forward - Forward messages (reply to use)

⚡ UTILITY COMMANDS
  • /get_chat_id - Show current notify chat ID
  • /test_shiny_reply - Test shiny notification
  • /debug_messages - Debug message reception
  • /test_permissions - Test bot permissions
  • /backup - Backup accounts data
  • /emergency_unban - Emergency unban owner

🫧 HUNTING INFORMATION
  • Hunts auto-reset daily at 5:30 AM IST
  • Daily counts survive bot restarts
  • Notifications sent for shinies/limits
  • Rate limiting: 5-10 commands per minute

🆘 NEED HELP?
  • Contact owner for assistance
  • Check /today_stats for current status
  • Use /system_health for bot health
"""
    
    await update.message.reply_text(f"```{help_text}```", parse_mode="Markdown")
# ---------------- MAIN FUNCTION WITH ALL HANDLERS ---------------- #
def main():
    global main_bot_app  # Add this line at the beginning
    
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(send_startup_message).build()
    main_bot_app = app  # Set the global variable to the same instance

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
    app.add_handler(CommandHandler("names", banned_handler(names)))
    app.add_handler(CommandHandler("order_names", order_names))
    app.add_handler(CommandHandler("reorder", reorder_accounts))
    app.add_handler(CommandHandler("forward", forward))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("stop", stop_forward))
    
    # Message handlers
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Chat(chat_id=NOTIFY_CHAT_ID),
        handle_shiny_message
    ))
    
    # Test commands
    app.add_handler(CommandHandler("test_shiny_reply", test_shiny_reply))
    app.add_handler(CommandHandler("debug_messages", debug_messages))
    app.add_handler(CommandHandler("test_permissions", test_permissions))
    app.add_handler(CommandHandler("emergency_unban", emergency_unban))    
    
    # New improvement commands
    app.add_handler(CommandHandler("backup", backup_accounts))
    app.add_handler(CommandHandler("hunting_status", hunting_status_cmd))
    app.add_handler(CommandHandler("system_health", system_health))
    app.add_handler(CommandHandler("dash_boob", banned_handler(dash_boob)))  
    app.add_handler(CommandHandler("today_stats", banned_handler(today_stats)))
    app.add_handler(CommandHandler("help", banned_handler(help_command)))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
