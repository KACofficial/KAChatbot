from twitchio.ext import commands
import requests


class Spotify(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="nowplaying")
    async def now_playing(self, ctx: commands.Context):
        req = requests.get("http://localhost:5000/currently_playing_json")
        if req.status_code == 204:
            await ctx.send("No song playing...")
        else:
            content = req.json()
            await ctx.send(f"{content['title']} - {content['artists']}")


def setup(bot: commands.Bot):
    bot.add_cog(Spotify(bot))
