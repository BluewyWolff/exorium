import discord, asyncio, datetime
from discord.ext import commands

async def remove_reaction(payload):
    channel = payload.member.guild.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    await message.remove_reaction(payload.emoji, payload.member)

class Verification(commands.Cog):
    """ The TPK Verification System | Developed by DuckMasterAl """
    def __init__(self, bot):
        self.bot = bot
        self.channel = 123# Verification Channel ID
        self.message = 123# Verification Message ID
        self.role = 123# Muted (Default Autorole) Role ID

    @commands.Cog.listener('on_raw_reaction_add')
    async def reaction(self, payload):
        """ Checks for a Reaction on the Verification Message """
        if payload.message_id == self.message:
            unverified_role = payload.member.guild.get_role(self.role)
            if unverified_role not in payload.member.roles:# If the member is already verified
                return
            try:
                await payload.member.send('Thanks for wanting to verify in TPK [...]')# Sends the question to the member
            except discord.errors.HTTPException:
                return await remove_reaction(payload)
            else:
                def message_check(m):
                    if payload.member.id == m.author.id and payload.member.dm_channel == m.channel:
                        return True
                    else:
                        return False
                try:
                    msg1 = await self.bot.wait_for('message', check=message_check, timeout=300.0)
                except asyncio.TimeoutError:
                    await msg.edit(content=f'{msg.content}\n:x: You took too long to answer the question!')
                    return await remove_reaction(payload)

            channel = payload.member.guild.get_channel(self.channel)
            warning = ''# New user warning
            if payload.member.created_at >= datetime.datetime.now() - datetime.timedelta(days=7):
                warning = f'\n:warning: This account was made {payload.member.created_at.strftime("%B %d %Y at %H:%M UTC")}'
            
            embed = discord.Embed(title='New Verification Request', description=f'{payload.member.mention} just requested verification{warning}\n**Insert Question Here:**\n{msg1.content}', color=discord.Colour.blurple(), timestamp=payload.member.joined_at)
            embed.set_author(name=str(payload.member), icon_url=payload.member.avatar_url)
            embed.set_footer(text='This user joined the server')
            await channel.send(embed=embed)# Sending the Verification Message

def setup(bot):
    bot.add_cog(Verification(bot))
