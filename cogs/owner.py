from discord.ext import commands


class owner(commands.Cog, name="Owner"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shutdown", aliases=["logout"])
    @commands.is_owner()
    async def jsk_shutdown(self, ctx: commands.Context):
        """
        Logs this bot out.
        """

        await ctx.send("Logging out now")
        await ctx.bot.logout()

    @commands.command(brief="unload a cog")
    @commands.is_owner()
    async def unload(self, ctx, *, cog):
        if cog == 'cogs.owner':
            await ctx.send('**You cannot unload the owner cog as this cog allows unloading/reloading/loading cogs.**')
            return
        try:
            self.bot.unload_extension(cog)
            await ctx.send(f'Successfully unloaded`{cog}`.')
        except Exception as e:
            await ctx.send(f'Failed to unload {cog}\n```py\n{e}\n```')

    @commands.command(brief="load a cog")
    @commands.is_owner()
    async def load(self, ctx, *, cog):
        try:
            self.bot.load_extension(cog)
            await ctx.send(f'Successfully loaded `{cog}`.')
        except Exception as e:
            await ctx.send(f'Failed to load {cog}\n```py\n{e}\n```')

    @commands.command(brief="Reload a cog")
    @commands.is_owner()
    async def reload(self, ctx, *, cog):
        try:
            self.bot.reload_extension(cog)
            await ctx.send(f'Successfully reloaded `{cog}`.')
        except Exception as e:
            await ctx.send(f'Failed to load {cog}\n```py\n{e}\n```')

    @commands.group(brief="Change bot appearance")
    @commands.is_owner()
    async def change(self, ctx):
        if ctx.invoked_subcommand is None:
            pass
  
    @change.command(brief="Change playing status")
    @commands.is_owner()
    async def playing(self, ctx, *, playing: str):
        try:
            await self.bot.change_presence(
                activity=discord.Game(type=0, name=playing),
                status=discord.Status.online
            )
            await ctx.send(f"Successfully changed Playing status to:\n{playing}")
            await ctx.message.delete()
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @commands.command(brief="Get a gay overlay for your avatar")
    async def gay(self, ctx):
        link = f"https://some-random-api.ml/canvas/gay/?avatar={ctx.message.author.avatar_url}"
        e = discord.Embed(color=config.color)
        e.set_author(name=f"Gay avatar of {ctx.message.author}", icon_url=ctx.message.author.avatar_url)
        e.set_image(url=link)
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(owner(bot))
