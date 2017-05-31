import signal


def create_registerer(plugin):
    """Bind plugin so it is used when the returned function is called by the
    system.
    """
    def handle_sigterm(signum, frame):
        """Catch a sigterm and handle the processing to plugin"""
        # Send our good bye message
        plugin.handle_sigterm()
        # Halt execution
        raise KeyboardInterrupt()
    return handle_sigterm


def register(plugin):
    """Register a signal handler which calls plugin.handle_sigterm on SIGTERM.
    """
    signal.signal(signal.SIGTERM, create_registerer(plugin))
