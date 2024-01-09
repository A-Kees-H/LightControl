# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import webrepl, micropython

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect("BTHub6-TW6J", "JqJMWchDriY6")
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())
    
do_connect()
webrepl.start()
micropython.alloc_emergency_exception_buf(100)
from Reset import *

try:
    from L import *
    IP = "192.168.1.209"
    bulb = Bulb(IP)
    from Reset import *
except Exception as e:
    try:
        with open("errorlog.txt", "a") as f:
            f.append(e + "\n\n")
            f.close()
    except:
        pass