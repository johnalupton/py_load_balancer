from multiprocessing import Manager, Process

from lb.balancer import Balancer
from lb.request import Request
from lb.work_fns import weird_cube


nRequester = 2
nWorker = 5


if __name__ == "__main__":
    balancer = Balancer(nWorker)
    requester_return_queue = Manager().Queue()

    for i in range(10):
        r = Request(i, requester_return_queue, weird_cube, i, i + 1)
        balancer.work_requests_queue.put(r)

    # spawn non-blocking balancer
    Process(target=balancer.balance_work).

    # stop the balancer
    balancer.work_requests_queue.put(None)

    balancer.shutdown()

    while not requester_return_queue.empty():
        print(f"Returned queue {requester_return_queue.get()}")
