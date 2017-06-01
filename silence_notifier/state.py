import logging
import sys
from abc import ABCMeta, abstractmethod


class State(metaclass=ABCMeta):
    """Abstract class representing one state SilencePlugin can be in.

    Methods required by all state classes are defined as abstract methods on
    this class. Methods used by all state classes are also located here.
    """
    def __init__(self, plugin):
        self.communicator = plugin.communicator
        self.activate_no_responsible_state = self._create_activate_no_func(plugin)
        self.activate_some_responsible_state = self._create_activate_some_func(plugin)
        self.responsible_usernames = plugin.responsible_usernames
        self.settings = plugin.settings

    @staticmethod
    def _create_activate_no_func(plugin):
        """Create function for activating the NoResponsibleState state.

        Args:
            plugin: Instance of SilencePlugin to activate states on.

        Returns:
            Function which takes no arguments, which activates the
            NoResponsibleState when called.

        Work-around the fact that Python does not support cyclic dependencies.
        """
        return State._create_activate_func(
            plugin,
            plugin.activate_no_responsible_state
        )

    @staticmethod
    def _create_activate_some_func(plugin):
        """Create function for activating the SomeResponsibleState state.

        Args:
            plugin: Instance of SilencePlugin to activate states on.

        Returns:
            Function which takes no arguments, which activates the
            SomeResponsibleState when called.

        Work-around the fact that Python does not support cyclic dependencies.
        """
        return State._create_activate_func(
            plugin,
            plugin.activate_some_responsible_state
        )

    @staticmethod
    def _create_activate_func(plugin, func):
        """Create function which calls func when called."""
        # TODO: Refactor this so it is set directly in the constructor.
        def activate_state():
            func()
        return activate_state

    def send_custom(self, message, *args, **kwargs):
        """Shortcut for the Communication.send_custom method."""
        return self.communicator.send_custom(message, *args, **kwargs)

    def send(self, message_type, num_warnings=None, **kwargs):
        """Shortcut for the Communication.send method."""
        return self.communicator.send(message_type, num_warnings, **kwargs)

    @abstractmethod
    def handle_message(self, data):
        """Called when a message mentioning us is received."""
        pass

    @abstractmethod
    def handle_timer(self, num_invocations, minutes):
        """Called when it is time to send a warning, if applicable."""
        pass

    def handle_not_running(self):
        """Called when the LiquidSoap process has quit running."""
        self.send("not_running")
        logging.debug("LiquidSoap is no longer running, exiting")
        sys.exit(0)

    def _send_change_responsible(self):
        """Send message summarizing who is recorded as responsible for fixing
        the technical problems."""
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
        """Acknowledge one additional person signing themselves up as
        responsible.

        Args:
            userid: The userid of the person taking responsibility.
            data: The message this is in reply to, in the format received from
                the Slack message event.
        """
        self.send("new_responsible", user="<@{}>".format(userid), reply_to=data)
        self._send_change_responsible()

    def _get_reponsible_mention(self):
        """Returns string mentioning those responsible, using Slack's syntax."""
        mentions = set(["<@{}>".format(userid)
                        for userid in self.responsible_usernames])
        return " ".join(mentions)
