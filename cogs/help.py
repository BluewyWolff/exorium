import discord
import config
import time
import aiohttp
import psutil
import platform
import asyncio

from discord.ext import commands, menus
from utils.help import PenguinHelp
from utils import default
from collections import Counter


class HelpCog(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot
        bot.help_command = PenguinHelp()
        bot.help_command.cog = self
        self.help_icon = '<:Discovery:845656527347777548>'

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def ping(self, ctx):
        """ See bot's latency to discord """
        discord_start = time.monotonic()
        async with aiohttp.ClientSession() as session:
            async with session.get('https://discord.com') as r:
                if r.status == 200:
                    discord_end = time.monotonic()
                    discord_ms = f"{round((discord_end - discord_start) * 1000)}ms"
                else:
                    discord_ms = "fucking dead"
                await ctx.send(f"\U0001f3d3 Pong   |   {discord_ms}")  # You can use :ping_pong: instead of \U0001f3d3

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def invite(self, ctx):
        """ Invite Esquire to your server """
        e = discord.Embed(color=discord.Color.dark_teal())
        e.description = _('{0}[Default perms]({1})\n {2}[All perms]({3})').format(config.inv, config.invite, config.inv, config.invite2)
        await ctx.send(embed=e)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def privacy(self, ctx):
        """ Read our privacy policy """
        e = discord.Embed(color=discord.Color.dark_teal())
        e.description = _("You can read our privacy policy [on our website](https://glenntwebs.github.io/esqweb/legal.html)")
        await ctx.send(embed=e)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def support(self, ctx):
        """ Get support with Esquire """
        e = discord.Embed(color=discord.Color.dark_teal())
        e.description = _("""
You can get support here:
- [support server]({0})
- [Github issue](https://github.com/flitzstudios/exorium/issues/new)
- [Email us](https://quacky.xyz/email?email=flitzdevelopment@gmail.com)
""").format(config.support)
        await ctx.send(embed=e)

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def suggest(self, ctx, *, suggestion):
        """ Make suggestions for Esquire """
        channel = self.bot.get_channel(839962330787479592)
        if len(suggestion) >= 500:
            return await ctx.send(_("Please make your suggestion shorter then 500 characters."))
        e = discord.Embed(color=discord.Color.orange())
        e.set_author(icon_url=ctx.message.author.avatar_url, name=ctx.message.author)
        e.description = suggestion
        ra = await channel.send(embed=e)
        await ra.add_reaction(config.checkmark)
        await ra.add_reaction(config.crossmark)
        await ctx.send(_("Your suggestion was recorded in our support server."))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def id(self, ctx, member: discord.Member):
        """ Get a user's ID """
        await ctx.reply(member.id)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def av(self, ctx, user: discord.Member = None):
        """ Get a user's avatar """
        if not user:
            user = ctx.message.author

        e = discord.Embed(color=discord.Color.dark_teal())
        e.set_image(url=user.avatar.url)
        e.set_footer(text=f"avatar: {user}")
        await ctx.send(embed=e)

    @commands.command(aliases=["si"])
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def serverinfo(self, ctx):
        """ Get information about the server """

        owner = await self.bot.fetch_user(ctx.guild.owner_id)
        member_count = ctx.guild.member_count  # last known count because you don't have intents
        features = ", ".join(ctx.guild.features).lower().replace('_', ' ').title() if len(ctx.guild.features) != 0 else None
        mfa = _("Optional") if ctx.guild.mfa_level else _("Required")
        verification = str(ctx.guild.verification_level).capitalize()

        e = discord.Embed(color=discord.Color.dark_teal())
        e.set_author(name=_("{0} Information").format(ctx.guild.name), icon_url=ctx.guild.icon_url)
        e.add_field(name=_("**General Information**"),
                    value=_("**Owner:** {0} ({1})\n**Guild Created At:** {2}\n" \
                            "**MFA:** {3}\n**Verification Level:** {4}").format(owner, owner.id, default.date(ctx.guild.created_at), mfa, verification))
        e.add_field(name=_("**Other**"),
                    value=_("**Avg Member Count:** {0:,}\n**Text Channels:** {1}\n" \
                            "**Voice Channels:** {2}").format(member_count, len(ctx.guild.text_channels), len(ctx.guild.voice_channels)))
        #
        if features:
            e.add_field(name="**Server Features**",
                        value=features,
                        inline=False)

        if not ctx.guild.is_icon_animated():
            e.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
        elif ctx.guild.is_icon_animated():
            e.set_thumbnail(url=ctx.guild.icon_url_as(format="gif"))
        if ctx.guild.banner:
            e.set_image(url=ctx.guild.banner_url_as(format="png"))
        e.set_footer(text=f"Guild ID: {ctx.guild.id}")
        await ctx.send(embed=e)

    @commands.command(aliases=["ui"])
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def userinfo(self, ctx, *, user: discord.Member = None):
        """ See a user's info """
        if not user:
            user = ctx.author

        if str(user.status) == 'dnd':
            status = 'Do Not Disturb'
        else:
            status = user.status

        uroles = []
        for role in user.roles:
            if role.is_default():
                continue
            uroles.append(role.mention)

        uroles.reverse()

        if len(uroles) > 10:
            uroles = [f"{', '.join(uroles[:10])} (+{len(user.roles) - 11})"]

        e = discord.Embed(color=user.colour)
        e.set_author(name=user.display_name, icon_url=user.avatar_url)
        e.set_thumbnail(url=user.avatar_url)
        e.description = _("""
**Username:** {0}
**User ID:** {1}
**Created on {2}**
**Joined on {3}**
**Flag value:** {4}
**Status:** {5}
""").format(user, user.id, default.date(user.created_at), default.date(user.joined_at), user.public_flags.value, status)
        if len(uroles) > 0:
            e.add_field(name=_("__**Roles ({0})**__").format(len(user.roles) - 1),
                        value=", ".join(uroles), inline=False)

        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def roleinfo(self, ctx, *, role: discord.Role):
        """ See a role's info """

        managed = _("Yes") if role.managed else _("No")
        hoisted = _("Yes") if role.hoist else _("No")
        position = len(ctx.guild.roles) - role.position
        permissions = dict(role.permissions)
        perms = []
        for perm in permissions.keys():
            if permissions[
                perm] is True and not role.permissions.administrator:  # I guess role.permissions.administrator works, not sure
                perms.append(perm.lower().replace('_', ' ').title())

        if role.permissions.administrator:
            perms.append("Administrator")

        rolemembers = []
        for member in role.members:
            rolemembers.append(member.mention)

        if len(rolemembers) > 10:
            rolemembers = [f"{', '.join(rolemembers[:10])} (+{len(role.members) - 11})"]

        e = discord.Embed(color=role.color)
        e.description = _("""
**ID:** {0}
**Created at:** {1}
**Managed:** {2}
**Position:** {3}
**Hoisted:** {4}
**Color:** `{5}`
**Permissions:** `{6}`
**Members ({7}):** {8} 
""").format(role.id, default.date(role.created_at), managed, position, hoisted, role.colour, "`, `".join(perms), len(role.members), ", ".join(rolemembers))
        await ctx.send(_("Information about role **{0}**").format(role.name), embed=e)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def servericon(self, ctx):
        """ Get the server's icon """
        e = discord.Embed(color=discord.Color.dark_teal())
        e.set_image(url=ctx.guild.icon_url)
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_guild_permissions(add_reactions=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def poll(self, ctx, *, poll):
        """ Host a poll """
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        e = discord.Embed(color=discord.Color.green())
        e.description = poll
        e.set_footer(text=f"Host: {ctx.author}")
        pre = await ctx.send(embed=e)
        await pre.add_reaction(config.checkmark)
        await pre.add_reaction(config.crossmark)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def say(self, ctx, *, say):
        """ Say something with Esquire """
        e = discord.Embed(color=discord.Color.dark_teal())
        e.description = say
        e.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    @commands.command(aliases=["statistics", "about"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stats(self, ctx):
        """ See Esquire's statistics """

        chtypes = Counter(type(c) for c in self.bot.get_all_channels())
        voice = chtypes[discord.channel.VoiceChannel]
        text = chtypes[discord.channel.TextChannel]

        cpup = psutil.cpu_percent()
        core = psutil.cpu_count()
        mem = psutil.virtual_memory().total >> 20
        mem_usage = psutil.virtual_memory().used >> 20
        storage_free = psutil.disk_usage('/').free >> 30

        Joshua = await self.bot.fetch_user(809057677716094997)
        Moksej = await self.bot.fetch_user(345457928972533773)
        # devs = [f"{x.name}#{x.discriminator}" for x in
        #         self.bot.get_guild(755068089233834074).get_role(828339695314403378).members]
        # dev1 = ', '.join(devs)

        e = discord.Embed(color=discord.Color.dark_teal())
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.set_image(url="https://cdn.bluewy.xyz/yerZ.png")

        users = sum(x.member_count for x in self.bot.guilds)

        e.description = _("""
__**About**__
Developers:
- **[{0}](https://discordrep.com/u/809057677716094997#)**
- **[{1}](https://discordrep.com/u/345457928972533773#)**

Library: [enhanced dpy {2}](https://github.com/iDutchy/discord.py)
Links: [github](https://github.com/Foxx-org/exorium) | [Support]({3}) | [Invite]({4}) | [Privacy]({5})

__**Statistics**__
**{6}** Guilds
**{7:,}** Users
**{8:,}** text & **{9:,}** voice channels
**{10:,}** Commands

__**System**__
Hosted on **{11}**
**{12}** cores
**{13}**% CPU load
**{14}**/**{15}** MB memory used
**{16}** GB storage free 
""").format(Joshua, Moksej, discord.__version__, config.support, config.invite, config.privacy, len(self.bot.guilds),
            users, text, voice, len([c for c in set(self.bot.walk_commands())]), platform.platform(), core, cpup, mem_usage, mem, storage_free)

        await ctx.send(embed=e)

    @commands.group(aliases=["emoji", "e"])
    async def emote(self, ctx):
        """ Get emote info/url """
        if ctx.invoked_subcommand is None:
            #await ctx.send_help(ctx.command)
            e = discord.Embed(title=_("Emote help"), color=discord.Color.dark_teal())
            e.description = _("`url` **- Get an emote's URL**\n`info` **- Get info about an emote**")
            await ctx.send(embed=e)

    @emote.group(aliases=["link", "u"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def url(self, ctx, emote: discord.PartialEmoji):
        """ Get an emote's URL """
        await ctx.send(emote.url)

    @emote.group(aliases=["i"])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def info(self, ctx, emote: discord.Emoji):
        """ Get info about an emote """
        e = discord.Embed(color=discord.Color.dark_teal())
        e.set_author(name=emote.name, icon_url=emote.guild.icon_url)
        e.description = _("""
**Created on {0}**
**From** {1} (`{2}`)
**Emote ID:** `{3}`
**Emote URL:** [Click here]({4})
**Escaped:** \{5}
""").format(default.date(emote.created_at), emote.guild, emote.guild_id, emote.id, emote.url, emote)
        e.set_thumbnail(url=emote.url)
        await ctx.send(embed=e)

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def review(self, ctx, *, review):
        """ Review our bot! """
        channel = self.bot.get_channel(839962350521548871)
        e1 = discord.Embed(color=discord.Color.dark_teal())
        e1.set_author(name=_('From {0}').format(ctx.author), icon_url=ctx.author.avatar_url)
        e1.description = review
        await channel.send(embed=e1)
        await ctx.send(_("Thank you! Your review has been recorded in our support server."))

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def announce(self, ctx, channel: discord.TextChannel, *, desc):
        """ Announce something """
        if not channel:
            return await ctx.send(_('Please provide a channel to use.'))
        if len(desc) > 2000:
            return await ctx.send(_('Please make your announcement shorter then 2000 characters.'))
        if len(desc) < 2000:
            e = discord.Embed(color=discord.Color.dark_teal())
            e.description = _("Do you want the message embedded?")

            def check(r, u):
                return u.id == ctx.author.id and r.message.id == checkmsg.id

            try:
                checkmsg = await ctx.send(embed=e)
                await checkmsg.add_reaction(config.checkmark)
                await checkmsg.add_reaction(config.crossmark)
                react, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)

                if str(react) == config.checkmark:
                    try:
                        await checkmsg.clear_reactions()
                    except Exception:
                        pass
                    e = discord.Embed(color=discord.Color.random(), description=desc)
                    e.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                    await channel.send(embed=e)

                    embed = discord.Embed(color=discord.Color.green(), description=_("Sent embedded announcement in **{0}**.").format(channel))
                    await checkmsg.edit(embed=embed)
                    return

                if str(react) == config.crossmark:
                    try:
                        await checkmsg.clear_reactions()
                    except Exception:
                        pass
                    await channel.send(desc)

                    embed2 = discord.Embed(color=discord.Color.green(), description=_("Sent plain announcement in **{0}**.").format(channel))
                    await checkmsg.edit(embed=embed2)
                    return

            except asyncio.TimeoutError:
                try:
                    await checkmsg.clear_reactions()
                except Exception:
                    pass
                etimeout = discord.Embed(color=discord.Color.dark_red(), description=_("Command timed out, canceling..."))
                return await checkmsg.edit(embed=etimeout)


def setup(bot):
    bot.add_cog(HelpCog(bot))
