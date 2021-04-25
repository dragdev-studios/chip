from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument("--setup", "-S", action="store_true")
args = parser.parse_args()

if args.setup:
    from cli.setup import main
    main()
