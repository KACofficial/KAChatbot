from twitchio.ext import commands
from typing import Optional
import utils.time_utils as time_utils
import random
import requests


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="8ball")
    async def eight_ball(
        self, ctx: commands.Context, *, question: Optional[str] = None
    ):
        
        if question is None:  # if there is no question provided
            await ctx.reply("A question is required!")
            return
        responses = [  # a list of responses the 8ball can give
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes, definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]
        answer = random.choice(responses)
        await ctx.reply(
            f"I respond to `{question}` with, `{answer}`"
        )  # reply with an answer from the 8ball

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send(f"Hello {ctx.author.name}!")

    @commands.command()
    async def dice(self, ctx: commands.Context, sides: Optional[int] = None):
        if sides is None:
            sides = 6
        await ctx.send(
            f"{ctx.author.name} rolled a {sides} sided die and got {random.randint(1, sides)}"
        )

    @commands.command(name="quote")  # the command will be !quote
    async def random_quote(self, ctx: commands.Context):
        try:
            api_url = "https://zenquotes.io/api/random"
            response = requests.get(api_url)
            quote_data = response.json()[0]
        except Exception as e:
            await ctx.reply(f"An error accured while grabbing the quote: {e}")
            return
        await ctx.reply(f"\"{quote_data['q']}\" - {quote_data['a']}")

    @commands.command()
    async def joke(self, ctx: commands.Context):
        try:
            api_url = "https://v2.jokeapi.dev/joke/Programming?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single"  # the api for jokes
            response = requests.get(api_url)
            joke_data = response.json()
        except Exception as e:
            await ctx.reply(f"An error accured while grabbing the joke: {e}")
            return
        try:
            if (
                joke_data["type"] == "twopart"
            ):  # if there is a setup and punchline send post on two different messages
                await ctx.send(f"{joke_data['setup']} | {joke_data['delivery']}")
            elif joke_data["type"] == "single":
                await ctx.send(joke_data["joke"])
        except Exception as e:
            await ctx.reply(f"An error accured while parsing the joke: {e}")
            return

    @commands.command()
    async def coin(self, ctx):  # flips a coin
        """Flip a coin"""
        await ctx.reply(random.choice(["Heads!", "Tails!"]))
    
    @commands.command()
    async def test(self, ctx: commands.Context):
        print(ctx.channel)

    @commands.command()
    async def useless_fact(self, ctx: commands.Context):
        req = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
        fact_data = req.json()
        await ctx.reply(fact_data["text"])

    @commands.command()
    async def discord(self, ctx: commands.Context):
        await ctx.send(f"Join Hackers Nexus here: https://discord.gg/u6E64zkeS6")
    
    @commands.command()
    async def dadjoke(self, ctx: commands.Context):
        try:
            req = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"})
            
            if req.status_code == 200:
                joke = req.json()["joke"]
                await ctx.send(joke)
            else:
                await ctx.send("Couldn't fetch a joke at the moment, try again later!")
        except Exception as e:
            await ctx.reply(f"An error occurred while fetching the joke: {e}")


def setup(bot):
    bot.add_cog(Fun(bot))
