import sys
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument("--setup", "-S", action="store_true")
args = parser.parse_args()

if args.setup:
    from cli.setup import main

    try:
        main()
    except PermissionError:
        print("[FATAL] Unable to write configuration file")
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL] {e}")
        sys.exit(1)
