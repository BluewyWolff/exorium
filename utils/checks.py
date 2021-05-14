import discord
import aiohttp
from discord.ext import commands

class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.isdigit():
            member_id = int(argument, base=10)
            try:
                return await ctx.guild.fetch_ban(discord.Object(id=member_id))
            except discord.NotFound:
                raise commands.BadArgument('This member has not been banned before.') from None

        elif not argument.isdigit():
            ban_list = await ctx.guild.bans()
            entity = discord.utils.find(lambda u: str(u.user.name) == argument, ban_list)
            if entity is None:
                raise commands.BadArgument('This member has not been banned before.')
            return entity
        
async def lockdown(ctx):
    if ctx.bot.lockdown:
        if ctx.author.id == 809057677716094997:
            return False
        else:
            e = discord.Embed(color=discord.Color.red())
            e.description = f"Esquire is currently undergoing maintenance. Please stand by and wait. If you wanna see what's going on or stay updated on the maintenance, you are free to check out [the status page](https://flitzstudios.instatus.com/)"
            await ctx.send(embed=e)
            return True
    return False
