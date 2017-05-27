import logging

from rtmbot.core import Plugin, Job

from silence_notifier.no_responsible_state import NoResponsibleState
from silence_notifier.settings import Settings
from silence_notifier.communication import Communicator
from silence_notifier import signal_handler


class SilenceNotifyJob(Job):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._minutes_to_next = 0
        self._delays = []
        self._active_state = None

    def update_state(self, new_state):
        self._active_state = new_state

    def _populate_next_delay(self):
        next_delay = self._calculate_next_delay(self._delays)
        self._delays.append(next_delay)

    @staticmethod
    def _calculate_next_delay(previous_delays):
        """Find the next delay in the sequence 5, 5, 10, 15, 25, 40, 65, 105…"""
        if len(previous_delays) in (0, 1):
            return 5
        else:
            n_2 = previous_delays[-2]
            n_1 = previous_delays[-1]
            return n_2 + n_1

    def run(self, slack_client):
        self._minutes_to_next -= 1
        print("Der ble vi kjørt. Minutter igjen:", self._minutes_to_next)
        if self._minutes_to_next <= 0 and self._active_state:
            self._active_state.do_periodical_warning(len(self._delays))
            # Prepare to wait for next warning
            self._populate_next_delay()
            self._minutes_to_next = self._delays[-1]
            print("Oi, der slo vi inn. Delays nå:", self._delays)
        return []


class SilencePlugin(Plugin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._active_state = None
        self._silence_notify_job = None
        self.responsible_usernames = []
        self.settings = Settings()
        self.communicator = Communicator(self.slack_client, self.settings)

        self.activate_state(NoResponsibleState)
        signal_handler.register(self)

        logging.warning("Plugin init")

    def register_jobs(self):
        self._silence_notify_job = SilenceNotifyJob(10)
        self._silence_notify_job.update_state(self._active_state)
        self.jobs.append(self._silence_notify_job)
        logging.warning("Jobs registered")

    def activate_state(self, new_state_class):
        new_state_instance = new_state_class(self)
        self._active_state = new_state_instance
        if self._silence_notify_job:
            self._silence_notify_job.update_state(new_state_instance)

    def handle_sigterm(self):
        self._active_state.handle_silence_stop()

    def process_message(self, data):
        self._active_state.handle_message(data)
