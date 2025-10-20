from datetime import datetime, time, timedelta
from time import sleep
import math
import random
import re
from ollama import chat
from utils import read_json, write_json
from llm import submit_prompt
from mappings import mood_mappings, froggy_mappings, food_sprites
from constants import SPRITE_DIR, TAMAGOTCHI_JSON_PATH, STAT_MAX_VAL, STAT_DECAY_RATE
from draw import render_tamagotchi
from actions import MoodAction, SleepAction, MealAction, PoopAction, DeathAction

class Tamagotchi:

    def __init__(self):
        self.load_from_json()

    def load_from_json(self):
        try:
            data = read_json(TAMAGOTCHI_JSON_PATH)

            self.mind = data["mind"]
            self.body = data["body"]
            self.soul = data["soul"]
            self.care_score = data["care_score"]
            self.day_score = data["day_score"]
            self.age = data["age"]
            self.birth_date = datetime.fromisoformat(data["birth_date"])
            self.last_update_time = datetime.fromisoformat(data["last_update_time"])
            self.is_alive = data["is_alive"]
            self.sprite_mappings = froggy_mappings
 
        except Exception as e:
            print(f"Could not read {TAMAGOTCHI_JSON_PATH}: {e}")
            self.reset()

        print(f"Loaded from {TAMAGOTCHI_JSON_PATH}")
        self.print_state()

    def write_to_json(self):
        print(f"Writing to {TAMAGOTCHI_JSON_PATH}")

        try:
            data = {
                "mind": self.mind,
                "body": self.body,
                "soul": self.soul,
                "last_update_time": self.last_update_time,
                "care_score": self.care_score,
                "day_score": self.day_score,
                "age": self.age,
                "birth_date": self.birth_date,
                "is_alive": self.is_alive,
            }

            write_json(data, TAMAGOTCHI_JSON_PATH)
        except Exception as e:
            print(f"Could not write to {TAMAGOTCHI_JSON_PATH}: {e}")

    def reset(self):
        self.mind = STAT_MAX_VAL
        self.body = STAT_MAX_VAL
        self.soul = STAT_MAX_VAL
        self.care_score = 1
        self.day_score = 1
        self.age = 0
        self.birth_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.last_update_time = datetime.now()
        self.is_alive = True
        self.sprite_mappings = froggy_mappings

    def get_care_score(self):
        return (self.mind + self.body + self.soul) / (3 * STAT_MAX_VAL)

    def get_care_grade(self):
        grades = ["A", "B", "C", "D", "F"]
        modifiers = ["+", "", "-"]
        grade_span = 0.15

        grade_idx = int((1 - self.care_score) / grade_span)
        modifier_idx = (1 - self.care_score) % grade_span
        modifier_idx = min(int(modifier_idx * 3 / grade_span), len(modifiers) - 1)

        if grade_idx >= len(grades):
            grade_idx = len(grades) - 1
            modifier_idx = len(modifiers) - 1

        return f"{grades[grade_idx]}{modifiers[modifier_idx]}"
 
    def print_state(self):
        print(f"Is Alive: {self.is_alive}")
        print(f"Mind: {self.mind:.2f}/{STAT_MAX_VAL}")
        print(f"Body: {self.body:.2f}/{STAT_MAX_VAL}")
        print(f"Soul: {self.soul:.2f}/{STAT_MAX_VAL}")
        print(f"Care score: {self.get_care_grade()}")
        print(f"Age: {self.age}")

    def task_to_mood(self, task):
        system_prompt = """
            You are an agent that excels at choosing which buckets a user submitted task falls into: mind, body, or soul.
            'mind' bucket: Tasks that require a lot of thought. Commonly a task one needs to do. Like working on a project or planning one's future.
            'body' bucket: Tasks that are positive for one's health. Going to the gym, a bike ride, stretching all fall into this bucket.
            'soul' bucket: Tasks that are positive for one's deep well being, peace of mind, happiness. Commonly a task one wants to do. Spending time with family or friends, going to an event, being in nature.

            Respond with a list of buckets for the user's task: 'mind', 'body', or 'soul'.

            Examples:
            Climbing with a group of friends: body soul
            Coding a personal project: mind soul
            Planning a doctor's visit: mind
            Coding for work: mind
            Going to class: mind
            Eating with a group of friends: soul
            Playing a video game: soul
            """
            #Do not put a task into the body bucket purely because it involves physical activity, only if it is a type of working out.

        answer = None
        try:
            answer = submit_prompt(system_prompt, task)
        except Exception as e:
            print(f"Couldn't gen response: {e}")

        if "mind" in answer:
            return "mind"
        elif "body" in answer:
            return "body"
        elif "soul" in answer:
            return "soul"

        print(f"No mood found in response '{answer}'. Using a random one.")
        return random.choice(["mind", "body", "soul"])

    def score_task(self, task):
        mood = self.task_to_mood(task)

        print(f"Adding point to {mood} stat for '{task}'")
        if mood == "mind": 
            self.mind = min(self.mind + 1, STAT_MAX_VAL)
        elif mood == "body":
            self.body = min(self.body + 1, STAT_MAX_VAL)
        elif mood == "soul":
            self.soul = min(self.soul + 1, STAT_MAX_VAL)
        else:
            raise Exception(f"no mood found for {mood}")

    def update(self, task = None, persist = True):
        update_time = datetime.now()
        self.update_stats(update_time)
 
        if self.is_alive and task is not None:
                self.score_task(task)

        self.print_state()
        if persist:
            self.write_to_json()

    def update_stats(self, now):

        curr_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

        while self.last_update_time < curr_date:
            last_date = self.last_update_time.replace(hour=0, minute=0, second=0, microsecond=0)
            next_date = last_date + timedelta(days = 1)
            self.decay_stats(next_date)

            if not self.is_alive:
                return

            self.age = (self.last_update_time - self.birth_date).days + 1
            self.day_score = self.get_care_score()
            self.care_score = (self.care_score * self.age + self.day_score) / (self.age + 1)

            print(self.age, self.last_update_time, self.day_score, self.care_score)
 
        self.decay_stats(now)

        if not self.is_alive:
            return

        self.age = (self.last_update_time - self.birth_date).days + 1
        curr_score = self.get_care_score()

        if self.day_score > curr_score:
            return

        self.care_score = (self.care_score * self.age - self.day_score + curr_score) / self.age
        self.day_score = curr_score
        print(self.age, self.last_update_time, self.day_score, self.care_score)

    def decay_stats(self, now):
        dt_s = (now - self.last_update_time).total_seconds()
        dt_days = dt_s / 86400

        decay = STAT_DECAY_RATE * dt_days if self.is_alive else 0
        decay = min(decay, self.mind, self.body, self.soul)

        self.last_update_time = now
        self.mind -= decay
        self.body -= decay
        self.soul -= decay

        if (self.mind <= 0 or self.body <= 0 or self.soul <= 0):
            self.die()
 
        print(f"Decayed stats by {decay:.3f}. ({dt_s:.3f} seconds since last update)")
 
    def die(self):
        self.is_alive = False
        self.mind = max(self.mind, 0)
        self.body = max(self.body, 0)
        self.soul = max(self.soul, 0)

    def generate_image(self, action=None):
        now = datetime.now()
        action = action or self.get_current_action(now)
        quote = action.generate_quote()
        primary, secondary = action.get_sprites()

        primary_path = f"{SPRITE_DIR}/{primary}"
        secondary_path = f"{SPRITE_DIR}/{secondary}" if secondary is not None else None

        return render_tamagotchi(self, primary_path, secondary_path, quote)

    def get_current_action(self, now):

        def get_days_since_epoch(now):
            epoch = datetime(1970, 1, 1)
            return (now - epoch).days

        rng = random.Random(get_days_since_epoch(now))

        sleep_start = time(hour=22, minute=00)
        sleep_end = time(hour=7, minute=00)
        breakfast_start = time(hour=8, minute=00)
        breakfast_end = time(hour=8, minute=15)
        lunch_start = time(hour=12, minute=00)
        lunch_end = time(hour=12, minute=15)
        dinner_start = time(hour=19, minute=00)
        dinner_end = time(hour=19, minute=15)
        poop_1_start = time(hour=rng.randint(7, 21), minute=rng.randint(0, 59))
        poop_1_end = (datetime.combine(datetime.today(), poop_1_start) + timedelta(minutes=10)).time()
        poop_2_start = time(hour=rng.randint(7, 21), minute=rng.randint(0, 59))
        poop_2_end = (datetime.combine(datetime.today(), poop_2_start) + timedelta(minutes=10)).time()

        schedule = [
            {
                "action": SleepAction(self),
                "start_time": sleep_start,
                "end_time": sleep_end,
            },
            {
                "action": MealAction(self, "breakfast", rng.choice(food_sprites), breakfast_start, breakfast_end),
                "start_time": breakfast_start,
                "end_time": breakfast_end,
            },
            {
                "action": MealAction(self, "lunch", rng.choice(food_sprites), lunch_start, lunch_end),
                "start_time": lunch_start,
                "end_time": lunch_end,
            },
            {
                "action": MealAction(self, "dinner", rng.choice(food_sprites), dinner_start, dinner_end),
                "start_time": dinner_start,
                "end_time": dinner_end,
            },
            {
                "action": PoopAction(self),
                "start_time": poop_1_start,
                "end_time": poop_1_end,
            },
            {
                "action": PoopAction(self),
                "start_time": poop_2_start,
                "end_time": poop_2_end,
            },
        ]

        if not self.is_alive:
            return DeathAction(self)

        curr_action = MoodAction(self)
        for action in schedule:
            after_start = action["start_time"] < now.time()
            before_end = action["end_time"] > now.time()
            if action["start_time"] < action["end_time"] and after_start and before_end:
                curr_action = action["action"]
                break
            elif action["end_time"] < action["start_time"] and (after_start or before_end):
                curr_action = action["action"]
                break

        return curr_action


if __name__ == "__main__":
    t = Tamagotchi()

    # print(t.task_to_mood("meditated for 15 minutes"))
    # print(t.task_to_mood("went on a sushi date with etta"))
    # print(t.task_to_mood("biked to work"))
    # print(t.task_to_mood("went to work (coded all day)"))

    # print(t.mood_quote("mind"))
    # print(t.mood_quote("body"))
    # print(t.mood_quote("soul"))

    im = t.generate_image()
    im.show()
