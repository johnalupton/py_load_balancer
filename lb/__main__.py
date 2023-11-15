import time
from multiprocessing import Manager, Process

from lb.balancer import Balancer
from lb.constants import num_requesters, num_workers
from lb.helpers import spawn_requesters, spawn_workers, stop_workers_with_blocking

if __name__ == "__main__":
    manager = Manager()

    # initialise balancer and workers
    balancer = Balancer(manager)
    workers = spawn_workers(num_workers, manager, balancer.done_queue)
    balancer.workers = workers

    # start requesters
    requesters, processes_req = spawn_requesters(
        num_requesters, balancer.request_queue, manager
    )

    t = time.time()

    # start balancer balancing
    # will start to put results into the results queues of the requesters
    p_bal = Process(target=balancer.balance_requests)
    p_bal.start()

    # start results pollers for each requester
    # each requester has its own results notification channel
    processes_res = []
    for requester in requesters:
        p = Process(target=requester.poll_results)
        p.start()
        processes_res.append(p)

    # balancer can be stopped once all requesters have finished requesting
    # complete all request senders
    for p in processes_req:
        p.join()

    balancer.stop_requests()

    # block while wait for processes to stop
    stop_workers_with_blocking()

    # wait for balancer to close
    p_bal.join()

    # finish all results polling before exiting
    for requester in requesters:
        requester.stop_polling_results()

    for p in processes_res:
        p.join()

    # processing done here
    t = time.time() - t

    # drain balancer done
    balancer.drain_work_done()
    print(f"elapsed time = {t}s")
