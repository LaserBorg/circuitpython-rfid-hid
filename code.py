"""
circuitpython-rfid-hid
convert RFID Tag Data into keystrokes by emulating a USB Keyboard on a Pi Pico.
https://github.com/LaserBorg/circuitpython-rfid-hid
"""

import board
import time
import json
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
import neopixel
import mfrc522


# lookup for tag types
tag_types = {0: "nothing",
             16: "MIFARE Classic 1K"}

# Pins for MFRC522
sck = board.GP6
mosi = board.GP7
miso = board.GP4 
rst = board.GP18
cs = board.GP5  # = sda
# additional pins
led_pin = board.GP0


delay =          0.1  # sleep between rfid scans, in seconds
notfound_limit = 4    # threshold how often *notfound* before leave-event, has to be >= 2

# # TODO: try writing with process_rfid(write=True, adress=8, data=testdata)
# testdata = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"


# # READ known_tags from JSON
# known_tags = {"0x4348b603": "WHITE CARD", "0x09a929b3": "BLUE TOKEN"}
def get_known_tag_list(filename='known_tags.json'):
    with open(filename, 'r') as file:
        known_tags = json.load(file)
    return known_tags


# TODO: WRITE new tags to JSON
def dump_known_tag_list(known_tags):
    with open('known_tags.json', 'w') as file:  # or use 'a' for append
        json.dump(known_tags, file)


def get_color_from_string(text):
    if 'blue' in text.lower():
        color = (0, 0, 255)
    elif 'white' in text.lower():
        color = (255, 255, 255)
    else:
        color = (255, 0, 0)
    return color


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
    # INIT
    rdr = mfrc522.MFRC522(sck, mosi, miso, rst, cs, delay=int(delay * 1000))  # RFID
    rdr.set_antenna_gain(0x07 << 4)

    kbd = Keyboard(usb_hid.devices)  # Keyboard
    keyboard = KeyboardLayoutUS(kbd)

    led = neopixel.NeoPixel(led_pin, 1, pixel_order=neopixel.RGB)  # NeoPixel LED
    led[0] = (0, 0, 0)

    # read from known_tag JSON
    known_tags = get_known_tag_list()

    # state variables
    prev_uid = notfound = 0
    
    print("ready..")
    
    while True:
        uid, payload = process_rfid(adress=8)
        
        # NO CARD FOUND
        if uid == 0:
            if uid != prev_uid and notfound >= notfound_limit:
                prev_uid = notfound = 0
                
                print("leave")
                keyboard.write("leave" + "\n")
                led[0] = (0, 0, 0)
            
            elif notfound < notfound_limit:
                notfound += 1
        
        else:
            if prev_uid == 0:
                # CARD APPEARED
                text = known_tags[uid] if uid in known_tags else uid
                
                print(text)
                keyboard.write(text + "\n")
                led[0] = get_color_from_string(text)
                 
            elif prev_uid == uid:
                # CARD STILL THERE
                time.sleep(delay)
                
            notfound = 0
            prev_uid = uid
