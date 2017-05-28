import logging
import random

import requests
from slackclient import SlackClient


class Communicator:
    channel_mention = "<!channel>"
    current_shows_uri = "/v2/sendinger/currentshows"

    def __init__(self, slack_client: SlackClient, settings):
        self.slack_client = slack_client
        self.settings = settings
        self.first_message_ts = None
        self.username = None
        self.userid = None

    def send(self, message_type, num_warnings=None, **kwargs):
        possible_unformatted_message = self.settings.messages[message_type]

        if num_warnings is not None:
            try:
                possible_unformatted_message = \
                    possible_unformatted_message[num_warnings]
            except KeyError:
                possible_unformatted_message = \
                    possible_unformatted_message['n']

        unformatted_message = random.choice(possible_unformatted_message)

        formatted_message = unformatted_message.format(
            channel=self.channel_mention,
            **kwargs
        )
        self.send_custom(formatted_message)

    def send_custom(self, message):
        data = self.slack_client.api_call(
            "chat.postMessage",
            channel=self.settings.channel,
            text=message,
            as_user=True
        )
        assert data['ok'], data
        if not self.first_message_ts:
            self.first_message_ts = data['ts']

    def thumb_up_msg(self, received_message):
        data = self.slack_client.api_call(
            "reactions.add",
            name="+1",
            timestamp=received_message["ts"],
            channel=received_message["channel"]
        )
        assert data['ok'], data

    def get_userid(self):
        if not self.userid:
            self.populate_identity()
        return self.userid

    def get_username(self):
        if not self.username:
            self.populate_identity()
        return self.username

    def populate_identity(self):
        data = self.slack_client.api_call(
            "auth.test"
        )
        assert data['ok'], data
        self.userid = data['user_id']
        self.username = data['user']

    def get_first_message_ts(self):
        return self.first_message_ts

    def get_current_show(self):
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

