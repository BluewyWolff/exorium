import asyncio
import discord
import traceback
import config
from discord.ext import commands
from utils import checks
#from cogs.admin import admin_only

class error(commands.Cog, name="Error"):
    def __init__(self, bot):
        self.bot = bot

    async def bot_check(self, ctx):
        if await checks.lockdown(ctx):
            return False
        return True


    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, commands.CommandNotFound):
            return

        if isinstance(err, commands.MissingPermissions):
            perms = "`" + '`, `'.join(err.missing_perms) + "`"
            return await ctx.send(_("{0} **You are missing {1} permissions.**").format(config.crossmark, perms))

        if isinstance(err, commands.BotMissingPermissions):
            perms = "`" + '`, `'.join(err.missing_perms) + "`"
            return await ctx.send(_("{0} **I'm missing {1} permissions**").format(config.crossmark, perms))

        if isinstance(err, commands.MissingRequiredArgument):
            return await ctx.send(_("{0} **`{1}` is a required argument!**").format(config.crossmark, err.param.name))

        if isinstance(err, commands.CommandOnCooldown):
            clog = self.bot.get_channel(1017158555620626442)
            e = discord.Embed(color=discord.Color.red())
            e.description = _("**{0} has a `{1:.0f}` second cooldown on command `{2}`**\nGuild **{3}** with ID `{4}` | User ID: `{5}`").format(ctx.author, err.retry_after, ctx.command.qualified_name, ctx.guild, ctx.guild.id, ctx.author.id)
            await clog.send(embed=e)
            return await ctx.send(_("`{0}` **is on cooldown for __{1:.0f}__ more seconds.**").format(ctx.command.qualified_name, err.retry_after))

        if isinstance(err, commands.NotOwner):
            return await ctx.send(_("{0} **Only __bot owners__ can use this command.**").format(config.crossmark))

        if isinstance(err, commands.MemberNotFound):
            return await ctx.send(_("{0} **Could not find user `{1}`**").format(config.confused, err.argument))

        if isinstance(err, commands.ChannelNotFound):
            return await ctx.send(_("{0} **Could not find channel `{1}`**").format(config.confused, err.argument))

        if isinstance(err, commands.MessageNotFound):
            return await ctx.send(_("{0} **Could not find message `{1}`**").format(config.confused, err.argument))

        if isinstance(err, commands.RoleNotFound):
            return await ctx.send(_("{0} **Could not find this role**").format(config.confused))
        
        if isinstance(err, commands.EmojiNotFound):
            return await ctx.send(_("{0} **Could not find emote `{1}~**").format(config.confused, err.emote))
        
        if isinstance(err, discord.NotFound):
            return await ctx.send(_("I could not find the argument you have provided."))

        if isinstance(err, commands.NoPrivateMessage):
            return await ctx.send(_("{0} **You can only use this command in servers.**").format(config.crossmark))

        if isinstance(err, commands.DisabledCommand):
            return await ctx.send(_("{0} **{1} is currently disabled.**").format(config.crossmark, ctx.command.qualified_name))

        #if not isinstance(err, int):
        #    return await ctx.send("You must specify a number!")

        if isinstance(err, commands.CheckFailure):
            return

        else:

            elog = self.bot.get_channel(1017158555620626442)
            le = discord.Embed(color=discord.Color.red())
            le.description = f"\n```py\n{''.join(traceback.format_exception(type(err), err, err.__traceback__))}\n```"
            le.add_field(name="__**Additional information**__",
                         value=f"""
                         **Command:** {ctx.message.clean_content}
                         **Author:** {ctx.author} ({ctx.author.id})
                         **Guild:** {ctx.guild} ({ctx.guild.id})
                         **Channel:** {ctx.channel} ({ctx.channel.id})
                               """)
            await elog.send(embed=le)
            print(err.__traceback__)

            def check(r, u):
                return u.id == ctx.author.id and r.message.id == checkmsg.id

            e = discord.Embed(title="traceback", color=discord.Color.red())
            e.description = f"```py\n{err}\n```"
            #e.description = f"```py\n{''.join(traceback.format_exception(type(err), err, err.__traceback__))}\n```"
            e.set_footer(text=_("Do you want a developer to join and investigate?"))
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
                    se.description = f"```py\n{err}\n```"
                    #se.description = f"```py\n{''.join(traceback.format_exception(type(err), err, err.__traceback__))}\n```"
                    se.set_footer(text=_("A developer will join soon. Thank you."))

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
                    se.set_footer(text=_("A invite will not be created."))

                    return await checkmsg.edit(embed=se)

            except asyncio.TimeoutError:
                try:
                    await checkmsg.clear_reactions()
                except Exception:
                    pass

                se = discord.Embed(title="traceback", color=discord.Color.red())
                se.description = f"```py\n{''.join(traceback.format_exception(type(err), err, err.__traceback__))}\n```"
                se.set_footer(text=_("Automatically canceled notifications."))

                return await checkmsg.edit(embed=se)


def setup(bot):
    bot.add_cog(error(bot))
