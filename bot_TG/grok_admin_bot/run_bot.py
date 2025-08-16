#!/usr/bin/env python3
"""
Simple launcher script for Grok AI Telegram Bot
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

def check_environment():
    """Check if required environment variables are set"""
    load_dotenv()
    
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "OPENAI_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file based on env_example.txt")
        return False
    
    return True

def main():
    """Main launcher function"""
    print("🤖 Grok AI Telegram Bot Launcher")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    print("✅ Environment variables loaded successfully")
    print("🚀 Starting bot...")
    
    try:
        # Import and run the bot
        from main_bot import main as run_bot
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
