import logging

from silence_notifier.state import State


class NoResponsibleState(State):
    """State for when no one is responsible for fixing the technical problems.
    """
    def handle_timer(self, num_invocations, minutes):
        """Send warning, if applicable."""
        if self.settings.warn_while_no_responsible or num_invocations == 0:
            self.send(
                "warnings",
                minutes,
                min=minutes,
                show=self.communicator.get_current_show()
            )

    def handle_message(self, data):
        """Handle a user mentioning us.

        Args:
            data: Dictionary provided by Slack in a message event.
        """
        userid = data["user"]
        self._handle_responsible(userid, data)

    def handle_silence_stop(self):
        """Handle the silence stopping."""
        if self.settings.mention_channel_when_no_responsible_and_sound:
            mentions_string = self.communicator.channel_mention
        else:
            mentions_string = ""

        self.send("sound", mentions=mentions_string)

    def _handle_responsible(self, userid, data):
        """Handle the first user assigning responsibility to themselves."""
        if self.settings.mention_channel_on_first_responsible:
            self._acknowledge_responsible(userid)
        self.responsible_usernames.append(userid)
        self._acknowledge_additional_responsible(userid, data)
        self.activate_some_responsible_state()

    def _acknowledge_responsible(self, userid):
        """Acknowledge the first user assigning responsibility to themselves."""
        self.send("first_responsible", user="<@{}>".format(userid))
