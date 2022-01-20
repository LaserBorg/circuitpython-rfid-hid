# circuitpython-rfid-hid
convert RFID Tag Data into keystrokes by emulating a USB Keyboard on a Pi Pico.

Hardware: 
- Raspberry Pi Pico (RP2040) with CircuitPython 7.x
- MFRC522-based RFID reader using SPI
- Mifare Classic 1k Tags (not sure if MFRC522 also supports different Standards..)


<small>RFID reader for [MFRC522](http://www.nxp.com/documents/data_sheet/MFRC522.pdf) is based on CircuitPython Class of [domdfcoding/circuitpython-mfrc522](https://github.com/domdfcoding/circuitpython-mfrc522),
which is a port from MicroPython [wendlers/micropython-mfrc522](https://github.com/wendlers/micropython-mfrc522)


## Usage

Copy ``code.py``, ``boot.py``, ``known_tags.json`` and the ``lib/`` directory with all it's content (``mfrc.py`` class and ``adafruit_bus_device/`` libraries) to the root of Pico's File System.

Pins:

| MFRC522 | Pico GPIO |
|---------|-----------|
| sck     | GP06      |
| mosi    | GP07      |
| miso    | GP04      |
| rst     | GP18      |
| cs/sda  | GP05      |


Write Access is enabled by grounding another Pin (-> GP02 to mass) which sets the USB-filesystem to *read-only* at boot time, which allows Pico to write to it's own memory. 
This is handled by ``boot.py`` as described [here](https://learn.adafruit.com/circuitpython-essentials/circuitpython-storage).
