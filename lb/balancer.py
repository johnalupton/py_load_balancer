from time import sleep
from lb.constants import STOP
from lb.request import Request


class Balancer:
    def __init__(self, manager):
        """Set up a new Balancer.

        Args:
            manager multiprocessing.Manager: Manager object to facilitate sharing of queues across spawned processes
        """
        # single inbound FIFO queue of requests
        self.request_queue = manager.Queue()
        # Queue for workers to report back to the balancer that a request sent to it is done
        self.done_queue = manager.Queue()
        # audit count of number of requests received by the balancer
        self.requests_received = 0
        # pool of workers to do work
        self.workers_pool = []
        # index into worker pool to indicate the last worker used
        self.last_worker_used = 0

    def allocate_next_worker(self):
        """Allocate the next worker to have work sent to it

        Returns:
            Worker: If a proiority queue/heap was created, using the count of pending requests
            that a worker has then could implement the return of the least loaded worker
            in the worker pool. For pragmatism here the next worker is simply iterating through
            all workers in the pool.
        """
        # calculate the index of the next worker to allocate
        self.last_worker_used = (self.last_worker_used + 1) % len(self.workers_pool)
        # return the allocated worker
        return self.workers_pool[self.last_worker_used]

    def balance_requests(self):
        """Loop while the request queue is not stopped. For each request retrieved, allocate the next worker
        and dispatch the request to the worker.
        """
        requests_loop_not_stopped = True
        while requests_loop_not_stopped:
            # while there are requests on the requests queue
            while not self.request_queue.empty():
                # get the next request
                req: Request = self.request_queue.get()

                # if the request signals stop then set requests_loop_not_stopped to false
                # the loop does not break her: reason being that any requests after the
                # STOP signal will get flushed (should never happen ...)
                if req == STOP:
                    requests_loop_not_stopped = False
                    print(
                        f"Request polling stopped - {self.requests_received} requests received",
                        flush=True,
                    )
                else:
                    # invrement requests received count
                    self.requests_received += 1
                    # allocate next worker and put this request onto the workers inbound request queue
                    self.allocate_next_worker().worker_request_queue.put(req)

    def stop_requests(self):
        """Send a STOP signal to the queue processing loop. There may still be requests in the queue
        in front of the STOP so loop while these are allocated to workers and then send a STOP to
        the workers.
        """
        # stop sending requests to workers
        self.request_queue.put(STOP)

        # do nothing until request queue empty
        while not self.request_queue.empty():
            sleep(0.01)

        # send stop signal to workers
        for w in self.workers_pool:
            w.stop_working()

    def drain_work_done(self):
        """Drain and report to stdout the contents of the work done queue. In a realistic application
        would likely do some audit statistics here to check all work done
        """
        count = 0
        while not self.done_queue.empty():
            # done queue items are a tuple of (Request.__repr__, result)
            req_id, result = self.done_queue.get()
            print(f"Done request {req_id} with result {result}")
            count += 1
        print(f"{count} requests were done")
