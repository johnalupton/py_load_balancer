import time
from multiprocessing import Manager, Process
from typing import Optional
from lb.request import Request
from uuid import uuid4


class Worker:
    def __init__(self, notify_work_done_queue, process_index: int):
        # buffered channel of requests incoming for this worker
        self._requests = Manager().Queue()
        # how long is request buffer to enable load balancer to balance load
        self._pending: int = 0
        self._id = uuid4()
        self._notify_work_done_queue = notify_work_done_queue
        self.process_index = process_index
        print(f"Creating worker {self}")

    def add_request(self, req: Optional[Request]):
        self._requests.put(req)

    def shutdown(self):
        print(f"Shutting worker {self}")
        self.add_request(None)
        # blocks until all work finished (i.e. queue is empty and "None" is processed)
        # self._process.join()

    def __repr__(self):
        return f"{str(self._id)[-6:]}"

    # overload requried for priority queue
    def __lt__(self, rhs):
        return self._pending < rhs.pending

    def __eq__(self, other):
        return self.__repr__ == other.__repr__

    def work(self):
        while True:
            # blocking wait for next item in queue
            req: Request = self._requests.get()
            if req == None:
                break

            req.execute_request()
            self._notify_work_done_queue.put(req)
