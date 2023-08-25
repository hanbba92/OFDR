import datetime
from threading import Thread, Event
import time
from typing import Callable


class TimedCalls(Thread):
    """Call function again every `interval` time duration after it's first run."""
    def __init__(self, func: Callable, interval: datetime.timedelta) -> None:
        super().__init__()
        self.func = func
        self.interval = interval
        self.stopped = Event()

    def cancel(self):
        self.stopped.set()

    def run(self):
        next_call = time.time()
        while not self.stopped.is_set():
            self.func()  # Target activity.
            next_call = next_call + self.interval
            # Block until beginning of next interval (unless canceled).
            self.stopped.wait(next_call - time.time())

