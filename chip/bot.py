import json
import logging
import sys
import pathlib
import traceback
from os import path

from .sql import Guild

import aiosqlite
import discord
from discord.ext import commands
from tabulate import tabulate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # For verbose output, set INFO to DEBUG, or set it to WARNING for just warnings.
handler = logging.FileHandler(filename="chip.log", encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)


def get_prefix_getter(default_prefix):
    async def _fetch_prefix(bot, message):
        if not message.guild:
            return default_prefix
        async with bot.db.execute("SELECT prefix FROM guilds WHERE id=?", (message.guild.id,)) as cursor:
            _prefix = await cursor.fetchone() or "//"
            logger.debug("Got prefix '{}' for guild '{}'.".format(_prefix, message.guild.id))
            _resolved_prefix = _prefix
        if bot.config["prefix"]["mention"]:
            return commands.when_mentioned_or(_resolved_prefix)
        return _resolved_prefix
    return _fetch_prefix


class ChipBot(commands.Bot):
    """
    Chip's custom subclass of commands.Bot with a few extra useful features.
    """

    def __init__(self):
        self.__version__ = "0.1.0a"
        logger.debug(f"Began initialising ChipBot v{self.__version__}.")
        if not path.exists("./config.json"):
            print("There is no configuration file. Please run `python3 main.py --setup`.")
            sys.exit(4)

        with open("./config.json") as config_raw:
            self.config = json.load(config_raw)
            safe_config = self.config.copy()
            safe_config["tokens"] = "[expunged]"
            logger.debug(f"Loaded configuration: {safe_config}")

        if self.config["prefix"]["mention"]:
            default_prefix = commands.when_mentioned_or(*self.config["prefix"]["set"])
        else:
            default_prefix = self.config["prefix"]["set"]
        logger.debug("Set default prefix to: " + str(default_prefix))

        super().__init__(
            get_prefix_getter(default_prefix),
            description="Chip - A multi-purpose, open-source, easy to use and powerful moderation bot.",
            case_insensitive=True,
            owner_ids=self.config["owners"] or None,
            strip_after_prefix=True,
            activity=discord.Activity(name=f"gears turn...", type=discord.ActivityType.watching),
            status=discord.Status.dnd,
            max_messages=self.config["control"]["max_messages"],
            intents=discord.Intents.all(),
            allowed_mentions=discord.AllowedMentions(**self.config["allowed_mentions"]),
        )

        logger.debug("Connecting to database...")
        if not self.config["sql"]:
            logger.debug("No SQL directory specified. Using ./main.db")
            self.config["sql"] = "./main.db"

        logger.debug("Resolving path...")
        _path = pathlib.Path(self.config["sql"])
        logger.debug("Resolved path - " + str(_path))
        self.db = self.loop.run_until_complete(aiosqlite.connect(str(_path)))
        self.loop.run_until_complete(Guild.create_table(self.db, name="guilds"))
        logger.debug("Connected to database.")

        # cogs = [
        #     "jishaku",  # debugging
        #     "chip.cogs.meta",  # meta cog
        # ]
        cogs = self.config["extensions"]
        for extension in cogs:
            try:
                self.load_extension(extension)
                logger.debug(f"Loaded extension {extension}.")
            except Exception as e:
                logger.warning(f"Failed to load extension {extension}.", exc_info=e)
        logger.debug("ChipBot initialised.")
        self.event(self.on_ready)  # This is basically the @bot.event decor, just called internally.

    async def on_ready(self):
        tabulatable = {
            "Bot Name": [self.user.name],
            "Guilds": [len(self.guilds)],
            "Channels": [len(tuple(self.get_all_channels()))],
            "Users": [len(self.users)],
            "Emojis": [len(self.emojis)]
        }
        table = tabulate(
            tabulatable,
            headers="keys",
            tablefmt="pretty",
        )
        print(table)

    async def on_error(self, event_method, *args, **kwargs):
        print('Ignoring exception in {}'.format(event_method), file=sys.stderr)
        traceback.print_exc()
        logger.error(
            "Ignoring exception in {}.".format(event_method),
            *args,
            **kwargs
        )
