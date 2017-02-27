import collections
import heapq
import threading


class Lock():

    def __init__(self):
        self._lock = threading.Lock()
        self.acquire = self._lock.acquire
        self.release = self._lock.release

    def __lt__(self, _):
        return False


class SessionQueue(object):

    def __init__(self):
        self._nowait_queue = collections.deque()
        self._wait_queue = collections.deque()
        self._waiters = []
        self._lock = threading.Lock()

    def put(self, item):
        with self._lock:
            if not self._waiters:
                self._nowait_queue.append(item)
                return
            self._wait_queue.append(item)
            self._notify()

    def get(self, priority):
        self._lock.acquire()
        if self._nowait_queue:
            item = self._nowait_queue.popleft()
            self._lock.release()
            return item
        return self._wait(priority)

    def _notify(self):
        _, waiter = heapq.heappop(self._waiters)
        waiter.release()

    def _wait(self, priority):
        waiter = Lock()
        waiter.acquire()
        heapq.heappush(self._waiters, (priority, waiter))
        self._lock.release()
        waiter.acquire()
        return self._wait_queue.popleft()
