from PIL import Image, ImageDraw, ImageFont 
from datetime import datetime
import os
import random
import math
from tamagotchi import Tamagotchi

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

def render_tamagotchi(tamagotchi, sprite_path, quote):
    font_size = 50
    font = ImageFont.truetype("./static/fonts/Tiny5-Regular.ttf", font_size)

    sprite_scale = 15
    sprite = Image.open(sprite_path)
    sprite_w, sprite_h = sprite.size
    sprite_w *= sprite_scale
    sprite_h *= sprite_scale
    sprite = sprite.resize((sprite_w, sprite_h), resample=Image.NEAREST)

    im = Image.new(mode="RGB", size=(SCREEN_W, SCREEN_H), color=(255, 255, 255))
    sprite_pos = (SPRITE_X - sprite_w // 2, SPRITE_Y - sprite_h // 2)
    im.paste(sprite, sprite_pos) 

    draw = ImageDraw.Draw(im)

    pos_y = 20
    draw_text(draw, font, f"mind: {math.ceil(tamagotchi.mind)}/{MAX_VALUE}", MARGIN, MARGIN + 0 * font_size)
    draw_text(draw, font, f"body: {math.ceil(tamagotchi.body)}/{MAX_VALUE}", MARGIN, MARGIN + 1 * font_size)
    draw_text(draw, font, f"soul: {math.ceil(tamagotchi.soul)}/{MAX_VALUE}", MARGIN, MARGIN + 2 * font_size)

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

t = Tamagotchi()
t.mind = random.random() * 8
t.body = random.random() * 8
t.soul = random.random() * 8
t.age = int(random.random() * 30)
t.care_score = random.random()
sprite = f"images/{t.get_sprite()}.png"
quote = t.generate_quote()
im = render_tamagotchi(t, sprite, quote)
im.show()
