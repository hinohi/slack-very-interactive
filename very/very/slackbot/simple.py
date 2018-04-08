# -*- coding: utf-8 -*-
from very.very.slackbot.bot import bot


@bot.listen_to('私は(.+)です')
def hello_name(name):
    bot.post('#random', f'{name}さんこんにちは')


@bot.listen_to('button')
def button():
    at = [
        {
            'fallback': 'ボタンは押せません',
            'callback_id': 'button_test',
            'actions': [
                {
                    'name': 'test',
                    'text': '1',
                    'type': 'button',
                    'value': 1,
                },
                {
                    'name': 'test',
                    'text': '2',
                    'type': 'button',
                },
                {
                    'name': 'test',
                    'text': '3',
                    'type': 'button',
                    'confirm': {
                        'title': '本当に?',
                        'text': '2とかじゃなくていいの？',
                        'ok_text': '3がいい',
                        'dismiss_text': 'やっぱやめる',
                    }
                }
            ]
        },
    ]
    bot.post('#random', 'ボタンのテスト', at)
