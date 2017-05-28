from silence_notifier.state import State


class NoResponsibleState(State):
    def handle_reaction_added(self, data):
        pass

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
        print(data)
        self.communicator.thumb_up_msg(data)

    def handle_silence_stop(self):
        mentions_string = self.communicator.channel_mention

        self.send("sound", mentions=mentions_string)
