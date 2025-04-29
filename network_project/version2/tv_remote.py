import websocket
import json
import time
import keyboard
import os


TV_IP = 'REPLACE WITH IP'
PORT = 8002
app_name = "Python_socket"


if (os.path.exists("my_token.txt")):  #to prevent constant authorization
    f = open("my_token.txt")
    TOKEN = f.read()


youtube_grid = { #to simulate keyboard on TV
    "a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6,
    "h": 7, "i": 8, "j": 9, "k": 10, "l": 11, "m": 12, "n":13,
    "o":14, "p":15, "q":16, "r":17, "s":18, "t":19, "u":20,
    "v":21, "w":22, "x":23, "y":24, "z":25, "-": 26, "'":27,
    " ": 28
}

youtube_number_grid = {
    "1": 0, "2": 1, "3": 2,
    "3": 7, "4": 8, "5": 9,
    "7": 14, "8":15, "9": 16,
    "0": 21
}


def send_command(key):
    payload = json.dumps({
    'method': 'ms.remote.control',
    'params': {
        'Cmd': 'Click',
        'DataOfCmd': char_to_key[key],
        'Option': 'false',
        'TypeOfRemote': 'SendRemoteKey'
    }
    })
    connection.send(payload)


char_to_key = {  #maps laptop keyboard to TV keys
    "left": "KEY_LEFT", "right": "KEY_RIGHT", "up": "KEY_UP", "down": "KEY_DOWN",
    "+": "KEY_VOLUP", "-": "KEY_VOLDOWN", "*": "KEY_MUTE",
    "enter": "KEY_ENTER", "backspace": "KEY_RETURN",
    "h": "KEY_HOME", "s": "KEY_SOURCE", "i": "KEY_INFO", "t": "KEY_TOOLS", "g": "KEY_GUIDE", "m": "KEY_MENU"
}

start = 0 #used for keyboard simulation logic
    

# --- Connect to the TV ---
ws_url = f"wss://{TV_IP}:{PORT}/api/v2/channels/samsung.remote.control?app={app_name}&token={TOKEN}"

connection = websocket.create_connection(ws_url, sslopt={"cert_reqs": 0})


if (not os.path.exists("my_token.txt")): #this is for first authorization check
    response = connection.recv()

    info = json.loads(response)
    token = info["data"]["token"]
    with open("my_token.txt", "w") as token_file:
        token_file.write(token)

print("Connected to Samsung TV")
print('''
    Commands List:
    Ctrl: Stop Program
    Arrows Keys, Enter: Arrows and Enter for TV
    Backspace: TV's Back 
    M: Menu
    I: Info
    H: Home
    S: Source
    T: Tools
    +, -, *: Volume Up, Volume Down, Mute
    F: Searches for app to run based on input
    K: Mimics Keyboard based on input
    J: Sends input to applicable apps
    ''')

while True:
    ev = keyboard.read_event(suppress=True)
    
    if (ev.event_type == keyboard.KEY_DOWN and ev.name == "ctrl"):
        connection.close()
        break
    elif (ev.event_type == keyboard.KEY_UP):
        print(ev.name)
        if ev.name == "j": #direct input to TV
            text = input("Enter word to search: ")
            time.sleep(.5)
            payload = json.dumps({
                "method": "ms.remote.control",
                "params": {
                    "Cmd": text,
                    "TypeOfRemote": "SendInputString",
                    "DataOfCmd": "text",
                }

            })
            connection.send(payload)
        elif ev.name == "k":
            start = 0
            word = input("Enter word(s) to search. Press enter when finished: ") #This does the keyboard simulation
            switch = False
            for char in word:
                    if (char == " "):
                        value = youtube_grid[char]
                        for i in range((value//7) - (start//7)): #checks to see how far down needs to go
                            send_command("down")
                            time.sleep(.2)
                        send_command("enter") #youtube automatically goes to space regardless of row position
                        time.sleep(.2)
                        send_command("up") #goes to previous row position
                        time.sleep(.2)
                        start = value - (7 - (start % 7)) #change it to this row position
                    else:
                        #this means we either encountered a number after letters or a letters after numbers
                        if ((switch != True and char.isdigit()) or (switch == True and char.isdigit() == False)): 
                            switch = not switch #switches keyboard
                            value = youtube_grid["n"] #set the endpoint to be at 13 becuase the key next to it changes to number or letter keyboard

                            while((start % 7) < (value % 7)): #same logic as below
                                send_command("right")
                                start += 1
                                time.sleep(.2)
                            while ((start % 7) > (value % 7)):
                                send_command("left")
                                start -= 1
                                time.sleep(.2)
                            while(start + 7 <= value):
                                    start += 7
                                    send_command("down")
                                    time.sleep(.2)
                            while (start - 7 >= value):
                                    start -= 7
                                    send_command("up")
                                    time.sleep(.2)

                            send_command("right")
                            time.sleep(.2)
                            send_command("enter") #this changes to number or letter keyboard
                            time.sleep(.2)
                            send_command("left") #goes to position 13 at the keyboard
                            time.sleep(.2)
                            start = 13

                        if (switch == False):    
                            value = youtube_grid[char]
                        else:
                            value = youtube_number_grid[char]

                        while((start % 7) < (value % 7)): #this means that our endpoint is to the right of us
                            send_command("right")
                            start += 1
                            time.sleep(.2)
                        while ((start % 7) > (value % 7)): #this means it is to the left       
                            send_command("left")
                            start -= 1
                            time.sleep(.2)
                        while(start + 7 <= value): #this means we are on the same column but is below us
                            start += 7
                            send_command("down")
                            time.sleep(.2)
                        while (start - 7 >= value): #same as above, but now it is on top of us
                            start -= 7
                            send_command("up")
                            time.sleep(.2)
                        
                        send_command("enter")
                        time.sleep(.2)

        elif (ev.name in char_to_key): #only accepts the key listed on command list above
            send_command(ev.name)

