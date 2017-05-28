from silence_notifier.state import State


class SomeResponsibleState(State):
    def handle_reaction_added(self, data):
        pass

    def handle_reaction_removed(self, data):
        pass

    def handle_timer(self, num_invocations):
        pass

    def handle_message(self, data):
        pass

    def handle_silence_stop(self):
        mentions = ["<@{}>".format(user[0])
                    for user in self.responsible_usernames]
        mentions_string = " ".join(mentions)
        self.send("sound", mentions=mentions_string)
