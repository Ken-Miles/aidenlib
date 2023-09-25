import discord
from discord import Thread
from discord.abc import PrivateChannel, GuildChannel
from discord.ext import commands
import datetime
from typing import Optional, Union, Literal

bot_: Optional[commands.Bot] = None
owner_name: Optional[str] = None

async def getorfetch_channel(channelid: int, guild: Optional[discord.Guild]=None, bot: Optional[commands.Bot]=bot_) -> Optional[Union[GuildChannel, Thread, PrivateChannel]]:
    """Gets a channel from a guild or bot, if not found, fetches it. If a fetch is forbidden/not found, returns None"""
    global bot_
    if bot is not None: bot_ = bot
    channel: Optional[Union[GuildChannel, Thread, PrivateChannel]] = None
    if guild is not None:
        channel = guild.get_channel_or_thread(channelid)
        if channel is None:
            try:
                channel = await guild.fetch_channel(channelid)
            except (discord.errors.Forbidden, discord.errors.NotFound):
                return None
    elif bot_ is not None:
        channel = bot_.get_channel(channelid)
        if channel is None:
            try:
                channel = await bot_.fetch_channel(channelid)
            except (discord.errors.Forbidden, discord.errors.NotFound):
                return None
    return channel

async def getorfetch_user(userid: int, guild: Optional[discord.Guild]=None, 
    bot: Optional[commands.Bot]=bot_) -> Optional[Union[discord.User, discord.Member]]:
    """Gets a user from a guild or bot, if not found, fetches it. If a fetch is forbidden/not found, returns None"""
    global bot_
    if bot is not None: bot_ = bot
    user: Optional[Union[discord.User, discord.Member]] = None
    if guild is not None:
        user = guild.get_member(userid)
        if user is None:
            try:
                user = await guild.fetch_member(userid)
            except (discord.errors.Forbidden, discord.errors.NotFound):
                return None
    elif bot_ is not None:
        user = bot_.get_user(userid)
        if user is None:
            try:
                user = await bot_.fetch_user(userid)
            except (discord.errors.Forbidden, discord.errors.NotFound):
                return None
    return user

async def getorfetch_guild(guildid: int, bot: Optional[commands.Bot]=bot_) -> Optional[discord.Guild]:
    """Gets a guild from a bot, if not found, fetches it. If a fetch fails, returns None"""
    global bot_
    if bot is not None: bot_ = bot
    if bot_ is not None:
        guild = bot_.get_guild(guildid)
        if guild is None:
            try:
                guild = await bot_.fetch_guild(guildid)
            except (discord.errors.Forbidden, discord.errors.NotFound):
                return None
        return guild

def makeembed(title: Optional[str]=None,timestamp: Optional[datetime.datetime]=None,color: Optional[discord.Colour]=None,
    description: Optional[str]=None, author: Optional[str]=None, author_url: Optional[str]=None, 
    author_icon_url: Optional[str]=None, footer: Optional[str]=None, footer_icon_url: Optional[str]=None, 
    url: Optional[str]=None,image: Optional[str]=None,thumbnail: Optional[str]=None, 
    embedtype: Optional[str]='rich') -> discord.Embed:
    """Kind of useless, method is a bit shorter than chaining setters for an embed.
    Makes a discord.Embed object with the given parameters. If a parameter is None, it will not be added to the embed."""
    embed = discord.Embed()
    if title is not None:       embed.title = title
    if timestamp is not None:   embed.timestamp = timestamp
    if color is not None:       embed.color = color
    if description is not None: embed.description = description
    if url is not None:         embed.url = url
    if author is not None:      embed.set_author(name=author,url=author_url,icon_url=author_icon_url)
    if footer is not None:      embed.set_footer(text=footer,icon_url=footer_icon_url)
    if image is not None:       embed.set_image(url=image)
    if thumbnail is not None:   embed.set_thumbnail(url=thumbnail)
    return embed

def makeembed_bot(title: Optional[str]=None,timestamp: Optional[datetime.datetime]=datetime.datetime.now(),
    color: Optional[discord.Colour]=discord.Colour.green(),description: Optional[str]=None, author: Optional[str]=None, 
    author_url: Optional[str]=None, author_icon_url: Optional[str]=None,footer: str='Made by {user}', 
    footer_icon_url: Optional[str]=None, url: Optional[str]=None,image: Optional[str]=None,
    thumbnail: Optional[str]=None,) -> discord.Embed:#embedtype: str='rich'):
    """Depricated/Useless.
    Similar to :makeembed except has some defaults for a fancy looking one.
    Legacy function for my programs which use a call. Not recommended to use.
    
    You can set the static variable owner_name to control what is in place of {user} in the footer defaultt"""
    global bot_
    if bot_ is not None and footer == 'Made by {user}':  
        footer = footer.format(user=owner_name if owner_name is not None else "{user}")
    return makeembed(title=title,timestamp=timestamp,color=color,description=description,author=author,author_url=author_url,author_icon_url=author_icon_url,footer=footer,footer_icon_url=footer_icon_url,url=url,image=image,thumbnail=thumbnail)

def parsetime(date: str, time: Optional[str]    =None) -> Optional[datetime.datetime]:
    """Parses a date and time string into a datetime.datetime object. Not fully complete, not recomended to use."""
    try:
        if date is not None and time is not None:
            return datetime.datetime.strptime(f"{date} {time}", "%Y.%m.%d %H:%M:%S")
        elif date is not None:
            return datetime.datetime.strptime(f"{date}", "%d.%m.%Y")
        elif time is not None:
            return datetime.datetime.strptime(f"{time}", "%H:%M:%S")
    except:
        return None

timestamptype = Literal["t","T","d","D","f","F","R"]

def dctimestamp(dt: Union[datetime.datetime, int, float, str], format: Optional[timestamptype]=None) -> str:
    """
    Formats a Discord timestamp from a datetime.datetime object or a integer/float/numeric string, similar to discord.utils.format_dt
    Timestamp Styles
    STYLE |	EXAMPLE OUTPUT	              | DESCRIPTION
    t	  | 16:20	                      | Short Time
    T	  | 16:20:30	                      | Long Time
    d	  | 20/04/2021	                      | Short Date
    D	  | 20 April 2021	              | Long Date
    f  	  | 20 April 2021 16:20	              | Short Date/Time
    F	  | Tuesday, 20 April 2021 16:20      | Long Date/Time
    R	  | 2 months ago	              | Relative Time
    """
    if isinstance(dt, str): dt = float(dt) # it may be a float we dont know
    if isinstance(dt, datetime.datetime): dt = int(dt.timestamp())
    if isinstance(dt, float): dt = int(dt)
    return f"<t:{int(dt)}{':' if format is not None else ''}{f':{format[:1]}' if format is not None else ''}>" 

def dchyperlink(url: str, texttoclick: str, hovertext: Optional[str]=None):
    '''Formats a Discord Hyperlink so that it can be clicked on.
    "[Text To Click](https://www.youtube.com/ \"Hovertext\")"'''
    texttoclick, hovertext = f"[{texttoclick}]", f" \"{hovertext}\"" if hovertext is not None else ""
    return f"{texttoclick}({url}{hovertext})"
