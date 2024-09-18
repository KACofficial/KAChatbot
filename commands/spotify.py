from twitchio.ext import commands
import requests
from typing import Optional
from datetime import datetime, timedelta

class Spotify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_requests = {}  # Dictionary to track user request timestamps

    @commands.command(name="request")
    async def request(self, ctx: commands.Context, *, song: Optional[str] = None):
        if song is None:
            await ctx.reply("Please specify a song to request!")
            return

        user_id = ctx.author.id
        now = datetime.now()

        # Check if user is VIP or broadcaster
        if ctx.author.is_mod or ctx.author.is_vip or ctx.author.is_broadcaster:
            # Skip rate limit for VIPs or broadcasters
            can_request = True
        else:
            # Check last request time
            last_request_time = self.user_requests.get(user_id)
            if last_request_time:
                # Check if 5 minutes have passed since last request
                if now - last_request_time < timedelta(minutes=5):
                    wait_time = timedelta(minutes=5) - (now - last_request_time)
                    minutes, seconds = divmod(wait_time.seconds, 60)
                    await ctx.reply(f"You can only request one song every 5 minutes. Please wait {minutes}m {seconds}s.")
                    return
            
            # Update the last request time
            self.user_requests[user_id] = now
            can_request = True

        # Send the song request to the API
        req = requests.post("http://localhost:5000/request-song", data={"song": song})

        if req.status_code == 200:
            await ctx.reply(f"Song `{song}` requested!")
        else:
            error_message = req.json().get("message", "Failed to request song :(")
            await ctx.reply(error_message)

def setup(bot: commands.Bot):
    bot.add_cog(Spotify(bot))
