from .hylight import Connect
import time
import datetime
import sys

def off():
	bulb.off()

def on():
	bulb.on()

def on_off():
	if is_on():
		bulb.off()
		return 0
	else:
		bulb.on()
		return 1

def is_on():
	return bulb.get_on_or_off()

def set_colour(h, s, v, w=0):
	bulb.set_hsv(h, s, v)

def set_white():
	bulb.set_hsv(0, 0, bulb.get_brightness())
	
def get_colour():
	return bulb.get_hsv()

def get_brightness():
	return round(bulb.get_brightness() * 100/255)

def get_real_brightness():
	return bulb.get_brightness()

def set_brightness(hundred):
	bulb.set_brightness(round(hundred * 255/100))

def set_real_brightness(number):
	bulb.set_brightness(number)

def set_brightness_and_on(brightness):
	print(brightness)
	print(round(brightness * 255/100))
	req = {'smartlife.iot.smartbulb.lightingservice': {'transition_light_state': {'brightness': round(brightness * 255/100), 'on_off': 1, 'ignore_default': 1}}}
	return bulb.query(req)

def set_real_brightness_and_on(brightness):
	req = {'smartlife.iot.smartbulb.lightingservice': {'transition_light_state': {'brightness': brightness, 'on_off': 1, 'ignore_default': 1}}}
	return bulb.query(req)

def set_brightness_and_off(brightness):
	req = {'smartlife.iot.smartbulb.lightingservice': {'transition_light_state': {'brightness': round(brightness * 255/100), 'on_off': 0, 'ignore_default': 1}}}
	bulb.query(req)

def get_warmth():
	#print(f"real temp: {bulb.warmth}")
	return round((bulb.get_warmth() - 2500) * 100/6500)

def get_real_warmth():
	return bulb.get_warmth()

def set_real_warmth(temp):
	bulb.set_warmth(temp)

def set_warmth(number):
	color_temp = 2500 + round(number * 6500/100)
	#print(color_temp)
	bulb.set_warmth(color_temp)

def up():
	increment = 5
	if not is_on():
		set_brightness_and_on(0)
		brightness = 0
	else:
		brightness = get_brightness()
	if brightness + increment > 99:
		set_brightness(100)
	else:
		set_brightness(brightness + increment)

def down():
	increment = 5
	if not is_on():
		return
	brightness = get_brightness()
	if brightness - increment < 1:
		set_brightness_and_off(0)
	else:
		set_brightness(brightness - increment)


def cool():
	#print(f"warmth: {get_warmth()}, new: {get_warmth() + 10}, converted: {2500 + round(get_warmth() + 10 * 6500/100)}")
	if not is_on():
		return
	warmth = get_real_warmth()
	if warmth < 2500:
		set_real_warmth(2500)
	if warmth + 650 > 8999:
		set_real_warmth(9000)
	else:
		set_real_warmth(warmth + 650)


def warm():
	if not is_on():
		return
	warmth = get_real_warmth()
	if warmth < 2500:
		set_real_warmth(2500)
	if warmth - 650 < 2501:
		set_real_warmth(2500)
	else:
		set_real_warmth(warmth - 650)

def max():
	set_brightness_and_on(100)

def min():
	set_brightness_and_on(0)

def change_bulb_name(name):
	bulb.query({'system':{'set_dev_alias':{'alias':name}}})

def reconnect():
	bulb.connect()

def delay(seconds):
	time.sleep(seconds)

#nice debugging function
def write(e):
	with open("C:\\Users\\Andrew\\Documents\\tool_light_log.txt", "a") as f:
		f.write(f"{datetime.datetime.now()}\n{e}\n\n")
		f.close()

def in_parse(trigger):
	write(trigger)
	if trigger == "up":
		up()
	elif trigger == "down":
		down()
	elif trigger == "on":
		on()
	elif trigger == "off":
		off()
	elif trigger == "onoff":
		on_off()
	elif trigger == "warm":
		warm()
	elif trigger == "cool":
		cool()
	elif " " in trigger:
		try: 
			pass
			#hsv = trigger.split(" ")
			#set_colour(int(hsv[0]), int(hsv[1]), int(hsv[2]))
		except Exception as e:
			pass

bulb_ip = "192.168.12.150"
bulb = Connect(bulb_ip)