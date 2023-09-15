from RPI.Communication.pc import PC

if __name__ == "__main__":
    test = PC()
    test.connect()
    test.disconnect()