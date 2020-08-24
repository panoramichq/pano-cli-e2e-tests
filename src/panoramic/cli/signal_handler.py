import os
import signal
from contextlib import contextmanager


@contextmanager
def handle_interrupt():
    try:
        yield None
    except KeyboardInterrupt:
        os._exit(128 + signal.SIGINT)
