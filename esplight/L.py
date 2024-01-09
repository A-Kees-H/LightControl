import socket
import gc, utime as time
from machine import Pin, Timer
import machine
import micropython
import json

class Bulb:
    def __init__(s, IP="192.168.1.209"):
        s.on_bytes = b'\x00\x00\x00k\xd0\xf2\x81\xec\x8d\xff\x8b\xe7\x8e\xe8\x8d\xa3\xca\xa5\xd1\xff\x8c\xe1\x80\xf2\x86\xe4\x91\xfd\x9f\xb1\xdd\xb4\xd3\xbb\xcf\xa6\xc8\xaf\xdc\xb9\xcb\xbd\xd4\xb7\xd2\xf0\xca\xea\x91\xb3\xc7\xb5\xd4\xba\xc9\xa0\xd4\xbd\xd2\xbc\xe3\x8f\xe6\x81\xe9\x9d\xc2\xb1\xc5\xa4\xd0\xb5\x97\xad\x8d\xf6\xd4\xbb\xd5\x8a\xe5\x83\xe5\xc7\xfd\xdd\xec\xc0\xe0\xc2\xab\xcc\xa2\xcd\xbf\xda\x85\xe1\x84\xe2\x83\xf6\x9a\xee\xcc\xf6\xd6\xe7\x9a\xe7\x9a'
        s.off_bytes = b'\x00\x00\x00k\xd0\xf2\x81\xec\x8d\xff\x8b\xe7\x8e\xe8\x8d\xa3\xca\xa5\xd1\xff\x8c\xe1\x80\xf2\x86\xe4\x91\xfd\x9f\xb1\xdd\xb4\xd3\xbb\xcf\xa6\xc8\xaf\xdc\xb9\xcb\xbd\xd4\xb7\xd2\xf0\xca\xea\x91\xb3\xc7\xb5\xd4\xba\xc9\xa0\xd4\xbd\xd2\xbc\xe3\x8f\xe6\x81\xe9\x9d\xc2\xb1\xc5\xa4\xd0\xb5\x97\xad\x8d\xf6\xd4\xbb\xd5\x8a\xe5\x83\xe5\xc7\xfd\xdd\xed\xc1\xe1\xc3\xaa\xcd\xa3\xcc\xbe\xdb\x84\xe0\x85\xe3\x82\xf7\x9b\xef\xcd\xf7\xd7\xe6\x9b\xe6\x9b'
        s.get_state_bytes = b'\x00\x00\x00D\xd0\xf2\x81\xec\x8d\xff\x8b\xe7\x8e\xe8\x8d\xa3\xca\xa5\xd1\xff\x8c\xe1\x80\xf2\x86\xe4\x91\xfd\x9f\xb1\xdd\xb4\xd3\xbb\xcf\xa6\xc8\xaf\xdc\xb9\xcb\xbd\xd4\xb7\xd2\xf0\xca\xea\x91\xb3\xd4\xb1\xc5\x9a\xf6\x9f\xf8\x90\xe4\xbb\xc8\xbc\xdd\xa9\xcc\xee\xd4\xf4\x8f\xf2\x8f\xf2'
        s.gsb = s.get_state_bytes

        s.IP = IP
        s.addr = socket.getaddrinfo(s.IP, 9999)[0][-1]
        s.connect()
        s.times = 0
        in_pin_num = 0 #set to 0 to use boot button, or whatever else to use whatever other pin
        out_pin_num = 14
        s.pin = Pin(in_pin_num, Pin.IN)
        s.pin2 = Pin(out_pin_num, Pin.OUT)
        s.pin2.value(1)
        s.tim = Timer(-1)
        s.tim.init(mode=Timer.PERIODIC, freq=400, callback=lambda t: s.checkpin())
        s.prev_pin_value = 0
        #s.pin.irq(lambda p:s.button_press)
        #alt approach with timer?

    def checkpin(s):
        current_pin_value = s.pin.value()
        if s.prev_pin_value != 1 and current_pin_value == 1:
            s.times += 1
            s.button_press()
        s.prev_pin_value = current_pin_value

    def connect(s, IP=None):
        print("Connecting...")
        if IP != None:
            s.IP = IP
        s.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for i in range(5):
            try:
                s.sock.connect(s.addr)
                print("Connected")
                break
            except Exception as e:
                time.sleep(0.05)
                print(f"Connection Failed {i+1} time{'s' if i else ''}:\n" + e)
        s.last_send_time = time.ticks_ms()

    def button_press(s):
        # if an interaction with the socket has been initiated in the last 350ms, don't bother
        print(f"{s.times} - motion")
        if time.ticks_ms() - s.last_send_time > 3000:    
            if s.on_off():
                s.off()
            else:
                s.on()
            s.last_send_time = time.ticks_ms()
    
    def send(s, bytes_):
        for i in range(5):
            try:
                s.sock.send(bytes_)
                break
            except Exception as e:
                print("send error:", e)
                s.connect()
        for x in range(4):
            try:
                return s.sock.recv(4096)
            except Exception as e:
                print("receive error:", e)

    def on_off(s):
        return s.send(s.get_state_bytes)[68] != 201 #if it does = 201, then it's off, so return 0
            
    def on(s):
        s.send(s.on_bytes)

    def off(s):
        s.send(s.off_bytes)

    def get_state(s):
        data = s.send(s.get_state_bytes)
        return list(json.loads(s.decrypt(data[4:]))["smartlife.iot.smartbulb.lightingservice"].values())[0]

    @staticmethod
    def decrypt(cyphertext):
        key = 171
        buffer = []
        for cypherbyte in cyphertext:
            plainbyte = key ^ cypherbyte
            key = cypherbyte
            buffer.append(plainbyte)
        #print(buffer)
        plaintext = bytes(buffer)
        #print(plaintext)
        return plaintext.decode()
