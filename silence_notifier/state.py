from abc import ABCMeta, abstractmethod


class State(metaclass=ABCMeta):
    def __init__(self, plugin):
        self.communicator = plugin.communicator
        self.activate_no_responsible_state = self._create_activate_no_func(plugin)
        self.activate_some_responsible_state = self._create_activate_some_func(plugin)
        self.responsible_usernames = plugin.responsible_usernames
        self.settings = plugin.settings

    @staticmethod
    def _create_activate_no_func(plugin):
        return State._create_activate_func(
            plugin,
            plugin.activate_no_responsible_state
        )

    @staticmethod
    def _create_activate_some_func(plugin):
        return State._create_activate_func(
            plugin,
            plugin.activate_some_responsible_state
        )

    @staticmethod
    def _create_activate_func(plugin, func):
        def activate_state():
            func()
        return activate_state

    def send_custom(self, message):
        return self.communicator.send_custom(message)

    def send(self, message_type, num_warnings=None, **kwargs):
        return self.communicator.send(message_type, num_warnings, **kwargs)

    @abstractmethod
    def handle_message(self, data):
        pass

    @abstractmethod
    def handle_timer(self, num_invocations, minutes):
        pass

    def _send_change_responsible(self):
        if self.responsible_usernames:
            self.send(
                "change_responsible",
                users=self._get_reponsible_mention()
            )
        else:
            self.send(
                "change_none_responsible"
            )

    def _acknowledge_additional_responsible(self, userid, data):
        self.send("new_responsible", user="<@{}>".format(userid), reply_to=data)
        self._send_change_responsible()

    def _get_reponsible_mention(self):
        mentions = set(["<@{}>".format(userid)
                        for userid in self.responsible_usernames])
        return " ".join(mentions)
