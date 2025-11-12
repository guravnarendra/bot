from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, ChatJoinRequestHandler
import logging
import os
from flask import Flask
import threading

# Configuration - Get token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8317002546:AAH9W9ieBPil6HGKm_K3yikJ7MPtvJ5hR1Q')

# Setup clean logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

# Suppress spam logs
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Create Flask app for health checks
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Auto Join Bot is running!"

@app.route('/health')
def health():
    return "✅ Bot is healthy!"

class AdvancedJoinBot:
    def __init__(self):
        self.updater = Updater(BOT_TOKEN, use_context=True)
        self.approved_count = 0
        self.setup_handlers()
        print("🚀 Advanced Join Bot Initialized!")
    
    def setup_handlers(self):
        # For python-telegram-bot v13, we use different approach
        dp = self.updater.dispatcher
        
        # Add join request handler
        dp.add_handler(ChatJoinRequestHandler(self.handle_join_request))
        dp.add_handler(CommandHandler("start", self.start_command))
    
    def handle_join_request(self, update: Update, context: CallbackContext):
        user = update.chat_join_request.from_user
        chat = update.chat_join_request.chat
        
        # Approve the request
        update.chat_join_request.approve()
        self.approved_count += 1
        
        username = user.username if user.username else "NoUsername"
        logger.info(f"📥 {user.first_name} (@{username}) joined | Total: {self.approved_count}")
        
        # Send welcome
        try:
            welcome_text = f"Welcome @{username} to {chat.title if chat.title else 'the channel'}!"
            context.bot.send_message(chat_id=user.id, text=welcome_text)
        except Exception as e:
            logger.warning(f"⚠️ Welcome failed: {e}")
    
    def start_command(self, update: Update, context: CallbackContext):
        update.message.reply_text("🤖 Auto Join Bot - Status: ACTIVE ✅")
    
    def run(self):
        print("🔄 Starting polling...")
        self.updater.start_polling()
        print("✅ Bot is now running!")
        self.updater.idle()

def run_flask():
    """Run Flask web server"""
    port = int(os.environ.get('PORT', 3000))
    print(f"🌐 Flask server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def run_bot():
    """Run Telegram bot"""
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN not set!")
        return
    
    try:
        bot = AdvancedJoinBot()
        bot.run()
    except Exception as e:
        print(f"❌ Bot error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # Check if running on Render
    if os.environ.get('RENDER') or os.environ.get('PORT'):
        print("🌐 Render environment detected!")
        
        # Start Flask in a thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Run bot in main thread
        run_bot()
    else:
        # Local development
        print("💻 Local development environment")
        
        # Start Flask in a thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Run bot in main thread
        run_bot()