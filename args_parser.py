import argparse


def parse_args():
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("storage", help="full_path")

    parser = argparse.ArgumentParser(parents=[parent_parser])
    subparsers = parser.add_subparsers(
        title="available commands", dest="command")

    subparsers.add_parser("init", help="initialize storage")

    add_parser = subparsers.add_parser(
        "add", help="add value by specified key")
    add_parser.add_argument(
        "items", metavar="item", nargs="+", help="key or value")

    get_parser = subparsers.add_parser(
        "get", help="get values by specified key")
    get_parser.add_argument("keys", metavar="key", nargs="+")

    del_parser = subparsers.add_parser(
        "del", help="delete value by specified key")
    del_parser.add_argument("keys", metavar="key", nargs="+")

    exs_parser = subparsers.add_parser(
        "exist", help="check if key in storage")
    exs_parser.add_argument("keys", metavar="keys", nargs="+")

    subparsers.add_parser("keys", help="get all keys")

    subparsers.add_parser("values", help="get all values")

    return parser.parse_args()
