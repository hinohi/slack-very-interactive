# -*- coding: utf-8 -*-
import time
from logging import getLogger
from ssl import SSLError
import json
from collections import deque
from contextlib import contextmanager

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
        import requests
        import slacker

        with requests.Session() as session:
            yield slacker.Slacker(self.token, session=session)


class SlackHandler(MessageHandlerBase):

    def __init__(self, conf, client):
        super().__init__(conf, client)
        self._handlers = {}
        self._matcher = []

    def register_event_handler(self, type_, handler, block_main_loop=False):
        self._handlers[type_] = (handler, block_main_loop)

    def register_message_matcher(self, matcher, handler):
        self._matcher.append((matcher, handler))

    def handle(self, event):
        type_ = event['type']
        if type_ == 'message':
            self.handle_message(event)
        elif type_ in self._handlers:
            handler, block_main_loop = self._handlers[type_]
            handler(event)

    def handle_message(self, event):
        pass


class SlackBot:

    def __init__(self, conf):
        self.conf = conf
        self.bot_icon = getattr(self.conf, 'SLACK_BOT_ICON', None)
        self.bot_emoji = getattr(self.conf, 'SLACK_BOT_EMOJI', None)

        self.login_data = {}
        self.users = {}
        self.channels = {}

        self.client = SlackClient(self.conf)
        self.handler = SlackHandler(self.conf, self.client)
        self.register_handler()

    def register_handler(self):
        self.handler.register_event_handler('login', self.handle_login, True)
        for type_ in ['channel_created', 'channel_rename',
                      'group_joined', 'group_rename',
                      'im_created']:
            self.handler.register_event_handler(type_, self.handle_channels, True)
        for type_ in ['team_join', 'user_change']:
            self.handler.register_event_handler(type_, self.handler_users, True)

    def handle_login(self, event):
        self.login_data = event['data']
        self.users = {u['id']: u for u in self.login_data['users']}
        self.channels = {}
        for key in ['channels', 'groups', 'ims']:
            self.channels.update({c['id']: c for c in self.login_data[key]})

    def handle_channels(self, event):
        self.channels[event['channel']['id']] = event['channel']

    def handler_users(self, event):
        self.users[event['user']['id']] = event['user']

    def run(self):
        self.handler.loop()
