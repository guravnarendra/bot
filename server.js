const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const moment = require('moment');
const fetch = require('node-fetch');

// Configuration - Get token from environment variable for security
const BOT_TOKEN = "8284891252:AAG8fWcoprmDxe220rz17gD8tg7l32CwD0A";
const PORT = process.env.PORT || 3000;
const TARGET_URL = "https://bot-pyjx.onrender.com/";

// Create Express app for health checks
const app = express();

// Middleware to suppress unnecessary logs
const originalConsoleLog = console.log;
console.log = function(message) {
  if (typeof message === 'string' && (
    message.includes('httpx') || 
    message.includes('httpcore') || 
    message.includes('telegram') ||
    message.includes('apscheduler')
  )) {
    return;
  }
  originalConsoleLog.apply(console, arguments);
};

// Ping function to keep the app alive
async function ping() {
  try {
    const res = await fetch(TARGET_URL);
    console.log(`[${new Date().toISOString()}] Ping: ${res.status}`);
  } catch (err) {
    console.error(`[${new Date().toISOString()}] Error:`, err.message);
  }
}

// Setup routes
app.get('/', (req, res) => {
  res.send("🤖 Auto Join Bot is running!");
});

app.get('/health', (req, res) => {
  res.send("✅ Bot is healthy!");
});

class AdvancedJoinBot {
  constructor(token) {
    this.bot = new TelegramBot(token, { 
      polling: true,
      skipPending: true
    });
    this.approvedCount = 0;
    this.startTime = new Date();
    
    this.setupHandlers();
    
    // Print startup message
    console.log("🚀 Advanced Join Bot Started!");
    console.log(`⏰ Started at: ${this.startTime.toLocaleString()}`);
    console.log(`🔑 Token: ${BOT_TOKEN.substring(0, 10)}...`); // Only show first 10 chars for security
  }
  
  setupHandlers() {
    // Handle chat join requests
    this.bot.on('chat_join_request', (msg) => this.handleJoinRequest(msg));
    
    // Command handlers
    this.bot.onText(/\/start/, (msg) => this.startCommand(msg));
    this.bot.onText(/\/status/, (msg) => this.statusCommand(msg));
  }
  
  async handleJoinRequest(msg) {
    try {
      const user = msg.from;
      const chat = msg.chat;
      
      // INSTANT APPROVAL
      await this.bot.approveChatJoinRequest(chat.id, user.id);
      
      // Update counter
      this.approvedCount++;
      
      // Calculate stats for logging
      const uptime = moment().diff(this.startTime);
      const hours = uptime / (1000 * 3600);
      const ratePerHour = hours > 0 ? this.approvedCount / hours : 0;
      
      // Single line log with all info
      const username = user.username ? user.username : "NoUsername";
      console.log(`📥 ${user.first_name} (@${username}) joined | Total: ${this.approvedCount} | Rate: ${ratePerHour.toFixed(1)}/hour`);
      
      // Send welcome to user
      await this.sendWelcomeMessage(user, chat);
      
      // Send notification to channel
      await this.sendChannelNotification(chat, user);
      
    } catch (error) {
      console.error(`❌ Error: ${error.message}`);
    }
  }
  
  async sendWelcomeMessage(user, chat) {
    try {
      const welcomeText = `Welcome @${user.username || user.first_name} to ${chat.title || chat.username}!`;
      
      await this.bot.sendMessage(
        user.id,
        welcomeText
      );
    } catch (error) {
      console.warn(`⚠️ Could not send welcome: ${error.message}`);
    }
  }
  
  async sendChannelNotification(chat, user) {
    try {
      const notification = `Welcome @${user.username || user.first_name} to ${chat.title || chat.username}!`;
      
      await this.bot.sendMessage(
        chat.id,
        notification
      );
    } catch (error) {
      // Only log if it's not a permission error (common for channels)
      if (!error.message.includes('administrator rights')) {
        console.warn(`⚠️ Channel notification failed: ${error.message}`);
      }
    }
  }
  
  async startCommand(msg) {
    const chatId = msg.chat.id;
    
    await this.bot.sendMessage(
      chatId,
      "🤖 **Auto Join Bot**\n\n" +
      "I automatically accept join requests for our private channel!\n\n" +
      "✅ **Status:** ACTIVE\n",
      { parse_mode: 'Markdown' }
    );
  }
  
  async statusCommand(msg) {
    const chatId = msg.chat.id;
    const uptime = moment().diff(this.startTime);
    const uptimeString = moment.utc(uptime).format('HH:mm:ss');
    
    await this.bot.sendMessage(
      chatId,
      `🤖 **Bot Status**\n\n` +
      `✅ **Status:** Running\n` +
      `👥 **Total Approved:** ${this.approvedCount}\n` +
      `⏰ **Uptime:** ${uptimeString}\n` +
      `🚀 **Host:** ${process.env.RENDER ? 'Render Cloud' : 'Local'}`,
      { parse_mode: 'Markdown' }
    );
  }
  
  run() {
    console.log("🔄 Starting polling...");
    // Polling is automatically started when creating the bot instance
  }
}

function runBot() {
  if (!BOT_TOKEN) {
    console.log("❌ ERROR: BOT_TOKEN environment variable is not set!");
    return;
  }
  
  const bot = new AdvancedJoinBot(BOT_TOKEN);
  bot.run();
}

function runWebServer() {
  console.log(`🌐 Express server starting on http://0.0.0.0:${PORT}`);
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`✅ Server is running on port ${PORT}`);
    
    // Start ping interval after server is running
    console.log(`🔄 Starting ping service to ${TARGET_URL} every 5 minutes`);
    
    // Ping immediately
    ping();
    
    // Ping every 5 minutes (300,000 milliseconds)
    setInterval(ping, 5 * 60 * 1000);
  });
}

// Main execution
if (require.main === module) {
  // Check if we're running on Render (has RENDER environment variable)
  if (process.env.RENDER || process.env.PORT) {
    console.log("🌐 Render environment detected!");
    
    // Start web server
    runWebServer();
    
    // Start bot
    runBot();
  } else {
    // Local development
    console.log("💻 Local development environment");
    
    console.log("🌐 Starting Express server...");
    runWebServer();
    
    console.log("🤖 Starting Telegram bot...");
    runBot();
  }
}