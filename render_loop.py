import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'waveshare/pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'waveshare/lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd3in97
from datetime import datetime, timedelta
import time
import threading
from draw import render_tamagotchi
from mappings import get_current_action
from tamagotchi import Tamagotchi

def minute_loop(func):
    target_time = datetime.now().replace(second=0)

    while True:
        now = datetime.now()

        if now > target_time:
            func()
            target_time = target_time + timedelta(minutes=1)
        else:
            timeout = (target_time - now).total_seconds()
            timeout = max(timeout, 0)
            time.sleep(timeout)

def launch_render_loop(tamagotchi):
    epd = epd3in97.EPD()

    def render():
        now = datetime.now()
        sprite = t.get_sprite()
        quote = "Testing..."#t.generate_quote()
        print(now)
        action = get_current_action(now)
        print(action)
        im = render_tamagotchi(t, sprite, None, quote)
        # im.show()
        epd.init()
        epd.display(epd.getbuffer(im))

    minute_thread = threading.Thread(target=minute_loop, args=(render,))
    minute_thread.start()

if __name__ == "__main__":
    t = Tamagotchi()
    launch_render_loop(t)
