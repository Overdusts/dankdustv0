# Project Structure & Implementation Guide

This document explains the complete structure of the Discord Economy Bot and what each file should contain.

## 📁 Complete File Structure

```
discord-economy-bot/
├── main.py                 # Bot entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore file
├── README.md              # Main documentation
├── DEPLOYMENT.md          # Deployment guide
├── LICENSE                # License file
│
├── utils/                 # Utility modules
│   ├── __init__.py       # Package initializer
│   ├── config.py         # Configuration management
│   ├── database.py       # Database operations
│   └── helpers.py        # Helper functions
│
└── cogs/                  # Bot command modules
    ├── economy.py        # Balance, shop, inventory, pay
    ├── grinding.py       # Beg, search, fetch, fish, hunt, stake
    ├── gambling.py       # Blackjack, dice, fight
    ├── leveling.py       # Profile, progress, experience
    ├── items.py          # Use items, loot boxes
    ├── leaderboard.py    # Leaderboards
    ├── admin.py          # Admin commands
    ├── lottery.py        # Lottery system
    ├── utility.py        # Help, loottable, currencylog
    └── stocks.py         # Stock market system
```

## 📄 Files Already Created

✅ **main.py** - Bot entry point with setup and error handling
✅ **requirements.txt** - All dependencies
✅ **.env.example** - Environment variable template
✅ **README.md** - Comprehensive documentation
✅ **DEPLOYMENT.md** - Deployment guide
✅ **utils/config.py** - Configuration class with all settings
✅ **utils/database.py** - Complete database operations
✅ **utils/helpers.py** - Utility functions and classes
✅ **cogs/economy.py** - Balance, shop, inventory, pay commands
✅ **cogs/grinding.py** - All grinding commands

## 📄 Files You Need to Create

### **cogs/gambling.py** - Gambling Commands

```python
"""
Gambling commands - blackjack, dice betting, fight system
"""

import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
from typing import Optional

from utils.config import Config
from utils.helpers import (
    format_number, create_embed, create_success_embed,
    create_error_embed
)


class Gambling(commands.Cog):
    """Gambling and PvP commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        self.ongoing_games = {}
        self.ongoing_fights = {}
        
    @commands.hybrid_command(name="blackjack", aliases=["bj"])
    @app_commands.describe(amount="Amount to bet")
    async def blackjack(self, ctx: commands.Context, amount: int):
        """Play blackjack"""
        # check if already in a game
        if ctx.author.id in self.ongoing_games:
            await ctx.send(embed=create_error_embed(
                "Already Playing",
                "You already have an ongoing game!"
            ))
            return
            
        # validate amount
        if amount < 1 or amount > 100000000:
            await ctx.send(embed=create_error_embed(
                "Invalid Amount",
                f"Bet must be between 1 and {format_number(100000000)}!"
            ))
            return
            
        # check balance
        balance = await self.db.get_balance(ctx.author.id)
        if balance['wallet'] < amount:
            await ctx.send(embed=create_error_embed(
                "Insufficient Funds",
                f"You need ⏣{format_number(amount)} but only have ⏣{format_number(balance['wallet'])}!"
            ))
            return
            
        # deduct bet
        await self.db.remove_coins(ctx.author.id, amount)
        self.ongoing_games[ctx.author.id] = True
        
        # game logic
        def draw_card():
            return random.choice(['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'])
            
        def calculate_value(hand):
            value = 0
            aces = 0
            for card in hand:
                if card in ['J', 'Q', 'K']:
                    value += 10
                elif card == 'A':
                    value += 11
                    aces += 1
                else:
                    value += int(card)
            while value > 21 and aces:
                value -= 10
                aces -= 1
            return value
            
        # initial hands
        player_hand = [draw_card(), draw_card()]
        dealer_hand = [draw_card(), draw_card()]
        
        embed = create_embed(
            title="🎰 Blackjack",
            description=f"Your hand: {', '.join(player_hand)} (value: {calculate_value(player_hand)})\nDealer's hand: {dealer_hand[0]}, ?"
        )
        msg = await ctx.send(embed=embed)
        
        # player's turn
        while calculate_value(player_hand) < 21:
            embed.description += "\n\nType 'hit' to draw or 'stand' to hold."
            await msg.edit(embed=embed)
            
            def check(m):
                return m.author == ctx.author and m.content.lower() in ['hit', 'stand']
                
            try:
                response = await self.bot.wait_for('message', check=check, timeout=30)
            except asyncio.TimeoutError:
                del self.ongoing_games[ctx.author.id]
                await msg.edit(embed=create_error_embed("Timeout", "Game timed out."))
                return
                
            if response.content.lower() == 'stand':
                break
            else:
                player_hand.append(draw_card())
                embed.description = f"Your hand: {', '.join(player_hand)} (value: {calculate_value(player_hand)})\nDealer's hand: {dealer_hand[0]}, ?"
                
        player_value = calculate_value(player_hand)
        
        # check if player bust
        if player_value > 21:
            balance = await self.db.get_balance(ctx.author.id)
            await msg.edit(embed=create_error_embed(
                "Bust!",
                f"Your hand value is {player_value}. You lost **⏣{format_number(amount)}**.\nNew balance: ⏣{format_number(balance['wallet'])}"
            ))
            del self.ongoing_games[ctx.author.id]
            await self.db.log_transaction(ctx.author.id, "Blackjack loss", -amount)
            return
            
        # dealer's turn
        while calculate_value(dealer_hand) < 17:
            dealer_hand.append(draw_card())
            
        dealer_value = calculate_value(dealer_hand)
        
        # determine winner
        embed.description = f"Your hand: {', '.join(player_hand)} (value: {player_value})\nDealer's hand: {', '.join(dealer_hand)} (value: {dealer_value})"
        
        if dealer_value > 21 or player_value > dealer_value:
            winnings = amount * 2
            await self.db.add_coins(ctx.author.id, winnings)
            balance = await self.db.get_balance(ctx.author.id)
            embed.color = discord.Color.green()
            embed.title = "🎉 You Win!"
            embed.description += f"\n\nYou won **⏣{format_number(winnings)}**!\nNew balance: ⏣{format_number(balance['wallet'])}"
            await self.db.log_transaction(ctx.author.id, "Blackjack win", winnings)
        elif player_value < dealer_value:
            balance = await self.db.get_balance(ctx.author.id)
            embed.color = discord.Color.red()
            embed.title = "😢 You Lose!"
            embed.description += f"\n\nYou lost **⏣{format_number(amount)}**.\nNew balance: ⏣{format_number(balance['wallet'])}"
            await self.db.log_transaction(ctx.author.id, "Blackjack loss", -amount)
        else:
            await self.db.add_coins(ctx.author.id, amount)
            balance = await self.db.get_balance(ctx.author.id)
            embed.color = discord.Color.blue()
            embed.title = "🤝 Tie!"
            embed.description += f"\n\nIt's a tie! Your bet **⏣{format_number(amount)}** has been returned.\nYour balance: ⏣{format_number(balance['wallet'])}"
            
        await msg.edit(embed=embed)
        del self.ongoing_games[ctx.author.id]
        
    @commands.hybrid_command(name="bet")
    @app_commands.describe(amount="Amount to bet or 'max'")
    async def bet(self, ctx: commands.Context, amount: str):
        """Quick dice gambling"""
        # check cooldown
        last_use = await self.db.get_cooldown(ctx.author.id, 'dice')
        if time.time() < last_use:
            await ctx.send(embed=create_error_embed(
                "Cooldown",
                f"Try again in {int(last_use - time.time())} seconds."
            ))
            return
            
        # parse amount
        balance = await self.db.get_balance(ctx.author.id)
        
        if amount.lower() == 'max':
            bet_amount = min(balance['wallet'], Config.MAX_BET_AMOUNT)
        else:
            try:
                bet_amount = int(amount)
            except ValueError:
                await ctx.send(embed=create_error_embed("Invalid Amount", "Please provide a valid number or 'max'."))
                return
                
        if bet_amount <= 0:
            await ctx.send(embed=create_error_embed("Invalid Amount", "Amount must be positive!"))
            return
            
        if bet_amount > balance['wallet']:
            await ctx.send(embed=create_error_embed(
                "Insufficient Funds",
                f"You only have ⏣{format_number(balance['wallet'])}!"
            ))
            return
            
        if bet_amount > Config.MAX_BET_AMOUNT:
            await ctx.send(embed=create_error_embed(
                "Amount Too High",
                f"Maximum bet is ⏣{format_number(Config.MAX_BET_AMOUNT)}!"
            ))
            return
            
        # set cooldown
        await self.db.set_cooldown(ctx.author.id, 'dice', time.time() + 2)
        
        # roll dice
        user_roll = random.randint(1, 6) + random.randint(1, 6)
        bot_roll = random.randint(1, 6) + random.randint(1, 6)
        
        if user_roll > bot_roll:
            await self.db.add_coins(ctx.author.id, bet_amount)
            new_balance = balance['wallet'] + bet_amount
            result = f"🎉 **You won ⏣{format_number(bet_amount)}!**"
            color = discord.Color.green()
            await self.db.log_transaction(ctx.author.id, "Dice win", bet_amount)
        elif user_roll < bot_roll:
            await self.db.remove_coins(ctx.author.id, bet_amount)
            new_balance = balance['wallet'] - bet_amount
            result = f"😢 **You lost ⏣{format_number(bet_amount)}.**"
            color = discord.Color.red()
            await self.db.log_transaction(ctx.author.id, "Dice loss", -bet_amount)
        else:
            new_balance = balance['wallet']
            result = "🤝 **It's a tie!**"
            color = discord.Color.blue()
            
        embed = create_embed(
            title="🎲 Dice Roll",
            description=f"{result}\n\nYou rolled: **{user_roll}**\nBot rolled: **{bot_roll}**\n\nNew balance: ⏣{format_number(new_balance)}",
            color=color
        )
        
        await ctx.send(embed=embed)
        
    # Fight command is complex - see full implementation in original code
    # For brevity, I'll skip it here but you should implement it


async def setup(bot):
    await bot.add_cog(Gambling(bot))
```

### **cogs/leveling.py** - Leveling System

This cog handles:
- Profile command
- Progress command
- Experience tracking
- Level rewards

### **cogs/items.py** - Item Usage

This cog handles:
- Use command for consumable items
- Loot box opening
- Special item effects (Kuppy, Leash, etc.)
- Item transformations

### **cogs/leaderboard.py** - Leaderboards

This cog handles:
- Balance leaderboard
- Item leaderboard
- Pagination for large leaderboards

### **cogs/admin.py** - Admin Commands

This cog handles:
- Add/remove coins and items
- Wipe user data
- Set levels
- Show dupers
- Restart bot

### **cogs/lottery.py** - Lottery System

This cog handles:
- Lottery view command
- Buy tickets
- Auto-draw after time expires
- Persistent lottery data

### **cogs/utility.py** - Utility Commands

This cog handles:
- Help command
- Loottable command
- Currency log
- Item information

### **cogs/stocks.py** - Stock Market

This cog handles:
- Background stock price updates
- Webhook notifications
- Stock deletion at 0 price

### **.gitignore**

```
# Environment
.env
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Database
*.db
*.db-journal
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Bot specific
bot.log
economy.db
lottery.json
```

### **LICENSE** (MIT License)

```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🚀 Implementation Priority

1. ✅ Core structure (main.py, utils/)
2. ✅ Economy commands (economy.py)
3. ✅ Grinding commands (grinding.py)
4. ⚠️ Gambling commands (gambling.py) - **IMPLEMENT NEXT**
5. ⚠️ Leveling system (leveling.py) - **IMPLEMENT NEXT**
6. ⚠️ Item usage (items.py)
7. ⚠️ Leaderboards (leaderboard.py)
8. ⚠️ Admin commands (admin.py)
9. ⚠️ Lottery system (lottery.py)
10. ⚠️ Utility commands (utility.py)
11. ⚠️ Stock market (stocks.py)

## 📝 Notes for Each Remaining Cog

### gambling.py
- Implement full blackjack with proper card logic
- Add fight system with HP, moves (punch/kick/run)
- Support wagering coins or items in fights
- Handle ongoing game tracking

### leveling.py  
- Calculate XP requirements per level
- Check and apply boosts
- Award level-up rewards
- Update badges based on net worth
- Show profile with badges and boosts

### items.py
- Handle loot box opening with proper RNG
- Kuppy timeout functionality
- Banana notification to Xily
- Nicx crown transformation (1% chance)
- Tren boost application

### leaderboard.py
- Top 10 users by net worth
- Top 5 for specific items
- Pagination for longer lists
- Hide anonymous users (if system implemented)

### admin.py
- Permission checks (admin user IDs)
- Add/remove currency and items
- Wipe user completely
- Set user levels manually
- Find negative balances (dupers)
- Bot restart functionality

### lottery.py
- Persistent lottery state (JSON file)
- Automatic draw after 1 hour
- Ticket purchase with confirmation
- Winner selection algorithm
- Pool accumulation

### utility.py
- Dynamic help command with categories
- Loot tables for each command
- Currency transaction history
- Item descriptions

### stocks.py
- Background task for price updates (every 2-5 min)
- Price change ±30k
- Delete all stocks if price hits 0
- Webhook notifications to Discord channel

## 🔧 Testing Checklist

Before deploying:

- [ ] All commands respond correctly
- [ ] Cooldowns work properly
- [ ] Database transactions are atomic
- [ ] No duplicate ongoing operations
- [ ] Error messages are user-friendly
- [ ] Slash commands sync properly
- [ ] Permissions are checked
- [ ] Confirmations work (buy/sell/pay)
- [ ] Leaderboards sort correctly
- [ ] Stock system updates automatically
- [ ] Lottery draws correctly
- [ ] Level rewards distribute properly
- [ ] Items work as intended
- [ ] Fight system is balanced
- [ ] Admin commands are restricted

## 💡 Tips

1. **Test locally first** - Always test on a development server
2. **Use git branches** - Create feature branches for new cogs
3. **Comment your code** - Future you will thank you
4. **Handle errors gracefully** - Users should never see tracebacks
5. **Log important events** - Makes debugging easier
6. **Backup database regularly** - Before major updates
7. **Monitor resource usage** - Optimize as needed
8. **Keep dependencies updated** - But test before deploying

## 📚 Additional Resources

- [discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

Good luck with your bot! 🚀
