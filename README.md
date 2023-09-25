# AidenLib

Aidenlib is a library made by `@aidenpearce3066` with some discord.py helper functions. 
I mainly made this to avoid repeated code in my discord bots, but anybody is free to use it.

Ill add more methods in the near future.

`dctimestamp` which is like `discord.utils.format_dt` except you can give it a `string` (numeric),  `float`, `int` or `datetime` to turn into a discord timestamp

`dchyperlink` which creates a discord formatted hyperlink 

`makeembed` which can make an embed in one line, a bit shorter syntax than chaining setters

`makeembed_bot` is useless/depricated dont use it

`getorfetch` methods which will attempt to retrieve channels/guilds/users/members from the cache, and if it returns `None` will automatically fetch it and return it to you
(ex `await getorfetch_channel`, works for any type)

`parsetime` which just tries to parse a `datetime`, not finished working on it yet

Install it via `pip install -U aidenlib`

Import/Use the methods via `from aidenlib.main import getorfetch_channel, dctimestamp, etc etc`

PR's are welcome if you have any suggestions/implementations.