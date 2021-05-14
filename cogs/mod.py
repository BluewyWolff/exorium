import config
import discord
import asyncio
from discord.ext import commands

from utils.checks import BannedMember


class mod(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot
        self.help_icon = "<:ban:842138747134541829>"

    @commands.command(brief="Ban someone")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True, manage_messages=True)
    async def ban(self, ctx, ban_user: discord.User, *, reason="No reason provided"):
        """
        Ban the specified user with the specified reason
        *Reason defaults to __no reason specified__*
        """
        checkmark = '<a:checkmark:813798012399779841>'
        crossmark = '<a:cross:813798012626141185>'
        
        try:
            if ban_user == ctx.message.author:
                return await ctx.send("You can not ban yourself, please try someone else.")
            
            if member.top_role > ctx.author.top_role:
                return await ctx.send("I cannot ban users with a higher role then you.")

            if ban_user == self.bot.user:
                
                def check(r, u):
                    return u.id == ctx.author.id and r.message.id == checkmsg.id
            
                try:
                    checkmsg = await ctx.reply(f"I guess you want me to leave then <:sadcat:647705878597730315> Press the {checkmark} reaction to confirm.")
                    await checkmsg.add_reaction(checkmark)
                    await checkmsg.add_reaction(crossmark)
                    react, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)
                    
                    if str(react) == checkmark:
                        try:
                            await checkmsg.clear_reactions()
                        except Exception:
                            pass
                        await checkmsg.edit(content="Okay, leaving this guild.")
                        await ctx.guild.leave()
                        return
                
                    if str(react) == crossmark:
                        try: 
                            await checkmsg.clear_reactions()
                        except Exception:
                            pass
                        return await checkmsg.edit(content="Okay, i will stay in your server :D")
                        
                except asyncio.TimeoutError:
                    try:
                        await checkmsg.clear_reactions()
                    except Exception:
                        pass
                    return await checkmsg.edit(content="Command timed out, canceling...")
       
            botmember = ctx.guild.me
            if ctx.guild.get_member(ban_user.id) is not None:
                member = ctx.guild.get_member(ban_user.id)
                if member.top_role > botmember.top_role:
                    return await ctx.send("My role is too low in the hierarchy. Please move it above the highest role the user you are trying to ban has.")
                await ctx.message.delete()
                messageok = f"You were banned from `{ctx.guild.name}` with reason:\n\n{reason}"
                try:
                    await member.send(messageok)
                except discord.errors.HTTPException:
                    pass
                await member.ban(reason=f"Moderator: {ctx.message.author} | Reason: {reason}")
                e = discord.Embed(title=f"{member} was banned | {reason}", color=config.red)
                await ctx.send(embed=e)
            else:
                await ctx.guild.ban(ban_user, reason=f"Moderator: {ctx.message.author} | Reason: {reason}")
                e = discord.Embed(title=f"{ban_user} ({ban_user.id}) was banned | {reason}", color=config.red)
                await ctx.send(embed=e)
        except Exception as e:
            await ctx.send(f"```py\n{e}\n```")


    @commands.command(brief="Unban someone from the server")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True, manage_messages=True)
    async def unban(self, ctx, user: BannedMember, *, reason="No reason provided"):
        """
        Unban the specified user with the specified reason
        *Reason defaults to __no reason specified__*
        """
        try:
            if user == self.bot.user or ctx.message.author:
                return await ctx.send(f"This user was never banned from this guild.", delete_after=5)
            await ctx.message.delete()
            await ctx.guild.unban(user.user, reason=f"moderator: {ctx.message.author} | {reason}")
            e = discord.Embed(color=config.green)
            e.description = f"{user.user.name} has been unbanned | {reason}"
            await ctx.send(embed=e)
        except Exception as e:
            await ctx.send(f"```py\n{e}\n```")


    @commands.command(brief="Ban and immediately unban someone")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True, manage_messages=True)
    async def softban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """
        bans and unbans the specified user with the specified reason
        *Reason defaults to __no reason specified__*
        """
        try:
            if member == ctx.message.author:
                return await ctx.send("You can not softban yourself, please try someone else.")
            if member == self.bot.user:
                return await ctx.send(f"Please softban someone else rather than me, thanks.", delete_after=5)
            botmember = ctx.guild.me
            if member.top_role > botmember.top_role: 
                return await ctx.send("My role is too low in the hierarchy. Please move it above the highest role the user you are trying to softban has.")
            await ctx.message.delete()
            messageok = f"You were softbanned from `{ctx.guild.name}` with reason:\n\n{reason}"
            try:
                await member.send(messageok)
            except discord.errors.HTTPException:
                pass
            await member.ban(reason=f"Moderator {ctx.message.author} | Reason: {reason}")
            await ctx.guild.unban(member, reason=f"moderator: {ctx.message.author} | softban")
            e = discord.Embed(title=f"{member} was softbanned | {reason}", color=config.red)
            await ctx.send(embed=e)
        except Exception as e:
            await ctx.send(f"```py\n{e}\n```")


    @commands.command(brief="Kick someone from the server")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """
        Kicks the specified user with the specified reason
        *Reason defaults to __no reason specified__*
        """
        checkmark = '<a:checkmark:813798012399779841>'
        crossmark = '<a:cross:813798012626141185>'
        
        try:
            if member == self.bot.user:
                
                def check(r, u):
                    return u.id == ctx.author.id and r.message.id == checkmsg.id
            
                try:
                    checkmsg = await ctx.reply(f"I guess you want me to leave then <:sadcat:647705878597730315> Press the {checkmark} reaction to confirm.")
                    await checkmsg.add_reaction(checkmark)
                    await checkmsg.add_reaction(crossmark)
                    react, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)
                    
                    if str(react) == checkmark:
                        try:
                            await checkmsg.clear_reactions()
                        except Exception:
                            pass
                        await checkmsg.edit(content="Okay, leaving this guild.")
                        await ctx.guild.leave()
                        return
                
                    if str(react) == crossmark:
                        try: 
                            await checkmsg.clear_reactions()
                        except Exception:
                            pass
                        return await checkmsg.edit(content="Okay, i will stay in your server :D")
                        
                except asyncio.TimeoutError:
                    try:
                        await checkmsg.clear_reactions()
                    except Exception:
                        pass
                    return await checkmsg.edit(content="Command timed out, canceling...")
       
            if member == ctx.message.author:
                return await ctx.send(f"Please kick someone else rather then yourself.", delete_after=5)
            botmember = ctx.guild.me
            if member.top_role > botmember.top_role:
                return await ctx.send("My role is too low in the hierarchy. Please move it above the highest role the user you are trying to kick has.")
            await ctx.message.delete()
            messageok = f"You've been kicked from __**{ctx.guild.name}**__ with reason:\n\n{reason}"
            try:
                await member.send(messageok)
            except discord.errors.HTTPException:
                pass
            await member.kick(reason=f"Moderator {ctx.message.author} | Reason: {reason}")
            e = discord.Embed(title=f"{member} was kicked | {reason}", color=config.red)
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
            return await ctx.send('Please provide a positive number of messages to purge. (Between 2-500 messages)', delete_after=10)
        if amount >= 500:
            return await ctx.send('Please purge less than 500 messages at a time.', delete_after=10)
        if amount <= 500:
            try:
                await ctx.message.delete()
                await ctx.channel.purge(limit=amount, check=ducks_pin_message_check)
                await ctx.send(f'{ctx.message.author} purged {amount} messages successfully.', delete_after=10)
            except Exception as e:
                await ctx.send(f"```py\n{e}\n```")


def setup(bot):
    bot.add_cog(mod(bot))
