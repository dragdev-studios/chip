import time
from datetime import datetime

import discord
from discord.ext import commands

from ..bot import ChipBot


class Meta(commands.Cog):
    """This cog contains commands for meta about the bot (e.g. version, credits, ping)."""
    def __init__(self, bot: ChipBot):
        self.bot = bot

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


def setup(bot):
    bot.add_cog(Meta(bot))
