from logging import Logger
import discord
from discord import app_commands, Interaction, Embed, ui
from collections import deque
from discord.ext import commands
from ..main import getorfetch_user, makeembed
import datetime
import traceback
import pkgutil
import os
from typing import Optional, NamedTuple, Any, Union, List, Collection

class CopiedMessage(NamedTuple):
    content: Optional[str]
    files: list[discord.File]
    embeds: list[discord.Embed]
    view: Optional[discord.ui.View]
    replied_message: Optional[discord.Message]
    copied_replied_message: Optional["CopiedMessage"]
    created_at: datetime.datetime
    edited_at: Optional[datetime.datetime]
    author: Union[discord.User, discord.Member]

    def as_kwargs(self) -> dict[str, Any]:
        content = self.content
        if reply := self.replied_message:
            msg = f"Replied to {reply.jump_url}"
            if content:
                content = f"{reply}\n\n{content}"
            else:
                content = msg
        
        return {
            "content": content,
            "files": self.files,
            "embeds": self.embeds,
            "view": self.view
        }
    
    def __str__(self):
        returnv =  f"[<t:{int(self.created_at.timestamp())}:T>] {self.author}: {self.content}"
        if self.edited_at is not None:
            returnv += f" (edited <t:{int(self.edited_at.timestamp())}>"
        if self.replied_message is not None:
            returnv += f" (replied to {self.replied_message.jump_url})"
        return returnv

me: Collection[int] = []
logger_: Optional[Logger] = None
guilds: List[int] = []


emojidict: dict[str | int, str] = {
'discord': '<:discord:1080925531580682360>',
# global
"x": '<a:X_:1046808381266067547>',
'x2': "\U0000274c",
"check": '<a:check_:1046808377373769810>',
"check2": '\U00002705',

"calendar": "\U0001f4c6",
"notepad": "\U0001f5d2",
"alarmclock": "\U000023f0",
"timer": "\U000023f2",
True: "<:check:1046808377373769810>",
"maybe": "\U0001f937",
False: "<a:X_:1046808381266067547>",
"pong": "\U0001f3d3",

}


async def copy_message(
    message: discord.Message,
) -> CopiedMessage:
    files = [
        await a.to_file()
        for a in message.attachments
    ]
    view = discord.ui.View.from_message(message)
    reply = None
    if (ref := message.reference):
        if (refs := ref.resolved) and isinstance(refs, discord.Message):
            reply = refs

    copied_reply = await copy_message(reply) if reply else None
    return CopiedMessage(
        content=message.content,
        embeds=message.embeds,
        files=files,
        view=view,
        replied_message=reply,
        copied_replied_message=copied_reply,
        created_at=message.created_at,
        edited_at=message.edited_at,
        author=message.author
    )

class EmbedPaginatorView(ui.View):
    def __init__(self, embeds: List[Embed]):
        self._embeds = embeds
        self._queue = deque(embeds) # collections.deque
        self._initial = embeds[0]
        self._len = len(embeds)

        super().__init__(timeout=90)

    @ui.button(emoji='\N{LEFTWARDS BLACK ARROW}')
    async def previous_embed(self, interaction: Interaction, button: ui.Button):
        self._queue.rotate(-1)
        embed = self._queue[0]
        await interaction.response.edit_message(embed=embed)


    @ui.button(emoji='\N{BLACK RIGHTWARDS ARROW}')
    async def next_embed(self, interaction: Interaction, button: ui.Button):
        self._queue.rotate(1)
        embed = self._queue[0]
        await interaction.response.edit_message(embed=embed)

    @property
    def initial(self) -> Embed:
        return self._initial

# sending it

async def reload_autocomp(interaction, current: str) -> List[app_commands.Choice[str]]:
    if interaction.user.id in me:
        returnv: List[app_commands.Choice[str]] = []
        returnv2: List[app_commands.Choice[str]] = []
        current = current.lower().strip()
        for ext in pkgutil.iter_modules():
            name = ext.name
            if name+'.py' in os.listdir():
                name = name.lower().strip()
                if name.startswith(current):
                    returnv.append(app_commands.Choice(name=ext.name,value=ext.name))
                elif name in current:
                    returnv2.append(app_commands.Choice(name=ext.name,value=ext.name))
            if len(returnv) + len(returnv2) >= 25:
                break
        returnv.extend(returnv2)
        return returnv
    return []

def logger_info(message: str) -> bool:
    global logger_
    if logger_ is not None:
        logger_.info(message)
        return True
    return False

def logger_warning(message: str) -> bool:
    global logger_
    if logger_ is not None:
        logger_warning(message)
        return True
    return False

def logger_error(message: str) -> bool:
    global logger_
    if logger_ is not None:
        logger_error(message)
        return True
    return False

def is_me():
    def predicate(interaction: discord.Interaction) -> bool:
        if isinstance(interaction.client, commands.Bot):
            return interaction.client.is_owner(interaction.user)
    return app_commands.check(predicate)

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
    @commands.hybrid_command(name="ping",description="see what the bot's ping is",) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
    async def ping(self, ctx: commands.Context):
        msg: Optional[discord.Message] = None
        a: float = datetime.datetime.now().timestamp()
        if ctx.interaction is None: await ctx.message.add_reaction(str(emojidict.get('pong')))
        else: msg = await ctx.reply("Testing ping...")
        b: float = datetime.datetime.now().timestamp()
        if msg: await msg.edit(content=f"{emojidict.get('pong')} Pong! Latency is `{str(self.bot.latency*1000)}`ms (edit time `{round(b-a)}`).")
        else: await ctx.reply(f"{emojidict.get('pong')} Pong! Latency is `{str(self.bot.latency*1000)}`ms (edit time `{round(b-a)}`).")
        logger_info(f"Latency is {str(self.bot.latency*1000)}ms (edit time {round(b-a)}).")

    @commands.hybrid_command(name='updatecommands',description='Owner only. Updates command tree.',with_app_command=True, guilds=[discord.Object(x) for x in guilds])
    @app_commands.guilds(*guilds)
    @is_me()
    async def updatecommands(self, ctx: commands.Context,guildonly: bool=False,guildid: Optional[str]=None):
        await ctx.defer(ephemeral=True)
        guildid_: Optional[int] = None
        if ctx.author.id in me:
            if guildonly and ctx.guild:
                if guildid is None: guildid_ = ctx.guild.id
                else: guildid_ = int(guildid)
                await self.bot.tree.sync(guild=discord.Object(int(guildid_)))
            elif not guildonly:
                await self.bot.tree.sync()
            date = datetime.datetime.fromtimestamp(int(datetime.datetime.timestamp(datetime.datetime.now())))
            print(f"{date}: updated tree")
            await ctx.reply("Updated command tree.",ephemeral=True)
            logger_info(f"Updated command tree: guildonly: {guildonly}, guildid: {guildid}")
        else:
            await ctx.reply("You are not authorized to run this command.",delete_after=5,ephemeral=True)

    @app_commands.command(name='changestatus',description='Changes the status of the bot.')
    @app_commands.choices(activitytype=[
    app_commands.Choice(name='Playing',value=1),
    app_commands.Choice(name='Streaming',value=2),
    app_commands.Choice(name='Listening (to)',value=3),
    app_commands.Choice(name='Watching',value=4),
    app_commands.Choice(name='Custom',value=5),
    app_commands.Choice(name='Competing',value=6),
    ],
    statustype=[
    app_commands.Choice(name='Online',value=1),
    app_commands.Choice(name='Offline',value=2),
    app_commands.Choice(name='Idle',value=3),
    app_commands.Choice(name='Do Not Disturb',value=4),
    app_commands.Choice(name='Invisible',value=5),
    ])
    @app_commands.guilds(*guilds)
    @is_me()
    async def changestatus(self, interaction: discord.Interaction, activitytype: Optional[app_commands.Choice[int]]=None, activitytext: Optional[str]=None, statustype: Optional[app_commands.Choice[int]]=None):
        if interaction.user.id not in me:
            await interaction.response.send_message("This command is not for you")
            return

        activitytype_: int

        if activitytype is not None:
            activitytype_ = activitytype.value
        else:
            activitytype_ = 7

        if statustype is not None:
            statustype_ = statustype.value
        else:
            statustype_ = 6

        if activitytext is None:
            activitytext = self.bot.activity.name

        activity: Optional[discord.Activity] = None
        status: Optional[discord.Status] = None

        if activitytype == 1:
            activity = discord.Activity(type=discord.ActivityType.playing,name=activitytext)
        elif activitytype == 2:
            activity = discord.Activity(type=discord.ActivityType.streaming,name=activitytext)
        elif activitytype == 3:
            activity = discord.Activity(type=discord.ActivityType.listening,name=activitytext)
        elif activitytype == 4:
            activity = discord.Activity(type=discord.ActivityType.watching,name=activitytext)
        elif activitytype == 5:
            activity = discord.Activity(type=discord.ActivityType.custom,name=activitytext)
        elif activitytype == 6:
            activity = discord.Activity(type=discord.ActivityType.competing,name=activitytext)
        else:
            activity = discord.Activity(type=self.bot.activity.type,name=activitytext)

        if statustype == 1:
            status = discord.Status.online
        elif statustype == 2:
            status = discord.Status.offline
        elif statustype == 3:
            status = discord.Status.idle
        elif statustype == 4:
            status = discord.Status.dnd
        elif statustype == 5:
            status = discord.Status.invisible
        else:
            status = self.bot.status

        try:
            await self.bot.change_presence(activity=activity,status=status)
            await interaction.response.send_message(f"Changed Status.",ephemeral=True)
            logger_info(f"Changed activity to {activity}, status to {str(status).title()}")
        except Exception as e:
            await interaction.response.send_message(f"Exception: `{e}`",ephemeral=True)


    @commands.hybrid_command(name='purge',description='boom',hidden=True)
    @app_commands.guilds(*guilds)
    @is_me()
    async def pur(self, ctx: commands.Context, amount: int, user: Optional[discord.User]=None):
        try:
            if ctx.author.id not in me:
                await ctx.reply("This command is not for you.")
                return
            try:
                await ctx.message.add_reaction(str(emojidict.get("check")))
            except:
                await ctx.defer(ephemeral=True)
            try:
                check = discord.utils.MISSING
                if user:
                    check = lambda x: x.author == user and x.author is not None
                if isinstance(ctx.channel, discord.abc.GuildChannel):
                    deleted_msgs = await ctx.channel.purge(limit=amount, check=check)
                    await ctx.reply(f"Deleted {len(deleted_msgs)} messages.")
            except Exception as e:
                await ctx.reply(f"Could not delete messages: {e}")
                logger_error(f"Problem deleting messages: {e}")    
        except:
            logger_error(traceback.format_exc())
    

    @commands.hybrid_command(name='react',description="add reaction",hidden=True)
    @app_commands.guilds(*guilds)
    @is_me()
    async def react_1(self, interaction: commands.Context, emoji: str, msgid: str):
        await interaction.defer(ephemeral=True)
        if interaction.author.id not in me:
            await interaction.reply("This command is not for you.")
            return
        msg = await interaction.channel.fetch_message(int(msgid))
        try:
            await msg.add_reaction(emoji)
            await interaction.reply("Added reaction.",ephemeral=True)
        except:
            await interaction.reply("Could not add reaction.")


    # @app_commands.command(name="reloadext",description="Owner only. Reloads an extension.",guilds=[discord.Object(x) for x in guilds])
    # async def reload_extension(self, ctx: discord.Interaction, extension: str):
    #     #ctx.user = ctx.author
    #     await ctx.response.defer(thinking=True,ephemeral=True)
    #     if ctx.user.id in me:
    #         extension = extension.replace(".py","")
    #         try:
    #             await self.bot.reload_extension(extension)
    #             await ctx.followup.send(f"Reloaded extension `{extension}(.py)`.",ephemeral=True)
    #             logger_info(f"Reloaded extension {extension}.")
    #         except Exception as e:
    #             logger_warning(traceback.format_exc())
    #             await ctx.reply(f"Exception: `{e}`",ephemeral=True)
    #     else:
    #         await ctx.followup.send("You are not authorized to run this command.",ephemeral=True)

    @commands.hybrid_command(name="reloadext",description="Owner only. Reloads an extension.",guilds=[discord.Object(x) for x in guilds])
    @app_commands.autocomplete(extension=reload_autocomp)
    @app_commands.guilds(*guilds)
    @is_me()
    async def reload_extension(self, ctx: commands.Context, extension: str):
        await ctx.defer(ephemeral=True)
        if ctx.author.id in me:
            extension = extension.replace(".py","")
            try:
                await self.bot.reload_extension(extension)
                await ctx.reply(f"Reloaded extension `{extension}(.py)`.",ephemeral=True)
                logger_info(f"Reloaded extension {extension}.")
            except Exception as e:
                logger_warning(traceback.format_exc())
                await ctx.reply(f"Exception: `{e}`",ephemeral=True)
        else:
            await ctx.reply("You are not authorized to run this command.",ephemeral=True)
    
    @commands.has_permissions(ban_members=True)
    @commands.command(name="ban",description="Owner only. Bans a user.",guilds=[discord.Object(x) for x in guilds])
    @app_commands.guilds(*guilds)
    @is_me()
    async def ban(self, ctx: commands.Context, user: Optional[discord.User]=None, id: Optional[str]=None, reason: str="A reason was not provided."):
        await ctx.defer(ephemeral=True)
        user_: Optional[Union[discord.User,discord.Member]] = None
        if id is not None and ctx.guild:
            user_ = user if user is not None else await getorfetch_user(int(id),ctx.guild)
        elif user:
            user_ = user
        
        if user_ is None:
            await ctx.reply("Invalid user id.",ephemeral=True)
            return

        if ctx.author.id not in me:
            await ctx.reply("You are not authorized to run this command.",ephemeral=True)
            return

        # getorfetch_dm
        if user_ is not None:
            dm = user_.dm_channel    
            if dm is None:
                dm = await user_.create_dm()
        
            try:
                if ctx.guild:
                    await dm.send(embed=makeembed(title=f"You were banned from {ctx.guild.name}.",description=f"""You were banned from {ctx.guild.name} for the following reason: {reason}
        This ban is permenant and cannot be appealed.""",color=discord.Colour.red()))
                    await ctx.reply(f"Banned user {user_} ({user_.id}) for the following reason: `{reason}`",ephemeral=True)
            except:
                await ctx.reply("Could not send dm to user.",ephemeral=True)

        try:
            if ctx.guild:
                await ctx.guild.ban(user=user_,reason=reason)
        except Exception as e:
            await ctx.reply(f"Could not ban user: {e}",ephemeral=True)
            return


    @commands.command(name="dmhistory",description="Owner only. Sends the last 10 messages in a user's dm.",hidden=True,guilds=[discord.Object(x) for x in guilds])
    @app_commands.guilds(*guilds)
    @is_me()
    async def dmhistory(self, ctx: commands.Context, user: Optional[discord.User]=None, id: Optional[str]=None):
        user_: Optional[Union[discord.User, discord.Member]] = None
        msgs = []
        if id is not None and ctx.guild and user is None:
            user_ = await getorfetch_user(int(id),ctx.guild)
            if user_ is None:
                await ctx.reply("Invalid user id.")
                return
        if user_:
            if user_.dm_channel is None:
                await ctx.reply("User does not have a dm channel.")
                return
            msgs = [msg async for msg in user_.dm_channel.history(limit=None)]
        msgs.reverse()
        # returnv = ""
        # for msg in msgs:
        #     returnv += f"[<t:{msg.created_at.timestamp()}:T>] {msg.author}: {msg.content}\n"
        # paginator = commands.Paginator(prefix='',suffix='',max_size=2000,allowed_mentions=discord.AllowedMentions.none())
        # for line in returnv.splitlines():
        #     paginator.add_line(line)
        returnv = []
        for msg in msgs:
            copied_msg = await copy_message(msg)
            returnv.append(makeembed(description=f"{copied_msg}\n"))
        view = EmbedPaginatorView(returnv)
        await ctx.reply(embed=view.initial,view=view)


        
async def setup(bot: commands.Bot):
    global me
    await bot.add_cog(BasicCog(bot))
    # info = await bot.application_info()
    # if info.owner.id is not None:    me = [info.owner.id]
    # elif info.team is not None: me = [member.id for member in info.team.members]
    # else: me = []
