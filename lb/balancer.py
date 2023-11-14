from time import sleep
from multiprocessing import Manager
from typing import Callable
from lb.request import Request


class Balancer:
    def __init__(self, nWorker: int):
        _manager = Manager()

        # queue to notify work has been done
        # in bound notification of completed work
        self.notify_work_done_queue = _manager.Queue()
        # outbound distribution of work
        self.work_requests_queue = _manager.Queue()

        # cab rank of workers
        self.worker_pool = []

        self.work_sent = dict()
        self.num_requests_at_workers = 0

    def balance_work(self):
        process_requests = True
        while process_requests:
            # empty work done
            #
            # empty work_requests
            while not self.work_requests_queue.empty():
                sleep(0.5)

                r: Request = self.work_requests_queue.get()
                if r is None:
                    process_requests = False
                    break
                print(f"Doing {r}")
                r.do_work()

    def shutdown(self):
        pass
