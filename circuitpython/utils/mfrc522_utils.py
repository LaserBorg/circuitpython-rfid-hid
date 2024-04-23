
tag_types = {0: "nothing", 16: "MIFARE Classic 1K"}


def read_rfid(rdr, address=8):
    try:
        # SEARCH FOR CARDS
        (stat, tag_type) = rdr.request(rdr.REQIDL)

        # If no card found, return immediately
        if stat != rdr.OK:
            return 0, [0]

        # FOUND -> ASK FOR UID
        (stat, raw_uid) = rdr.anticoll()

        # If can't read UID, return immediately
        if stat != rdr.OK:
            return 0, [0]

        # UID RECEIVED
        uid = "0x" + "%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3])

        # If failed to select tag, return immediately
        if rdr.select_tag(raw_uid) != rdr.OK:
            return uid, [0]

        # If authentication error, return immediately
        if rdr.auth(rdr.AUTHENT1A, address, rdr.KEY, raw_uid) != rdr.OK:
            return uid, [0]

        # READ
        data = rdr.read(address)

        # Format data as a string of hexadecimal numbers
        data = " ".join("0x{:02x}".format(b) for b in data)

        rdr.stop_crypto1()
        return uid, data

    except Exception as e:
        print("Error reading RFID tag:", e)
        return 0, [0]


def write_rfid(rdr, uid, data, address=8):
    try:
        # Convert uid back to raw_uid
        raw_uid = [int(uid[i:i+2], 16) for i in range(2, 10, 2)]

        # If failed to select tag, return immediately
        if rdr.select_tag(raw_uid) != rdr.OK:
            print("Failed to select tag.")
            return False

        # If authentication error, return immediately
        if rdr.auth(rdr.AUTHENT1A, address, rdr.KEY, raw_uid) != rdr.OK:
            print("Authentication error.")
            return False

        # WRITE
        stat = rdr.write(address, data)

        rdr.stop_crypto1()

        if stat == rdr.OK:
            print("Write successful.")
            return True
        else:
            print("Write failed.")
            return False

    except Exception as e:
        print("Error writing to RFID tag:", e)
        return False