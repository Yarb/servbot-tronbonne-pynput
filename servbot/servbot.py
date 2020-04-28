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

import ssl
import pathlib




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
parser.add_argument('-S', dest='base_filename',
                    help='Use SSL. Provide filename for .key and .crt files. Eg. "file" -> "file.crt" and "file.key".')

args = parser.parse_args()
IP = args.ip
PORT = args.port
KEY_OUTPUT = args.output
ssl_state = False

# SSL cert and key checking and loading
if args.base_filename:
    fn = args.base_filename
    try:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        cert_pem = pathlib.Path(__file__).with_name(fn + ".crt")
        key = pathlib.Path(__file__).with_name(fn + ".key")
        ssl_context.load_cert_chain(cert_pem, keyfile=key)
        ssl_state = True
    except FileNotFoundError:
        print("SSL init error:")
        print(fn + ".key and/or " + fn + ".crt not found in the same directory")
        exit(-1)
    except ssl.SSLError:
        print("SSL init error: Bad .key or .crt?")
        exit(-1)
        
        
ADMIN_ENABLE = {"value": False}

USERS1 = set()
USERS2 = set()
ADMIN = set()

# Simple random token generator
def random_token(value):
    a = ""
    for i in range(value):
        a += str(random.randint(0,9))
    return a

def generate_tokens():
    global token1, token2
    token1 = random_token(4)
    token2 = random_token(4)
    

# Tokens
token1 = ""
token2 = ""
ADMIN_TOKEN = random_token(5)
# Generate user tokens
generate_tokens()


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
    keylist = KEYLIST_PLAYER1
  elif player == 2:
    keylist = KEYLIST_PLAYER2
  else:
    return

  for i in range(len(keylist)):
    output_keyboard.release(keylist[i])
    if keys[i] == 1:
      print(keylist[i])
      output_keyboard.press(keylist[i])


def state_event(statelist, player):
    if (KEY_OUTPUT and ADMIN_ENABLE["value"]):
        keypresser(list(statelist.values()), player)
    return json.dumps({"type": "state", "value": list(statelist.values()), "id": player - 1})



# Generate JSON of all users in given list
def users_event(userlist):
    if userlist is USERS1:
        id = 1
    elif userlist is USERS2:
        id = 2
    else: 
        id = 0
    users = [" "]
    if userlist:
        users = [i for h,i in userlist]
    return json.dumps({"type": "users", "value": users, "id":id})
        
# Send notification to given userlist and to admins
async def notify_users(userlist):
    message = users_event(userlist)
    if userlist:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([user.send(message) for user, username in userlist])
    if ADMIN:
        await asyncio.wait([user.send(message) for user, username in ADMIN])

# Notify given userlist of events, send monitoring data to admins
async def notify_state(player):
    if player == 1:
        if USERS1:  # asyncio.wait doesn't accept an empty list
            message = state_event(BUTTONSTATE1, 1)
            await asyncio.wait([user.send(message) for user, username in USERS1])
    elif player == 2:
        if USERS2:  # asyncio.wait doesn't accept an empty list
            message = state_event(BUTTONSTATE2, 2)
            await asyncio.wait([user.send(message) for user, username in USERS2])
    if ADMIN and message:
        await asyncio.wait([user.send(message) for user, username in ADMIN])

# Send the virtual keyboard state to admins
async def notify_admin():
    if ADMIN:
        message = json.dumps({"type": "keystate", **ADMIN_ENABLE})
        await asyncio.wait([user.send(message) for user, username in ADMIN])

# Send the session tokens to admins        
async def send_admin_tokens():
    if ADMIN:
        message = json.dumps({"type": "tokens", "value": [token1, token2, ADMIN_TOKEN]})
        await asyncio.wait([user.send(message) for user, username in ADMIN])

# Register websocket
async def register(websocket, user, userlist):
    userlist.add((websocket, user))
    await notify_users(userlist)

# Remove registered websocket
async def unregister(websocket, userlist):
    for client in userlist:
        if client[0] == websocket:
            userlist.remove(client)
            await notify_users(userlist)
            return True
    return False
            
# Check if websocket exists in given userlist
def check_client(websocket, userlist):
    for client in userlist:
        if client[0] == websocket:
            return True
    return False

# Restart the session. This removes all the users except for admins
# and generates new set of session tokens
async def restart_session():
    while USERS1:
        client = USERS1.pop()
        await client[0].close()
    while USERS2:
        client = USERS2.pop()
        await client[0].close()
    await notify_users(USERS1)
    await notify_users(USERS2)
    generate_tokens()


# Main server loop
async def server(websocket, path):
    # register(websocket) sends user_event() to websocket
    try:
        #await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)

            # If websocket registered - check commands
            if check_client(websocket, USERS1):
                # check token
                if data["token"] == token1:
                    # check command
                    if data["action"] in BUTTONSTATE1:
                        BUTTONSTATE1[data["action"]] = data["value"]
                        await notify_state(1)
            elif check_client(websocket, USERS2):
                # check token
                if data["token"] == token2:
                    # check command
                    if data["action"] in BUTTONSTATE2:
                        BUTTONSTATE2[data["action"]] = data["value"]
                        await notify_state(2)
            elif check_client(websocket, ADMIN):
                if data["token"] == ADMIN_TOKEN:
                    # check command
                    if data["action"] == "Enable":
                        ADMIN_ENABLE["value"] = True
                        await notify_admin()
                        
                    elif data["action"] == "Disable":
                        ADMIN_ENABLE["value"] = False
                        await notify_admin()
                        
                    elif data["action"] == "KILL clients":
                        print("Servbot, restarting session:")
                        await restart_session()
                        await notify_admin()
                        await send_admin_tokens()
                        print_settings()
            # else check login 
            else:
                # New websocket login
                if data["action"] == "login":
                    if data["token"] == token1 and data["user"]:
                        await register(websocket, data["user"], USERS1)
                    elif data["token"] == token2 and data["user"]:
                        await register(websocket, data["user"], USERS2)

                # New admin login
                elif data["action"] == "ADMIN" and data["token"] == ADMIN_TOKEN:
                    await register(websocket, data["user"], ADMIN)
                    await notify_admin()
                    await send_admin_tokens()
                    await notify_users(USERS1)
                    await notify_users(USERS2)
                    
                # Something else, report.
                else:
                    logging.error("Token error or bad message", data)

    finally:
            # Go throught the lists one y one and try to unregister the websocket
            # This needs to be done in order, which is why it is done this way.
            if not await unregister(websocket, USERS1):
                if not await unregister(websocket, USERS2):
                    await unregister(websocket, ADMIN)


def print_settings():
    print("\n---\n")

    if (KEY_OUTPUT):
        print("Virtual keyboard is ACTIVE.")
    else:
        print("Connection testing mode. Virtual keyboard is DISABLED.")

    print("\nServbot running at: " )
    if ssl_state:
        print("wss://" + IP + ":" + str(PORT))
    else:
        print("ws://" + IP + ":" + str(PORT))
    print("---")
    print("ADMIN token is: " + ADMIN_TOKEN)
    print("\n")
    print("Player 1 session token is: " + token1)
    print("Player 2 session token is: " + token2)
    print("\n---\n")

if ssl_state:
    start_server = websockets.serve(server, IP, PORT, ssl=ssl_context)
else:
    start_server = websockets.serve(server, IP, PORT)



print_settings()

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


