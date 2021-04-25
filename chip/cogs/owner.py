import logging
import traceback

from ..bot import ChipBot
from discord.ext import commands

logger = logging.getLogger(__name__)


class Owner(commands.Cog):
    """Owner-related commands. used for bot management."""
    def __init__(self, bot: ChipBot):
        self.bot = bot

    async def cog_check(self, ctx):
        is_owner = await self.bot.is_owner(ctx.author)
        if is_owner:
            return True
        raise commands.NotOwner

    @commands.command()
    async def reload(self, ctx: commands.Context, *cogs: str):
        """Reloads all the provided extensions.

        *cogs: A space-delimited list of cogs to reload. Pass only "auto" or "~" ro reload all loaded cogs."""
        def format_message(r):
            m = ""
            for c in r:
                if isinstance(c, tuple):  # failed to reload
                    m += f"\N{cross mark} `{c[0]}`\n"
                else:
                    m += f"\N{white heavy check mark} `{c}`\n"
            return m

        if len(cogs) == 1:
            if cogs in ["auto", "~"]:
                status = []
                logger.debug(f"Reloading all cogs at the request of {ctx.author}...")
                for ext in self.bot.extensions:
                    try:
                        self.bot.reload_extension(ext)
                    except commands.ExtensionError as e:
                        logger.error(f"Failed to re-load extension {ext}.", exc_info=e)
                        status.append((ext, e))
                    else:
                        status.append(ext)
                return await ctx.send(format_message(status))
            else:
                try:
                    self.bot.reload_extension(cogs[0])
                except commands.ExtensionError:
                    text = traceback.format_exc()
                    paginator = commands.Paginator("```py")
                    for line in text.splitlines():
                        paginator.add_line(line[:1980].replace("`", "`\u200b"))  # zwsp will avoid markdown breaking.
                    await ctx.send(f"\N{cross mark} Failed to load `{cogs[0]}`:")
                    for page in paginator.pages:
                        await ctx.send(page)
                    return
                else:
                    await ctx.message.add_reaction("\N{white heavy check mark}")
        else:
            status = []
            for ext in cogs:
                try:
                    self.bot.reload_extension(ext)
                except commands.ExtensionError as e:
                    logger.error(f"Failed to re-load extension {ext}.", exc_info=e)
                    status.append((ext, e))
                else:
                    status.append(ext)
            return await ctx.send(format_message(status))


def setup(bot):
    bot.add_cog(Owner(bot))
