import json
import emoji
import argparse
from typing import Tuple, List
from werkzeug.wrappers import Request, Response

from sentiment import Sentiment


class MessageHistory:
    """
    Class-emulation of a database that stores message history.
    """

    def __init__(self):
        self._history = {}

    def append_message(self, user: str, message: str) -> None:
        """
        Append a message from a user or a bot to user's history.
        :param user: user name
        :param message: message to add
        """
        if user in self._history:
            self._history[user].append(message)
        else:
            self._history[user] = [message]

    def get_messages_rest(self, user, last_seen) -> Tuple[List[str], int]:
        """
        Acquire all messages after last_seen
        :param user: user name
        :param last_seen: last seen index of a message
        :return: list of messaged and the latest message index
        """
        if user in self._history:
            user_messages = self._history[user]
            messages = user_messages[last_seen+1:]
            return messages, len(user_messages)-1
        else:
            return [], -1


""" Singleton for in-RAM storage of all users' chat histories. """
g_message_history = MessageHistory()

""" Sentiment analysis neural network. """
g_sentiment = Sentiment()


@Request.application
def application(request):
    """
    Werkzeug application to process web requests.
    :param request: inbound HTTP request
    :return: Response object
    """

    global g_message_history

    print("Got request", request)
    if request.method == 'POST':
        """ This section parses a chat message sent by user. """

        if request.path == "/send" and request.content_type == "application/json":
            response_str = "Message received and being processed"
            message_dict = json.loads(request.data)
            print("Message from client:", message_dict)

            user = message_dict['user']
            message = message_dict['message']

            # Original user message is added to message history
            g_message_history.append_message(message_dict['user'], message)

            # Neural network inference
            bot_reply = g_sentiment(message)
            # Transform bool happiness value into a Unicode smiley
            emoji_str = ":smiley:" if bot_reply else ":worried:"
            bot_emoji = emoji.emojize(emoji_str, use_aliases=True)
            # Messages by bot are marked with [BOT] prefix
            bot_reply_full = f"[BOT] {bot_emoji} ({emoji_str})"
            g_message_history.append_message(user, bot_reply_full)
        else:
            response_str = "Unknown POST format"

    elif request.method == 'GET':
        """ This section is a REST responder for quieries of chat history. """

        if request.path == "/messages":
            if 'user' in request.values and 'last_seen' in request.values:
                user = request.values['user']
                last_seen = int(request.values['last_seen'])
                messages, new_last_seen = g_message_history.get_messages_rest(user, last_seen)
                messages_dict = {'messages': messages, 'last_seen': new_last_seen}
                messages_json = json.dumps(messages_dict)
                response_str = messages_json
            else:
                response_str = "Wrong format of urlencoded"
        else:
            response_str = "404"
    else:
        response_str = ""
        print("Have no idea what to do with this request")

    print("Responding:", response_str)
    return Response(response_str)


def launch_server(args):
    """ Launches werkzeug server. """
    print("Launching sever")
    from werkzeug.serving import run_simple
    run_simple(args.hostname, args.port, application)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hostname', type=str, default="localhost", help='Hostname')
    parser.add_argument('--port', type=int, default=8080, help='Port')
    args = parser.parse_args()

    launch_server(args)


if __name__ == "__main__":
    main()
