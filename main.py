import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import when_mentioned
import datetime
from typing import Optional, Union, Literal
from discord.utils import MISSING



async def getorfetch_channel(channelid: int, guild: discord.Guild=None, bot: commands.Bot=None) -> Optional[Union[discord.TextChannel, discord.VoiceChannel, discord.abc.GuildChannel]]:
    """Gets a channel from a guild or bot, if not found, fetches it"""
    channel = None
    if guild != None:
        channel = guild.get_channel(channelid)
        if channel is None:
            channel = await guild.fetch_channel(channelid)
    else:
        if bot != None:
            channel = bot.get_channel(channelid)
            if channel is None:
                channel = await bot.fetch_channel(channelid)
    return channel

async def getorfetch_user(userid: int, guild: discord.Guild, bot: commands.Bot) -> Optional[Union[discord.User, discord.Member]]:
    """Gets a user from a guild or bot, if not found, fetches it"""
    user = None
    if guild != None:
        user = guild.get_member(userid)
        if user is None:
            user = await guild.fetch_member(userid)
    else:
        user = bot.get_user(userid)
        if user is None:
            user = await bot.fetch_user(userid)
    return user


def makeembed(title: str=None,timestamp: datetime.datetime=None,color: discord.Colour=None,description: str=MISSING, author: str=MISSING, author_url: str=MISSING, author_icon_url: str=MISSING, footer: str=MISSING, footer_icon_url: str=MISSING, url: str=MISSING,image: str=MISSING,thumbnail: str=MISSING,) -> Optional[discord.Embed]:#embedtype: str='rich'):
    """Makes an Embed object without all the set_ garbage"""
    embed = discord.Embed()
    if title != None: embed.title = title
    if timestamp != None: embed.timestamp = timestamp
    if color != None: embed.color = color
    if description != None: embed.description = description
    if url != None: embed.url = url
    if author != None: embed.set_author(name=author,url=author_url,icon_url=author_icon_url)
    if footer != None: embed.set_footer(text=footer,icon_url=footer_icon_url)
    if image != None: embed.set_image(url=image)
    if thumbnail != None: embed.set_thumbnail(url=thumbnail)
    return embed

def makeembed_bot(title: str=None,timestamp: datetime.datetime=datetime.datetime.now(),color: discord.Colour=discord.Colour.green(),description: str=MISSING, author: str=MISSING, author_url: str=MISSING, author_icon_url: str=MISSING,footer: str='Made by @aidenpearce3066', footer_icon_url: str=MISSING, url: str=MISSING,image: str=MISSING,thumbnail: str=MISSING) -> Optional[discord.Embed]:#embedtype: str='rich'):
    return makeembed(title=title,timestamp=timestamp,color=color,description=description,author=author,author_url=author_url,author_icon_url=author_icon_url,footer=footer,footer_icon_url=footer_icon_url,url=url,image=image,thumbnail=thumbnail)

def parsetime(date: str, time: str=None) -> Optional[datetime.datetime]:
    """Parses a date and time string into a datetime.datetime object"""
    try:
        if date != None and time != None:
            return datetime.datetime.strptime(f"{date} {time}", "%Y.%m.%d %H:%M:%S")
        elif date != None:
            return datetime.datetime.strptime(f"{date}", "%d.%m.%Y")
        elif time != None:
            return datetime.datetime.strptime(f"{time}", "%H:%M:%S")
    except:
        return None

timestamptype = Literal["t","T","d","D","f","F","R"]

def dctimestamp(dt: Union[datetime.datetime, int, float], format: timestamptype="f") -> str:
    """
    Timestamp Styles
    STYLE |	EXAMPLE OUTPUT	              | DESCRIPTION
    t	  | 16:20	                      | Short Time
    T	  | 16:20:30	                  | Long Time
    d	  | 20/04/2021	                  | Short Date
    D	  | 20 April 2021	              | Long Date
    f  	  | 20 April 2021 16:20	          | Short Date/Time
    F	  | Tuesday, 20 April 2021 16:20  | Long Date/Time
    R	  | 2 months ago	              | Relative Time
    """
    if type(dt) == datetime.datetime: dt = int(dt.timestamp())
    if isinstance(dt, int, float):
        return f"<t:{int(dt)}:{format[:1]}>" 
    return 

def dchyperlink(url: str, texttoclick: str, hovertext: str=None):
    '''Formats a Discord Hyperlink so that it can be clicked on.
    "[Text To Click](https://www.youtube.com/ \"Hovertext\")"'''
    texttoclick, hovertext = f"[{texttoclick}]", f" \"{hovertext}\"" if hovertext != None else ""
    return f"{texttoclick}({url}{hovertext})"
