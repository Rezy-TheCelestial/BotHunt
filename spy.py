import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Your MongoDB configuration from the screenshot
MONGO_URI = "mongodb+srv://pokemon_bot_user:PokemonBot2024!Secure@cluster0pokemon-bot-clu.iveqoue.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0pokemon-bot-cluster"
DB_NAME = "pokemon_guess_bot"
ACCOUNTS_COLL = "Accounts"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class MongoDBHandler:
    def __init__(self):
        self.client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        self.db = self.client[DB_NAME]
        self.accounts_coll = self.db[ACCOUNTS_COLL]
        
    def get_all_accounts(self):
        """Retrieve all accounts from the Accounts collection"""
        try:
            # Get all accounts and sort by account number if available
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
        '/accounts - Show all accounts with numbers'
    )

async def accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send all accounts with their numbers when /accounts is issued."""
    try:
        # Get all accounts from MongoDB
        accounts = mongo_handler.get_all_accounts()
        
        if not accounts:
            await update.message.reply_text("📭 No accounts found in the database.")
            return
        
        # Format the response
        response = "📋 **All Accounts:**\n\n"
        
        for i, account in enumerate(accounts, 1):
            # Extract account information - adjust field names based on your actual document structure
            account_id = account.get('_id', 'N/A')
            account_number = account.get('account_number', account.get('number', i))
            username = account.get('username', account.get('name', 'N/A'))
            email = account.get('email', 'N/A')
            status = account.get('status', account.get('active', 'Unknown'))
            
            response += f"**{i}. Account Details:**\n"
            response += f"   🔢 Number: {account_number}\n"
            response += f"   👤 Username: {username}\n"
            if email and email != 'N/A':
                response += f"   📧 Email: {email}\n"
            response += f"   📊 Status: {status}\n"
            response += "   " + "─" * 30 + "\n"
        
        # If response is too long, split it into multiple messages
        if len(response) > 4096:  # Telegram message limit
            chunks = [response[i:i+4096] for i in range(0, len(response), 4096)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode='Markdown')
        else:
            await update.message.reply_text(response, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Error in accounts command: {e}")
        await update.message.reply_text("❌ Sorry, there was an error retrieving the accounts.")

async def debug_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Debug command to see the actual structure of account documents"""
    try:
        accounts = mongo_handler.get_all_accounts()
        
        if not accounts:
            await update.message.reply_text("No accounts found.")
            return
            
        # Show the first account's structure
        sample_account = accounts[0]
        response = "🔍 **Account Document Structure:**\n\n"
        response += "```json\n"
        import json
        response += json.dumps(sample_account, indent=2, default=str)
        response += "\n```"
        
        await update.message.reply_text(response, parse_mode='MarkdownV2')
        
    except Exception as e:
        logger.error(f"Error in debug command: {e}")
        await update.message.reply_text(f"Error: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates."""
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    """Start the bot."""
    # Replace with your actual bot token
    BOT_TOKEN = "8275817464:AAGnjwnKXvJ9NrTNE4SEnsZAHs1gm1bLDP8"
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("accounts", accounts))
    application.add_handler(CommandHandler("debug", debug_accounts))  # Optional debug command
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    logger.info("Bot is running...")
    application.run_polling()
    
    # Close MongoDB connection when bot stops
    mongo_handler.close_connection()

if __name__ == '__main__':
    main()