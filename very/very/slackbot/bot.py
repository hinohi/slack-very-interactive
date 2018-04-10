# -*- coding: utf-8 -*-
import os
from very.very import conf


def _make_bot():
    from very.core.chatbot.slack import SlackBot, SlackClient
    print('make bot')
    token = os.environ['SLACK_BOT_TOKEN']
    conf.SLACK_BOT_TOKEN = token
    client = SlackClient(conf)
    return SlackBot(conf, client)


bot = _make_bot()
