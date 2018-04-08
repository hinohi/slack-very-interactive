# -*- coding: utf-8 -*-
import os
from very.very import conf
from very.core.chatbot.slack import SlackBot


def _make_bot():
    token = os.environ['SLACK_BOT_TOKEN']
    conf.SLACK_BOT_TOKEN = token
    return SlackBot(conf)


bot = _make_bot()
