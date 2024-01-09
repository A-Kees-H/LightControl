from keyboard import add_hotkey, call_later, wait
import time
from hylight import Connect
from light_control import *

def on_off_():
	for i in range(2):
		try:
			on_off()
			break
		except Exception as e:
			print(e)


def set_brightness_and_on_(brightness):
	brightness = round(brightness * 100/9)
	for i in range(2):
		try:
			print(set_real_brightness_and_on(brightness))
			break
		except Exception as e:
			print(e)

for i in range(10):
	add_hotkey(f"ctrl+alt+{i}", set_brightness_and_on_, args=[i])
add_hotkey('ctrl+shift+#', on_off_)
#add_hotkey('ctrl+alt+page up', lambda: call_later(up))
#add_hotkey('ctrl+alt+page down', lambda: call_later(down))

wait()

#loop = asyncio.get_event_loop()
#loop.run_forever(async_loop)
#press_and_release('shift+s, space')
#write('The quick brown fox jumps over the lazy dog.')
#add_hotkey('ctrl+shift+#', on_off, args=('triggered', 'hotkey'))
# Press PAGE UP then PAGE DOWN to type "foobar".
#add_hotkey('page up, page down', lambda: write('foobar'))
# Blocks until you press esc.
#wait('esc')
# Record events until 'esc' is pressed.
#recorded = record(until='esc')
# Then replay back at three times the speed.
#play(recorded, speed_factor=3)
# Type @@ then press space to replace with abbreviation.
#add_abbreviation('@@', 'my.long.email@example.com')
# Block forever, like `while True`.