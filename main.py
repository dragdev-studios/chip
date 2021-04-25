import sys
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument("--setup", "-S", action="store_true")
parser.add_argument("--run", "-R", action="store", choices=["production", "beta", "development"], required=False,
                    default=None)
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

if args.run:
    print("Starting bot...")
    from chip.run import run_bot
    run_bot(args.run)
