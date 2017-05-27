from silence_notifier.state import State


class SomeResponsibleState(State):
    def handle_message(self, data):
        pass

    def handle_silence_stop(self):
        pass

    def do_periodical_warning(self, num_warning):
        pass
