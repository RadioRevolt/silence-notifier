import logging
import signal
import threading


def create_registerer(plugin):
    """Bind plugin so it is used when the returned function is called by the
    system.
    """
    lock = threading.Lock()

    def handle_sigterm(signum, frame):
        """Catch a sigterm and handle the processing to plugin"""
        # Protect so only one sigterm is handled, not two at once
        if lock.acquire(blocking=False):
            logging.debug("First SIGTERM received.")
            # Send our good bye message
            plugin.handle_sigterm()
            # Halt execution
            raise KeyboardInterrupt()
        else:
            logging.debug("SIGTERM received, but we are already handling one.")
    return handle_sigterm


def register(plugin):
    """Register a signal handler which calls plugin.handle_sigterm on SIGTERM.
    """
    signal.signal(signal.SIGTERM, create_registerer(plugin))
