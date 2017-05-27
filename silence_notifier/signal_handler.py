import signal


def create_registerer(plugin):
    def handle_sigterm(signum, frame):
        # Send our good bye message
        plugin.handle_sigterm()
        # Halt execution
        raise KeyboardInterrupt()
    return handle_sigterm


def register(plugin):
    signal.signal(signal.SIGTERM, create_registerer(plugin))
