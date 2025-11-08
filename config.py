"""
Configuration management for the bot
"""

import os
from typing import List, Optional


class Config:
    """Bot configuration loaded from environment variables"""
    
    # discord settings
    PREFIX: str = os.getenv('PREFIX', ',')
    GUILD_ID: Optional[int] = int(os.getenv('GUILD_ID')) if os.getenv('GUILD_ID') else None
    
    # admin settings
    ADMIN_IDS: List[int] = [
        int(id.strip()) 
        for id in os.getenv('ADMIN_IDS', '').split(',') 
        if id.strip()
    ]
    
    # lottery settings
    LOTTERY_CHANNEL_ID: Optional[int] = int(os.getenv('LOTTERY_CHANNEL_ID')) if os.getenv('LOTTERY_CHANNEL_ID') else None
    LOTTERY_TICKET_PRICE: int = 10000
    LOTTERY_INITIAL_POOL: int = 100000
    LOTTERY_DURATION: int = 3600  # 1 hour in seconds
    
    # stock market settings
    STOCK_WEBHOOK_URL: Optional[str] = os.getenv('STOCK_WEBHOOK_URL')
    STOCK_UPDATE_MIN: int = int(os.getenv('STOCK_UPDATE_MIN_SECONDS', '120'))
    STOCK_UPDATE_MAX: int = int(os.getenv('STOCK_UPDATE_MAX_SECONDS', '300'))
    STOCK_INITIAL_PRICE: int = 100000
    STOCK_MAX_CHANGE: int = 30000
    STOCK_MIN_BUY_PRICE: int = 10000
    
    # game settings
    DEFAULT_COOLDOWN: int = int(os.getenv('DEFAULT_COOLDOWN', '60'))
    MAX_BET_AMOUNT: int = int(os.getenv('MAX_BET_AMOUNT', '500000000000'))
    
    # database
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///economy.db')
    
    # shop items with prices and properties
    SHOP_ITEMS = {
        'beard': {
            'name': ':man_beard: Mohamed ki beard',
            'price': 10000,
            'id': 'beard',
            'buyable': True,
            'sellable': True
        },
        'sarthak': {
            'name': ':troll: Sarthak',
            'price': 100000,
            'id': 'sarthak',
            'buyable': True,
            'sellable': True
        },
        'dog': {
            'name': '🐶 Doggy',
            'price': 300000,
            'id': 'dog',
            'buyable': True,
            'sellable': True
        },
        'sun': {
            'name': '🌞 Sunny',
            'price': 500000,
            'id': 'sun',
            'buyable': True,
            'sellable': True
        },
        'skull': {
            'name': '<:SKULL_SKELETON:1247908834861777017> SKULL SKELETON',
            'price': 1000000,
            'id': 'skull',
            'buyable': True,
            'sellable': True
        },
        'banana': {
            'name': '🍌 Xily ka banana',
            'price': 10000000,
            'id': 'banana',
            'buyable': True,
            'sellable': True
        },
        'bone': {
            'name': ':bone: Bone',
            'price': 5000,
            'id': 'bone',
            'buyable': False,
            'sellable': True
        },
        'leash': {
            'name': ":service_dog: Robert's Leash",
            'price': 25000,
            'id': 'leash',
            'buyable': False,
            'sellable': True
        },
        'dogfood': {
            'name': ':canned_food: Dog Food',
            'price': 100000,
            'id': 'dogfood',
            'buyable': False,
            'sellable': True
        },
        'rarelootbox': {
            'name': ':gift: Rare Loot Box',
            'price': 5000,
            'id': 'rarelootbox',
            'buyable': False,
            'sellable': True
        },
        'legendarylootbox': {
            'name': ':gift: Legendary Loot Box',
            'price': 100000,
            'id': 'legendarylootbox',
            'buyable': False,
            'sellable': True
        },
        'bestlootbox': {
            'name': ':gift: Best Loot Box',
            'price': 4000000,
            'id': 'bestlootbox',
            'buyable': False,
            'sellable': True
        },
        'bolb': {
            'name': ':red_circle: bolb',
            'price': 50000000,
            'id': 'bolb',
            'buyable': False,
            'sellable': True
        },
        'dupe': {
            'name': ':man_technologist: Dupe Hunter',
            'price': 2500000,
            'id': 'dupe',
            'buyable': False,
            'sellable': True
        },
        'kuppy': {
            'name': ':dog2: Kuppy',
            'price': 50000,
            'id': 'kuppy',
            'buyable': False,
            'sellable': True
        },
        'grass': {
            'name': ':island: Grass',
            'price': 200000,
            'id': 'grass',
            'buyable': False,
            'sellable': True
        },
        'pyramid': {
            'name': '<:pyramid:1247931115763925082> Mohameds Pyramid',
            'price': 911000,
            'id': 'pyramid',
            'buyable': True,
            'sellable': True
        },
        'nicx': {
            'name': '<a:nicxcrown:1247935115900751933> Nicx Crown',
            'price': 1000000,
            'id': 'nicx',
            'buyable': False,
            'sellable': True
        },
        'enicx': {
            'name': '<a:enicxcrown:1247935144489386094> Enchanted Nicx Crown',
            'price': 75000000,
            'id': 'enicx',
            'buyable': False,
            'sellable': True
        },
        'deepsegirl': {
            'name': ":girl: Deep's Egirl",
            'price': 10,
            'id': 'deepsegirl',
            'buyable': False,
            'sellable': True
        },
        'godbox': {
            'name': '<:godbox:1247980941310427157> God Box',
            'price': 40000000,
            'id': 'godbox',
            'buyable': True,
            'sellable': True
        },
        'stock': {
            'name': ':scroll: Stock',
            'price': None,  # dynamic pricing
            'id': 'stock',
            'buyable': True,
            'sellable': True
        },
        'duck': {
            'name': ':swan: wise duck',
            'price': 25000,
            'id': 'duck',
            'buyable': False,
            'sellable': True
        },
        'cat': {
            'name': "<a:weltan:1249106180677308466> weltan's cat",
            'price': 25000000,
            'id': 'cat',
            'buyable': False,
            'sellable': True
        },
        'temple': {
            'name': ":hindu_temple: sid's temple",
            'price': 300000,
            'id': 'temple',
            'buyable': False,
            'sellable': True
        },
        'tren': {
            'name': "<:tren:1249596585961324545> sunny's tren",
            'price': 100000000,
            'id': 'tren',
            'buyable': False,
            'sellable': True
        }
    }
    
    # search locations with their loot tables
    SEARCH_LOCATIONS = {
        'outside': {
            'description': 'Outside area',
            'base_coins': (500, 5000),
            'loot': [
                ('sun', 0.05, 1)  # 5% chance for sunny
            ]
        },
        'mohamedhouse': {
            'description': "Mohamed's house",
            'base_coins': (500, 5000),
            'loot': [
                ('beard', 0.20, 1),
                ('legendarylootbox', 0.05, 1),
                ('pyramid', 0.04, 1)
            ]
        },
        'mountain': {
            'description': 'A tall mountain',
            'base_coins': (500, 5000),
            'loot': [
                ('rarelootbox', 0.20, 1)
            ]
        },
        'street': {
            'description': 'City street',
            'base_coins': (500, 5000),
            'loot': []
        },
        'dog': {
            'description': 'Dog park',
            'base_coins': (500, 5000),
            'loot': [
                ('bestlootbox', 0.01, 1),
                ('kuppy', 0.05, 1)
            ]
        },
        'grass': {
            'description': 'Grassy field',
            'base_coins': (500, 5000),
            'loot': [
                ('grass', 0.02, 1)
            ]
        },
        'pyramid': {
            'description': 'Ancient pyramid',
            'base_coins': (500, 5000),
            'loot': [
                ('pyramid', 0.02, 1),
                ('nicx', 0.02, 1)
            ]
        },
        'gbroad': {
            'description': 'GB Road (risky!)',
            'base_coins': (500, 5000),
            'loot': [
                ('sun', 0.01, 1),
                ('bestlootbox', 0.01, 1),
                ('nicx', 0.01, 1)
            ]
        },
        'delhi': {
            'description': 'Delhi (very risky!)',
            'base_coins': (500, 5000),
            'special': 'death',  # 10% chance to lose half wallet
            'loot': [
                ('sun', 0.10, 1)
            ]
        },
        'fighthub': {
            'description': 'Fight hub arena',
            'base_coins': (500, 5000),
            'loot': [
                ('deepsegirl', 0.30, 1),
                ('beard', 0.10, 1),
                ('rarelootbox', 0.01, 1),
                ('legendarylootbox', 0.01, 1),
                ('bestlootbox', 0.01, 1)
            ]
        }
    }
    
    # fish types with size ranges and spawn rates
    FISH_TYPES = [
        ('🐠 Clownfish', 2, 4, 0.30),
        ('🐡 Pufferfish', 4, 8, 0.25),
        ('🐟 Trout', 20, 30, 0.20),
        ('🐢 Sea Turtle', 24, 48, 0.10),
        ('🐠 Sailfish', 60, 84, 0.07),
        ('🦈 Shark', 72, 240, 0.05),
        ('🐬 Dolphin', 72, 144, 0.025),
        ('🐋 Blue Whale', 840, 1080, 0.0025)
    ]
    
    FISH_BASE_PRICE = 100
    FISH_GROWTH_FACTOR = 1.0073
    
    # level rewards
    LEVEL_REWARDS = {
        1: {'coins': 50000},
        3: {'coins': 100000},
        5: {'items': [('grass', 1)]},
        8: {'items': [('nicx', 1)]},
        10: {'items': [('bestlootbox', 2)]},
        12: {'items': [('kuppy', 10), ('bestlootbox', 2), ('nicx', 1)]},
        14: {'items': [('banana', 1)]},
        15: {'items': [('godbox', 1)]},
        17: {'items': [('bolb', 1)]},
        18: {'items': [('godbox', 2)]},
        19: {'items': [('enicx', 1)]},
        20: {'coins': 50000000, 'items': [('bolb', 1)]},
        21: {'coins': 25000000, 'items': [('tren', 1)]}
    }
    
    @classmethod
    def get_level_reward_coins(cls, level: int) -> int:
        """Calculate scaling rewards for levels 22+"""
        if level < 22:
            return 0
        return int(150000000 * (1.2 ** (level - 21)))
