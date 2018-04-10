# -*- coding: utf-8 -*-
import os
from very.very import conf


bot = None


def _make_bot():
    global bot
    if bot is None:
        from very.core.chatbot.slack import SlackBot, SlackClient
        print('make bot')
        token = os.environ['SLACK_BOT_TOKEN']
        conf.SLACK_BOT_TOKEN = token
        client = SlackClient(conf)
        bot = SlackBot(conf, client)


_make_bot()


if __name__ == '__main__':
    bot.run()
