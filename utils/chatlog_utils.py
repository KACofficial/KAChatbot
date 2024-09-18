import os
import json
import threading
import utils.time_utils as time_utils
from typing import Optional

class Chatlog:
    def __init__(self):
        self.chatlog_lock = threading.Lock()
        self.chatlog_struct = {"channels": {}}

    def save_chatlog(self):
        try:
            if not os.path.exists("chatlogs"):
                os.makedirs("chatlogs")
            with self.chatlog_lock:
                with open(f"chatlogs/{time_utils.get_current_time('%m-%d-%Y')}.json", "w") as f:
                    json.dump(self.chatlog_struct, f, indent=2)
        except Exception as e:
            print(f"Error saving chat log: {e}")

    def check_and_load_chatlog(self, date: str):
        try:
            if os.path.exists(f"chatlogs/{date}.json"):
                print(f"Loading chat log for {date}...", end="")
                with self.chatlog_lock:
                    with open(f"chatlogs/{date}.json", "r") as f:
                        self.chatlog_struct = json.load(f)
                print("Done!")
        except Exception as e:
            print(f"Error loading chat log: {e}")
    
    def read_chatlog(self, channel: Optional[str] = None, date: str = None):
        if date is None:
            date = time_utils.get_current_time("%m-%d-%Y")
        if channel is None:
            channel = 'all'
            
        if date is not None:
            date = date.split("/")[-1]
            
        if channel is not None:
            channel = channel.split("/")[-1]
        
            
        chatlog_path = f"chatlogs/{date}.json"
        if os.path.exists(chatlog_path):
            with self.chatlog_lock:
                with open(chatlog_path, "r") as f:
                    chatlog_data = json.load(f)
            
            if channel == 'all':
                return chatlog_data # Return all channels' data
            
            # Return specific channel data if available
            channel_data = chatlog_data.get("channels", {}).get(channel, None)
            return { "channels": { channel: channel_data } } if channel_data else None
        else:
            return None





