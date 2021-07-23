import discord
import config

from discord.ext import commands

class management(commands.Cog, name="Management"):
    def __init__(self, bot):
        self.bot = bot
        self.help_icon = '<:cog:863130088547287070>'

    @commands.group()
    async def prefix(self, ctx):
        if ctx.invoked_subcommand is None:
            results = await self.bot.database.fetchval(f"SELECT prefix FROM guildprefix WHERE guild_id = $1", ctx.guild.id)

            await ctx.send(f"The guild prefix is currently `{'`e?`' if not results else results}`. You can change it using `prefix set <prefix>`.")

    @prefix.command(name="set")
    @commands.has_permissions(manage_guild=True)
    async def prefix_set(self, ctx, prefix):
        if len(prefix) > 10:
            return await ctx.send("Your prefix can not be longer than 10 characters!")

        if prefix == 'e?':
            await self.bot.database.execute(f"DELETE FROM guildprefix WHERE guild_id = $1", ctx.guild.id)
            return await ctx.send("The prefix has been changed back to the default. (`e?`)")

        else:
            query = """
            INSERT INTO guildprefix VALUES($1, $2)
            ON CONFLICT (guild_id) DO UPDATE
            SET prefix = $2
            WHERE guildprefix.guild_id = $1
                    """

            await self.bot.database.execute(query, ctx.guild.id, prefix)
            await ctx.send(f"The prefix has successfully changed to `{prefix}`.")

def setup(bot):
    bot.add_cog(management(bot))