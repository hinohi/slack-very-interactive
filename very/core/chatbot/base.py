# -*- coding: utf-8 -*-
import time


__all__ = [
    'ChatClientBase',
    'MessageHandlerBase',
]


class ChatClientBase:

    def __init__(self, conf):
        self.conf = conf

    def get_event(self):
        raise NotImplemented


class MessageHandlerBase:

    def __init__(self, conf, client):
        self.conf = conf
        self.client = client

    def handle(self, event):
        raise NotImplemented

    def loop(self):
        while True:
            event = self.client.get_event()
            self.handle(event)
            time.sleep(1)
