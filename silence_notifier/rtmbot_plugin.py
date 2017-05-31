import logging

from rtmbot.core import Plugin, Job

from silence_notifier.no_responsible_state import NoResponsibleState
from silence_notifier.settings import Settings
from silence_notifier.communication import Communicator
from silence_notifier import signal_handler
from silence_notifier.some_responsible_state import SomeResponsibleState


class SilenceNotifyJob(Job):
    """Job run every minute to enable periodical warnings"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._minutes_to_next = 0
        self._delays = []
        self._active_state = None
        self.settings = None

    def update_state(self, new_state):
        """Update which state is the currently active one.

        Args:
            new_state: Instance of an implementation of State.
        """
        self._active_state = new_state

    def set_settings(self, settings):
        """Inform this instance of the settings.

        Args:
            settings: Instance of settings.Settings
        """
        self.settings = settings

    def _populate_next_delay(self):
        """Extend self._delays with the next delay."""
        next_delay = self._calculate_next_delay(self._delays)
        self._delays.append(next_delay)

    def _calculate_next_delay(self, previous_delays):
        """Return the next delay, based on the earlier delays.

        Args:
            previous_delays: List of earlier delays.
        """
        num_delays = len(previous_delays)
        warning_delays = self.settings.warning_delays
        if num_delays < len(warning_delays):
            # Use the delays from the settings
            return warning_delays[num_delays]
        elif len(warning_delays) == 1:
            # Just repeat the one delay
            return warning_delays[0]
        else:
            # Do some fib stuff
            n_2 = previous_delays[-2]
            n_1 = previous_delays[-1]
            return n_2 + n_1

    def run(self, slack_client):
        """Function run by RtmBot every minute."""
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
    """RtmBot Plugin for sending warnings about silence on the radio stream.

    The plugin assumes that the silence lasts as long as the program is running.
    """

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
        """
        Method run by RtmBot to register jobs which should be run periodically.
        """
        self._silence_notify_job = SilenceNotifyJob(self.settings.sec_per_min)
        self._silence_notify_job.update_state(self._active_state)
        self._silence_notify_job.set_settings(
            self.settings
        )
        self.jobs.append(self._silence_notify_job)
        logging.debug("Jobs registered")

    def activate_no_responsible_state(self):
        """Method for states, used to switch to the NoResponsibleState."""
        self.activate_state(NoResponsibleState)

    def activate_some_responsible_state(self):
        """Method for states, used to switch to the SomeResponsibleState."""
        self.activate_state(SomeResponsibleState)

    def activate_state(self, new_state_class):
        """Change to the given state.

        Args:
            new_state_class: The class of the state we should switch to.
        """
        logging.debug("Changing to state " + new_state_class.__name__)
        new_state_instance = new_state_class(self)
        self._active_state = new_state_instance
        if self._silence_notify_job:
            self._silence_notify_job.update_state(new_state_instance)

    def handle_sigterm(self):
        """Do whatever must be done when the program is asked to shut down."""
        logging.debug("Reacting to SIGTERM")
        self._active_state.handle_silence_stop()

    def process_message(self, data):
        """Method run by RtmBot to process messages received.

        Check if the message pertains to us, and let the currently active state
        handle it.

        Args:
            data: The received data from Slack.
        """
        if self.relevant_message(data):
            logging.debug("Relevant message: " + data['text'])
            self._active_state.handle_message(data)

    def relevant_message(self, data):
        """Check whether the message is relevant to us.

        Relevant here means that our bot is mentioned.
        """
        mentions_us = 'text' in data and self.userid in data['text']
        return mentions_us
