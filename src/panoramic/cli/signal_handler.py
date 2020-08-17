import os
import signal


def _exit(signum: int, frame):
    os._exit(128 + signum)


def setup_exit_signal_handler():
    signal.signal(signal.SIGINT, _exit)
    signal.signal(signal.SIGTERM, _exit)
