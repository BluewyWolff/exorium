from discord.ext import commands, tasks
import config
import discordlists
import delpy  # pip install del.py

class DiscordListsPost(commands.Cog, name="DLP"):
    def __init__(self, bot):
        self.bot = bot
        self.api = discordlists.Client(self.bot)  # Create a Client instance
        # self.api.set_auth("discordextremelist.xyz", config.DELTOKEN) # Set authorisation token for a bot list
        self.api.set_auth("top.gg", config.TOPTOKEN)
        self.api.set_auth("discordbotlist.com", config.DBLTOKEN)
        self.api.start_loop()  # Posts the server count automatically every 30 minutes
        self.delpy = delpy.Client(bot, config.DELTOKEN, bot.loop)
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        try:
            await self.delapi.post_stats(guildCount=len(self.bot.guilds), shardCount=len(self.bot.shards))
        except Exception as e:
            channel = self.bot.get_channel(839963309540638741)
            await channel.send(f"Failed to post stats to Discord Extreme List - `{e}`")

    @update_stats.before_loop
    async def before_guild_delete(self):
        await self.bot.wait_until_ready()
        print("[BACKGROUND] Started posting guild & shard count to Discord Extreme List")

    @commands.command()
    @commands.is_owner()
    async def post(self, ctx: commands.Context):
        """
        Manually posts guild count using discordlists.py (BotBlock)
        """
        try:
            result = await self.api.post_count()
        except Exception as e:
            await ctx.send("Request failed: `{}`".format(e))
            return
        await ctx.send("Successfully manually posted server count ({:,}) to {:,} lists."
                       "\nFailed to post server count to {:,} lists.".format(self.api.server_count,
                                                                             len(result["success"].keys()),
                                                                             len(result["failure"].keys())))
def setup(bot):
    bot.add_cog(DiscordListsPost(bot))
