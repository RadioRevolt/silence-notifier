import logging

from rtmbot.core import Plugin, Job

from silence_notifier.no_responsible_state import NoResponsibleState
from silence_notifier.settings import Settings
from silence_notifier.communication import Communicator
from silence_notifier import signal_handler
from silence_notifier.some_responsible_state import SomeResponsibleState


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
        logging.debug("Regular job run. Minutes to next warning: " +
                      str(self._minutes_to_next))
        if self._minutes_to_next <= 0 and self._active_state:
            self._active_state.handle_timer(
                len(self._delays),
                sum(self._delays)
            )
            # Prepare to wait for next warning
            self._populate_next_delay()
            self._minutes_to_next = self._delays[-1]
            logging.debug("Warning sent. New delays: " + str(self._delays))
        return []


class SilencePlugin(Plugin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.debug("Initializing SilencePlugin")
        self._active_state = None
        self._silence_notify_job = None
        self.responsible_usernames = []
        self.settings = Settings()
        self.communicator = Communicator(self.slack_client, self.settings)

        self.activate_state(NoResponsibleState)
        signal_handler.register(self)

        self.userid = self.communicator.get_userid()
        self.username = self.communicator.get_username()
        logging.debug("Initialized SilencePlugin")

    def register_jobs(self):
        self._silence_notify_job = SilenceNotifyJob(10)
        self._silence_notify_job.update_state(self._active_state)
        self.jobs.append(self._silence_notify_job)
        logging.debug("Jobs registered")

    def activate_no_responsible_state(self):
        self.activate_state(NoResponsibleState)

    def activate_some_responsible_state(self):
        self.activate_state(SomeResponsibleState)

    def activate_state(self, new_state_class):
        logging.debug("Changing to state " + new_state_class.__name__)
        new_state_instance = new_state_class(self)
        self._active_state = new_state_instance
        if self._silence_notify_job:
            self._silence_notify_job.update_state(new_state_instance)

    def handle_sigterm(self):
        logging.debug("Reacting to SIGTERM")
        self._active_state.handle_silence_stop()

    def process_message(self, data):
        if self.relevant_message(data):
            logging.debug("Relevant message: " + data['text'])
            self._active_state.handle_message(data)

    def process_reaction_added(self, data):
        if self.relevant_reaction(data):
            logging.debug("Relevant reaction added: {} from {} to {}".format(
                data['reaction'], data['user'], data['item']['ts']
            ))
            self._active_state.handle_reaction_added(data)

    def process_reaction_removed(self, data):
        if self.relevant_reaction(data):
            logging.debug("Relevant reaction removed: {} from {} to {}".format(
                data['reaction'], data['user'], data['item']['ts']
            ))
            self._active_state.handle_reaction_removed(data)

    def relevant_reaction(self, data):
        reaction_to_our_message = data['item_user'] == self.userid
        reaction_to_recent_message = \
            data['item']['type'] == "message" and \
            self.communicator.get_first_message_ts() and \
            data['item']['ts'] >= self.communicator.get_first_message_ts()
        recognized_reaction = \
            data['reaction'] in self.settings.recognized_reactions
        return reaction_to_our_message and reaction_to_recent_message and \
               recognized_reaction

    def relevant_message(self, data):
        mentions_us = self.userid in data['text']
        return mentions_us
