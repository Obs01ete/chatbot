import json
import emoji
import argparse
import http.client
import urllib.parse
from typing import Tuple, List
from werkzeug.wrappers import Request, Response

from sentiment import Sentiment


SERVER_URL = "localhost"
CLIENT_URL = "localhost"
PORT = 8080


class MessageHistory:
    def __init__(self):
        self._history = {}

    def append_message(self, user, message):
        if user in self._history:
            self._history[user].append(message)
        else:
            self._history[user] = [message]

    def get_messages_rest(self, user, last_seen) -> Tuple[List[str], int]:
        if user in self._history:
            user_messages = self._history[user]
            messages = user_messages[last_seen+1:]
            return messages, len(user_messages)-1
        else:
            return [], -1


g_message_history = MessageHistory()
g_sentiment = Sentiment()


@Request.application
def application(request):
    global g_message_history

    print("Got request", request)
    if request.method == 'POST':
        if request.path == "/send" and request.content_type == "application/json":
            response_str = "Message received and being processed"
            message_dict = json.loads(request.data)
            print(message_dict)

            user = message_dict['user']
            message = message_dict['message']

            g_message_history.append_message(message_dict['user'], message)

            bot_reply = g_sentiment(message)
            emoji_str = ":happy:" if bot_reply else ":sad:"
            bot_emoji = emoji.emojize(emoji_str)
            bot_reply_full = f"[BOT] {bot_emoji}"
            g_message_history.append_message(user, bot_reply_full)
        else:
            response_str = "Unknown POST format"
    elif request.method == 'GET':
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

    print(response_str)
    return Response(response_str)


def launch_server():
    print("Launching sever")
    from werkzeug.serving import run_simple
    run_simple(SERVER_URL, PORT, application)


class BotClient:
    def __init__(self, user_name):
        print("Launching client")
        self._user_name = user_name
        self._conn = http.client.HTTPConnection(CLIENT_URL + ":" + str(PORT))
        self._last_seen = None

    def fetch_messages(self):
        last_seen = self._last_seen if self._last_seen is not None else -1
        try:
            params = urllib.parse.urlencode({
                'user': self._user_name,
                'last_seen': last_seen
            })
            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain"
            }
            self._conn.request("GET", "/messages", params, headers)
            response = self._conn.getresponse()
            #print(response.status, response.reason)
            json_str = response.read()
            messages_dict = json.loads(json_str)
            print(messages_dict)
            if 'messages' in messages_dict and 'last_seen' in messages_dict:
                for message in messages_dict['messages']:
                    print("Bot:", message)
                self._last_seen = messages_dict['last_seen']
            else:
                pass

        except:
            print("Cannot connect")

    def send_message(self, message: str):
        content_obj = {'user': self._user_name, 'message': message}
        content = json.dumps(content_obj)
        headers = {"Content-type": "application/json",
                   "Accept": "text/plain"}

        try:
            self._conn.request("POST", "/send", content, headers)
            response = self._conn.getresponse()
            #print(response.status, response.reason)
            data = response.read()
            print(data)
        except:
            print("Cannot connect 2")

    def __del__(self):
        self._conn.close()


def launch_client():
    import time
    time.sleep(0.5)
    bc = BotClient("Dmitrii")
    bc.fetch_messages()
    bc.send_message("I am so happy!")
    bc.fetch_messages()
    bc.send_message("I am sad")
    bc.fetch_messages()
    bc.send_message("And again happy!")
    bc.fetch_messages()
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', action='store_true', help='Launch as a server')
    args = parser.parse_args()

    if args.server:
        launch_server()
    else:
        launch_client()


if __name__ == "__main__":
    main()
