from datetime import datetime, timedelta
import time
import threading
from draw import render_tamagotchi
from tamagotchi import Tamagotchi
from actions import TaskAction
from utils import read_json, write_json
from constants import QUEUE_JSON_PATH

def minute_loop(refresh_event, func, *args):
    target_time = datetime.now()

    def next_minute(now):
        return now.replace(second=0) + timedelta(minutes=1)

    while True:
        now = datetime.now()

        timeout = (target_time - now).total_seconds()
        timeout = max(timeout, 0)
        with refresh_event:
            refreshed = refresh_event.wait(timeout=timeout)
        func(*args)
        if refreshed:
            target_time = next_minute(datetime.now() + timedelta(seconds=20))
        else:
            target_time = next_minute(datetime.now())


def launch_render_loop(refresh_event):

    def render(epd):
        with refresh_event:
            try:
                queue = read_json(QUEUE_JSON_PATH)
            except:
                queue = []
            task = None
            if len(queue) > 0:
                task = queue.pop(0)
            write_json(queue, QUEUE_JSON_PATH)

        tamagotchi = Tamagotchi()
        tamagotchi.update(task)
        task_action = TaskAction(tamagotchi, task) if task is not None else None
        im = tamagotchi.generate_image(task_action)
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

        minute_loop(refresh_event, render, epd)

    minute_thread = threading.Thread(target=launch)
    minute_thread.start()


if __name__ == "__main__":
    # t = Tamagotchi()
    # launch_render_loop(t)
    refresh_event = threading.Condition()
    launch_render_loop(refresh_event)
    while True:
        test = input("Press enter to trigger refresh")
        with refresh_event:
            refresh_event.notify()
