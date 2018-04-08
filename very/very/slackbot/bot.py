# -*- coding: utf-8 -*-
import os
from very.very import conf
from very.core.chatbot.slack import SlackBot


bot = None


def _make_bot():
    global bot
    if bot is None:
        print('make bot')
        token = os.environ['SLACK_BOT_TOKEN']
        conf.SLACK_BOT_TOKEN = token
        bot = SlackBot(conf)


_make_bot()


if __name__ == '__main__':
    bot.run()
