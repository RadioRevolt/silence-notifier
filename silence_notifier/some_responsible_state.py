from silence_notifier.state import State


class SomeResponsibleState(State):
    def handle_timer(self, num_invocations, minutes):
        # Not warning anyone
        pass

    def handle_message(self, data):
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
        self.send(
            "new_not_responsible",
            user="<@{}>".format(userid),
            reply_to=data
        )

    def handle_silence_stop(self):
        mentions_string = self._get_reponsible_mention()
        self.send("sound", mentions=mentions_string)

    def _handle_additional_responsible(self, userid, data):
        self.responsible_usernames.append(userid)
        self._acknowledge_additional_responsible(userid, data)

    def _handle_none_responsible(self):
        self._send_change_responsible()
        self._warn_none_responsible()
        self.activate_no_responsible_state()

    def _warn_none_responsible(self):
        self.send("no_responsible")


