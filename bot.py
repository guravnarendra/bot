from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, ChatJoinRequestHandler
import logging
from datetime import datetime
import sys
import os
from flask import Flask
import threading
import time

# Configuration
BOT_TOKEN = "8284891252:AAG8fWcoprmDxe220rz17gD8tg7l32CwD0A"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Suppress unnecessary logs
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('apscheduler').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Auto Join Bot is running!"

@app.route('/health')
def health():
    return "✅ Bot is healthy!"

@app.route('/bot-status')
def bot_status():
    return "✅ Bot is running!"

class AdvancedJoinBot:
    def __init__(self, token):
        self.token = token
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.approved_count = 0
        self.start_time = datetime.now()
        self.setup_handlers()
        
        print("🚀 Advanced Join Bot Started!")
        print(f"⏰ Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔑 Token: {self.token[:10]}...")
    
    def setup_handlers(self):
        self.dispatcher.add_handler(ChatJoinRequestHandler(self.handle_join_request))
        self.dispatcher.add_handler(CommandHandler("start", self.start_command))
        self.dispatcher.add_handler(CommandHandler("status", self.status_command))
    
    def handle_join_request(self, update: Update, context: CallbackContext):
        try:
            user = update.chat_join_request.from_user
            chat = update.chat_join_request.chat
            
            # INSTANT APPROVAL
            update.chat_join_request.approve()
            self.approved_count += 1
            
            username = user.username if user.username else "NoUsername"
            logger.info(f"📥 {user.first_name} (@{username}) joined | Total: {self.approved_count}")
            
            self.send_welcome_message(context, user, chat)
            self.send_channel_notification(context, chat, user)
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
    
    def send_welcome_message(self, context, user, chat):
        try:
            welcome_text = f"Welcome @{user.username if user.username else user.first_name} to {chat.title if chat.title else chat.username}!"
            context.bot.send_message(chat_id=user.id, text=welcome_text)
        except Exception as e:
            logger.warning(f"⚠️ Could not send welcome: {e}")
    
    def send_channel_notification(self, context, chat, user):
        try:
            notification = f"Welcome @{user.username if user.username else user.first_name} to {chat.title if chat.title else chat.username}!"
            context.bot.send_message(chat_id=chat.id, text=notification)
        except Exception as e:
            if "administrator rights" not in str(e):
                logger.warning(f"⚠️ Channel notification failed: {e}")
    
    def start_command(self, update: Update, context: CallbackContext):
        update.message.reply_text("🤖 **Auto Join Bot**\n\nI automatically accept join requests!\n\n✅ **Status:** ACTIVE")
    
    def status_command(self, update: Update, context: CallbackContext):
        uptime = datetime.now() - self.start_time
        update.message.reply_text(f"🤖 **Bot Status**\n\n✅ **Running**\n👥 **Approved:** {self.approved_count}\n⏰ **Uptime:** {str(uptime).split('.')[0]}")
    
    def run(self):
        print("🔄 Starting bot polling...")
        self.updater.start_polling()
        self.updater.idle()

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Flask server starting on port {port}")
    print(f"📊 Health check: http://localhost:{port}/health")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Always run both locally and on Render
    print("🚀 Starting both bot and Flask server...")
    
    # Start Flask in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    time.sleep(2)  # Give Flask a moment to start
    
    print("✅ Flask server started in background")
    print("🤖 Starting Telegram bot in main thread...")
    
    # Run bot in main thread
    bot = AdvancedJoinBot(BOT_TOKEN)
    bot.run()