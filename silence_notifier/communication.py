from slackclient import SlackClient


class Communicator:
    def __init__(self, slack_client: SlackClient, settings):
        self.slack_client = slack_client
        self.settings = settings

    def send(self, message):
        self.slack_client.api_call(
            "chat.postMessage",
            channel=self.settings.channel,
            text=message
        )

    def thumb_up_msg(self, received_message):
        self.slack_client.api_call(
            "reactions.add",
            name="+1",
            timestamp=received_message["ts"],
            channel=received_message["channel"]
        )
