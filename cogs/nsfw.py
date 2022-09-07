import requests
import discord
import config

from discord.ext import commands

class nsfw(commands.Cog, name="Nsfw"):
    def __init__(self, bot):
        self.bot = bot
        self.help_icon = '🔞'

    @commands.command()
    async def e621(self, ctx, *, tags):
        if tags.lower() in ["scat", "child"]:
            await ctx.send("This tag is blacklisted.")
            return
        tagurl = tags.replace(' ', '+')
        delmsg = await ctx.send("Waiting for results...")
        response = requests.get(
            f'https://e621.net/posts.json?tags={tagurl}',
            headers={'User-Agent': config.e621agent},
            auth=HTTPBasicAuth(config.e621username, config.e621key)
        )
        if not response.json()["posts"]:
            await delmsg.delete()
            await ctx.send(f"Sadly, we couldn't get you `{tags}`")
            return
        finalimg = random.choice(response.json()["posts"])["file"]["url"]
        while True:
            if finalimg.endswith(".webm"):
                finalimg = random.choice(response.json()["posts"])["file"]["url"]
            else:
                break
        embed = discord.Embed(title='Random yiff')
        embed.set_image(url=finalimg)
        embed.set_footer(text='Powered by e621.')
        await delmsg.delete()
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(nsfw(bot))
