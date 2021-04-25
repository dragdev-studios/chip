import time
import aiohttp
from datetime import datetime
from subprocess import run as run_shell
from functools import partial

import aiosqlite
import discord
import jishaku
import tabulate
from discord.ext import commands

from ..bot import ChipBot


class Meta(commands.Cog):
    """This cog contains commands for meta about the bot (e.g. version, credits, ping)."""
    def __init__(self, bot: ChipBot):
        self.bot = bot

    async def run_async(self, part):
        """
        Async runs a blocking function in the event executor (makes it non-blocking)

        :param part: a functools.partial function.
        :return: The result of the partial
        """
        return await self.bot.loop.run_in_executor(None, part)

    @commands.command(name="ping", aliases=['pong'])
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(5, 5, commands.BucketType.channel)
    async def ping(self, ctx: commands.Context):
        """Shows you the bot's ping"""
        start = time.time_ns()
        msg = await ctx.send("Pinging...")
        end = time.time_ns()

        http_time = round((end-start)/1000000, 2)
        ws_time = round(self.bot.latency*1000, 2)

        embed = discord.Embed(
            title="Pong!",
            description=f"API latency: `{http_time}ms`\n"
                        f"Gateway Latency: `{ws_time}ms`",
            colour=discord.Colour.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_author(name=ctx.author.display_name, icon_url=str(ctx.author.avatar_url))
        return await msg.edit(embed=embed, content=None)

    @commands.command(name="credits", aliases=['about', 'info'])
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def credits(self, ctx: commands.Context):
        """Displays loads of metadata about the bot."""
        msg = await ctx.send("Loading...")
        # head = await self.run_async(partial(run_shell, ["git", "rev-parse", "HEAD", "--short"], shell=True))
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.github.com/repos/dragdev-studios/chip/tags") as response:
                data = await response.json()
                if response.status != 200 or not data:
                    out_of_date = False
                    our_version = "0.0.0a"
                    their_version = "999.999.999-post"
                    newest_release = {
                        "name": "haha it broke"
                    }
                else:
                    our_version = tuple(self.bot.__version__.split("."))
                    newest_release = data[0]
                    newest_version = tuple(newest_release["name"].split("."))
                    out_of_date = newest_version > our_version

        embed = discord.Embed(
            title="About Chip:",
            description="ChipBot is open-source! Contribute [here](https://github.com/dragdev-studios/chip)",
            colour=discord.Colour.orange(),
            timestamp=datetime.utcnow()
        )

        if out_of_date:
            newest_release_text = f"Newest Release: [v{newest_release['name']}](https://github.com/dragdev-studios/" \
                                  f"chip/releases/{newest_release['name']})"
        else:
            newest_release_text = ""
        embed.add_field(
            name="Bot Version:",
            value=f"{self.bot.__version__}\nRelease: {our_version}\n{newest_release_text}"
        )
        embed.add_field(
            name="Dependency Versions:",
            value=f"discord.py: {discord.__version__}\n"
                  f"Jishaku: {jishaku.__version__}\n"
                  f"Tabulate: {tabulate.__version__}\n"
                  f"aiosqlite: {aiosqlite.__version__}",
            inline=False
        )
        return await msg.edit(content=None, embed=embed)


def setup(bot):
    bot.add_cog(Meta(bot))
