const ADDRESS = "ws://localhost:6789/";
var value = document.querySelector('.value'),
    users = document.querySelector('.users'),
    login = document.querySelector('.login'),
    error = document.querySelector('.error'),
    state = [0,0,0,0,0,0,0,0,0,0,0,0],
    token = "",
    
    
    buttons = ["up", "down", "left", "right", 
               "A","B","C","X","Y","Z"],
    button_img = ["up_","dw_","lf_","rt_","r_", "g_", "b_", "y_", "w_", "bl_"],
    keymap =     {87:0 ,83:1 ,65:2 ,68:3 ,74:4, 75:5, 76:6, 78:7, 77:8, 188:9};

window.websocket = new WebSocket(ADDRESS);

createWebsocket = function() {
    window.websocket = new WebSocket(ADDRESS);
}

keypress = function (event, value) {
    var x = event.which || event.keyCode;
    if (keymap[x] >= 0 && login.style.display == "none") {
        if (state[keymap[x]] != value) {
            sendButtonChange(keymap[x], value);
        }
    }
}


connect = function () {
    name = document.querySelector('#username').value;
    secret = document.querySelector('#Secret').value;
    console.log("Form returned:");
    console.log(name + ' ' + secret);
    token = secret;
    window.websocket.send(JSON.stringify({action: 'login', user: name, token: token}));
}

sendButtonChange = function(button, val) {
    if (login.style.display == "none") {
        if (state[button] !== val)
        window.websocket.send(JSON.stringify({action: buttons[button], value: val, token : token}));
        state[button] = val;
    }
}

for (let j = 0; j < buttons.length; j++) {
    
    document.querySelector("." + buttons[j]).ontouchstart = function (event) {
        sendButtonChange(j,1);
    }
    
    document.querySelector("." + buttons[j]).ontouchend = function (event) {
        sendButtonChange(j,0);
    }

    document.querySelector("." + buttons[j]).onmousedown = function (event) {
        sendButtonChange(j,1);
    }
    
    document.querySelector("." + buttons[j]).onmouseout = function (event) {
        sendButtonChange(j,0);
    }
    
    document.querySelector("." + buttons[j]).onmouseup = function (event) {
        sendButtonChange(j,0);
    }
}



window.websocket.onmessage = function (event) {
    data = JSON.parse(event.data);
    switch (data.type) {
        case 'state':
            console.log("Data : " + data.value)
            for (let i = 0; i < buttons.length; i++ ) {
                if (data.value[i]) {
                    document.querySelector('.' + buttons[i]).src="images/" + button_img[i] + "down.png";
                } else {
                    document.querySelector('.' + buttons[i]).src="images/" + button_img[i] + "up.png";
                }
            }
            break;
        case 'users':
            text = "";
            for (let i = 0; i < data.value.length; i++ ) {
                if (i == 0) {
                    text += data.value[i].toString();
                }else {
                    text += " , "  + data.value[i].toString();
                }
            }
            login.style.display = "none";
            lower.style.display = "none";
            upper.style.display = "flow-root";
            users.textContent = (text);
            break;
        default:
            console.error(
                "unsupported event", data);
    }
};

window.websocket.onclose = function (event) {
    console.log('Connection closed');
    login.style.display = "none";
    lower.style.display = "block";
    upper.style.display = "none";
    users.textContent = "Connection closed, another servbot gone...";
};
window.websocket.onerror = function(evt) {
    error.textContent = "Connection error, try refresh";
    login.style.display = "none";
    lower.style.display = "block";
    upper.style.display = "none";
    console.log(evt);
};