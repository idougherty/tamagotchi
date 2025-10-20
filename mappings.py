from datetime import time, datetime, UTC
import random
from abc import ABC, abstractmethod

poop_sprites = ["poop-1.png", "poop-2.png"]

food_sprites = [
    {
        "name": "bread",
        "sprites": [
            "bread-1.png",
            "bread-2.png",
            "bread-3.png",
        ],
    },
    {
        "name": "burger",
        "sprites": [
            "burger-1.png",
            "burger-2.png",
            "burger-3.png",
        ],
    },
    {
        "name": "cake",
        "sprites": [
            "cake-1.png",
            "cake-2.png",
        ],
    },
    {
        "name": "candy",
        "sprites": [
            "candy-1.png",
            "candy-2.png",
            "candy-3.png",
        ],
    },
    {
        "name": "rice",
        "sprites": [
            "rice-1.png",
            "rice-2.png",
            "rice-3.png",
        ],
    },
    {
        "name": "rice-ball",
        "sprites": [
            "rice-ball-1.png",
            "rice-ball-2.png",
            "rice-ball-3.png",
        ],
    }
]


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

