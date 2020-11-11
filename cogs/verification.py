import discord
from discord.ext import commands

class Verification(commands.Cog):
    """ The TPK Verification System | Developed by DuckMasterAl """
    def __init__(self, bot):
        self.bot = bot
        self.channel = 123# Verification Channel ID
        self.message = 123# Verification Message ID

    @commands.Cog.listener('on_raw_reaction_add')
    async def reaction(self, payload):
        """ Checks for a Reaction on the Verification Message """
        if payload.message_id == self.message:
            try:
                await payload.member.send('Thanks for wanting to verify in TPK [...]')# wait_for
            except discord.errors.HTTPException:
                channel = guild.get_channel(payload.channel_id)
                message = await channel.fetch_message(payload.message_id)
                return await message.remove_reaction(payload.emoji, payload.member)
            channel = payload.guild.get_channel(self.channel)
            await channel.send('hi nerd')# Verification Message

def setup(bot):
    bot.add_cog(Verification(bot))
