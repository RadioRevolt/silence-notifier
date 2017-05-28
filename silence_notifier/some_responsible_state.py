from silence_notifier.state import State


class SomeResponsibleState(State):
    def handle_timer(self, num_invocations, minutes):
        # Not warning anyone
        pass

    def handle_message(self, data):
        userid = data["user"]
        if userid in self.responsible_usernames:
            # The user was already registered, so unregister.
            while userid in self.responsible_usernames:
                self.responsible_usernames.remove(userid)

            if self.responsible_usernames:
                # User removed, but others remain
                self._acknowledge_one_less_responsible(userid)
            else:
                self._handle_none_responsible()
        else:
            # The user wants to be registered
            self._handle_additional_responsible(userid)

    def _acknowledge_one_less_responsible(self, userid):
        self.send("new_not_responsible", user="<@{}>".format(userid))

    def handle_silence_stop(self):
        mentions = set(["<@{}>".format(userid)
                    for userid in self.responsible_usernames])
        mentions_string = " ".join(mentions)
        self.send("sound", mentions=mentions_string)

    def _handle_additional_responsible(self, userid):
        if userid not in self.responsible_usernames:
            self._acknowledge_additional_responsible(userid)
        self.responsible_usernames.append(userid)

    def _acknowledge_additional_responsible(self, userid):
        self.send("new_responsible", user="<@{}>".format(userid))

    def _handle_none_responsible(self):
        self._warn_none_responsible()
        self.activate_no_responsible_state()

    def _warn_none_responsible(self):
        self.send("no_responsible")
