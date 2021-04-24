# Chip - A customisable discord moderation bot

## What is it?
Chip is a discord moderation bot designed to be easy to use but powerful.
Chip allows you to moderate your server with relative ease, without missing
any critical features or quality of life.

## How do I use it? \[installing\]
To install chip, you can either use the public copy ([here](https://dragdev.xyz)),
or install from github.

**If you don't know how to run/make a discord bot, you should just use our public copy.**
Chip is not a simple bot.

### Step-by-step:
**MAKE SURE YOU HAVE PYTHON 3.8 OR LATER BEFORE CONTINUING!!**
1. Install git (windows, use git for windows. Unix, just install it with your package manager).
2. Run `git clone https://github.com/dragdev-studios/chip`.
3. Run `cd chip`.
4. Install dependencies via `pip install -Ur requirements.txt`.
5. Run `[py3] main.py --setup` to install and set up the bot. replace `[py3]` with your python command.

Now it's installed!
However, you're not done yet.

### Starting the bot \[setting tokens]
Once you've created all the meta stuff for the bot, you'll need to give it tokens.
Open `config.json`, and locate the `tokens` key. From there, there will be three
entries - production, beta and development.
You only need one of these, and they try to boot in that order (e.g. if production is missing, it'll use beta)

1. open the [discord developer portal](https://discord.com/developers/applications/@me).
2. Select or create an application.
3. Go to "bot". If you haven't created the bot yet, click the create bot button.
4. Click "copy token".
5. Paste that inside a value for production (it should look like `"production": "NjE0MjYw...",`)
6. Save

Feel free to change any of the other settings in there.

### Running the bot
To run the bot, you'll need to have a server with python 3.9 or above installed. 3.8 might work too.

First, complete [setup](#step-by-step).

Then, run `[py3] main.py --env production` (replace `[py3]` with your python command and `production` with whatever
environment you're running like development or beta).

## Debugging
Since Chip uses python's in-built logging module, assuming there's no OS issues, when running the bot you
should get a file called `chip.log` created.
By default, this has some relatively verbose logging, however nothing *too* useful for debugging.

If you want to get rather verbose and track down the little details, go to [chip/bot.py](./chip/bot.py),
line #8 and change "logging.INFO" to "logging.DEBUG".

Chip will log basically everything to that file.

⚠️ **Make sure you occasionally rotate the log file**, otherwise it'll get quite large!️
