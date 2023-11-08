from uuid import uuid4
import time

from multiprocessing import Manager
from typing import Callable


class Request:

    def __init__(self, fn: Callable, c, requester: int, id):
        self.fn: Callable = fn
        self.c = c
        self.id = requester * 10000000 + id
        self.requester = requester
        self.requested_at = time.time()

    def do_work(self):
        self.result = self.fn()
        self.completed_at = time.time()

    def __repr__(self):
        return f"{self.requester},{self.id}"
