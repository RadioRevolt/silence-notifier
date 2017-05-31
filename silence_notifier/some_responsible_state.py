from silence_notifier.state import State


class SomeResponsibleState(State):
    """State for when at least one person has taken responsibility for fixing
    the problems."""
    def handle_timer(self, num_invocations, minutes):
        """Do not send any warning, since someone is looking into it."""
        # Not warning anyone
        pass

    def handle_message(self, data):
        """Handle either someone taking responsibility, or someone leaving it.

        Args:
            data: Dictionary of the data received from the message Slack event.
        """
        userid = data["user"]
        if userid in self.responsible_usernames:
            # The user was already registered, so unregister.
            self.responsible_usernames.remove(userid)
            self._acknowledge_one_less_responsible(userid, data)

            if not self.responsible_usernames:
                self._handle_none_responsible()
        else:
            # The user wants to be registered
            self._handle_additional_responsible(userid, data)

    def _acknowledge_one_less_responsible(self, userid, data):
        """Acknowledge someone leaving responsibility.

        Args:
            userid: userid of the user leaving responsibility.
            data: Dictionary of the data received from the message Slack event.
        """
        self.send(
            "new_not_responsible",
            user="<@{}>".format(userid),
            reply_to=data
        )

    def handle_silence_stop(self):
        """Notice the appropriate people of the silence ending."""
        mentions_string = self._get_reponsible_mention()
        self.send("sound", mentions=mentions_string)

    def _handle_additional_responsible(self, userid, data):
        """Handle that one more person has taken responsibility.

        Args:
            userid: userid of the user taking responsbility.
            data: Dictionary of the data received from the message Slack event.
        """
        self.responsible_usernames.append(userid)
        self._acknowledge_additional_responsible(userid, data)

    def _handle_none_responsible(self):
        """Handle that the last person has left responsibility."""
        self._send_change_responsible()
        self._warn_none_responsible()
        self.activate_no_responsible_state()

    def _warn_none_responsible(self):
        """Warn on Slack that no one has responsibility any longer."""
        self.send("no_responsible")


