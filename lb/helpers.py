from multiprocessing import Process

from lb.constants import num_requests_per_requester
from lb.requester import Requester
from lb.worker import Worker

workers = []
workers_processes = []


def spawn_workers(n: int, manager, done_queue):
    for i in range(n):
        w = Worker(manager)
        workers.append(w)
        p = Process(target=w.do_work, args=(done_queue,))
        workers_processes.append(p)
        p.start()

    return workers


def stop_workers_with_blocking():
    for p in workers_processes:
        p.join()


requesters = []
processes_req = []


# start all requesters (contingent on balancer being created so that the request queue exists)
def spawn_requesters(n, request_queue, manager):
    for i in range(n):
        requester = Requester(request_queue, manager)
        p = Process(
            target=requester.generate_requests, args=(num_requests_per_requester,)
        )
        p.start()
        processes_req.append(p)

        requesters.append(requester)
    return requesters, processes_req
