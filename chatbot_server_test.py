"""
Werkzeug server testing concept taken here:
https://www.programcreek.com/python/example/58710/werkzeug.test.Client
"""

import json
import unittest
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from chatbot_server import application


class ChatbotServerTest(unittest.TestCase):

    def test_wrong_messages(self):
        c = Client(application, BaseResponse)
        resp = c.get("/messages")
        payload = resp.data.splitlines()[0]
        self.assertEqual(payload, b'Wrong format of urlencoded')

    def test_messages(self):
        c = Client(application, BaseResponse)
        resp = c.get("/messages?user=Dmitrii&last_seen=-1")
        payload = resp.data.splitlines()[0]
        payload_dict = json.loads(payload)
        self.assertTrue('messages' in payload_dict)
        self.assertTrue('last_seen' in payload_dict)
        self.assertTrue(isinstance(payload_dict['messages'], list))
        self.assertTrue(isinstance(payload_dict['last_seen'], int))

    def test_send(self):
        c = Client(application, BaseResponse)
        resp = c.post("/send", data=b'{"user":"Dmitrii","message":"Hello, world!"}',
                      content_type='application/json')
        payload = resp.data.splitlines()[0]
        self.assertEqual(payload, b'Message received and being processed')

        resp = c.get("/messages?user=Dmitrii&last_seen=-1")
        payload = resp.data.splitlines()[0]
        payload_dict = json.loads(payload)
        self.assertTrue('messages' in payload_dict)
        self.assertTrue('last_seen' in payload_dict)
        messages = payload_dict['messages']
        last_seen = payload_dict['last_seen']
        self.assertTrue(isinstance(messages, list))
        self.assertTrue(isinstance(last_seen, int))
        self.assertEqual(len(messages), 2)
        self.assertEqual(last_seen, 1)
        self.assertEqual(messages[0], "Hello, world!")
        self.assertTrue("[BOT]" in messages[1])


if __name__ == "__main__":
    unittest.main()
