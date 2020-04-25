#!/usr/bin/env python

# Servbot, a WS server that obeys every whim of Tron Bonne (AKA clients).
# In short, incoming button presses are sent to all clients and sent as
# keypresses to the system.
# NOTE! 
# This should be run in controlled environment as giving
# Internet access to limited virtual keyboard without decent security 
# is not the best idea in the long run. You have been warned. 

import asyncio
import json
import logging
import websockets
import random

import argparse

from pynput.keyboard import Controller

output_keyboard = Controller()

logging.basicConfig()

STATE = {"value": 0}
BUTTONSTATE = {"up": 0, 
               "down": 0,
               "left": 0,
               "right": 0,
               "hpunch": 0,
               "lpunch": 0,
               "hkick": 0,
               "lkick": 0
               }


USERS = set()

# Generate a random token for each session
def random_token():
    a = ""
    for i in range(4):
        a += str(random.randint(0,9))
    return a

TOKEN = random_token()

parser = argparse.ArgumentParser(description='Servbot. WS server for accepting button presses from browsers')
parser.add_argument('-a', dest='ip', required=True,
                    help='IP address of the server.')
parser.add_argument('-p', type=int, default=6789, dest='port',
                    help='Server port (default 6789).')
parser.add_argument('-k', action='store_const',const=1 , metavar='', dest='output',
                    help='Output keypresses.')

args = parser.parse_args()
IP = args.ip
PORT = args.port
KEY_OUTPUT = args.output

keylist = ['w','s','a','d','r','t','y','u']

def keypresser(keys):
  for i in range(len(keylist)):
    output_keyboard.release(keylist[i])
    if keys[i] == 1:
      print(keylist[i])
      output_keyboard.press(keylist[i])


def state_event():
    if (KEY_OUTPUT):
        keypresser(list(BUTTONSTATE.values()))
    return json.dumps({"type": "state", "value": list(BUTTONSTATE.values())})


def users_event():
    return json.dumps({"type": "users", "value": [i for h,i in USERS]})


async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user, username in USERS])


async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user, username in USERS])


async def register(websocket, user):
    USERS.add((websocket, user))
    await notify_users()

async def unregister(websocket):
    for client in USERS:
        if client[0] == websocket:
            USERS.remove(client)
            await notify_users()
            break


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            if data["action"] in BUTTONSTATE:
                BUTTONSTATE[data["action"]] = data["value"]
                await notify_state()
            elif data["action"] == "login":
                if data["token"] == TOKEN and data["user"]:
                    await register(websocket, data["user"])
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)


start_server = websockets.serve(counter, IP, PORT)
print("Server running at: " + IP + ":" + str(PORT))
print("Session password is: " + TOKEN)
if (KEY_OUTPUT):
    print("Virtual keyboard is ACTIVE.")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
