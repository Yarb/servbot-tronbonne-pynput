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

# Simple random token generator
def random_token():
    a = ""
    for i in range(4):
        a += str(random.randint(0,9))
    return a

USERS1 = set()
USERS2 = set()

# generate two tokens
TOKEN1 = random_token()
TOKEN2 = random_token()

# Button list. TODO: Make this easier to modify
KEYLIST_PLAYER1 = ['w','s','a','d','r','t','y','u','i','o']
KEYLIST_PLAYER2 = ['p','l','ö','ä','h','j','k','n','m',',']

BUTTONSTATE1 = {"up": 0,
               "down": 0,
               "left": 0,
               "right": 0,
               "A": 0,
               "B": 0,
               "C": 0,
               "X": 0,
               "Y": 0,
               "Z": 0
               }

BUTTONSTATE2 = {"up": 0,
               "down": 0,
               "left": 0,
               "right": 0,
               "A": 0,
               "B": 0,
               "C": 0,
               "X": 0,
               "Y": 0,
               "Z": 0
               }





def keypresser(keys, player):
  if player == 1:
    keylist == KEYLIST_PLAYER1
  elif player == 2:
    keylist == KEYLIST_PLAYER2
  else:
    return

  for i in range(len(keylist)):
    output_keyboard.release(keylist[i])
    if keys[i] == 1:
      print(keylist[i])
      output_keyboard.press(keylist[i])


def state_event(statelist, player):
    if (KEY_OUTPUT):
        keypresser(list(statelist.values()), player)
    return json.dumps({"type": "state", "value": list(statelist.values())})


# Generate JSON of all users in given list
def users_event(userlist):
    return json.dumps({"type": "users", "value": [i for h,i in userlist]})

# Send notification to given userlist
async def notify_users(userlist):
    if userlist:  # asyncio.wait doesn't accept an empty list
        message = users_event(userlist)
        await asyncio.wait([user.send(message) for user, username in userlist])

# Notify given userlist of events
async def notify_state(player):
    if player == 1:
        if USERS1:  # asyncio.wait doesn't accept an empty list
            message = state_event(BUTTONSTATE1, 1)
            await asyncio.wait([user.send(message) for user, username in USERS1])
    elif player == 2:
        if USERS2:  # asyncio.wait doesn't accept an empty list
            message = state_event(BUTTONSTATE2, 2)
            await asyncio.wait([user.send(message) for user, username in USERS2])




async def register(websocket, user, userlist):
    userlist.add((websocket, user))
    await notify_users(userlist)

async def unregister(websocket, userlist):
    for client in userlist:
        if client[0] == websocket:
            userlist.remove(client)
            await notify_users(userlist)
            return True
    return False

def check_client(websocket, userlist):
    for client in userlist:
        if client[0] == websocket:
            return True
    return False


async def server(websocket, path):
    # register(websocket) sends user_event() to websocket
    try:
        #await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)

            # If websocket registered - check commands
            if check_client(websocket, USERS1):
                # check token
                if data["token"] == TOKEN1:
                    # check command
                    if data["action"] in BUTTONSTATE1:
                        BUTTONSTATE1[data["action"]] = data["value"]
                        await notify_state(1)
            elif check_client(websocket, USERS2):
                # check token
                if data["token"] == TOKEN2:
                    # check command
                    if data["action"] in BUTTONSTATE2:
                        BUTTONSTATE2[data["action"]] = data["value"]
                        await notify_state(2)
            # else check login 
            else:
                if data["action"] == "login":
                    if data["token"] == TOKEN1 and data["user"]:
                        await register(websocket, data["user"], USERS1)
                    elif data["token"] == TOKEN2 and data["user"]:
                        await register(websocket, data["user"], USERS2)
                else:
                    logging.error("unsupported event: {}", data)

    finally:
        if not await unregister(websocket, USERS1):
            await unregister(websocket, USERS2)


start_server = websockets.serve(server, IP, PORT)
print("\n---\n")

if (KEY_OUTPUT):
    print("Virtual keyboard is ACTIVE.")
else:
    print("Connection testing mode. Virtual keyboard is DISABLED.")

print("\nServbot running at: \n" + IP + ":" + str(PORT))
print("Player 1 session token is: " + TOKEN1)
print("Player 2 session token is: " + TOKEN2)
print("\n---\n")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
