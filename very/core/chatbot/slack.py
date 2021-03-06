# -*- coding: utf-8 -*-
import time
from logging import getLogger
from ssl import SSLError
import json
from collections import deque
from contextlib import contextmanager
from typing import Optional

import requests
import slacker

from .base import *


_logger = getLogger(__name__)


class SlackClient(ChatClientBase):

    def __init__(self, conf):
        super().__init__(conf)
        self.token = getattr(self.conf, 'SLACK_BOT_TOKEN')
        assert self.token.startswith('xoxb-')

        self.websocket = None
        self.events_buffer = deque([])

    def connect(self):
        import slacker
        from websocket import create_connection

        rtm = slacker.Slacker(self.token).rtm
        wait = 2
        while True:
            try:
                login_data = rtm.start().body
                time.sleep(1)
                self.websocket = create_connection(login_data['url'])
                self.websocket.sock.setblocking(0)
                _logger.info('connected to slack rtm websocket')
                return {'type': 'login', 'data': login_data}
            except Exception as e:
                _logger.exception('failed to connect: %s', e)
                time.sleep(wait)
                wait += 2

    def websocket_safe_read(self):
        from websocket import WebSocketException, WebSocketConnectionClosedException

        data_list = []
        if self.websocket is None:
            data_list.append(self.connect())
        while True:
            try:
                data = self.websocket.recv()
                data_list.append(data)
            except WebSocketException as e:
                if isinstance(e, WebSocketConnectionClosedException):
                    _logger.warning('lost websocket connection, try to reconnect now')
                else:
                    _logger.warning('websocket exception: %s', e)
                data_list.append(self.connect())
            except Exception as e:
                if isinstance(e, SSLError) and e.errno == 2:
                    pass
                else:
                    _logger.warning('Exception in websocket_safe_read: %s', e)
                return data_list

    def get_event(self):
        while not self.events_buffer:
            for json_data in self.websocket_safe_read():
                if json_data and isinstance(json_data, str):
                    self.events_buffer.append(json.loads(json_data))
                elif isinstance(json_data, dict):
                    self.events_buffer.append(json_data)
        return self.events_buffer.popleft()

    @contextmanager
    def session(self):
        with requests.Session() as session:
            yield slacker.Slacker(self.token, session=session)


class SlackMessage:

    listen_message_subtypes = {
        'message',  # default
        'channel_topic',
        'file_comment',
        'group_purpose',
        'me_message',
        'thread_broadcast',
    }

    def __init__(self, body: dict):
        self.body = body
        self.subtype: str = body.get('subtype', 'message')
        if self.subtype in self.listen_message_subtypes:
            self.active = True
            self.text: str = body['text']
            self.user_id: str = body['user']
            self.is_bot = 'bot_id' in body
            self.channel_id: str = body['channel']
            self.ts: str = body['ts']
            self.thread_ts: Optional[str] = body.get('thread_ts')
        else:
            self.active = False


class SlackBot(MessageHandlerBase):

    def __init__(self, conf, client):
        super().__init__(conf, client)
        self.conf = conf
        self.bot_icon = getattr(self.conf, 'SLACK_BOT_ICON', None)
        self.bot_emoji = getattr(self.conf, 'SLACK_BOT_EMOJI', None)

        self.login_data = {}
        self.users = {}
        self.channels = {}

        self._handlers = {}
        self._matchers = []
        self.register_handler()

    def register_handler(self):
        self._handlers['message'] = (self._handle_message, False)
        self._handlers['login'] = (self._handle_login, True)
        for type_ in ['channel_created', 'channel_rename',
                      'group_joined', 'group_rename',
                      'im_created']:
            self._handlers[type_] = (self._handle_channels, True)
        for type_ in ['team_join', 'user_change']:
            self._handlers[type_] = (self._handler_users, True)

    def _handle_login(self, event):
        import importlib

        self.login_data = event['data']
        self.users = {u['id']: u for u in self.login_data['users']}
        self.channels = {}
        for key in ['channels', 'groups', 'ims']:
            self.channels.update({c['id']: c for c in self.login_data[key]})

        for name in getattr(self.conf, 'SLACK_BOT_MODULES'):
            try:
                _logger.info('try import %s', name)
                importlib.import_module(name)
            except ImportError:
                _logger.error('cannot import %s', name)
            except Exception as e:
                _logger.exception('cannot import %s: %s', name, e)

    def _handle_channels(self, event):
        self.channels[event['channel']['id']] = event['channel']

    def _handler_users(self, event):
        self.users[event['user']['id']] = event['user']

    def _handle_message(self, event):
        print(json.dumps(event, ensure_ascii=False))
        msg = SlackMessage(event)
        if not msg.active or msg.is_bot:
            return

        matched = False
        for matcher, handler in self._matchers:
            m = matcher.match(msg.text)
            if m is not None:
                matched = True
                handler(*m.args, **m.kwargs)
        if not matched:
            _logger.warning('through message: %s', msg.text)

    def run(self):
        self.loop()

    def handle(self, event):
        type_ = event['type']
        if type_ in self._handlers:
            handler, block_main_loop = self._handlers[type_]
            handler(event)

    def post(self, channel, message, attachments=None):
        with self.client.session() as s:
            s.chat.post_message(
                channel,
                message,
                username=self.login_data['self']['name'],
                icon_url=self.bot_icon,
                icon_emoji=self.bot_emoji,
                as_user=True,
                attachments=attachments,
            )

    def listen_to(self, pattern, flag=0):
        from .matcher import Matcher, RegexTokenizer

        def wrapper(func):
            _logger.warning('register matcher: %s %s', pattern, func)
            m = Matcher([RegexTokenizer(pattern, flag)])
            self._matchers.append([m, func])
        return wrapper

    def respond_to(self, pattern, flag=0):
        pass
