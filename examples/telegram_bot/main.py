#!/usr/bin/env python3
"""
Simple Telegram Bot example using Claude MultiAgent Framework
"""

import asyncio
import os
from claude_framework import Framework, track_mcp_call
from claude_framework.templates import TelegramBot

class AIBot(TelegramBot):
    """AI-powered Telegram bot with monitoring"""
    
    def __init__(self, token: str):
        super().__init__(token)
        self.framework = Framework()
        
    @track_mcp_call("telegram_bot", "handle_message")
    async def handle_message(self, message):
        """Process incoming messages with AI"""
        
        # Get architect agent for response planning
        architect = self.framework.get_agent('architect')
        if architect:
            task = {
                'type': 'message_processing',
                'text': message.text,
                'user_id': message.from_user.id
            }
            
            result = await architect.process(task)
            return result.get('response', 'Hello! I am an AI bot powered by Claude MultiAgent Framework.')
        
        return 'Hello! Framework not initialized properly.'
    
    @track_mcp_call("telegram_bot", "handle_photo")
    async def handle_photo(self, photo):
        """Process photo messages"""
        return "Photo received! AI analysis would go here."

async def main():
    """Main bot function"""
    
    # Get bot token from environment
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        print("❌ BOT_TOKEN environment variable is required")
        return
    
    # Initialize and start bot
    bot = AIBot(bot_token)
    
    print("🤖 Starting AI Telegram Bot...")
    print("📊 Monitoring enabled - all MCP calls will be tracked")
    
    await bot.start()

if __name__ == "__main__":
    asyncio.run(main())
