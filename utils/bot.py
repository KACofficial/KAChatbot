from twitchio.ext import commands
from utils.config_utils import load_twitch_config
import utils.time_utils as time_utils
from utils.chatlog_utils import Chatlog


twitch_config = load_twitch_config()
client_id = twitch_config.get("client_id")
client_secret = twitch_config.get("client_secret")
access_token = twitch_config.get("access_token")

chatlog = Chatlog()

class Bot(commands.Bot):
    def __init__(self):
        self.initial_channels = ["epicman21221", "audaciousgabe"]
        self.prefix = '?'
        super().__init__(token=access_token, prefix=self.prefix, initial_channels=self.initial_channels)

    async def event_ready(self):
        chatlog.check_and_load_chatlog(time_utils.get_current_time('%m-%d-%Y'))
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

        for channel in self.initial_channels:
            with chatlog.chatlog_lock:
                # Only initialize chat log if it doesn't already exist
                if channel not in chatlog.chatlog_struct["channels"]:
                    chatlog.chatlog_struct["channels"][channel] = {"chatlog": []}
                
            # channel = self.get_channel(channel)
            # await channel.send("I am here, the one and only KAC Chat Bot!")
        

    async def event_message(self, message):
        if message.echo:
            return

        # Safely append to chatlog_struct
        with chatlog.chatlog_lock:
            chatlog.chatlog_struct["channels"][message.channel.name]["chatlog"].append(
                {
                    "timestamp": time_utils.get_current_time("%Y-%m-%dT%H:%M:%SZ"),
                    "username": message.author.name,
                    "message": message.content,
                    "badges": message.author.badges
                }
            )
        print(f"saving chat: `{message.author.name}: {message.content}`")
        chatlog.save_chatlog()

        await self.handle_commands(message)
    
    async def event_command_error(self, ctx: commands.Context, error):
        command = ctx.message.content.split(" ")[0]
        if isinstance(error, commands.CommandNotFound):
            await ctx.reply(f"Command {command} not found.")
        raise error
