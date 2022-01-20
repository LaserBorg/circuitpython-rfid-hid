"""
circuitpython-rfid-hid
convert RFID Tag Data into keystrokes by emulating a USB Keyboard on a Pi Pico.
https://github.com/LaserBorg/circuitpython-rfid-hid
"""
import board
import mfrc522
import time
import json
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS


# lookups
tag_types = {0: "nothing",
             16: "MIFARE Classic 1K"}

# define pins for MFRC522
sck = board.GP6
mosi = board.GP7
miso = board.GP4 
rst = board.GP18
cs = board.GP5  # = sda

# sleep between rfid scans, in seconds 
delay = 0.1

# threshold how often *notfound* before leave-event, has to be >= 2
notfound_limit = 3


# # TODO: try writing with process_rfid(write=True, adress=8, data=testdata)
# testdata = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"


# initialize mfrc522 with pins and delay and set antenna to maximum gain
rdr = mfrc522.MFRC522(sck, mosi, miso, rst, cs, delay=int(delay*1000))
rdr.set_antenna_gain(0x07 << 4)


# # READ JSON
# known_tags = {"0x4348b603": "WHITE CARD", "0x09a929b3": "BLUE TOKEN"}
with open('known_tags.json', 'r') as file:
    known_tags = json.load(file)

# # TODO: WRITE JSON (or 'a' for APPEND)
# with open('known_tags.json', 'w') as file:
#     json.dump(known_tags, file)


# initialize Keyboard
kbd = Keyboard(usb_hid.devices)
keyboard = KeyboardLayoutUS(kbd)


def process_rfid(write=False, adress=8, data=None):
    # SEARCH FOR CARDS
    (stat, tag_type) = rdr.request(rdr.REQIDL)

    if stat == rdr.OK:
        # FOUND -> ASK FOR UID
        (stat, raw_uid) = rdr.anticoll()
        # print(tag_types[tag_type])
        
        if stat == rdr.OK:
            # UID RECEIVED
            uid = "0x" + "%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])
            #print("\n" + known_tags[uid])
            
            # SELECT CARD BY UID
            if rdr.select_tag(raw_uid) == rdr.OK:
                
                # DECRYPT
                if rdr.auth(rdr.AUTHENT1A, adress, rdr.KEY, raw_uid) == rdr.OK:
                    
                    if write:
                        if data is not None:
                            # WRITE
                            stat = rdr.write(adress, data)
                    else:
                        # READ
                        data = rdr.read(adress)
                  
                    rdr.stop_crypto1()
                    return uid, data
                
                else:
                    # print("authentication error")
                    return uid, [0]
            else:
                # print("failed to select tag")
                return uid, [0]
        else:
            # print("can't read UID")
            return 0, [0]
    else:
        # print("no tag detected")
        return 0, [0]


if __name__ == "__main__":
    prev_uid = notfound = 0
    print("ready..")
    
    while True:
        uid, payload = process_rfid(adress=8)
        
        # NO CARD
        if uid == 0:
            if uid != prev_uid and notfound >= notfound_limit:
                prev_uid = notfound = 0
                print("leave")
                keyboard.write("leave" + "\n")
                
            elif notfound >= notfound_limit:
                # NO CARD FOUND
                continue
            
            else:
                notfound += 1
        
        else:
            if prev_uid == 0:
                # CARD APPEARED
                text = known_tags[uid] if uid in known_tags else uid
                print(f"{text} appeared")
                keyboard.write(text + "\n")
            
            elif prev_uid == uid:
                # CARD STILL THERE
                time.sleep(delay)
                
            notfound = 0
            prev_uid = uid
