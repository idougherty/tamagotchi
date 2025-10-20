import math
import random
from datetime import datetime, timedelta, time
from abc import ABC, abstractmethod
from mappings import mood_mappings, froggy_mappings, poop_sprites, food_sprites
from constants import SPRITE_DIR, STAT_MAX_VAL, MAX_QUOTE_TOKENS
from llm import submit_prompt

class ActionBase(ABC):
    @abstractmethod
    def get_sprites(self):
        pass

    @abstractmethod
    def generate_quote(self):
        pass


class MoodAction(ActionBase):
    def __init__(self, tamagotchi, mood=None):
        moods = ["mind", "body", "soul"]
        self.mood = mood or random.choice(moods)
        self.tamagotchi = tamagotchi

    def get_sprites(self):
        if self.mood == "mind":
            stat = self.tamagotchi.mind / STAT_MAX_VAL
        elif self.mood == "body":
            stat = self.tamagotchi.body / STAT_MAX_VAL
        elif self.mood == "soul":
            stat = self.tamagotchi.soul / STAT_MAX_VAL
        else:
            raise Exception(f"No mood found for {self.mood}")

        vals = ["negative", "neutral", "positive"]
        idx = min(int(stat * 3), 2)
 
        primary = random.choice(self.tamagotchi.sprite_mappings[vals[idx]])
        secondary = None

        return primary, secondary

    def get_closest_mood(self, moods, stat_value):
        best_mood = None
        best_dist = math.inf 

        for mood in moods:
            dist = abs(mood["value"] - stat_value / STAT_MAX_VAL) 
            if dist < best_dist:
                best_dist = dist
                best_mood = mood["name"]

        return best_mood

    def generate_quote(self):
        time = datetime.now().strftime("%I:%M%p %A, %B %d, %Y")

        choices = [
            {
                "name": "mind",
                "value": self.tamagotchi.mind,
                "desc": "a measure of smartness",
                "mood": self.get_closest_mood(mood_mappings["mind"], self.tamagotchi.mind),
            },
            {
                "name": "body",
                "value": self.tamagotchi.body,
                "desc": "a measure of health",
                "mood": self.get_closest_mood(mood_mappings["body"], self.tamagotchi.body),
            },
            {
                "name": "soul",
                "value": self.tamagotchi.soul,
                "desc": "a measure of well-being",
                "mood": self.get_closest_mood(mood_mappings["soul"], self.tamagotchi.soul),
            },
        ]

        stat = next((x for x in choices if x["name"] == self.mood), None)
        if stat is None:
            raise Exception(f"No stat found for mood {self.mood}")

        modifiers = ["low", "medium", "high"]
        mod_idx = min(int(stat["value"] / STAT_MAX_VAL * 3), 2)
        mod = modifiers[mod_idx]

        system_prompt = f"""
            You are a tamagotchi.
            Don't directly restate your mood. Try to let the context just subtly guide your response.
            Respond with an interesting thought describing how you currently feel. Keep the response under 10 words.
            """

        user_prompt = f"""
            Your current mood is {stat["mood"]} which corresponds to a {mod} '{stat["name"]}' stat, {stat["desc"]}.
        """

        options = {
            # crank up the temperature for more creative responses
            "temperature": 2.0,
            "num_predict": MAX_QUOTE_TOKENS,
        }

        return submit_prompt(system_prompt, user_prompt, options=options)


class DeathAction(ActionBase):
    def __init__(self, tamagotchi):
        self.tamagotchi = tamagotchi

    def get_sprites(self):
        return "grave.png", None

    def generate_quote(self):
        death_date = self.tamagotchi.birth_date + timedelta(days=self.tamagotchi.age)
        birth_str = self.tamagotchi.birth_date.strftime("%m/%d/%y");
        death_str = death_date.strftime("%m/%d/%y");
        return f"Rest in peace.\n{birth_str}-{death_str}"


class SleepAction(ActionBase):
    def __init__(self, tamagotchi):
        self.tamagotchi = tamagotchi

    def get_sprites(self):
        sprites = self.tamagotchi.sprite_mappings["sleeping"]
        primary = random.choice(sprites)
        secondary = None
        return primary, secondary

    def generate_quote(self):
        system_prompt = f"""
            You are a tamagotchi. You are currently sleeping.
            Respond with a vague string of words as your dream. Keep the response under 10 words.
            """

        user_prompt = "Zzz"

        options = {
            # crank up the temperature for more creative responses
            "temperature": 3.0,
            "num_predict": MAX_QUOTE_TOKENS,
        }

        return submit_prompt(system_prompt, user_prompt, options=options)


class PoopAction(ActionBase):
    def __init__(self, tamagotchi):
        self.tamagotchi = tamagotchi
        self.mood_action = MoodAction(tamagotchi)

    def get_sprites(self):
        primary, _ = self.mood_action.get_sprites()
        secondary = random.choice(poop_sprites)
        return primary, secondary

    def generate_quote(self):
        system_prompt = """
            You are a tamagotchi.
            Respond concisely about your current action. Keep the response under 10 words.
        """

        user_prompt = "You are currently pooping."

        options = {
            # crank up the temperature for more creative responses
            "temperature": 2.0,
            "num_predict": MAX_QUOTE_TOKENS,
        }

        return submit_prompt(system_prompt, user_prompt, options=options)


class MealAction(ActionBase):
    def __init__(self, tamagotchi, meal, meal_data, start_time, end_time):
        self.tamagotchi = tamagotchi
        self.mood_action = MoodAction(tamagotchi)
        self.start_time = start_time
        self.end_time = end_time
        self.meal = meal
        self.food = meal_data["name"]
        self.sprites = meal_data["sprites"]

    def get_sprites(self):
        primary, _ = self.mood_action.get_sprites()

        # will not work overnight
        now = datetime.now()
        start_time = datetime.combine(datetime.today(), self.start_time)
        end_time = datetime.combine(datetime.today(), self.end_time)
        if now <= start_time:
            return primary, self.sprites[0]

        if now >= end_time:
            return primary, self.sprites[-1]

        span_s = (end_time - start_time).total_seconds()
        prog_s = (now - start_time).total_seconds()
        t = prog_s / span_s
        idx = int(t * len(self.sprites))

        secondary = self.sprites[idx]
        return primary, secondary

    def generate_quote(self):
        system_prompt = """
            You are a tamagotchi.
            Respond creatively about how you feel about your food. Keep the response under 10 words.
        """

        user_prompt = f"You are currently eating {self.food} for {self.meal}"

        options = {
            # crank up the temperature for more creative responses
            "temperature": 2.0,
            "num_predict": MAX_QUOTE_TOKENS,
        }

        return submit_prompt(system_prompt, user_prompt, options=options)


class TaskAction(ActionBase):
    def __init__(self, tamagotchi, task):
        self.tamagotchi = tamagotchi
        self.mood_action = MoodAction(tamagotchi)
        self.task = task

    def get_sprites(self):
        primary, _ = self.mood_action.get_sprites()
        secondary = None
        return primary, secondary

    def generate_quote(self):
        system_prompt = """
            You are a tamagotchi.
            Respond concisely about the task you just completed. Keep the response under 10 words.
        """

        user_prompt = self.task

        options = {
            # crank up the temperature for more creative responses
            "temperature": 1.0,
            "num_predict": MAX_QUOTE_TOKENS,
        }

        return submit_prompt(system_prompt, user_prompt, options=options)


if __name__ == "__main__":
    from tamagotchi import Tamagotchi
    t = Tamagotchi()
    breakfast_start = time(hour=8, minute=00)
    breakfast_end = time(hour=8, minute=15)
    food = random.choice(food_sprites)
    action = MealAction(t, "breakfast", food, breakfast_start, breakfast_end)
    print(action.generate_quote())
    print(action.get_sprites())
