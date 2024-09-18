import threading
import os
import atexit

from utils.chatlog_utils import Chatlog
from utils.webui.webui import run_webui
from utils.config_utils import load_twitch_config
import importlib
from utils.bot import Bot
import twitchio

twitch_config = load_twitch_config()
client_id = twitch_config.get("client_id")
client_secret = twitch_config.get("client_secret")
access_token = twitch_config.get("access_token")

if not all([client_id, client_secret, access_token]):
    raise ValueError(
        "Twitch credentials (client_id, client_secret, access_token) are not set properly."
    )

# WebUI thread
webui_thread = threading.Thread(target=run_webui, daemon=True)

chatlog = Chatlog

bot = Bot()

def start_webui():
    print("Starting Web UI!")
    webui_thread.start()


def end_webui():
    print("Stopping Web UI...")
    # Ensure that webui_thread can exit cleanly
    webui_thread.join(timeout=5)


def start_bot():
    load_cogs(bot)
    bot.run()


def load_cogs(bot):
    for filename in os.listdir("./commands"):
        if filename.endswith(".py") and filename != "__init__.py":
            cog_name = filename[:-3]
            module_name = f"commands.{cog_name}"
            try:
                module = importlib.import_module(module_name)
                module.setup(bot)
            except Exception as e:
                print(f"Failed to load cog {module_name}: {e}")

if __name__ == "__main__":
    start_webui()
    # check_and_load_chatlog(time_utils.get_current_time('%m-%d-%Y'))
    atexit.register(end_webui)
    try:
        try:
            start_bot()
        except twitchio.AuthenticationError:
            print(
                "Access token expired or invalid, please ensure client_id and client_secret are set under twitch in config.json..."
            )
            print(
                "If so, open http://localhost:5000/twitch_login in your browser and authorize your bot's account."
            )
            input("Press Enter after login...")
            start_bot()  # Retry starting the bot
    except Exception as e:
        chatlog.save_chatlog()  # Save the chat log if any other exception occurs
        end_webui()  # Ensure web UI ends gracefully
        raise e  # Re-raise the exception for further handling/logging
