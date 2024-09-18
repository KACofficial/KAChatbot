from twitchio.ext import commands
import requests


class Core(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="lurk")
    async def start_lurking(self, ctx: commands.Context):
        req = requests.post(f"http://localhost:5000/lurk/{ctx.author.display_name}")
        if req.json()['status'] == "success":
            await ctx.send("Started lurking!")
        elif req.json()['status'] == "error" and req.json()['message'] == "Lurker already exists":
            await ctx.send(f"{ctx.author.name}, you are already lurking!")
            
    @commands.command(name="unlurk")
    async def stop_lurking(self, ctx: commands.Context):
        req = requests.post(f"http://localhost:5000/unlurk/{ctx.author.display_name}")
        if req.json()['status'] == "success":
            await ctx.send("Stopped lurking!")
        elif req.json()['status'] == "error" and req.json()['message'] == "Lurker not found":
            await ctx.send(f"{ctx.author.name}, you are not lurking!")


def setup(bot: commands.Bot):
    bot.add_cog(Core(bot))
