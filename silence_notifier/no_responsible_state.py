import logging

from silence_notifier.state import State


class NoResponsibleState(State):
    def handle_timer(self, num_invocations, minutes):
        if self.settings.warn_while_no_responsible or num_invocations == 0:
            self.send(
                "warnings",
                minutes,
                min=minutes,
                show=self.communicator.get_current_show()
            )

    def handle_message(self, data):
        userid = data["user"]
        self._handle_responsible(userid, data)

    def handle_silence_stop(self):
        if self.settings.mention_channel_when_no_responsible_and_sound:
            mentions_string = self.communicator.channel_mention
        else:
            mentions_string = ""

        self.send("sound", mentions=mentions_string)

    def _handle_responsible(self, userid, data):
        if self.settings.mention_channel_on_first_responsible:
            self._acknowledge_responsible(userid)
        self.responsible_usernames.append(userid)
        self._acknowledge_additional_responsible(userid, data)
        self.activate_some_responsible_state()

    def _acknowledge_responsible(self, userid):
        self.send("first_responsible", user="<@{}>".format(userid))
