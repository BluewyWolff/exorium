import discord
import config
# import aiohttp
# import psutil
import traceback
from discord.ext import commands


def get_prefix(bot, message):
    prefixes = ["daddy "]
    
    return commands.when_mentioned_or(*prefixes)(bot, message)


#  bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True,
#  allowed_mentions=discord.AllowedMentions(roles=False, users=False, everyone=False))

bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True, 
    allowed_mentions=discord.AllowedMentions.none(), 
    max_messages=10000,
    #intents=discord.Intents.all(),
    status=discord.Status.online,
    activity=discord.Activity(type=discord.ActivityType.playing, name='e!help'),
    description="A very gay and annoying beta bot"
)
bot.cmd_edits = {}
bot.msgedit = {}


class EditingContext(commands.Context):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def send(self, content=None, *, tts=False, embed=None, file=None, files=None, delete_after=None, nonce=None, allowed_mentions=discord.AllowedMentions.none()):
        if file or files:
            return await super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions)
        reply = None
        try:
            reply = self.bot.cmd_edits[self.message.id]
        except KeyError:
            pass
        if reply:
            try:
                msg = await reply.edit(content=content, embed=embed, delete_after=delete_after, allowed_mentions=allowed_mentions)
                return msg
            except:
                return
        msg = await super().send(content=content, tts=tts, embed=embed, file=file, files=files, delete_after=delete_after, nonce=nonce, allowed_mentions=allowed_mentions)
        self.bot.cmd_edits[self.message.id] = msg
        return msg


@commands.Cog.listener()
async def on_message(message):
    if message.author.bot:
        return

    try:
        ctx = await bot.get_context(message, cls=EditingContext)
        if ctx.valid:
            msg = await bot.invoke(ctx)
    except:
        return


@commands.Cog.listener()
async def on_message_edit(before, after):

    if before.author.bot:
        return

    if after.content != before.content:
        try:
            ctx = await bot.get_context(after, cls=EditingContext)
            if ctx.valid:
                msg = await bot.invoke(ctx)
        except discord.NotFound:
            return


@commands.Cog.listener()
async def on_ready():
    # activity = discord.Activity(type=discord.ActivityType.watching, name="a movie")
    await bot.change_presence(status=discord.Status.dnd)

for extension in config.extensions:
    try:
        bot.load_extension(extension)
        print(f'[extension] {extension} was loaded successfully!')
    except Exception as e:
        tb = traceback.format_exception(type(e), e, e.__traceback__)
        tbe = "".join(tb) + ""
        print(f'[WARNING] Could not load extension {extension}: {tbe}')

bot.run(config.token)
