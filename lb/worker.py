from uuid import uuid4

from lb.constants import STOP
from lb.request import Request


class Worker:
    def __init__(self, manager):
        self.worker_request_queue = manager.Queue()
        self.requests_received = 0
        self.id = uuid4()

    def __repr__(self):
        return str(self.id)[-6:]

    def stop_working(self):
        self.worker_request_queue.put(STOP)

    def do_work(self, done_queue):
        loop_for_requests = True
        while loop_for_requests:
            while not self.worker_request_queue.empty():
                req: Request = self.worker_request_queue.get()

                if req == STOP:
                    loop_for_requests = False
                else:
                    self.requests_received += 1
                    req.evaluate_and_return_result()
                    done_queue.put((req.__repr__(), req.result))
