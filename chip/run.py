import logging

import discord

from .bot import ChipBot


def run_bot(environment):
    bot = ChipBot()
    logging.info("Starting bot")
    try:
        bot.run(bot.config["tokens"][environment or bot.config["tokens"]["default"]])
    except discord.LoginFailure as e:
        logging.error("Invalid token for environment '{}'.".format(environment), e)
        raise
    except KeyboardInterrupt:
        logging.critical("Please, have some patience, and don't spam KeyboardInterrupt. The bot needs to shut down.")
        raise
