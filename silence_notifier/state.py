class State:
    def __init__(self, plugin):
        self.communicator = plugin.communicator
        self.activate_state = self._create_activate_func(plugin)
        self.responsible_usernames = plugin.responsible_usernames
        self.settings = plugin.settings

    @staticmethod
    def _create_activate_func(plugin):
        def activate_state(new_state):
            plugin.activate_state(new_state)
        return activate_state

    def send(self, message, *args, **kwargs):
        return self.communicator.send(message, *args, **kwargs)
