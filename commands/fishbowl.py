from twitchio.ext import commands
from typing import Optional
import utils.time_utils as time_utils
import random
import requests

class Fishbowl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="join")
    async def join_fishbowl(self, ctx: commands.Context):
        if ctx.author.is_vip:
            req = requests.post(f"http://localhost:5000/add-fish/{ctx.author.display_name}/vip")
        elif ctx.author.is_broadcaster:
            req = requests.post(f"http://localhost:5000/add-fish/{ctx.author.display_name}/broadcaster")
        elif ctx.author.is_mod:
            req = requests.post(f"http://localhost:5000/add-fish/{ctx.author.display_name}/mod")
        else:
            req = requests.post(f"http://localhost:5000/add-fish/{ctx.author.display_name}/normal")
            
        if req.json()['message'] == "Fish already exists":
            await ctx.reply(f"{ctx.author.display_name}, you are already in the tank!")
        
        await ctx.reply(f"Welcome to the tank {ctx.author.display_name}!")
    
    @commands.command(name="leave")
    async def leave_fishbowl(self, ctx: commands.Context):
        req = requests.post(f"http://localhost:5000/remove-fish/{ctx.author.display_name}")
        if req.json()['message'] == "Fish not found":
            await ctx.reply(f"{ctx.author.display_name}, you are not in the tank!")
        await ctx.reply(f"Goodbye {ctx.author.display_name}!")
        
    @commands.command()
    async def clearfish(self, ctx: commands.Context):
        if ctx.author.is_broadcaster:
            requests.post(f"http://localhost:5000/clear-fishbowl")
            await ctx.reply("Fishbowl cleared!")
        else:
            await ctx.reply("Only broadcaster can use this command!")

def setup(bot):
    bot.add_cog(Fishbowl(bot))