from time import sleep
from multiprocessing import Manager, Process
from lb.request import Request
from lb.worker import Worker


class Balancer:
    def __init__(self, num_workers: int):
        _manager = Manager()

        # queue to notify work has been done
        # in bound notification of completed work
        self._notify_work_done_queue = _manager.Queue()
        # outbound distribution of work
        self._work_requests_queue = _manager.Queue()

        # cab rank of workers
        self._worker_pool = []
        self._worker_pool_processes = dict()
        self.last_process_index = 0

        self._work_sent = dict()
        self._num_requests_at_workers = 0
        self._active_workers = 0
        self._start_more_workers(num_workers)

    def _shutdown_running_workers(self, num_workers):
        if num_workers > 0:
            self._start_more_workers(-num_workers)
            return
        for _ in range(num_workers):
            self._shutdown_one_worker()

    def _start_more_workers(self, num_workers):
        if num_workers < 0:
            self._shutdown_running_workers(-num_workers)
            return
        for _ in range(num_workers):
            self._start_one_worker()

    def _get_next_worker(self):
        return self._worker_pool[0]

    def balance_work(self):
        process_requests = True
        while process_requests:
            # empty work done
            #
            # empty work_requests
            while not self._work_requests_queue.empty():
                sleep(0.5)

                req: Request = self._work_requests_queue.get()
                if req is None:
                    process_requests = False
                    break
                print(f"Doing {req}")
                w: Worker = self._get_next_worker()
                w.add_request(req)

    def _adjust_worker_count(self, n: int):
        # guard to make sure no tomfoolery
        if self._active_workers + n < 0:
            raise IndexError(
                f"self.num_workers is {self._active_workers} and can not be adjusted by {n} to make it negative"
            )

        self._active_workers += n

    def _start_one_worker(self):
        w = Worker(self._notify_work_done_queue, self.last_process_index)
        self.last_process_index += 1
        self._worker_pool.append(w)
        p = Process(target=w.work)
        # self._worker_pool_processes[w.process_index] = p
        p.start()
        self._adjust_worker_count(1)

    def _shutdown_one_worker(self):
        # shut down least loaded worker as this will be quickest to remove
        w: Worker = self._worker_pool.pop()
        w.shutdown()
        self._adjust_worker_count(-1)

    def shutdown(self):
        # shutdown all workers
        # drive off actually running workers to ensure no hanging processes
        # raise any error *after* workers shut down as least destructive
        # in the case of an error
        # len(self.worker_pool) dynamic as workers removed so need to cache start len
        n = len(self._worker_pool)
        for _ in range(n):
            self._shutdown_one_worker()

        if self._active_workers != 0:
            raise IndexError(
                f"self.num_workers is {self._active_workers} not zero after shutting all workers in the worker pool"
            )

        self._worker_pool = []
