import random

import discord, asyncio, config
from discord.ext import commands
from utils import default as functions
import config

class currency(commands.Cog, name="Currency"):
    def __init__(self, bot):
        self.bot = bot
        self.help_icon = '💰'

    @commands.command(aliases=['setbal'])
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def setbalance(self, ctx, member: discord.Member, balance: int):
        """ set someone's balance """
        currency = await self.bot.database.fetchval("SELECT currency FROM gcurrency WHERE guild_id = $1", ctx.guild.id)
        if currency is None:
            currency = 'Ezeqs'

        query = """
INSERT INTO balance VALUES($1, $2, $3)
ON CONFLICT (user_id, guild_id) DO UPDATE
SET money = $3
WHERE balance.guild_id = $2
AND balance.user_id = $1
        """

        await self.bot.database.execute(query, member.id, ctx.guild.id, balance)
        e = discord.Embed(color=discord.Color.grass())
        e.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        e.description = f"Updated {member.mention}'s balance\nnew balance: **{balance:,}** {currency}"
        await ctx.send(embed=e)
        await functions.currencylogs(self, ctx, 'Balance manually adjusted', balance, ctx.author, member)
        # dbchan = await self.bot.database.fetchval("SELECT channel_id FROM moneylogs WHERE guild_id = $1", ctx.guild.id)

        # if not dbchan:
            # return
        # else:
            # channel = self.bot.get_channel(dbchan)

        # await channel.send(f"User {ctx.author} has added {balance} to {member}'s balance.")

    @commands.command(aliases=['resetbal'])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def resetbalance(self, ctx):
        """ Reset your balance to 0"""
        checkmsg = await ctx.send("Are you sure you want to reset your balance?")

        def check(r, u):
            return u.id == ctx.author.id and r.message.id == checkmsg.id

        try:
            await checkmsg.add_reaction(config.checkmark)
            await checkmsg.add_reaction(config.crossmark)
            react, user = await self.bot.wait_for('reaction_add', check=check, timeout=30)

            if str(react) == config.checkmark:
                try:
                    await checkmsg.clear_reactions()
                except Exception:
                    pass
                await self.bot.database.execute("DELETE FROM balance WHERE user_id = $1", ctx.author.id)
                await functions.currencylogs(self, ctx, 'Balance reset', '0', ctx.author, ctx.author)
                await checkmsg.edit(content=_("Your balance has been reset successfully."))
                return

            if str(react) == config.crossmark:
                try:
                    await checkmsg.clear_reactions()
                except Exception:
                    pass
                return await checkmsg.edit(content=_("Your balance will be kept."))

        except asyncio.TimeoutError:
            try:
                await checkmsg.clear_reactions()
            except Exception:
                pass
            return await checkmsg.edit(content=_("Command timed out, canceling..."))

    @commands.command(aliases=['bal'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def balance(self, ctx, member: discord.Member = None):
        """ check your balance """
        currency = await self.bot.database.fetchval("SELECT currency FROM gcurrency WHERE guild_id = $1", ctx.guild.id)
        if currency is None:
            currency = 'Ezeqs'

        if member is None:
            member = ctx.author

        try:
            query = "SELECT money FROM balance WHERE balance.guild_id = $1 AND balance.user_id = $2"

            results = await self.bot.database.fetchval(query, ctx.guild.id, member.id)

            if results is None:
                results = '0'

            e = discord.Embed(color=discord.Color.grassy_green())
            e.title = f"{member}'s balance"
            if member is ctx.author:
                e.description = f"You have **{int(results):,}** {currency}."
            else:
                e.description = f"They have **{int(results):,}** {currency}."

            await ctx.send(embed=e)
        except Exception as e:
            print(e)

    @commands.command()
    @commands.cooldown(1, 500, commands.BucketType.user)
    async def work(self, ctx):
        """ Work for your money """
        currency = await self.bot.database.fetchval("SELECT currency FROM gcurrency WHERE guild_id = $1", ctx.guild.id)
        if currency is None:
            currency = 'Ezeqs'
        addbal = random.randint(100, 500)
        chargebal = random.randint(100, 200)
        response1 = f"You went to work and earned {addbal:,} {currency} through your hard work!"
        response2 = f"You came late, and lost any chance for earning money today."
        response3 = f"You broke the machines while working, and the boss charged back {chargebal:,} {currency}"

        rc = random.choice([response1, response2, response3])

        if rc is response1:

            query = """
            INSERT INTO balance VALUES($1, $2, $3)
            ON CONFLICT (user_id, guild_id) DO UPDATE
            SET money = balance.money + $3
            WHERE balance.guild_id = $2
            AND balance.user_id = $1
                    """

            await self.bot.database.execute(query, ctx.author.id, ctx.guild.id, addbal)
            # self, ctx, action, money, author, user
            await functions.currencylogs(self, ctx, 'Balance updated', addbal, self.bot.user, ctx.author)
            e = discord.Embed(color=discord.Color.grassy_green())
            e.description = response1
            e.set_footer(text="Do e?suggest to suggest responses and other things!")
            await ctx.send(embed=e)

        if rc is response3:
            query = """
            INSERT INTO balance VALUES($1, $2, $3)
            ON CONFLICT (user_id, guild_id) DO UPDATE
            SET money = balance.money - $3
            WHERE balance.guild_id = $2
            AND balance.user_id = $1
            """

            await self.bot.database.execute(query, ctx.author.id, ctx.guild.id, chargebal)
            await functions.currencylogs(self, ctx, 'Balance updated', chargebal, self.bot.user, ctx.author)
            e = discord.Embed(color=discord.Color.bright_red())
            e.description = response3
            e.set_footer(text="Do e?suggest to suggest responses and other things!")
            await ctx.send(embed=e)

        if rc is response2:
            e = discord.Embed(color=discord.Color.bright_red())
            e.description = response2
            e.set_footer(text="Do e?suggest to suggest responses and other things!")
            await ctx.send(embed=e)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pay(self, ctx, member: discord.Member, bal: int):
        """ Pay someone with the money YOU earned """
        if member == ctx.author:
            return await ctx.send("... You can't pay yourself, it doesn't work that way...")

        authorbal = await self.bot.database.fetchval("SELECT money FROM balance WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id)
        if authorbal is None:
            return await ctx.send("You don't have any money yourself, go get a job or something, jeez.")

        if bal > authorbal:
            return await ctx.send("You can't pay someone more then you have, unless you want debts.")

        await self.bot.database.execute("UPDATE balance SET money = balance.money - $1 WHERE guild_id = $2 AND user_id = $3", bal, ctx.guild.id, ctx.author.id)

        query = """
        INSERT INTO balance VALUES($1, $2, $3)
        ON CONFLICT (user_id, guild_id) DO UPDATE
        SET money = balance.money + $3
        WHERE balance.guild_id = $2
        AND balance.user_id = $1
                """

        await self.bot.database.execute(query, member.id, ctx.guild.id, bal)
        await ctx.send(f"{bal:,} has been transferred over to {member}'s balance.")
        # self, ctx, action, money, author, user
        await functions.currencylogs(self, ctx, 'Payment', bal, ctx.author, member)

    @commands.command(aliases=['clogs'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def currencylogs(self, ctx, channel: discord.TextChannel = None):
        """ This enables all currency logs in the specified channel """

        if channel and not channel.can_send or channel and not channel.permissions_for(ctx.guild.me).embed_links:
            return await ctx.send(_("{0} I'm missing permissions in that channel. Make sure you have given me the correct permissions!").format(config.crossmark))

        cl = await self.bot.database.fetchval("SELECT channel_id FROM moneylogs WHERE guild_id = $1", ctx.guild.id)

        if cl and not channel:
            await self.bot.database.execute("DELETE FROM moneylogs WHERE guild_id = $1", ctx.guild.id)
            return await ctx.send("Disabled currency logging.")
        elif cl and channel:
            await self.bot.database.execute("UPDATE moneylogs SET channel_id = $1 WHERE guild_id = $2", channel.id, ctx.guild.id)
            return await ctx.send(f"Your currency logging channel was set to {channel.mention}.")

        elif not cl and not channel:
            return await ctx.send("You do not have a logging channel")

        elif not cl and channel:
            await self.bot.database.execute("INSERT INTO moneylogs VALUES($1, $2)", ctx.guild.id, channel.id)
            return await ctx.send(f"Currency will now be logged in {channel.mention}")

        # await ctx.send(cl)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setcurrency(self, ctx, currency = None):
        """ Set the type of currency to use """
        if currency is None:
            currency = "Ezeqs"

        query = """
        INSERT INTO gcurrency VALUES($1, $2)
        ON CONFLICT (guild_id) DO UPDATE
        SET currency = $2
        WHERE gcurrency.guild_id = $1
                """

        await self.bot.database.execute(query, ctx.guild.id, currency)
        await ctx.send(f"Your currency has been set to {currency}")


def setup(bot):
    bot.add_cog(currency(bot))
