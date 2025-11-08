"""
Grinding commands - beg, search, fetch, fish, hunt, etc.
"""

import discord
from discord import app_commands
from discord.ext import commands
import random
import time
import asyncio

from utils.config import Config
from utils.helpers import (
    format_number, create_success_embed, create_error_embed,
    get_random_fish, get_search_location_loot, get_item_info
)


class Grinding(commands.Cog):
    """Commands for grinding coins and items"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.owners = ['sid', 'sunny', 'robert', 'nicx', 'deep', 'mohamed', 'weltan', 'xily']
        
    async def check_cooldown(self, user_id: int, command: str, cooldown_seconds: int) -> tuple[bool, float]:
        """Check if user is on cooldown. Returns (on_cooldown, remaining_time)"""
        last_use = await self.db.get_cooldown(user_id, command)
        current_time = time.time()
        
        if current_time < last_use:
            return (True, last_use - current_time)
        return (False, 0)
        
    @commands.hybrid_command(name="beg")
    async def beg(self, ctx: commands.Context):
        """Beg for coins"""
        # check cooldown
        on_cooldown, remaining = await self.check_cooldown(ctx.author.id, 'beg', 60)
        if on_cooldown:
            await ctx.send(embed=create_error_embed(
                "Cooldown",
                f"You can use this command again in {int(remaining)} seconds."
            ))
            return
            
        # set cooldown
        await self.db.set_cooldown(ctx.author.id, 'beg', time.time() + 60)
        
        # roll for success (75% chance)
        if random.random() < 0.75:
            amount = random.randint(1000, 10000)
            owner = random.choice(self.owners)
            
            await self.db.add_coins(ctx.author.id, amount)
            await self.db.log_transaction(ctx.author.id, "Begged", amount)
            
            await ctx.send(embed=create_success_embed(
                "Success!",
                f"You begged so hard and {owner} gave you **⏣{format_number(amount)}**!"
            ))
        else:
            await ctx.send(embed=create_error_embed(
                "Failed",
                "Your begging attempt was unsuccessful. Better luck next time!"
            ))
            
    @commands.hybrid_command(name="search")
    async def search(self, ctx: commands.Context):
        """Search locations for coins and items"""
        # check cooldown
        on_cooldown, remaining = await self.check_cooldown(ctx.author.id, 'search', 60)
        if on_cooldown:
            await ctx.send(embed=create_error_embed(
                "Cooldown",
                f"You can use this command again in {int(remaining)} seconds."
            ))
            return
            
        # get random locations
        all_locations = list(Config.SEARCH_LOCATIONS.keys())
        locations = random.sample(all_locations, min(2, len(all_locations)))
        
        # send location selection
        location_text = "\n".join([f"`{loc}`" for loc in locations])
        msg = await ctx.send(embed=create_success_embed(
            "Search Locations",
            f"Where do you want to search?\n{location_text}"
        ))
        
        # wait for response
        def check(m):
            return m.author == ctx.author and m.content.lower() in locations
            
        try:
            response = await self.bot.wait_for('message', check=check, timeout=30)
        except asyncio.TimeoutError:
            await msg.edit(embed=create_error_embed("Timeout", "Search location selection timed out."))
            return
            
        location = response.content.lower()
        
        # set cooldown now
        await self.db.set_cooldown(ctx.author.id, 'search', time.time() + 60)
        
        # get loot
        coins, loot = get_search_location_loot(location)
        
        # special case: death in delhi
        if coins == -1:
            balance = await self.db.get_balance(ctx.author.id)
            coins_lost = balance['wallet'] // 2
            await self.db.remove_coins(ctx.author.id, coins_lost)
            
            await ctx.send(embed=create_error_embed(
                "Death!",
                f"You got raped and died in delhi and lost **⏣{format_number(coins_lost)}**!"
            ))
            return
            
        # add coins
        await self.db.add_coins(ctx.author.id, coins)
        await self.db.log_transaction(ctx.author.id, f"Searched {location}", coins)
        
        result_text = f"You searched **{location}** and found **⏣{format_number(coins)}**!"
        
        # add loot
        for item_id, quantity in loot:
            await self.db.add_item(ctx.author.id, item_id, quantity)
            item_info = get_item_info(item_id)
            result_text += f"\nYou also found **{quantity}x {item_info['name']}**!"
            
        await ctx.send(embed=create_success_embed("Search Complete", result_text))
        
    @commands.hybrid_command(name="fetch")
    async def fetch(self, ctx: commands.Context):
        """Fetch like a good doggy for coins and items"""
        # check cooldown
        on_cooldown, remaining = await self.check_cooldown(ctx.author.id, 'fetch', 75)
        if on_cooldown:
            await ctx.send(embed=create_error_embed(
                "Cooldown",
                f"You can use this command again in {int(remaining)} seconds."
            ))
            return
            
        # set cooldown
        await self.db.set_cooldown(ctx.author.id, 'fetch', time.time() + 75)
        
        # base coins
        coins = random.randint(1000, 10000)
        await self.db.add_coins(ctx.author.id, coins)
        await self.db.log_transaction(ctx.author.id, "Fetched", coins)
        
        result_text = f"You fetched like a good doggy and found **⏣{format_number(coins)}**!"
        
        # loot rolls
        roll = random.random()
        if roll < 0.3:
            await self.db.add_item(ctx.author.id, 'bone', 1)
            result_text += "\nYou also found a **:bone: Bone**!"
        elif roll < 0.45:
            await self.db.add_item(ctx.author.id, 'leash', 1)
            result_text += "\nYou also found **:service_dog: Robert's Leash**!"
        elif roll < 0.5:
            await self.db.add_item(ctx.author.id, 'dogfood', 1)
            result_text += "\nYou also found **:canned_food: Dog Food**!"
            
        await ctx.send(embed=create_success_embed("Fetch Complete", result_text))
        
    @commands.hybrid_command(name="fish")
    async def fish(self, ctx: commands.Context):
        """Go fishing for valuable fish"""
        # check cooldown
        on_cooldown, remaining = await self.check_cooldown(ctx.author.id, 'fish', 60)
        if on_cooldown:
            await ctx.send(embed=create_error_embed(
                "Cooldown",
                f"You can use this command again in {int(remaining)} seconds."
            ))
            return
            
        # set cooldown
        await self.db.set_cooldown(ctx.author.id, 'fish', time.time() + 60)
        
        # get random fish
        fish_name, size, value = get_random_fish()
        
        await self.db.add_coins(ctx.author.id, value)
        await self.db.log_transaction(ctx.author.id, "Fished", value)
        
        await ctx.send(embed=create_success_embed(
            "Fishing Success",
            f"You caught a **{fish_name}** ({size} inches) and earned **⏣{format_number(value)}**!"
        ))
        
    @commands.hybrid_command(name="hunt")
    async def hunt(self, ctx: commands.Context):
        """Hunt for coins and items"""
        # check cooldown
        on_cooldown, remaining = await self.check_cooldown(ctx.author.id, 'hunt', 60)
        if on_cooldown:
            await ctx.send(embed=create_error_embed(
                "Cooldown",
                f"You can use this command again in {int(remaining)} seconds."
            ))
            return
            
        # set cooldown
        await self.db.set_cooldown(ctx.author.id, 'hunt', time.time() + 60)
        
        # base coins
        coins = random.randint(500, 5000)
        await self.db.add_coins(ctx.author.id, coins)
        await self.db.log_transaction(ctx.author.id, "Hunted", coins)
        
        result_text = f"You went hunting and earned **⏣{format_number(coins)}**!"
        
        # loot rolls
        roll = random.randint(1, 300)
        if 1 <= roll <= 20:
            await self.db.add_item(ctx.author.id, 'duck', 1)
            result_text += "\nYou also found a **:swan: wise duck**!"
        elif roll == 21:
            await self.db.add_item(ctx.author.id, 'cat', 1)
            result_text += "\nYou also found **<a:weltan:1249106180677308466> weltan's cat**!"
        elif 22 <= roll <= 30:
            await self.db.add_item(ctx.author.id, 'temple', 1)
            result_text += "\nYou also found **:hindu_temple: sid's temple**!"
        elif 31 <= roll <= 40:
            await self.db.add_item(ctx.author.id, 'legendarylootbox', 1)
            result_text += "\nYou also found a **:gift: Legendary loot box**!"
            
        await ctx.send(embed=create_success_embed("Hunt Complete", result_text))
        
    @commands.hybrid_command(name="stake")
    async def stake(self, ctx: commands.Context):
        """Gamble on stake.com for coins and loot boxes"""
        # check cooldown
        on_cooldown, remaining = await self.check_cooldown(ctx.author.id, 'stake', 150)
        if on_cooldown:
            await ctx.send(embed=create_error_embed(
                "Cooldown",
                f"You can use this command again in {int(remaining)} seconds."
            ))
            return
            
        # set cooldown
        await self.db.set_cooldown(ctx.author.id, 'stake', time.time() + 150)
        
        # base coins
        coins = random.randint(500, 5000)
        await self.db.add_coins(ctx.author.id, coins)
        await self.db.log_transaction(ctx.author.id, "Staked", coins)
        
        result_text = f"You gambled on stake.com all night and made **⏣{format_number(coins)}**!"
        
        # loot rolls
        roll = random.random()
        if roll < 0.01:
            await self.db.add_item(ctx.author.id, 'bestlootbox', 1)
            result_text += "\nYou also found a **:gift: Best loot box**!"
        elif roll < 0.05:
            await self.db.add_item(ctx.author.id, 'legendarylootbox', 1)
            result_text += "\nYou also found a **:gift: Legendary loot box**!"
        elif roll < 0.2:
            await self.db.add_item(ctx.author.id, 'rarelootbox', 1)
            result_text += "\nYou also found a **:gift: Rare loot box**!"
            
        await ctx.send(embed=create_success_embed("Stake Complete", result_text))


async def setup(bot):
    await bot.add_cog(Grinding(bot))
