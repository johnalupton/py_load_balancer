import time
from typing import Callable

RequestId = int


class Request:
    def __init__(
        self,
        id: RequestId,
        requester_return_queue,
        fn: Callable,
        *args,
    ):
        self.id = id
        self.requester_return_queue = requester_return_queue
        self.fn: Callable = fn
        self.args = args
        self.requested_at = time.time()

    def do_work(self):
        self.result = self.fn(*self.args)
        self.completed_at = time.time()
        self.requester_return_queue.put(self)
        print(f"Work output {self.result}")

    def __repr__(self):
        return f"{self.id}"
