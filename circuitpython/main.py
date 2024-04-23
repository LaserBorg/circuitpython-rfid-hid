"""
circuitpython-rfid-hid
convert RFID Tag Data into keystrokes by emulating a USB Keyboard on a Pi Pico.
https://github.com/LaserBorg/circuitpython-rfid-hid
"""

import time
import board                                                    # type: ignore
import neopixel                                                 # type: ignore
import usb_hid                                                  # type: ignore
from adafruit_hid.keyboard import Keyboard                      # type: ignore
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS    # type: ignore

from utils.mfrc522 import MFRC522
from utils.mfrc522_utils import read_rfid
from utils.json_utils import get_tags_dict


# SPI Pins for MFRC522
sck = board.GP6
mosi = board.GP7
miso = board.GP4 
rst = board.GP8
cs = board.GP5

# LED Pin
led_pin = board.GP0

# sleep between rfid scans, in seconds
delay = 0.1

# threshold how often *notfound* before leave-event, has to be >= 2
notfound_limit = 4    


# get RGB list from color name
def color(text):
    if 'blue' in text.lower():
        color = (0, 0, 255)
    elif 'white' in text.lower():
        color = (255, 255, 255)
    elif 'black' in text.lower():
        color = (0, 0, 0)
    else:
        color = (255, 0, 0)
    return color


if __name__ == "__main__":

    # init RFID
    rdr = MFRC522(sck, mosi, miso, rst, cs, delay=int(delay * 1000))  
    rdr.set_antenna_gain(0x07 << 4)

    # init Keyboard
    kbd = Keyboard(usb_hid.devices)  
    keyboard = KeyboardLayoutUS(kbd)

    # init NeoPixel
    led = neopixel.NeoPixel(led_pin, 1, pixel_order=neopixel.RGB)  
    led[0] = color("black")


    # get RFID Tag IDs
    known_tags = get_tags_dict('known_tags.json')

    
    # MAIN LOOP
    prev_uid = 0
    notfound = 0
    
    while True:
        uid, payload = read_rfid(rdr, address=8)
        
        # NO CARD FOUND
        if uid == 0:
            if uid != prev_uid and notfound >= notfound_limit:
                prev_uid = notfound = 0
                
                print("leave")
                keyboard.write("leave" + "\n")
                led[0] = color("black")
            
            elif notfound < notfound_limit:
                notfound += 1
        
        else:
            if prev_uid == 0:
                # CARD APPEARED
                text = known_tags[uid] if uid in known_tags else uid
                
                print(text)
                keyboard.write(text + "\n")
                led[0] = color(text)
                 
            elif prev_uid == uid:
                # CARD STILL THERE
                time.sleep(delay)
                
            notfound = 0
            prev_uid = uid
