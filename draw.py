from PIL import Image, ImageDraw, ImageFont 
from datetime import datetime
import os
import random
import math
from tamagotchi import Tamagotchi
from mappings import get_current_action

MAX_VALUE = 8
SCREEN_W = 480
SCREEN_H = 800

MARGIN = 30
SPRITE_Y = SCREEN_H * 42 // 100
SPRITE_X = SCREEN_W // 2

QUOTE_Y = SCREEN_H * 60 // 100

def draw_text(draw, font, text, pos_x, pos_y, anchor="la", align="left"):
    pos = (pos_x, pos_y)
    color = (0, 0, 0)
    draw.text(pos, text, fill=color, font=font, anchor=anchor, align=align)

def wrap_text(text: str, font: ImageFont.ImageFont,
                     line_length: int):
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            if len(lines) == 4:
                while font.getlength(lines[-1] + '..."') > line_length:
                    lines[-1] = lines[-1][:-1]
                lines[-1] += '..."'
                break
            lines.append(word)
    return '\n'.join(lines)

def scale_sprite(sprite, scale):
    sprite_w, sprite_h = sprite.size
    sprite_w *= scale
    sprite_h *= scale
    return sprite.resize((sprite_w, sprite_h), resample=Image.NEAREST)

def render_tamagotchi(tamagotchi, sprite_primary_path, sprite_secondary_path, quote):
    font_size = 50
    font = ImageFont.truetype("./static/fonts/Tiny5-Regular.ttf", font_size)

    sprite_scale = 15

    sprite_primary = Image.open(sprite_primary_path)
    sprite_primary = scale_sprite(sprite_primary, sprite_scale)

    if sprite_secondary_path is not None:
        sprite_secondary = Image.open(sprite_secondary_path)
        sprite_secondary = scale_sprite(sprite_secondary, sprite_scale)

    im = Image.new(mode="RGB", size=(SCREEN_W, SCREEN_H), color=(255, 255, 255))

    primary_w, primary_h = sprite_primary.size
    if sprite_secondary_path is None:
        primary_pos = (SPRITE_X - primary_w // 2, SPRITE_Y - primary_h // 2)
        im.paste(sprite_primary, primary_pos) 
    else:
        secondary_w, secondary_h = sprite_secondary.size
        spacing = (primary_w + secondary_w) // 2 + 20
        secondary_y = SPRITE_Y + primary_h // 2 - secondary_h

        primary_pos = (SPRITE_X - spacing // 2 - primary_w // 2, SPRITE_Y - primary_h // 2)
        secondary_pos = (SPRITE_X + spacing // 2 - secondary_w // 2, secondary_y)
        im.paste(sprite_primary, primary_pos) 
        im.paste(sprite_secondary, secondary_pos) 

    draw = ImageDraw.Draw(im)

    pos_y = 20
    draw_text(draw, font, f"mind: {round(tamagotchi.mind)}/{MAX_VALUE}", MARGIN, MARGIN + 0 * font_size)
    draw_text(draw, font, f"body: {round(tamagotchi.body)}/{MAX_VALUE}", MARGIN, MARGIN + 1 * font_size)
    draw_text(draw, font, f"soul: {round(tamagotchi.soul)}/{MAX_VALUE}", MARGIN, MARGIN + 2 * font_size)

    draw_text(draw, font, f"care: {tamagotchi.get_care_grade()}", SCREEN_W // 2 + MARGIN, MARGIN + 0 * font_size)
    draw_text(draw, font, f"age: {tamagotchi.age}", SCREEN_W // 2 + MARGIN, MARGIN + 1 * font_size)

    now = datetime.now()
    time = now.strftime("%I:%M%p");
    date = now.strftime("%a %m/%d")

    draw_text(draw, font, time, MARGIN, SCREEN_H - MARGIN, anchor="ld")
    draw_text(draw, font, date, SCREEN_W - MARGIN, SCREEN_H - MARGIN, anchor="rd")

    quote = f"\"{quote}\""
    wrap_quote = wrap_text(quote, font, SCREEN_W - 60)
    draw_text(draw, font, wrap_quote, MARGIN, QUOTE_Y, anchor="la")

    return im

if __name__ == "__main__":
    t = Tamagotchi()
    t.mind = random.random() * 8
    t.body = random.random() * 8
    t.soul = random.random() * 8
    t.age = int(random.random() * 30)
    t.care_score = random.random()
    sprite = t.get_sprite()
    quote = "Testing..."#t.generate_quote()
    now = datetime.now()
    now = now.replace(hour=random.randint(0,23), minute=random.randint(0, 59))
    print(now)
    print(get_current_action(now))
    im = render_tamagotchi(t, sprite, "images/rice-2.png", quote)
    im.show()
