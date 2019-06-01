import sys
import json
import argparse
import http.client
import urllib.parse


class BotClient:
    def __init__(self, user_name: str, hostname: str, port: int):
        print("Launching client")
        print(f"Logging in as {user_name}")
        self._user_name = user_name
        self._conn = http.client.HTTPConnection(hostname + ":" + str(port))
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
            json_str = response.read()
            messages_dict = json.loads(json_str)
            if 'messages' in messages_dict and 'last_seen' in messages_dict:
                for message in messages_dict['messages']:
                    print("Chat client:", message)
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
            data = response.read()
        except:
            print("Cannot connect 2")

    def __del__(self):
        self._conn.close()


def launch_client(args):

    bc = BotClient(args.user, args.hostname, args.port)

    if not args.no_debug_messages:
        bc.fetch_messages()
        bc.send_message("I'm very happy that my team won the world cup!")
        bc.fetch_messages()
        bc.send_message("I feel a bit sad today")
        bc.fetch_messages()

    try:
        while True:
            sys.stdout.write(">> ")
            sys.stdout.flush()
            line = sys.stdin.readline()
            stripped_line = line.rstrip()
            if stripped_line == "":
                continue
            bc.send_message(stripped_line)
            bc.fetch_messages()
    except KeyboardInterrupt:
        print("Bye!")

    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--hostname', type=str, default="localhost", help='Hostname')
    parser.add_argument('--port', type=int, default=8080, help='Port')
    parser.add_argument('--user', type=str, default="Dmitrii", help='User name')
    parser.add_argument('--no-debug-messages', action='store_true',
                        help='Send some test messages to the server')
    args = parser.parse_args()

    launch_client(args)


if __name__ == "__main__":
    main()
