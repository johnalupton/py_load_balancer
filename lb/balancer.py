import time

from multiprocessing import Manager, Process

from lb.request import Request

from lb.worker import Worker


class Balancer:
    def __init__(self, nWorker: int):
        # cab rank of workers
        self.worker_pool = []
        self.process_pool = []

        # pipe to notify work has been done

        self.done = Manager().Queue()

        self.next = 0

        self.work_sent = 0

        self.work_done = 0

        for i in range(nWorker):
            w = Worker()
            self.worker_pool.append(w)

            p = Process(target=w.work, args=(self.done,))
            p.start()
            self.process_pool.append(p)

    def dispatch(self, req: Request):
        # get least loaded worker

        w: Worker = self.worker_pool[self.next]

        w.requests.put(req)

        w.pending = w.pending + 1

        self.next = (self.next + 1) % len(self.worker_pool)

        self.work_sent += 1

    def completed(self, w: Worker):
        w.pending = w.pending - 1

        self.work_done += 1

    def balance(self, work):
        is_work = True
        last_work = time.time()

        while is_work or self.work_done < self.work_sent:
            # drain work in

            work_found = False

            while not work.empty():
                work_found = True

                req: Request = work.get()

                print(f"BAL,{req}")

                self.dispatch(req)

            if work_found:
                last_work = time.time()

            if time.time() - last_work > 5:
                is_work = False

            # drain work done

            while not self.done.empty():
                w: Worker = self.done.get()

                self.completed(w)

        for w in self.worker_pool:
            w.requests.put(-1)


        # for p in self.process_pool:
        #     p.join()

        # print(f"{self.work_done}/{self.work_sent:}")
