from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ChatJoinRequestHandler
import logging
from datetime import datetime
import sys
import os
from flask import Flask
import asyncio
import threading

# Configuration - Get token from environment variable for security
BOT_TOKEN = "8284891252:AAG8fWcoprmDxe220rz17gD8tg7l32CwD0A"

# Setup logging to suppress unnecessary logs
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Suppress all unnecessary logs
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('apscheduler').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Create Flask app for WSGI
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Auto Join Bot is running!"

@app.route('/health')
def health():
    return "✅ Bot is healthy!"

class AdvancedJoinBot:
    def __init__(self, token):
        self.application = Application.builder().token(token).build()
        self.approved_count = 0
        self.start_time = datetime.now()
        self.setup_handlers()
        
        # Print startup message
        print("🚀 Advanced Join Bot Started!")
        print(f"⏰ Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔑 Token: {BOT_TOKEN[:10]}...")  # Only show first 10 chars for security
    
    def setup_handlers(self):
        self.application.add_handler(ChatJoinRequestHandler(self.handle_join_request))
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
    
    async def handle_join_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Auto-approve join requests with enhanced features"""
        try:
            user = update.chat_join_request.from_user
            chat = update.chat_join_request.chat
            
            # INSTANT APPROVAL
            await update.chat_join_request.approve()
            
            # Update counter
            self.approved_count += 1
            
            # Calculate stats for logging
            uptime = datetime.now() - self.start_time
            hours = uptime.total_seconds() / 3600
            rate_per_hour = self.approved_count / hours if hours > 0 else 0
            
            # Single line log with all info
            username = user.username if user.username else "NoUsername"
            logger.info(f"📥 {user.first_name} (@{username}) joined | Total: {self.approved_count} | Rate: {rate_per_hour:.1f}/hour")
            
            # Send welcome to user
            await self.send_welcome_message(context, user, chat)
            
            # Send notification to channel
            await self.send_channel_notification(context, chat, user)
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
    
    async def send_welcome_message(self, context, user, chat):
        """Send welcome message to the user"""
        try:
            welcome_text = f"Welcome @{user.username if user.username else user.first_name} to {chat.title if chat.title else chat.username}!"
            
            await context.bot.send_message(
                chat_id=user.id,
                text=welcome_text
            )
        except Exception as e:
            logger.warning(f"⚠️ Could not send welcome: {e}")
    
    async def send_channel_notification(self, context, chat, user):
        """Send notification to channel about new member"""
        try:
            notification = f"Welcome @{user.username if user.username else user.first_name} to {chat.title if chat.title else chat.username}!"
            
            await context.bot.send_message(
                chat_id=chat.id,
                text=notification
            )
        except Exception as e:
            # Only log if it's not a permission error (common for channels)
            if "administrator rights" not in str(e):
                logger.warning(f"⚠️ Channel notification failed: {e}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 **Auto Join Bot**\n\n"
            "I automatically accept join requests for our private channel!\n\n"
            "✅ **Status:** ACTIVE\n"
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uptime = datetime.now() - self.start_time
        await update.message.reply_text(
            f"🤖 **Bot Status**\n\n"
            f"✅ **Status:** Running\n"
            f"👥 **Total Approved:** {self.approved_count}\n"
            f"⏰ **Uptime:** {str(uptime).split('.')[0]}\n"
            f"🚀 **Host:** Render Cloud"
        )

# Global bot instance
bot_instance = None

def run_bot():
    """Function to run the bot"""
    global bot_instance
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN environment variable is not set!")
        return
    
    bot_instance = AdvancedJoinBot(BOT_TOKEN)
    
    print("🔄 Starting polling...")
    bot_instance.application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

def start_bot():
    """Start bot in a separate thread"""
    print("🤖 Starting Telegram Bot...")
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    return bot_thread

# Start the bot when the module is imported
print("🚀 Initializing Auto Join Bot...")
bot_thread = start_bot()