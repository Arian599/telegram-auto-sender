import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
import random
from datetime import datetime
import logging
import os

# API credentials from environment variables (secure)
api_id = int(os.getenv('API_ID', '20802334'))
api_hash = os.getenv('API_HASH', '87651f947f76694298cb6db07bf901e0')
string_session = os.getenv('STRING_SESSION', '')

# Target group chat ID
chat_id = -1002307699887
message_text = "یا حسین"

# Time interval settings (2.5 to 3 minutes in seconds)
min_interval = 150  # 2.5 minutes
max_interval = 180  # 3 minutes

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def send_periodic_message():
    # Create Telegram client using string session
    client = TelegramClient(StringSession(string_session), api_id, api_hash)
    
    try:
        # Connect to Telegram (no phone verification needed)
        await client.start()
        logging.info("Successfully connected to Telegram using string session!")
        
        # Verify access to the group
        try:
            entity = await client.get_entity(chat_id)
            logging.info(f"Target group found: {entity.title}")
        except Exception as e:
            logging.error(f"Error finding group: {e}")
            return
        
        logging.info(f"Starting to send '{message_text}' every {min_interval/60:.1f}-{max_interval/60:.1f} minutes...")
        logging.info("Bot is running 24/7. Check logs for activity.")
        
        message_count = 0
        
        # Main message sending loop
        while True:
            try:
                # Send message
                await client.send_message(chat_id, message_text)
                message_count += 1
                
                # Generate random wait time between 2.5-3 minutes
                wait_time = random.randint(min_interval, max_interval)
                next_send_time = datetime.now().timestamp() + wait_time
                next_send_formatted = datetime.fromtimestamp(next_send_time).strftime("%H:%M:%S")
                
                logging.info(f"Message #{message_count} sent successfully. Next message at: {next_send_formatted}")
                
                # Wait for random interval
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                logging.error(f"Error sending message: {e}")
                # Wait 60 seconds before retrying on error
                await asyncio.sleep(60)
                
    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        # Auto-restart after 300 seconds on unexpected errors
        logging.info("Restarting in 5 minutes...")
        await asyncio.sleep(300)
        # Recursive call to restart
        await send_periodic_message()
    finally:
        await client.disconnect()
        logging.info("Telegram connection closed.")

async def main():
    """Main function with auto-restart capability for 24/7 operation"""
    restart_count = 0
    max_restarts = 10
    
    while restart_count < max_restarts:
        try:
            await send_periodic_message()
            restart_count = 0  # Reset counter on successful run
        except Exception as e:
            restart_count += 1
            logging.error(f"Critical error occurred (restart #{restart_count}): {e}")
            if restart_count < max_restarts:
                wait_time = min(300 * restart_count, 1800)  # Exponential backoff, max 30 min
                logging.info(f"Restarting bot in {wait_time//60} minutes...")
                await asyncio.sleep(wait_time)
            else:
                logging.error("Maximum restart attempts reached. Bot stopped.")
                break

if __name__ == "__main__":
    logging.info("=== Telegram Auto Sender Bot Started (24/7 Mode) ===")
    asyncio.run(main())
