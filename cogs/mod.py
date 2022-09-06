import config
import discord
import asyncio
from discord.ext import commands

from utils.checks import BannedMember


class mod(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot
        self.help_icon = "🔨"

    @commands.command(brief="Ban someone")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True, manage_messages=True)
    async def ban(self, ctx, ban_user: discord.User, *, reason=_("No reason provided")):
        """
        Ban the specified user with the specified reason
        *Reason defaults to __no reason specified__*
        """
        try:
            await ctx.guild.fetch_ban(ban_user)
            return await ctx.send(_("You cannot ban someone who is already banned."))
        except discord.NotFound:
            pass
        try:
            if ban_user == ctx.message.author:
                return await ctx.send(_("You can not ban yourself, please try someone else."))

            if ban_user == self.bot.user:
                
                def check(r, u):
                    return u.id == ctx.author.id and r.message.id == checkmsg.id
            
                try:
                    checkmsg = await ctx.reply(_("I guess you want me to leave then <a:sad:663138126767718401> Press the {0} reaction to confirm.").format(config.checkmark))
                    await checkmsg.add_reaction(config.checkmark)
                    await checkmsg.add_reaction(config.crossmark)
                    react, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)
                    
                    if str(react) == config.checkmark:
                        try:
                            await checkmsg.clear_reactions()
                        except Exception:
                            pass
                        await checkmsg.edit(content=_("Okay, leaving this guild."))
                        await ctx.guild.leave()
                        return
                
                    if str(react) == config.crossmark:
                        try: 
                            await checkmsg.clear_reactions()
                        except Exception:
                            pass
                        return await checkmsg.edit(content=_("Okay, i will stay in your server :D"))
                        
                except asyncio.TimeoutError:
                    try:
                        await checkmsg.clear_reactions()
                    except Exception:
                        pass
                    return await checkmsg.edit(content=_("Command timed out, canceling..."))
       
            botmember = ctx.guild.me
            try:
                member = await ctx.guild.fetch_member(ban_user.id)
                if member.top_role > botmember.top_role:
                    return await ctx.send(_("My role is too low in the hierarchy. Please move it above the highest role the user you are trying to ban has."))
                if member.top_role > ctx.author.top_role:
                    return await ctx.send(_("I cannot ban users with a higher role then you."))
                try:
                    await ctx.message.delete()
                except Exception:
                    pass
                try:
                    await member.send(f"You were banned from `{ctx.guild.name}` with reason:\n\n{reason}")
                except discord.errors.HTTPException:
                    pass
                await member.ban(reason=_("Moderator: {0} | Reason: {1}").format(ctx.message.author, reason))
                e = discord.Embed(color=discord.Color.red())
                e.description = _("{0} was banned | {1}").format(member, reason)
                await ctx.send(embed=e)
            except:
                await ctx.guild.ban(ban_user, reason=_("Moderator: {0} | Reason: {1}").format(ctx.message.author, reason))
                e = discord.Embed(title=_("{0} ({1}) was banned | {2}").format(ban_user, ban_user.id, reason), color=discord.Color.red())
                await ctx.send(embed=e)
        except Exception as e:
            await ctx.send(f"```py\n{e}\n```")


    @commands.command(brief="Unban someone from the server")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True, manage_messages=True)
    async def unban(self, ctx, user: BannedMember, *, reason=_("No reason provided")):
        """
        Unban the specified user with the specified reason
        *Reason defaults to __no reason specified__*
        """
        try:
            if user == self.bot.user or user == ctx.message.author:
                return await ctx.send(_("This user was never banned from this guild."), delete_after=5)
            try:
                await ctx.message.delete()
            except Exception:
                pass
            await ctx.guild.unban(user.user, reason=f"moderator: {ctx.message.author} | {reason}")
            e = discord.Embed(color=discord.Color.green())
            e.description = _("{0} has been unbanned | {1}").format(user.user.name, reason)
            await ctx.send(embed=e)
        except Exception as e:
            await ctx.send(f"```py\n{e}\n```")


    @commands.command(brief="Ban and immediately unban someone")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True, manage_messages=True)
    async def softban(self, ctx, member: discord.Member, *, reason=_("No reason provided")):
        """
        bans and unbans the specified user with the specified reason
        *Reason defaults to __no reason specified__*
        """
        try:
            if member == ctx.message.author:
                return await ctx.send(_("You can not softban yourself, please try someone else."))
            if member == self.bot.user:
                return await ctx.send(_("Please softban someone else rather than me, thanks."), delete_after=5)
            botmember = ctx.guild.me
            if member.top_role > botmember.top_role: 
                return await ctx.send(_("My role is too low in the hierarchy. Please move it above the highest role the user you are trying to softban has."))
            try:
                await ctx.message.delete()
            except Exception:
                pass
            messageok = "You were softbanned from `{ctx.guild.name}` with reason:\n\n{reason}"
            try:
                await member.send(messageok)
            except discord.errors.HTTPException:
                pass
            await member.ban(reason=_("Moderator {0} | Reason: {1}").format(ctx.message.author, reason))
            await ctx.guild.unban(member, reason=f"moderator: {ctx.message.author} | softban")
            e = discord.Embed(title=_("{0} was softbanned | {1}").format(member, reason), color=discord.Color.red())
            await ctx.send(embed=e)
        except Exception as e:
            await ctx.send(f"```py\n{e}\n```")


    @commands.command(brief="Kick someone from the server")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=_("No reason provided")):
        """
        Kicks the specified user with the specified reason
        *Reason defaults to __no reason specified__*
        """

        try:
            if member == self.bot.user:
                
                def check(r, u):
                    return u.id == ctx.author.id and r.message.id == checkmsg.id
            
                try:
                    checkmsg = await ctx.reply(_("I guess you want me to leave then <a:sad:663138126767718401> Press the {0} reaction to confirm.").format(config.checkmark))
                    await checkmsg.add_reaction(config.checkmark)
                    await checkmsg.add_reaction(config.crossmark)
                    react, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)
                    
                    if str(react) == config.checkmark:
                        try:
                            await checkmsg.clear_reactions()
                        except Exception:
                            pass
                        await checkmsg.edit(content=_("Okay, leaving this guild."))
                        await ctx.guild.leave()
                        return
                
                    if str(react) == config.crossmark:
                        try: 
                            await checkmsg.clear_reactions()
                        except Exception:
                            pass
                        return await checkmsg.edit(content=_("Okay, i will stay in your server :D"))
                        
                except asyncio.TimeoutError:
                    try:
                        await checkmsg.clear_reactions()
                    except Exception:
                        pass
                    return await checkmsg.edit(content=_("Command timed out, canceling..."))
       
            if member == ctx.message.author:
                return await ctx.send(_("Please kick someone else rather then yourself."), delete_after=5)
            botmember = ctx.guild.me
            if member.top_role > botmember.top_role:
                return await ctx.send(_("My role is too low in the hierarchy. Please move it above the highest role the user you are trying to kick has."))
            try:
                await ctx.message.delete()
            except Exception:
                pass
            messageok = f"You've been kicked from __**{ctx.guild.name}**__ with reason:\n\n{reason}"
            try:
                await member.send(messageok)
            except discord.errors.HTTPException:
                pass
            await member.kick(reason=_("Moderator {0} | Reason: {1}").format(ctx.message.author, reason))
            e = discord.Embed(title=_("{0} was kicked | {1}").format(member, reason), color=discord.Color.red())
            await ctx.send(embed=e)
        except Exception as e:
            await ctx.send(f"```py\n{e}\n```")


    @commands.command(brief="Purge the chat")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def purge(self, ctx, amount=0):
        """ Purge the channel (2-500 messages per purge) """
        def ducks_pin_message_check(duckmasteral):
            if duckmasteral.pinned is False:
                return True
            return False

        if amount <= 1:
            return await ctx.send(_('Please provide a positive number of messages to purge. (Between 2-500 messages)'), delete_after=10)
        if amount >= 500:
            return await ctx.send(_('Please purge less than 500 messages at a time.'), delete_after=10)
        if amount <= 500:
            try:
                try:
                    await ctx.message.delete()
                except Exception:
                    pass
                await ctx.channel.purge(limit=amount, check=ducks_pin_message_check)
                await ctx.send(_('{0} purged {1} messages successfully.').format(ctx.message.author, amount), delete_after=10)
            except Exception as e:
                await ctx.send(f"```py\n{e}\n```")

    # @commands.command()
    # @commands.guild_only()
    # @commands.has_permissions(manage_messages=True)
    # async def warn(self, ctx, user: commands.Greedy[discord.Member], reason="No reason provided"):
    #     await ctx.send(f"Testing {user} with {reason} by {ctx.author}")


def setup(bot):
    bot.add_cog(mod(bot))
