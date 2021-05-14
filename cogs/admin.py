import config
import discord
import asyncio
import typing
from discord.ext import commands
from utils import default

def admin():
    async def predicate(ctx):
        return ctx.author.id in ctx.bot.owner_ids
    return commands.check(predicate)

async def suggestion_command(self, ctx, type, color, reason):
    if ctx.channel.id != 839962330787479592:
        return await ctx.send(f"{config.crossmark} You must run this command in a suggestion channel!")
    elif ctx.message.reference is None:
        return await ctx.send(f"{config.crossmark} You must reply to the message you want to approve!")

    if ctx.message.reference.cached_message is None:
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
    else:
        message = ctx.message.reference.cached_message
    embed = message.embeds[0]
    embed.color = color
    if reason is not None:
        embed.add_field(name=f'Reason from {ctx.author.name}', value=str(reason))
    await message.edit(embed=embed)
    user = await self.bot.try_user(int(embed.author.icon_url.split('/')[4]))
    if user is not None:
        try:
            await user.send(content=f"{ctx.author.name} just {type} your suggestion!", embed=embed)
        except:
            pass
    await ctx.send(f'{config.checkmark} {type.capitalize()} the following suggestion.')

class Admin(commands.Cog, name="Admin"):
    def __init__(self, bot):
        self.bot = bot
        self.help_icon = "👑"
   
    @commands.group(invoke_without_command=True, aliases=['s'])
    @admin()
    async def suggestion(self, ctx):
        """ Manage the Suggestion Queue """
        await ctx.send_help(ctx.command)

    @suggestion.command(aliases=['a'])
    @admin()
    async def approve(self, ctx, *, reason=None):
        await suggestion_command(self, ctx, 'approved', discord.Color.green(), reason)

    @suggestion.command(aliases=['d'])
    @admin()
    async def deny(self, ctx, *, reason=None):
        await suggestion_command(self, ctx, 'denied', discord.Color.red(), reason)

    @commands.command()
    @admin()
    async def load(self, ctx, *, cog):
        """
        Load the specified cog
        """
        self.bot.load_extension(f'cogs.{cog}')
        await ctx.send(f"{config.checkmark} loaded cog **{cog}**")
        print(f"{ctx.author} loaded cog \"{cog}\" successfully.")

    @commands.command()
    @admin()
    async def reload(self, ctx, *, cog='~'):
        """
        Reload a specified/all cogs
        """
        if cog == '~':
            for extension in config.extensions:
                self.bot.reload_extension(extension)
            await ctx.send(f"{config.checkmark} Reloaded all cogs successfully.")
            print(f"{ctx.author} reloaded all cogs successfully.")
        else:
            self.bot.reload_extension(f'cogs.{cog}')
            await ctx.send(f"{config.checkmark} Reloaded cog **{cog}**")
            print(f"{ctx.author} reloaded \"{cog}\" successfully.")

    @commands.command()
    @admin()
    async def unload(self, ctx, *, cog):
        """
        Unload the specified cog
        """
        if cog == 'admin':
            return await ctx.send(f"{config.crossmark} Could not unload cog `admin`.")
        self.bot.unload_extension(f'cogs.{cog}')
        await ctx.send(f"{config.checkmark} Unloaded cog **{cog}**")
        print(f"{ctx.author} unloaded \"{cog}\" Successfully.")

    @commands.command()
    @admin()
    async def shutdown(self, ctx):
        """ Shuts down the bot. """
        await ctx.send('Shutting down.')
        await self.bot.change_presence(activity=discord.Game(type=0, name='Shutting Down.'), status=discord.Status.dnd)
        await self.bot.logout()

    @commands.command()
    @admin()
    async def leave(self, ctx, id):
        """
        Forcibly leave a guild through ID
        """

        checkmark = '<a:checkmark:813798012399779841>'
        crossmark = '<a:cross:813798012626141185>'

        def check(r, u):
            return u.id == ctx.author.id and r.message.id == checkmsg.id

        try:
            guild = await self.bot.fetch_guild(id)
        except Exception:
            return await ctx.send('This is not a discord server i\'m in.')
        e = discord.Embed(color=discord.Color.red())
        e.set_thumbnail(url=guild.icon_url)
        e.description = f"""
**Guild name:** {guild.name}
**Guild owner:** {await self.bot.fetch_user(guild.owner_id)}
**Guild owner ID:** {guild.owner_id}
Approximately **N/A** members

Created on {default.date(guild.created_at)}.
__**Are you sure you want me to leave this guild?**__
"""
        try:
            checkmsg = await ctx.send(embed=e)
            await checkmsg.add_reaction(checkmark)
            await checkmsg.add_reaction(crossmark)
            react, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)

            if str(react) == checkmark:
                try:
                    await checkmsg.clear_reactions()
                except Exception:
                    pass
                eleave = discord.Embed(color=discord.Color.dark_red(), description=f"Okay, leaving this guild.")
                await checkmsg.edit(embed=eleave)
                await guild.leave()
                await asyncio.sleep(3)

                log = await self.bot.get_channel(762203326519181312)

                await log.send(f"Forcibly left guild {guild}.")
                return

            if str(react) == crossmark:
                try:
                    await checkmsg.clear_reactions()
                except Exception:
                    pass
                estay = discord.Embed(color=discord.Color.green(), description=f"Okay, staying in this guild.")
                await checkmsg.edit(embed=estay)
                return

        except asyncio.TimeoutError:
            try:
                await checkmsg.clear_reactions()
            except Exception:
                pass
            etimeout = discord.Embed(color=discord.Color.dark_red(), description=f"Command timed out, canceling...")
            return await checkmsg.edit(embed=etimeout)

    @commands.group(aliases=["i"])
    @admin()
    async def info(self, ctx):
        """ Display admin user/guild info """
        if ctx.invoked_subcommand is None:
            e = discord.Embed(title="Info help", color=discord.Color.dark_teal())
            e.description = f"`guild` **- Guild Admin Information**\n`user` **-User Admin Information**"
            await ctx.send(embed=e)

    @info.group(aliases=["g"])
    @admin()
    async def guild(self, ctx, *, guild: int):
        """ Guild Admin Information """

        try:
            guild = self.bot.get_guild(guild)
            owner = await self.bot.fetch_user(guild.owner_id)
        except Exception:
            return await ctx.send("Could not find this guild.")
        sperms = dict(guild.me.guild_permissions)
        perm = []

        for p in sperms.keys():
            if sperms[p] is True and guild.me.guild_permissions.administrator is False:
                perm.append(f"`{p.replace('_', ' ').title()}`")
        if guild.me.guild_permissions.administrator:
            perm.append('Administrator')

        e = discord.Embed(color=discord.Color.dark_teal())
        e.description = f"If you want me to leave this guild, use:\n`exo leave {guild.id}`"
        e.set_thumbnail(url=guild.icon_url)
        e.add_field(name='Generic information', value=f"""
**Server name:** {guild}
**Guild ID:** {guild.id}
**Owner:** {owner} ({guild.owner_id})
**{guild.member_count}** members
**{len(guild.channels)}** channels & **{len(guild.roles)}** roles total
**Created on {default.date(guild.created_at)}**
**Joined on {default.date(guild.get_member(self.bot.user.id).joined_at)}**
""")
        e.add_field(name='My permissions', value=", ".join(perm))
        await ctx.send(guild.id, embed=e)

    @info.group(aliases=["u"])
    @admin()
    async def user(self, ctx, *, user: typing.Union[discord.User, str]):
        """ User Admin Information """
        try:
            e = discord.Embed(color=discord.Color.dark_teal())
            e.set_author(name=user, icon_url=user.avatar_url)
            e.set_thumbnail(url=user.avatar_url)
            e.description = f"""
**User profile:** [{user}](https://discord.com/users/{user.id})
**Avatar URL:** [Click here]({user.avatar_url})
**Created on {default.date(user.created_at)}**
**Public Flags value:** {user.public_flags.value}
**{len([x for x in self.bot.guilds if x.get_member(user.id)])}** mutual servers
"""
            await ctx.send(embed=e)
        except Exception:
            return await ctx.send(f'**I could not find {user} as user.**')
 


def setup(bot):
    bot.add_cog(Admin(bot))
