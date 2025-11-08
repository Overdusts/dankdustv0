"""
Helper utility functions
"""

import discord
import random
from typing import Union, Optional, List, Tuple
from discord.ext import commands

from utils.config import Config


def format_number(num: int) -> str:
    """Format a number with commas for readability"""
    return f"{num:,}"


def get_level_xp_requirement(level: int) -> int:
    """Calculate XP required for next level"""
    return level * level * 10 + level * 10 + 10


def calculate_fish_value(size: int) -> int:
    """Calculate the value of a fish based on its size"""
    return round(Config.FISH_BASE_PRICE * (Config.FISH_GROWTH_FACTOR ** (size - 1)))


def get_random_fish() -> Tuple[str, int, int]:
    """
    Get a random fish with weighted probabilities
    Returns: (fish_name, size, value)
    """
    cumulative_prob = []
    total = 0
    
    for fish in Config.FISH_TYPES:
        total += fish[3]
        cumulative_prob.append(total)
        
    roll = random.random()
    
    for i, prob in enumerate(cumulative_prob):
        if roll <= prob:
            fish_name, min_size, max_size, _ = Config.FISH_TYPES[i]
            size = random.randint(min_size, max_size)
            value = calculate_fish_value(size)
            return (fish_name, size, value)
            
    # fallback (shouldn't happen)
    fish_name, min_size, max_size, _ = Config.FISH_TYPES[0]
    size = random.randint(min_size, max_size)
    value = calculate_fish_value(size)
    return (fish_name, size, value)


def get_search_location_loot(location: str) -> Tuple[int, List[Tuple[str, int]]]:
    """
    Roll for loot from a search location
    Returns: (coins, [(item_id, quantity)])
    """
    location_data = Config.SEARCH_LOCATIONS.get(location)
    if not location_data:
        return (0, [])
        
    # base coins
    min_coins, max_coins = location_data['base_coins']
    coins = random.randint(min_coins, max_coins)
    
    # check for special effects
    if location_data.get('special') == 'death' and random.random() < 0.1:
        return (-1, [])  # signal for death (handled in command)
        
    # roll for loot
    loot = []
    for item_id, chance, quantity in location_data.get('loot', []):
        if random.random() < chance:
            loot.append((item_id, quantity))
            
    return (coins, loot)


def roll_loot_box(box_type: str) -> List[Tuple[str, int]]:
    """
    Open a loot box and return items
    Returns: [(item_id, quantity)]
    """
    items = []
    
    if box_type == 'rarelootbox':
        roll = random.random()
        if roll < 0.5:
            pass  # nothing
        elif roll < 0.8:
            items.append(('beard', 1))
        elif roll < 0.95:
            items.append(('sarthak', 1))
        else:
            items.append(('dog', 1))
            
    elif box_type == 'legendarylootbox':
        roll = random.random()
        if roll < 0.5:
            items.append(('sarthak', 1))
        elif roll < 0.8:
            pass  # nothing
        elif roll < 0.95:
            items.append(('sun', 1))
        else:
            items.append(('skull', 1))
            
    elif box_type == 'bestlootbox':
        roll = random.random()
        if roll < 0.3:
            items.append(('skull', 1))
        elif roll < 0.5:
            pass  # nothing
        elif roll < 0.7:
            items.append(('bestlootbox', 2))
        elif roll < 0.8:
            items.append(('banana', 1))
        elif roll < 0.89:
            items.append(('beard', 1))
        else:
            items.append(('bolb', 1))
            
    elif box_type == 'godbox':
        roll = random.random()
        if roll >= 0.5:
            items.append(('enicx', 1))
            
    return items


def create_progress_bar(current: int, maximum: int, length: int = 10) -> str:
    """Create a text-based progress bar"""
    filled = int((current / maximum) * length)
    empty = length - filled
    return f"[{'█' * filled}{'░' * empty}]"


def create_embed(
    title: str,
    description: str = "",
    color: discord.Color = discord.Color.blue(),
    **kwargs
) -> discord.Embed:
    """Create a standardized embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        **kwargs
    )
    return embed


def create_success_embed(title: str, description: str = "") -> discord.Embed:
    """Create a success embed (green)"""
    return create_embed(title, description, discord.Color.green())


def create_error_embed(title: str, description: str = "") -> discord.Embed:
    """Create an error embed (red)"""
    return create_embed(title, description, discord.Color.red())


def create_info_embed(title: str, description: str = "") -> discord.Embed:
    """Create an info embed (blue)"""
    return create_embed(title, description, discord.Color.blue())


def get_item_info(item_id: str) -> Optional[dict]:
    """Get item information from config"""
    return Config.SHOP_ITEMS.get(item_id)


def get_item_description(item_id: str) -> str:
    """Get special description for items"""
    descriptions = {
        'rarelootbox': '**When used:**\n- 50% Chance of nothing\n- 30% Chance of Mohamed ki beard\n- 15% Chance of Sarthak\n- 5% Chance of Doggy',
        'legendarylootbox': '**When used:**\n- 50% Chance of Sarthak\n- 30% Chance of Nothing\n- 15% Chance of Sunny\n- 5% Chance of SKULL SKELETON',
        'bestlootbox': '**When used:**\n- 30% Chance of SKULL SKELETON\n- 20% Chance of nothing\n- 20% Chance of x2 bestlootbox\n- 10% Chance of Xily ka banana\n- 9% Chance of Mohamed ki beard\n- 1% Chance of bolb',
        'banana': '**When used:**\n- Notifies xily u ate his bana (Item not consumed on use)',
        'leash': "**When used:**\n- Times out Robert for 5 minutes. Item consumed on use",
        'kuppy': '**When used:**\n- Mention a user to timeout them for 5 minutes. Item consumed on use',
        'stock': '**When used:**\n- Price changes every 2-5 minutes, maximum is +- 30k. if it goes to 0 all stocks get deleted.',
        'nicx': '**When used:**\n- 1% Chance of transforming into an Enchanted Nicx Crown. 99% Chance of being consumed without transforming.',
        'godbox': '**When used:**\n- 50% Chance of Enchanted Nicx Crown\n- 50% Chance of nothing',
        'tren': '**When used:**\n- Grants a 2x XP boost for 48 hours'
    }
    return descriptions.get(item_id, '')


async def send_with_retry(
    destination: Union[discord.TextChannel, discord.User],
    content: str = None,
    embed: discord.Embed = None,
    retries: int = 3
) -> Optional[discord.Message]:
    """Send a message with retry logic"""
    for attempt in range(retries):
        try:
            return await destination.send(content=content, embed=embed)
        except discord.Forbidden:
            if attempt < retries - 1:
                continue
            else:
                return None
        except Exception as e:
            if attempt < retries - 1:
                continue
            else:
                raise e
    return None


def is_admin(user_id: int) -> bool:
    """Check if user is an admin"""
    return user_id in Config.ADMIN_IDS


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


class ConfirmView(discord.ui.View):
    """Confirmation view with Yes/No buttons"""
    
    def __init__(self, user_id: int, timeout: float = 30.0):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.value = None
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allow the original user to interact"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "This confirmation is not for you!",
                ephemeral=True
            )
            return False
        return True
        
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.defer()
        
    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.defer()


class Paginator(discord.ui.View):
    """Pagination view for embeds"""
    
    def __init__(self, embeds: List[discord.Embed], user_id: int, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.embeds = embeds
        self.user_id = user_id
        self.current_page = 0
        
        # disable buttons if only one page
        if len(embeds) <= 1:
            self.previous_button.disabled = True
            self.next_button.disabled = True
            
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Only allow the original user to interact"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "This paginator is not for you!",
                ephemeral=True
            )
            return False
        return True
        
    def update_buttons(self):
        """Update button states"""
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.embeds) - 1
        
    @discord.ui.button(label="◀", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = max(0, self.current_page - 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        
    @discord.ui.button(label="▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = min(len(self.embeds) - 1, self.current_page + 1)
        self.update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
