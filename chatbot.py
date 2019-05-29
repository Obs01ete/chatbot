import json
import argparse
import http.client
import urllib.parse
from typing import Tuple, List

from werkzeug.wrappers import Request, Response


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


@Request.application
def application(request):
    global g_message_history

    print("Get request", request)
    if request.method == 'POST':
        if request.path == "/send" and request.content_type == "application/json":
            response_str = "Message received and being processed"
            message_dict = json.loads(request.data)
            print(message_dict)
            g_message_history.append_message(message_dict['user'], message_dict['message'])
        else:
            response_str = "Unknown POST format"
    elif request.method == 'GET':
        if request.path == "/messages":
            messages, last_seen = g_message_history.get_messages_rest("Dmitrii", -1)
            messages_dict = {'messages': messages, 'last_seen': last_seen}
            messages_json = json.dumps(messages_dict)
            response_str = messages_json
        else:
            response_str = "REST responses from the bot will be here"
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
    def __init__(self):
        print("Launching client")
        self._conn = http.client.HTTPConnection(CLIENT_URL + ":" + str(PORT))

    def fetch_messages(self):
        try:
            self._conn.request("GET", "/messages")
            r1 = self._conn.getresponse()
            print(r1.status, r1.reason)
            data1 = r1.read()
            print(data1)
        except:
            print("Cannot connect")

    def send_message_example(self, message):
        params = urllib.parse.urlencode({'@number': 12524, '@type': 'issue', '@action': 'show'})
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        self._conn.request("POST", "/send", params, headers)
        response = self._conn.getresponse()
        print(response.status, response.reason)
        data = response.read()
        print(data)

    def send_message(self, user: str, message: str):
        content_obj = {'user': user, 'message': message}
        content = json.dumps(content_obj)
        headers = {"Content-type": "application/json",
                   "Accept": "text/plain"}

        try:
            self._conn.request("POST", "/send", content, headers)
            response = self._conn.getresponse()
            print(response.status, response.reason)
            data = response.read()
            print(data)
        except:
            print("Cannot connect 2")

    def __del__(self):
        self._conn.close()


def launch_client():
    bc = BotClient()
    bc.fetch_messages()
    bc.send_message("Dmitrii", "I am so happy!")
    bc.fetch_messages()
    bc.send_message("Dmitrii", "And again happy!")
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
