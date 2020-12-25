import sys
import os


STORAGE_INIT_ERROR = -3
STORAGE_NOT_FOUND_ERROR = -4
STORAGE_PATH_ERROR = -2
MODULE_IMPORT_ERROR = -1


try:
    from args_parser import parse_args
    from storage import Storage, StorageInitError
except (ModuleNotFoundError, ImportError) as err:
    sys.stdout.write(str(err))
    sys.exit(MODULE_IMPORT_ERROR)


def check_path(path):
    if not os.path.exists(path):
        text = f"Storage '{path}' not found"
        sys.stdout.write(text)
        sys.exit(STORAGE_PATH_ERROR)


def main():
    args = parse_args()

    storage = Storage(args.storage)
    if args.command == "init":
        try:
            storage.init()
            return
        except StorageInitError as error:
            sys.stdout.write(error.text)
            sys.exit(STORAGE_INIT_ERROR)

    check_path(args.storage)
    with storage:

        if args.command == "add":
            if len(args.items) % 2 != 0:
                # Выкидывать ошибку
                return

            pair = list()
            for item in args.items:
                pair.append(item)
                if len(pair) == 2:
                    value = pair.pop()
                    key = pair.pop()
                    try:
                        key = int(key)
                    except ValueError:
                        pass
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                    storage[key] = value

        elif args.command == "get":
            for key in args.keys:
                try:
                    key = int(key)
                except ValueError:
                    pass
                value = storage[key]
                print(value, file=sys.stdout)

        elif args.command == "del":
            for key in args.keys:
                del storage[key]

        elif args.command == "exist":
            for key in args.keys:
                try:
                    key = int(key)
                except ValueError:
                    pass
                exist = key in storage
                print(exist)

        elif args.command == "keys":
            for key in storage:
                print(key, end=" ")

        elif args.command == "values":
            for key in storage:
                value = storage[key]
                print(value, end=" ")


if __name__ == "__main__":
    main()
