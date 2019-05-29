import argparse
import http.client
import urllib.parse
from werkzeug.wrappers import Request, Response


SERVER_URL = "localhost"
CLIENT_URL = "localhost"
PORT = 8080


def check_python_org():
    conn = http.client.HTTPSConnection("www.python.org")
    conn.request("GET", "/")
    r1 = conn.getresponse()
    print(r1.status, r1.reason)
    data1 = r1.read()
    print(data1)
    pass


@Request.application
def application(request):
    print("Get request", request)
    if request.method == 'POST':
        # Check that this is "/send"
        for key, value in request.values.items():
            print(key, value)
        response_str = "Message received and being processed"
    else:
        response_str = "REST responses from the bot will be here"
    return Response(response_str)


def launch_server():
    print("Launching sever")
    from werkzeug.serving import run_simple
    run_simple(SERVER_URL, PORT, application)


def launch_client():
    print("Launching client")
    conn = http.client.HTTPConnection(CLIENT_URL + ":" + str(PORT))
    conn.request("GET", "/messages")
    r1 = conn.getresponse()
    print(r1.status, r1.reason)
    data1 = r1.read()
    print(data1)

    params = urllib.parse.urlencode({'@number': 12524, '@type': 'issue', '@action': 'show'})
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn.request("POST", "/send", params, headers)
    response = conn.getresponse()
    print(response.status, response.reason)
    data = response.read()
    print(data)
    conn.close()
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
