import json
import logging
import sys
import pathlib
from base64 import b64decode
from os import path

from .sql import Guild

import aiosqlite
import discord
from discord.ext import commands
from tabulate import tabulate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # For verbose output, set INFO to DEBUG, or set it to WARNING for just warnings.
handler = logging.FileHandler(filename='chip.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class ChipBot(commands.Bot):
    """
    Chip's custom subclass of commands.Bot with a few extra useful features.
    """
    def __init__(self):
        logger.debug("Began initialising ChipBot.")
        if not path.exists("./config.json"):
            print("There is no configuration file. Please run `python3 main.py --setup`.")
            sys.exit(4)

        with open("./config.json") as config_raw:
            self.config = json.load(config_raw)
            logger.debug(f"Loaded configuration: {self.config}")

        logger.debug("Connecting to database...")
        if not self.config["sql"]:
            logger.debug("No SQL directory specified. Using ./main.db")
            self.config["sql"] = "./main.db"

        logger.debug("Resolving path...")
        _path = pathlib.Path(self.config["sql"])
        logger.debug("Resolved path - " + str(_path))
        self.db = self.loop.run_until_complete(aiosqlite.connect(str(_path)))
        logger.debug("Connected to database.")

        if self.config["prefix"]["mention"]:
            default_prefix = commands.when_mentioned_or(*self.config["prefix"]["set"])
        else:
            default_prefix = self.config["prefix"]["set"]
        logger.debug("Set default prefix to: " + str(default_prefix))

        async def _fetch_prefix(bot, message):
            if not message.guild:
                return default_prefix
            async with bot.db.execute("SELECT prefix FROM guilds WHERE id=?", (message.guild.id,)) as cursor:
                _prefix = await cursor.fetchone()
                _resolved_prefix = b64decode(str(_prefix)).decode()
            if bot.config["prefix"]["mention"]:
                return commands.when_mentioned_or(_resolved_prefix)

        super().__init__(
            _fetch_prefix,
            description="Chip - A multi-purpose, open-source, easy to use and powerful moderation bot.",
            case_insensitive=True,
            owner_ids=self.config["owners"] or None,
            strip_after_prefix=True,
            activity=discord.Activity(
                name=f"gears turn...",
                type=discord.ActivityType.watching
            ),
            status=discord.Status.dnd,
            max_messages=self.config["control"]["max_messages"],
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(**self.config["allowed_mentions"])
        )
        logger.debug("ChipBot initialised.")
        self.event(self.on_ready)  # This is basically the @bot.event decor, just called internally.

    async def on_ready(self):
        table = tabulate(
            [self.user.name, len(self.guilds), len(self.get_all_channels()), len(self.users)],
            ["Bot Name",     "Guilds",         "Channels",                   "Loaded Users"],
            tablefmt="pretty"
        )
        print(table)
