# Setup script
if __name__ == "__main__":
    raise RuntimeError("Cannot run script as stand-alone.")

import json
import sys
import os


def conditional(text: str):
    """
    Simple function to return a True or False for Yes or No questions.

    :param text: I wonder what this might be
    :return: True (y) or False (n)
    """
    return text.lower().strip().startswith(("y", "t", "1", "o"))


def attempt_map(text: str, _type):
    """
    function that attempts to map text into a provided callable. Useful for required() and conditional() and input().

    :param text: the text to map
    :param _type: the callable
    :return:
    """
    try:
        return _type(text)
    except (TypeError, ValueError):
        return ...


def interactive_attempt_map(text, _type, *, is_required: bool = False, default=None):
    while True:
        if is_required:
            inp = required(text)
        else:
            inp = input(text) or default
        mapped = attempt_map(inp, _type)
        if mapped is ...:
            print("Unable to convert input to {}. Please try again.".format(_type.__name__))
            continue
        return mapped


def required(text: str):
    """
    Abstracted input() that insures text is actually inputted.

    :param text: text to print
    :return: text inputted.
    """
    while True:
        inp = input(text)
        if not inp:
            print("An answer is required.")
            continue
        return inp


def main():
    try:
        with open("./template_config.json") as template_file:
            template: dict = json.load(template_file)
    except FileNotFoundError:
        print("No template file found. Please ensure you downloaded ChipBot correctly, and try again.")
        sys.exit(4)
    except json.JSONDecodeError:
        print("Failed to load template. Did you modify template_config.json?")
        sys.exit(2)

    real = template.copy()

    # Yes, we're gonna hardcode this in. I'm too lazy to add auto type detection.
    real["prefix"]["set"] = input("Please input a default prefix [//]: ") or "//"
    real["prefix"]["mention"] = conditional(input("Would you like to allow the bot's mention to be a prefix? [Y/N] "))
    real["prefix"]["custom"] = conditional(input("Would you like to allow custom prefixes? [Y/N] "))
    real["tokens"]["production"] = required("Please enter a primary (production) bot token: ")
    if conditional(required("Would you like to add extra (beta and development) bot tokens? [Y/N] ")):
        real["tokens"]["beta"] = input("Please insert a beta bot token [ ]: ") or None
        real["tokens"]["development"] = input("Please insert a development bot token [ ]: ") or None
    real["control"]["max_messages"] = interactive_attempt_map(
        "How large should the bot's max message cache be? [1000] ", int, is_required=False, default=1000
    )
    if conditional("Would you like to (at least temporarily) limit how many servers ChipBot can join? [Y/N] "):
        real["control"]["max_guilds"] = interactive_attempt_map(
            "How many servers can ChipBot join? [30] ", int, is_required=False, default=30
        )

    real["sql"] = (
        input("Please input a file path where the sqlite database should be located [./main.db]: ") or "./main.db"
    )
    for key, default in real["allowed_mentions"].items():
        real["allowed_mentions"][key] = conditional(
            input(f"Should the bot be allowed to mention {key}? [Y/N] (default: {default}) ") or str(default)
        )

    real["owners"] = (
        input("Please enter a list of owner user IDs (or hit enter for discord native bot ownership): ") or []
    )
    os.system("cls" if os.name == "nt" else "clear")
    print("Saving...")
    with open("./config.json", "w+") as config:
        json.dump(real, config, indent=2)
    print("Saved!")
