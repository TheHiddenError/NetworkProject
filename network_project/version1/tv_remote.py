import logging
import keyboard
import asyncio
from samsungtvws.async_remote import SamsungTVWSAsyncRemote
from samsungtvws.remote import SendRemoteKey, ChannelEmitCommand


# Increase debug level
logging.basicConfig(level=logging.INFO)

host = "ENTER YOUR IP"

port = 8002

youtube_grid = {
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

# disney_grid = {
#     "a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6,
#     "h": 7, "i": 8, "j": 9, "k": 10, "l": 11, "m": 12, "n":13,
#     "o":14, "p":15, "q":16, "r":17, "s":18, "t":19, "u":20,
#     "v":21, "w":22, "x":23, "y":24, "z":25,
#     "1":27, "2":28, "3":29, "4":30, "5":31, "6":32, "7":33,
#     "8":34, "9":35, "0":36
# }

# hulu_grid ={
#     "a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5,
#     "g": 6,"h": 7, "i": 8, "j": 9, "k": 10, "l": 11

# }



start = 0
    


async def main():
    tv = SamsungTVWSAsyncRemote(host=host, port=port, token_file="token_file", key_press_delay=0)
    await tv.start_listening()
    if (tv is not None):
        print("Connected to Samsung TV")
        print('''
            Commands List:
            Ctrl: Turn off TV and Stop Program
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
            ''')
    apps = await tv.app_list() #sometimes the TV causes an infinite loop with this command. 
    #apps = []
    await asyncio.sleep(1)
    while True:
        global start
        ev = keyboard.read_event(suppress=True)
        
        if (ev.event_type == keyboard.KEY_DOWN and ev.name == "ctrl"):
            await tv.send_command(SendRemoteKey.power())
            break
        elif (ev.event_type == keyboard.KEY_UP):
            print(ev.name)
            if ev.name == "right":
                await tv.send_command(SendRemoteKey.right())
            elif ev.name == "left":
                await tv.send_command(SendRemoteKey.left())
            elif ev.name == "up":
                await tv.send_command(SendRemoteKey.up())
            elif ev.name == "down":
                await tv.send_command(SendRemoteKey.down())
            elif ev.name == "+":
                await tv.send_command(SendRemoteKey.volume_up())
            elif ev.name == "-":
                await tv.send_command(SendRemoteKey.volume_down())
            elif ev.name == "enter":
                await tv.send_command(SendRemoteKey.enter())
            elif ev.name == "backspace":
                await tv.send_command(SendRemoteKey.back())
            elif ev.name == "i":
                await tv.send_command(SendRemoteKey.info())
            elif ev.name == "m":
                await tv.send_command(SendRemoteKey.menu())
            elif ev.name == "s":
                await tv.send_command(SendRemoteKey.source())
            elif ev.name == "t":
                await tv.send_command(SendRemoteKey.tools())
            elif ev.name == "*":
                await tv.send_command(SendRemoteKey.mute())
            elif ev.name == "f":
                search = input("Enter a app to load. Press enter when finished: ")
                for app in apps:
                    if (search == app["name"].lower()):
                        await tv.send_command(ChannelEmitCommand.launch_app(app["appId"]))
            elif ev.name == "h":
                await tv.send_command(SendRemoteKey.home())
            elif ev.name == "k":
                start = 0
                word = input("Enter word(s) to search. Press enter when finished: ")
                switch = False
                for char in word:
                        if (char == " "):
                            value = youtube_grid[char]
                            for i in range((value//7) - (start//7)):
                                await tv.send_command(SendRemoteKey.down())
                                await asyncio.sleep(.2)
                            await tv.send_command(SendRemoteKey.enter())
                            await asyncio.sleep(.2)
                            await tv.send_command(SendRemoteKey.up())
                            await asyncio.sleep(.2)
                            start = value - (7 - (start % 7))
                        else:
                            if ((switch != True and char.isdigit()) or (switch == True and char.isdigit() == False)):
                                switch = not switch
                                value = youtube_grid["n"]
                                while((start % 7) < (value % 7)):
                                    await tv.send_command(SendRemoteKey.right())
                                    start += 1
                                    await asyncio.sleep(.2)
                                while ((start % 7) > (value % 7)):
                                    await tv.send_command(SendRemoteKey.left())
                                    start -= 1
                                    await asyncio.sleep(.2)

                                while(start + 7 <= value):
                                        start += 7
                                        await tv.send_command(SendRemoteKey.down())
                                        await asyncio.sleep(.2)
                                while (start - 7 >= value):
                                        start -= 7
                                        await tv.send_command(SendRemoteKey.up())
                                        await asyncio.sleep(.2)
                                await tv.send_command(SendRemoteKey.right())
                                await asyncio.sleep(.2)
                                await tv.send_command(SendRemoteKey.enter())
                                await asyncio.sleep(.2)
                                await tv.send_command(SendRemoteKey.left())
                                await asyncio.sleep(.2)
                                start = 13

                            if (switch == False):    
                                value = youtube_grid[char]
                            else:
                                value = youtube_number_grid[char]

                            while((start % 7) < (value % 7)):
                                await tv.send_command(SendRemoteKey.right())
                                start += 1
                                await asyncio.sleep(.2)
                            while ((start % 7) > (value % 7)):             
                                await tv.send_command(SendRemoteKey.left())
                                start -= 1
                                await asyncio.sleep(.2)
                            while(start + 7 <= value):
                                start += 7
                                await tv.send_command(SendRemoteKey.down())
                                await asyncio.sleep(.2)
                            while (start - 7 >= value):
                                start -= 7
                                await tv.send_command(SendRemoteKey.up())
                                await asyncio.sleep(.2)
                            
                            await tv.send_command(SendRemoteKey.enter())
                            await asyncio.sleep(.2)

    await tv.close()
asyncio.run(main())
    




