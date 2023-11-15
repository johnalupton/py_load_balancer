from multiprocessing import Process

from lb.constants import num_requests_per_requester
from lb.requester import Requester
from lb.worker import Worker

workers = []
workers_processes = []


def spawn_workers(num_workers: int, manager, done_queue):
    """Create and spawn new Workers as independent processes

    Args:
        num_workers (int): number of workers to spawn
        manager (mutiprocessing.Manager): Manager object to coordinate inter-process queues
        done_queue (mutiprocessing.Queue): Queue back to the balancer to notify work done

    Returns:
        List[Worker]: List of workers set up
    """
    for i in range(num_workers):
        # create new Worker
        w = Worker(manager)
        # Add to workers created list
        workers.append(w)

        # create new process for worker to "do_work" - loop processing incoming work Requests
        p = Process(target=w.do_work, args=(done_queue,))
        # Appened process to the list of spawned processes (required later to join)
        workers_processes.append(p)
        # start the process
        p.start()

    return workers


def stop_workers_with_blocking():
    """Stop all previously started worker processes"""
    # join blocks until all processes joined (ended)
    for p in workers_processes:
        p.join()


requesters = []
processes_req = []


def spawn_requesters(num_requesters, request_queue, manager):
    """Start all requesters (contingent on balancer being created so that the request queue exists)

    Args:
        num_requesters (int): number of requester processes to start
        request_queue (multiprocessing.Queue): The FIFO request queue into the Balancer
        manager (mutiprocessing.Manager): Manager object to coordinate inter-process queues

    Returns:
        (List[Requesters], List[Process]): List of requesters and Processes of spawned Requesters
        to enable management and termination
    """
    for i in range(num_requesters):
        requester = Requester(request_queue, manager)
        p = Process(
            target=requester.generate_requests, args=(num_requests_per_requester,)
        )
        p.start()
        processes_req.append(p)

        requesters.append(requester)
    return requesters, processes_req
