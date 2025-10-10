from datetime import datetime, timedelta
import time
import threading
from draw import render_tamagotchi
from mappings import get_current_action
from tamagotchi import Tamagotchi

def minute_loop(func, arg):
    target_time = datetime.now().replace(second=0)

    while True:
        now = datetime.now()

        if now > target_time:
            func(arg)
            target_time = target_time + timedelta(minutes=1)
        else:
            timeout = (target_time - now).total_seconds()
            timeout = max(timeout, 0)
            time.sleep(timeout)

def launch_render_loop():

    def render(epd):
        tamagotchi = Tamagotchi()
        tamagotchi.update(persist=False)
        sprite = tamagotchi.get_sprite()
        quote = tamagotchi.generate_quote()
        now = datetime.now()
        print(now)
        action = get_current_action(now)
        print(action)
        im = render_tamagotchi(tamagotchi, sprite, None, quote)
        # im.show()
        epd.display(epd.getbuffer(im))

    def launch():
        import sys
        import os
        picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'waveshare/pic')
        libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'waveshare/lib')
        if os.path.exists(libdir):
            sys.path.append(libdir)
	
        from waveshare_epd import epd3in97

        epd = epd3in97.EPD()
        epd.init()
        epd.Clear()

        minute_loop(render, epd)


    minute_thread = threading.Thread(target=launch)
    minute_thread.start()

if __name__ == "__main__":
    t = Tamagotchi()
    launch_render_loop(t)
