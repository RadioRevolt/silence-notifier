from silence_notifier.state import State


class NoResponsibleState(State):
    def handle_message(self, data):
        print(data)
        self.communicator.thumb_up_msg(data)

    def handle_silence_stop(self):
        self.send("Nå stopper vi")

    def do_periodical_warning(self, num_warning):
        self.send("Dette er et varsel")
