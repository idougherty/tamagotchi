from datetime import time, datetime, UTC
import random
from abc import ABC, abstractmethod

SPRITE_DIR='images'

food_sprites = [
    [
        "bread-1.png",
        "bread-2.png",
        "bread-3.png",
    ],
    [
        "burger-1.png",
        "burger-2.png",
        "burger-3.png",
    ],
    [
        "cake-1.png",
        "cake-2.png",
        "cake-3.png",
    ],
    [
        "candy-1.png",
        "candy-2.png",
        "candy-3.png",
    ],
    [
        "rice-1.png",
        "rice-2.png",
        "rice-3.png",
    ],
    [
        "rice-ball-1.png",
        "rice-ball-2.png",
        "rice-ball-3.png",
    ],
]

def get_current_action(now):
    random.seed(get_days_since_epoch(now))

    breakfast_start = time(hour=8, minute=00)
    breakfast_end = time(hour=8, minute=15)
    lunch_start = time(hour=12, minute=00)
    lunch_end = time(hour=12, minute=15)
    dinner_start = time(hour=17, minute=00)
    dinner_end = time(hour=17, minute=15)

    action_mappings = [
        {
            "action": "sleeping",
            "sprite_primary": SpriteMappingRandom(froggy_mappings["sleeping"]),
            "sprite_secondary": None, # TODO: Zzz sprite
            "start_time": time(hour=22, minute=00),
            "end_time": time(hour=7, minute=00),
        },
        {
            "action": "eating breakfast",
            "sprite_primary": None,
            "sprite_secondary": SpriteMappingProgression(random.choice(food_sprites), breakfast_start, breakfast_end),
            "start_time": breakfast_start,
            "end_time": breakfast_end,
        },
        {
            "action": "eating lunch",
            "sprite_primary": None,
            "sprite_secondary": SpriteMappingProgression(random.choice(food_sprites), lunch_start, lunch_end),
            "start_time": lunch_start,
            "end_time": lunch_end,
        },
        {
            "action": "eating dinner",
            "sprite_primary": None,
            "sprite_secondary": SpriteMappingProgression(random.choice(food_sprites), dinner_start, dinner_end),
            "start_time": dinner_start,
            "end_time": dinner_end,
        },
        {
            "action": "pooping",
            "sprite_primary": None,
            "sprite_secondary": SpriteMappingRandom(["poop-1.png", "poop-2.png"]),
            "start_time": time(hour=9, minute=00),
            "end_time": time(hour=9, minute=10),
        },
    ]

    curr_action = None
    for action in action_mappings:
        after_start = action["start_time"] < now.time()
        before_end = action["end_time"] > now.time()
        if action["start_time"] < action["end_time"] and after_start and before_end:
            curr_action = action
            break
        elif action["end_time"] < action["start_time"] and (after_start or before_end):
            curr_action = action
            break

    return curr_action


def get_days_since_epoch(now):
    epoch = datetime(1970, 1, 1)
    days_since_epoch = (now - epoch).days

class SpriteMappingBase(ABC):
    @abstractmethod
    def get_sprite(self):
        pass

class SpriteMappingFixed(SpriteMappingBase):
    def __init__(self, sprite):
        self.sprite = sprite

    def get_sprite(self):
        return self.sprite

class SpriteMappingRandom(SpriteMappingBase):
    def __init__(self, sprites):
        self.sprites = sprites

    def get_sprite(self):
        return random.choice(self.sprites)

class SpriteMappingProgression(SpriteMappingBase):
    def __init__(self, sprites, start_time, end_time):
        self.sprites = sprites
        self.start_time = start_time
        self.end_time = end_time

    def get_sprite(self):
        # will not work overnight
        now = datetime.now()
        if now <= start_time:
            return self.sprites[0]

        if now >= end_time:
            return self.sprites[-1]

        span_s = (end_time - start_time).total_seconds()
        prog_s = (now - start_time).total_seconds()
        t = prog_s / span_s
        idx = int(t * len(self.sprites))

        return self.sprites[idx]

mood_mappings = {
    "mind": [
        { "name": "brilliant",      "value": 1.0 },
        { "name": "smart",          "value": 0.9 },
        { "name": "focused",        "value": 0.8 },
        { "name": "curious",        "value": 0.7 },
        { "name": "geeky",          "value": 0.6 },
        { "name": "nonchalant",     "value": 0.5 },
        { "name": "bored",          "value": 0.4 },
        { "name": "groggy",         "value": 0.3 },
        { "name": "disinterested",  "value": 0.2 },
        { "name": "dumb",           "value": 0.1 },
        { "name": "stupid",         "value": 0.0 },
    ],
    "body": [
        { "name": "athletic",       "value": 1.0 },
        { "name": "energetic",      "value": 0.9 },
        { "name": "healthy",        "value": 0.8 },
        { "name": "refreshed",      "value": 0.7 },
        { "name": "chilling",       "value": 0.6 },
        { "name": "idle",           "value": 0.5 },
        { "name": "tired",          "value": 0.4 },
        { "name": "sluggish",       "value": 0.3 },
        { "name": "weak",           "value": 0.2 },
        { "name": "drunk",          "value": 0.1 },
        { "name": "couch potatoey", "value": 0.0 },
    ],
    "soul": [
        { "name": "euphoric",       "value": 1.0 },
        { "name": "blissful",       "value": 0.9 },
        { "name": "loved",          "value": 0.8 },
        { "name": "content",        "value": 0.7 },
        { "name": "good",           "value": 0.6 },
        { "name": "okay",           "value": 0.5 },
        { "name": "blase",          "value": 0.4 },
        { "name": "apathetic",      "value": 0.3 },
        { "name": "anxious",        "value": 0.2 },
        { "name": "crazy",          "value": 0.1 },
        { "name": "depressed",      "value": 0.0 },
    ],
}

froggy_mappings = {
    "positive": [
        "tamagotchi-adult-froggy-1.png",
        "tamagotchi-adult-froggy-3.png",
    ],
    "neutral": [
        "tamagotchi-adult-froggy-4.png",
        "tamagotchi-adult-froggy-5.png",
        "tamagotchi-adult-froggy-8.png",
    ],
    "negative": [
        "tamagotchi-adult-froggy-6.png",
        "tamagotchi-adult-froggy-7.png",
    ],
    "sleeping": [
        "tamagotchi-adult-froggy-9.png",
        "tamagotchi-adult-froggy-10.png",
    ]
}

