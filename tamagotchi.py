from datetime import datetime, timedelta
from time import sleep
import math
import random
import re
from ollama import chat
from utils import read_json, write_json
from llm import submit_prompt
from mappings import mood_mappings, froggy_mappings, SPRITE_DIR

TAMAGOTCHI_JSON_PATH = "data/tamagotchi.json"
STAT_MAX_VAL = 8
STAT_DECAY_RATE = 1 # meaasured in units per day

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
            You are an agent that excels at choosing whether a user submitted task falls into one of three buckets: mind, body, or soul.
            'mind' bucket: tasks that are positive for one's brain and require thought. Like working on a project or planning one's future.
            'body' bucket: tasks that are positive for one's health. Going to the gym, a bike ride, stretching all fall into this bucket.
            'soul' bucket: tasks that are positive for one's deep well being. Spending time with family or friends, going to an event, being in nature.

            Do not put a task into the body bucket purely because it involves physical activity, only if it is a type of working out.
            Respond with exactly one word 'mind', 'body', or 'soul'.
            """

        answer = submit_prompt(system_prompt, task)

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

    def update(self, task = None):
        update_time = datetime.now()
        self.update_stats(update_time)
 
        if self.is_alive and task is not None:
                self.score_task(task)

        self.print_state()
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

    def get_closest_mood(self, moods, stat_value):
        best_mood = None
        best_dist = math.inf 

        for mood in moods:
            dist = abs(mood["value"] - stat_value / STAT_MAX_VAL) 
            if dist < best_dist:
                best_dist = dist
                best_mood = mood["name"]

        return best_mood

    def get_mood(self):
        candidates = [
            self.get_closest_mood(mood_mappings["mind"], self.mind),
            self.get_closest_mood(mood_mappings["body"], self.body),
            self.get_closest_mood(mood_mappings["soul"], self.soul),
        ]

        return random.choice(candidates)

    def mood_quote(self):
        time = datetime.now().strftime("%I:%M%p %A, %B %d, %Y")

        choices = [
            {
                "name": "mind",
                "value": self.mind,
                "desc": "a measure of smartness",
                "mood": self.get_closest_mood(mood_mappings["mind"], self.mind),
            },
            {
                "name": "body",
                "value": self.body,
                "desc": "a measure of health",
                "mood": self.get_closest_mood(mood_mappings["body"], self.body),
            },
            {
                "name": "soul",
                "value": self.soul,
                "desc": "a measure of well-being",
                "mood": self.get_closest_mood(mood_mappings["soul"], self.soul),
            },
        ]
        stat = random.choice(choices)
        modifiers = ["low", "medium", "high"]
        mod_idx = min(int(stat["value"] / STAT_MAX_VAL * 3), 2)
        mod = modifiers[mod_idx]

        prompt = f"""
            You are a tamagotchi.
            Your current mood is {stat["mood"]} which corresponds to a {mod} '{stat["name"]}' stat, {stat["desc"]}.
            Don't directly restate your mood. Try to let the context just subtly guide your response.
            Your output should be an interesting thought indicating how you currently feel. Keep the response short.
            """

        return submit_prompt(prompt)

    def generate_quote(self):
        if not self.is_alive:
            death_date = self.birth_date + timedelta(days=self.age)
            birth_str = self.birth_date.strftime("%m/%d/%y");
            death_str = death_date.strftime("%m/%d/%y");
            return f"Rest in peace.\n{birth_str}-{death_str}"

        return self.mood_quote()

    def get_sprite(self):
        self.sprite_mappings = froggy_mappings

        care_score = self.get_care_score() 
        vals = ["negative", "neutral", "positive"]
        idx = min(int(care_score * 3), 2)

        if not self.is_alive:
            return f"{SPRITE_DIR}/grave.png"
 
        return f"{SPRITE_DIR}/{random.choice(self.sprite_mappings[vals[idx]])}"

