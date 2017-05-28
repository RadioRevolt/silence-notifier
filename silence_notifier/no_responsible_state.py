import logging

from silence_notifier.state import State


class NoResponsibleState(State):
    def handle_reaction_added(self, data):
        userid = data["user"]
        self._handle_responsible(userid)

    def handle_reaction_removed(self, data):
        pass

    def handle_timer(self, num_invocations, minutes):
        self.send(
            "warnings",
            num_invocations,
            min=minutes,
            show=self.communicator.get_current_show()
        )

    def handle_message(self, data):
        userid = data["user"]
        self._handle_responsible(userid)
        self.communicator.thumb_up_msg(data)

    def handle_silence_stop(self):
        mentions_string = self.communicator.channel_mention

        self.send("sound", mentions=mentions_string)

    def _handle_responsible(self, userid):
        self._acknowledge_responsible(userid)
        self.responsible_usernames.append(userid)
        self.activate_some_responsible_state()

    def _acknowledge_responsible(self, userid):
        self.send("first_responsible", user="<@{}>".format(userid))
