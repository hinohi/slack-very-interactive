# -*- coding: utf-8 -*-


def _fix_path():
    import sys
    import pathlib
    path = str(pathlib.Path().absolute())
    if path is sys.path:
        sys.path.remove(path)
    sys.path.insert(0, str(path))


def main():
    _fix_path()
    from very.very.slackbot.bot import bot

    bot.run()


if __name__ == '__main__':
    main()
