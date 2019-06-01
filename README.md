# Empathetic chat bot

## Overview

A chat bot that expresses happy or sad emotion for every user message.

## Algorithm

A pretrained emoji prediction neural network is used for inference. The net is trained on Twitter's dataset.

The following implementation is used.

https://github.com/huggingface/torchMoji

Original DeepMoji paper:

"Using millions of emoji occurrences to learn any-domain representations for detecting sentiment, emotion and sarcasm"

https://arxiv.org/pdf/1708.00524.pdf

The mapping of 64 emojis to their "happiness" boolean flag is given by sentiment.json.

## How to install and launch

Clone this repo:

`git clone --recursive git://github.com/Obs01ete/chatbot`

Create conda (or any other) environment:

`conda create -n chatbot_env python=3.6`

`source activate chatbot_env`

Install requirements. An old PyTorch version 0.3.1 is used.

`pip install -r requirements.txt`

In one terminal, launch server:

`python chatbot_server.py`

In another terminal, launch a console client:

`python chatbot_client.py`

This is the expected output of the client
```
Launching client
Logging in as Dmitrii
Chat client: I'm very happy that my team won the world cup!
Chat client: [BOT] 😃 (:smiley:)
Chat client: I feel a bit sad today
Chat client: [BOT] 😟 (:worried:)
>>
```

Type your message followed by newline to see bot's response.

## HTTP API

To query messages via REST call:

`GET localhost:8080/messages?user=Dmitrii&last_seen=-1`

It returns a JSON with user's and bot's messages.

To post a message:

`POST localhost:8080/send {"user":"Dmitrii","message":"Good job!"}`

The message will be processed by the bot and a response can be acquired via REST.

## How to run tests

To test torchMoji wrapper:

`python sentiment_test.py`

To test web server:

`python chatbot_server_test.py`

