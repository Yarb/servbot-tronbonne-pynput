# servbot-tronbonne
Description: Simple WebSocket solution for sharing a controller(emulated keyboard) over Internet.


Servbot:
-
The Websocket server that Tronbonne-clients connect to. Includes a virtual keyboard mechanism to output given commands to game or whatnot.
Note that using the virtual keyboard basically exposes it to the wonders of Internet and security is basically non-existent in this simple version. Take necessary precautions.
Currently access to server is verified by simple login token. If you plan to use this in something more permanent, improve upon this (for instance, by passing the token with every keypress event, not just on login.) 

Tronbonne:
-
Simple website that contains necessary code to access the servbot and execute keypresses. Just like it's namesake, all Tronbonne clients have their strong opinions on what commands should be executed by the connected servbot. Thus every client can press any assigned button on the 'controller'. End result should resemble multiplayer gaming....or chaos.

Installation:
-
Requirements:
 * Python 3.6.1+
 * Python Websockets 8.1 (https://pypi.org/project/websockets/).
 * Pynput (https://pypi.org/project/pynput/).

Modify the Tronbonne scripts to contain correct address of the target Servbot and host the webpage. Note that as long as the client running the webpage has access to the Servbot address, everything should just work. This allows for flexibility in deployment.

Run the Servbot with:
`python3 servbot.py -a <ip-address>`

For additional commands, including enabling the virtual keyboard,  run:
`python3 servbot.py -h`


Have fun - Johan Strandman
