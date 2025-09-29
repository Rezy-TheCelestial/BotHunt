import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Your MongoDB configuration
MONGO_URI = "mongodb+srv://pokemon_bot_user:PokemonBot2024!Secure@cluster0pokemon-bot-clu.iveqoue.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0pokemon-bot-cluster"
DB_NAME = "pokemon_guess_bot"
ACCOUNTS_COLL = "Accounts"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class MongoDBHandler:
    def __init__(self):
        self.client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        self.db = self.client[DB_NAME]
        self.accounts_coll = self.db[ACCOUNTS_COLL]
        
    def get_all_accounts(self):
        """Retrieve all accounts from the Accounts collection"""
        try:
            accounts = list(self.accounts_coll.find({}))
            return accounts
        except Exception as e:
            logger.error(f"Error fetching accounts: {e}")
            return []
    
    def close_connection(self):
        """Close MongoDB connection"""
        self.client.close()

# Initialize MongoDB handler
mongo_handler = MongoDBHandler()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        '👋 Hello! I am your Pokemon Bot.\n\n'
        'Available commands:\n'
        '/start - Show this welcome message\n'
        '/accounts - Show all accounts with FULL session strings\n'
        '/count - Show total number of accounts'
    )

async def accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send all accounts with FULL session strings"""
    try:
        accounts = mongo_handler.get_all_accounts()
        
        if not accounts:
            await update.message.reply_text("📭 No accounts found in the database.")
            return
        
        response = "📱 **All Accounts - Full Session Strings:**\n\n"
        
        for i, account in enumerate(accounts, 1):
            # Extract phone number and session information
            phone_number = account.get('phone_number', 
                              account.get('phone', 
                              account.get('number', 
                              account.get('contact', 'N/A'))))
            
            # Get FULL session string
            session_string = account.get('session_string', 
                                account.get('session', 
                                account.get('session_id', 
                                account.get('auth_string', 'N/A'))))
            
            username = account.get('username', account.get('name', 'N/A'))
            status = account.get('status', account.get('active', 'Unknown'))
            user_id = account.get('user_id', account.get('telegram_id', 'N/A'))
            
            response += f"**{i}. Account #{i}**\n"
            response += f"   📞 **Phone:** `{phone_number}`\n"
            
            if username and username != 'N/A':
                response += f"   👤 **Username:** {username}\n"
            
            if user_id and user_id != 'N/A':
                response += f"   🆔 **User ID:** `{user_id}`\n"
            
            response += f"   📊 **Status:** {status}\n"
            
            # Show FULL session string
            if session_string and session_string != 'N/A':
                response += f"   🔐 **Full Session String:**\n"
                response += f"   `{session_string}`\n"
            else:
                response += f"   🔐 **Session String:** N/A\n"
            
            response += "   " + "─" * 40 + "\n\n"
        
        # Send as multiple messages if too long
        if len(response) > 4096:
            # Split into chunks
            chunks = []
            current_chunk = ""
            
            for line in response.split('\n'):
                if len(current_chunk + line + '\n') > 4096:
                    chunks.append(current_chunk)
                    current_chunk = line + '\n'
                else:
                    current_chunk += line + '\n'
            
            if current_chunk:
                chunks.append(current_chunk)
            
            for i, chunk in enumerate(chunks, 1):
                if i == 1:
                    await update.message.reply_text(chunk, parse_mode='Markdown')
                else:
                    await update.message.reply_text(f"**Continued...**\n\n{chunk}", parse_mode='Markdown')
        else:
            await update.message.reply_text(response, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Error in accounts command: {e}")
        await update.message.reply_text("❌ Sorry, there was an error retrieving the accounts.")

async def count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show total number of accounts"""
    try:
        accounts = mongo_handler.get_all_accounts()
        count = len(accounts)
        await update.message.reply_text(f"📊 **Total Accounts:** {count}")
    except Exception as e:
        logger.error(f"Error in count command: {e}")
        await update.message.reply_text("❌ Error counting accounts.")

def main():
    """Start the bot."""
    # Your bot token
    BOT_TOKEN = "8275817464:AAGnjwnKXvJ9NrTNE4SEnsZAHs1gm1bLDP8"
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("accounts", accounts))
    application.add_handler(CommandHandler("count", count))
    
    # Start the Bot
    logger.info("Bot is running with FULL session strings...")
    application.run_polling()
    
    # Close MongoDB connection when bot stops
    mongo_handler.close_connection()

if __name__ == '__main__':
    main()
