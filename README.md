# servbot-tronbonne
Servbot-Tronbonne. Simple WebSocket solution for sharing a controller(emulated keyboard) over Internet.
Author: Johan Strandman

Servbot:
The Websocket server that Tronbonne-clients connect to. Includes a virtual keyboard mechanism to output given commands to game or whatnot.
Note that using the virtual keyboard basically exposes it to the wonders of Internet and security is basically non-existent in this simple version. Take necessary precautions.
Currently access to server is verified by simple login token. If you plan to use this in something more permanent, improve upon this (for instance, by passing the token with every keypress event, not just on login.) 

Tronbonne:
Simple website that contains necessary code to access the servbot and execute keypresses. Just like it's namesake, all Tronbonne clients have their strong opinions on what commands should be executed by the connected servbot. Thus every client can press any assigned button on the 'controller'. End result should resemble multiplayer gaming....or chaos.
