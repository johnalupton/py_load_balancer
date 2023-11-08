import time
from multiprocessing import Manager
from lb.request import Request
from uuid import uuid4
import lb.ids


class Worker:
    def __init__(self):
        # buffered channel of requests incoming for this worker
        self.requests = Manager().Queue()
        # how long is request buffer to enable load balancer to balance load
        self.pending: int = 0
        self.id = lb.ids.worker_id

    def __repr__(self):
        return f"Worker:{self.id:04d}({self.pending}):"

    # overload requried for priority queue
    def __lt__(lhs, rhs):
        return lhs.pending < rhs.pending

    def __eq__(self, other):
        return self.__repr__ == other.__repr__

    def work(self, done):
        while True:
            # blocks
            req: Request = self.requests.get()
            if req == -1:
                break
            req.c.put(req)
            done.put(self)
