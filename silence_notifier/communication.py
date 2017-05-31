import logging
import random

import requests
from slackclient import SlackClient


class Communicator:
    """Class handling communication to Slack, and with Radio REST API."""
    channel_mention = "<!channel>"
    current_shows_uri = "/v2/sendinger/currentshows"

    def __init__(self, slack_client: SlackClient, settings):
        self.slack_client = slack_client
        self.settings = settings
        self.first_message_ts = None
        self.username = None
        self.userid = None

    def send(self, message_type, num_minutes=None, reply_to=None, **kwargs):
        """Send the given message type to Slack.

        Args:
            message_type: The key of self.settings.messages to use to look up
                message texts, from which one is picked at random.
            num_minutes: If provided, the value of
                self.settings.messages[message_type] is assumed to be a dict.
                All items in that dict which have a key less than or equal to
                num_minutes are chosen, or all messages from the highest key
                which matches that criteria if
                settings.messages['warnings_cumulative'] is False.
            reply_to: If provided, the message sent will be a reply to the
                given message. This should be the dictionary received from the
                Slack message event.
            kwargs: The text string will have {key} replaced with value for
                each key=value given to this method.
        """
        possible_unformatted_message = self.settings.messages[message_type]

        if num_minutes is not None:
            matching_messages = []
            max_from_minute = 0
            for from_minute, messages in possible_unformatted_message.items():
                if from_minute <= num_minutes:
                    if self.settings.messages['warnings_cumulative']:
                        matching_messages.extend(messages)
                    elif from_minute >= max_from_minute:
                        matching_messages = messages
                        max_from_minute = from_minute

            possible_unformatted_message = matching_messages

        unformatted_message = random.choice(possible_unformatted_message)

        formatted_message = unformatted_message.format(
            channel=self.channel_mention,
            **kwargs
        )
        self.send_custom(formatted_message, reply_to)

    def send_custom(self, message, reply_to=None):
        """Send the given message to Slack.

        Args:
            message: The text to post on Slack.
            reply_to: If provided, the message will be sent as a reply to the
                message whose information is provided in this argument. Its
                format is equal to the dictionary received in message events
                from Slack.
        """
        other_message_args = {
            'channel': self.settings.channel,
        }

        if reply_to:
            if 'thread_ts' in reply_to:
                thread_ts = reply_to['thread_ts']
            else:
                thread_ts = reply_to['ts']
            other_message_args['thread_ts'] = thread_ts
            other_message_args['channel'] = reply_to['channel']

        data = self.slack_client.api_call(
            "chat.postMessage",
            text=message,
            as_user=True,
            **other_message_args
        )
        assert data['ok'], data
        if not self.first_message_ts:
            self.first_message_ts = data['ts']

    def thumb_up_msg(self, received_message):
        """React with :+1: to the given message.

        Args:
            received_message: The dictionary received from a Slack message event
        """
        data = self.slack_client.api_call(
            "reactions.add",
            name="+1",
            timestamp=received_message["ts"],
            channel=received_message["channel"]
        )
        assert data['ok'], data

    def get_userid(self):
        """Get the userid of the logged in bot."""
        if not self.userid:
            self.populate_identity()
        return self.userid

    def get_username(self):
        """Get the username of the logged in bot."""
        if not self.username:
            self.populate_identity()
        return self.username

    def populate_identity(self):
        """Populate username and userid of the logged in bot."""
        data = self.slack_client.api_call(
            "auth.test"
        )
        assert data['ok'], data
        self.userid = data['user_id']
        self.username = data['user']

    def get_first_message_ts(self):
        """Get the ts of the first message sent by us in this session."""
        return self.first_message_ts

    def get_current_show(self):
        """Get the name of the show currently active on radio."""
        r = requests.get(self.settings.rr_api + self.current_shows_uri)
        try:
            r.raise_for_status()
        except Exception as e:
            logging.exception("Error occurred while retrieving current show")
            return "Ukjent (ikke kontakt med pappagorg, eller APIet er nede)"
        data = r.json()
        try:
            return data["current"]["title"]
        except KeyError:
            logging.error("No show found when trying to obtain current show")
            return "Ukjent (ingen sending i autoavvikler)"

