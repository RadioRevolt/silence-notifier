from abc import ABCMeta, abstractmethod


class State(metaclass=ABCMeta):
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

    def send_custom(self, message):
        return self.communicator.send_custom(message)

    def send(self, message_type, num_warnings=None, **kwargs):
        return self.communicator.send(message_type, num_warnings, **kwargs)

    @abstractmethod
    def handle_message(self, data):
        pass

    @abstractmethod
    def handle_reaction_added(self, data):
        pass

    @abstractmethod
    def handle_reaction_removed(self, data):
        pass

    @abstractmethod
    def handle_timer(self, num_invocations, minutes):
        pass
