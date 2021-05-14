import asyncio
import discord
import traceback
import config
from discord.ext import commands
#from cogs.admin import admin_only

class error(commands.Cog, name="Error"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, commands.CommandNotFound):
            return

        if isinstance(err, commands.MissingPermissions):
            perms = "`" + '`, `'.join(err.missing_perms) + "`"
            return await ctx.send(f"{config.crossmark} **You are missing {perms} permissions.**")

        if isinstance(err, commands.BotMissingPermissions):
            perms = "`" + '`, `'.join(err.missing_perms) + "`"
            return await ctx.send(f"{config.crossmark} **I'm missing {perms} permissions**")

        if isinstance(err, commands.MissingRequiredArgument):
            return await ctx.send(f"{config.crossmark} **`{err.param.name}` is a required argument!**")

        if isinstance(err, commands.CommandOnCooldown):
            clog = self.bot.get_channel(839963291623096320)
            e = discord.Embed(color=discord.Color.red())
            e.description = f"**{ctx.author} has a `{err.retry_after:.0f}` second cooldown on command `{ctx.command.qualified_name}`**" \
                            f"\nGuild **{ctx.guild}** with ID `{ctx.guild.id}` | User ID: `{ctx.author.id}`"
            await clog.send(embed=e)
            return await ctx.send(f"`{ctx.command.qualified_name}` **is on cooldown for __{err.retry_after:.0f}__ more seconds.**")

        if isinstance(err, commands.NotOwner):
            return await ctx.send(f"{config.crossmark} **Only __bot owners__ can use this command.**")

        if isinstance(err, commands.MemberNotFound):
            return await ctx.send(f"{config.confused} **Could not find user `{err.argument}`**")

        if isinstance(err, commands.ChannelNotFound):
            return await ctx.send(f"{config.confused} **Could not find channel `{err.argument}`**")

        if isinstance(err, commands.MessageNotFound):
            return await ctx.send(f"{config.confused} **Could not find message `{err.argument}`**")

        if isinstance(err, commands.RoleNotFound):
            return await ctx.send(f"{config.confused} **Could not find this role**")
        
        if isinstance(err, commands.EmojiNotFound):
            return await ctx.send(f"{config.confused} **Could not find emote `{err.emote}~**")

        if isinstance(err, commands.NoPrivateMessage):
            return await ctx.send(f"{config.crossmark} **You can only use this command in servers.**")

        if isinstance(err, commands.DisabledCommand):
            return await ctx.send(f"{config.crossmark} **{ctx.command.qualified_name} is currently disabled.**")

        if isinstance(err, commands.CheckFailure):
            await ctx.send(f"{config.crossmark} **You do not have permission to use this command.**")

        else:

            elog = self.bot.get_channel(839963309540638741)
            le = discord.Embed(color=discord.Color.red())
            le.description = f"__**Full traceback**__" \
                            f"\n```py\n{''.join(traceback.format_exception(type(err), err, err.__traceback__))}\n```"
            le.set_author(name=f"{ctx.author} | {ctx.author.id} (Guild {ctx.guild.id})", icon_url=ctx.author.avatar_url)
            await elog.send(embed=le)

            def check(r, u):
                return u.id == ctx.author.id and r.message.id == checkmsg.id

            e = discord.Embed(title="traceback", color=discord.Color.red())
            e.description = f"```py\n{''.join(traceback.format_exception(type(err), err, err.__traceback__))}\n```"
            e.set_footer(text="Do you want a developer to join and investigate?")
            try:
                checkmsg = await ctx.reply(embed=e)
                await checkmsg.add_reaction(config.checkmark)
                await checkmsg.add_reaction(config.crossmark)
                react, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)

                if str(react) == config.checkmark:
                    try:
                        await checkmsg.clear_reactions()
                    except Exception:
                        pass

                    se = discord.Embed(title="traceback", color=discord.Color.red())
                    se.description = f"```py\n{''.join(traceback.format_exception(type(err), err, err.__traceback__))}\n```"
                    se.set_footer(text="A developer will join soon. Thank you.")

                    await checkmsg.edit(embed=se)
                    invite = await ctx.channel.create_invite()
                    return await elog.send(invite)

                if str(react) == config.crossmark:
                    try:
                        await checkmsg.clear_reactions()
                    except Exception:
                        pass

                    se = discord.Embed(title="traceback", color=discord.Color.red())
                    se.description = f"```py\n{''.join(traceback.format_exception(type(err), err, err.__traceback__))}\n```"
                    se.set_footer(text="A invite will not be created.")

                    return await checkmsg.edit(embed=se)

            except asyncio.TimeoutError:
                try:
                    await checkmsg.clear_reactions()
                except Exception:
                    pass

                se = discord.Embed(title="traceback", color=discord.Color.red())
                se.description = f"```py\n{''.join(traceback.format_exception(type(err), err, err.__traceback__))}\n```"
                se.set_footer(text="Automatically canceled notifications.")

                return await checkmsg.edit(embed=se)

    async def bot_check(self, ctx):
        if self.bot.lockdown:
            return await ctx.send(f"{self.bot.user} Is currently undergoing maintenance. Please stand by and wait. If you wanna see what's going on or stay updated on the maintenance, you are free to check out [the status page](https://flitzstudios.instatus.com/)")

def setup(bot):
    bot.add_cog(error(bot))
