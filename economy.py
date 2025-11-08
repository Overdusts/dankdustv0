"""
Economy commands - balance, shop, inventory, etc.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
import time

from utils.config import Config
from utils.helpers import (
    format_number, create_embed, create_success_embed,
    create_error_embed, get_item_info, get_item_description,
    ConfirmView
)


class Economy(commands.Cog):
    """Basic economy commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db
        
    @commands.hybrid_command(name="balance", aliases=["bal"])
    @app_commands.describe(user="The user to check balance for (optional)")
    async def balance(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        """Check your or someone else's balance"""
        target = user or ctx.author
        
        # get balance data
        balance = await self.db.get_balance(target.id)
        net_worth = await self.db.get_net_worth(target.id)
        
        # calculate inventory worth
        inventory_worth = net_worth - balance['wallet']
        
        embed = create_embed(
            title=f"{target.name}'s Balance",
            color=discord.Color.gold()
        )
        embed.add_field(name="💰 Wallet", value=f"⏣ {format_number(balance['wallet'])}", inline=True)
        embed.add_field(name="🏦 Bank", value=f"⏣ {format_number(balance['bank'])}", inline=True)
        embed.add_field(name="📦 Inventory", value=f"⏣ {format_number(inventory_worth)}", inline=True)
        embed.add_field(name="💎 Net Worth", value=f"⏣ {format_number(net_worth)}", inline=False)
        
        await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="shop")
    async def shop(self, ctx: commands.Context):
        """View the shop"""
        embed = create_embed(
            title="🏪 Weltanschauungen ki shop",
            color=discord.Color.blue()
        )
        
        # get current stock price
        stock_price = await self.db.get_stock_price()
        
        description = ""
        for item_id, item_data in Config.SHOP_ITEMS.items():
            if not item_data.get('buyable', True):
                continue
                
            price = item_data['price']
            if item_id == 'stock':
                price = stock_price
                
            description += f"{item_data['name']} | ⏣ {format_number(price)} | `{item_id}`\n"
            
        embed.description = description
        await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="inventory", aliases=["inv"])
    @app_commands.describe(user="The user to check inventory for (optional)")
    async def inventory(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        """View your or someone else's inventory"""
        target = user or ctx.author
        
        inventory = await self.db.get_inventory(target.id)
        
        if not inventory:
            embed = create_error_embed(
                title="Empty Inventory",
                description=f"{target.mention}'s inventory is empty."
            )
            await ctx.send(embed=embed)
            return
            
        # get stock price for calculations
        stock_price = await self.db.get_stock_price()
        
        # calculate values
        items_with_value = []
        total_value = 0
        
        for item_id, quantity in inventory:
            item_info = get_item_info(item_id)
            if not item_info:
                continue
                
            if item_id == 'stock':
                price = stock_price
            else:
                price = item_info['price']
                
            item_value = price * quantity
            items_with_value.append((item_info['name'], quantity, item_value))
            total_value += item_value
            
        # sort by value
        items_with_value.sort(key=lambda x: x[2], reverse=True)
        
        embed = create_embed(
            title=f"📦 {target.name}'s Inventory",
            color=discord.Color.blue()
        )
        
        description = ""
        for name, quantity, value in items_with_value:
            description += f"{name} | `{quantity}` | ⏣ {format_number(value)}\n"
            
        description += f"\n**Total Value:** ⏣ {format_number(total_value)}"
        
        embed.description = description
        await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="buy")
    @app_commands.describe(
        item="The item ID to buy",
        amount="How many to buy"
    )
    async def buy(self, ctx: commands.Context, item: str, amount: int = 1):
        """Buy items from the shop"""
        item = item.lower()
        
        # validate item
        item_info = get_item_info(item)
        if not item_info:
            await ctx.send(embed=create_error_embed("Invalid Item", "That item doesn't exist!"))
            return
            
        if not item_info.get('buyable', True):
            await ctx.send(embed=create_error_embed("Not Buyable", "That item is not available for purchase!"))
            return
            
        if amount <= 0:
            await ctx.send(embed=create_error_embed("Invalid Amount", "Amount must be positive!"))
            return
            
        # get price
        if item == 'stock':
            price = await self.db.get_stock_price()
            if price < Config.STOCK_MIN_BUY_PRICE:
                await ctx.send(embed=create_error_embed(
                    "Stock Too Low",
                    f"You can't buy stocks when the price is below ⏣{format_number(Config.STOCK_MIN_BUY_PRICE)}!"
                ))
                return
        else:
            price = item_info['price']
            
        total_price = price * amount
        
        # check balance
        balance = await self.db.get_balance(ctx.author.id)
        if balance['wallet'] < total_price:
            await ctx.send(embed=create_error_embed(
                "Insufficient Funds",
                f"You need ⏣{format_number(total_price)} but only have ⏣{format_number(balance['wallet'])}!"
            ))
            return
            
        # confirmation
        view = ConfirmView(ctx.author.id)
        confirm_msg = await ctx.send(
            embed=create_embed(
                title="Confirm Purchase",
                description=f"Buy **{amount}x {item_info['name']}** for ⏣{format_number(total_price)}?",
                color=discord.Color.orange()
            ),
            view=view
        )
        
        await view.wait()
        
        if view.value is None:
            await confirm_msg.edit(
                embed=create_error_embed("Timeout", "Purchase confirmation timed out."),
                view=None
            )
            return
            
        if not view.value:
            await confirm_msg.edit(
                embed=create_error_embed("Cancelled", "Purchase cancelled."),
                view=None
            )
            return
            
        # double check balance
        balance = await self.db.get_balance(ctx.author.id)
        if balance['wallet'] < total_price:
            await confirm_msg.edit(
                embed=create_error_embed("Insufficient Funds", "You don't have enough coins anymore!"),
                view=None
            )
            return
            
        # process purchase
        await self.db.remove_coins(ctx.author.id, total_price)
        await self.db.add_item(ctx.author.id, item, amount)
        await self.db.log_transaction(ctx.author.id, f"Bought {amount}x {item}", -total_price)
        
        await confirm_msg.edit(
            embed=create_success_embed(
                "Purchase Complete",
                f"You bought **{amount}x {item_info['name']}** for ⏣{format_number(total_price)}!"
            ),
            view=None
        )
        
    @commands.hybrid_command(name="sell")
    @app_commands.describe(
        item="The item ID to sell",
        amount="How many to sell"
    )
    async def sell(self, ctx: commands.Context, item: str, amount: int = 1):
        """Sell items to the shop"""
        item = item.lower()
        
        # validate item
        item_info = get_item_info(item)
        if not item_info:
            await ctx.send(embed=create_error_embed("Invalid Item", "That item doesn't exist!"))
            return
            
        if not item_info.get('sellable', True):
            await ctx.send(embed=create_error_embed("Not Sellable", "That item cannot be sold!"))
            return
            
        if amount <= 0:
            await ctx.send(embed=create_error_embed("Invalid Amount", "Amount must be positive!"))
            return
            
        # check inventory
        quantity = await self.db.get_item_quantity(ctx.author.id, item)
        if quantity < amount:
            await ctx.send(embed=create_error_embed(
                "Insufficient Items",
                f"You only have {quantity}x {item_info['name']}!"
            ))
            return
            
        # get price
        if item == 'stock':
            price = await self.db.get_stock_price()
        else:
            price = item_info['price']
            
        total_price = price * amount
        
        # confirmation
        view = ConfirmView(ctx.author.id)
        confirm_msg = await ctx.send(
            embed=create_embed(
                title="Confirm Sale",
                description=f"Sell **{amount}x {item_info['name']}** for ⏣{format_number(total_price)}?",
                color=discord.Color.orange()
            ),
            view=view
        )
        
        await view.wait()
        
        if view.value is None:
            await confirm_msg.edit(
                embed=create_error_embed("Timeout", "Sale confirmation timed out."),
                view=None
            )
            return
            
        if not view.value:
            await confirm_msg.edit(
                embed=create_error_embed("Cancelled", "Sale cancelled."),
                view=None
            )
            return
            
        # double check quantity
        quantity = await self.db.get_item_quantity(ctx.author.id, item)
        if quantity < amount:
            await confirm_msg.edit(
                embed=create_error_embed("Insufficient Items", "You don't have enough items anymore!"),
                view=None
            )
            return
            
        # process sale
        await self.db.remove_item(ctx.author.id, item, amount)
        await self.db.add_coins(ctx.author.id, total_price)
        await self.db.log_transaction(ctx.author.id, f"Sold {amount}x {item}", total_price)
        
        await confirm_msg.edit(
            embed=create_success_embed(
                "Sale Complete",
                f"You sold **{amount}x {item_info['name']}** for ⏣{format_number(total_price)}!"
            ),
            view=None
        )
        
    @commands.hybrid_command(name="item")
    @app_commands.describe(item="The item ID to view")
    async def item(self, ctx: commands.Context, item: str):
        """View information about an item"""
        item = item.lower()
        
        item_info = get_item_info(item)
        if not item_info:
            await ctx.send(embed=create_error_embed("Invalid Item", "That item doesn't exist!"))
            return
            
        # get price
        if item == 'stock':
            price = await self.db.get_stock_price()
        else:
            price = item_info['price']
            
        # get user quantity
        quantity = await self.db.get_item_quantity(ctx.author.id, item)
        total_worth = price * quantity
        
        embed = create_embed(
            title="Item Information",
            color=discord.Color.blue()
        )
        
        description = f"**{item_info['name']}** `{item}`\n"
        description += f"Price: **⏣{format_number(price)}**\n"
        description += f"Sellable? `{'yes' if item_info.get('sellable', True) else 'no'}`\n"
        description += f"Buyable? `{'yes' if item_info.get('buyable', True) else 'no'}`\n"
        description += f"You own: `{quantity}`\n"
        description += f"Worth: `⏣{format_number(total_worth)}`\n"
        
        # add special description
        special_desc = get_item_description(item)
        if special_desc:
            description += f"\n{special_desc}"
            
        embed.description = description
        await ctx.send(embed=embed)
        
    @commands.hybrid_command(name="pay", aliases=["give"])
    @app_commands.describe(
        user="The user to pay",
        amount="Amount to pay",
        item="Optional: item ID to pay (default: coins)"
    )
    async def pay(self, ctx: commands.Context, user: discord.Member, amount: int, item: Optional[str] = None):
        """Pay coins or items to another user"""
        if user == ctx.author:
            await ctx.send(embed=create_error_embed("Invalid Target", "You can't pay yourself!"))
            return
            
        if user.bot:
            await ctx.send(embed=create_error_embed("Invalid Target", "You can't pay bots!"))
            return
            
        if amount <= 0:
            await ctx.send(embed=create_error_embed("Invalid Amount", "Amount must be positive!"))
            return
            
        if item:
            # paying items
            item = item.lower()
            item_info = get_item_info(item)
            
            if not item_info:
                await ctx.send(embed=create_error_embed("Invalid Item", "That item doesn't exist!"))
                return
                
            # check quantity
            quantity = await self.db.get_item_quantity(ctx.author.id, item)
            if quantity < amount:
                await ctx.send(embed=create_error_embed(
                    "Insufficient Items",
                    f"You only have {quantity}x {item_info['name']}!"
                ))
                return
                
            # confirmation
            view = ConfirmView(ctx.author.id)
            confirm_msg = await ctx.send(
                embed=create_embed(
                    title="Confirm Payment",
                    description=f"Pay **{amount}x {item_info['name']}** to {user.mention}?",
                    color=discord.Color.orange()
                ),
                view=view
            )
            
            await view.wait()
            
            if view.value is None:
                await confirm_msg.edit(
                    embed=create_error_embed("Timeout", "Payment confirmation timed out."),
                    view=None
                )
                return
                
            if not view.value:
                await confirm_msg.edit(
                    embed=create_error_embed("Cancelled", "Payment cancelled."),
                    view=None
                )
                return
                
            # process transfer
            await self.db.remove_item(ctx.author.id, item, amount)
            await self.db.add_item(user.id, item, amount)
            
            await confirm_msg.edit(
                embed=create_success_embed(
                    "Payment Complete",
                    f"{ctx.author.mention} paid {user.mention} **{amount}x {item_info['name']}**!"
                ),
                view=None
            )
        else:
            # paying coins
            balance = await self.db.get_balance(ctx.author.id)
            if balance['wallet'] < amount:
                await ctx.send(embed=create_error_embed(
                    "Insufficient Funds",
                    f"You only have ⏣{format_number(balance['wallet'])}!"
                ))
                return
                
            # confirmation
            view = ConfirmView(ctx.author.id)
            confirm_msg = await ctx.send(
                embed=create_embed(
                    title="Confirm Payment",
                    description=f"Pay **⏣{format_number(amount)}** to {user.mention}?",
                    color=discord.Color.orange()
                ),
                view=view
            )
            
            await view.wait()
            
            if view.value is None:
                await confirm_msg.edit(
                    embed=create_error_embed("Timeout", "Payment confirmation timed out."),
                    view=None
                )
                return
                
            if not view.value:
                await confirm_msg.edit(
                    embed=create_error_embed("Cancelled", "Payment cancelled."),
                    view=None
                )
                return
                
            # process transfer
            await self.db.remove_coins(ctx.author.id, amount)
            await self.db.add_coins(user.id, amount)
            await self.db.log_transaction(ctx.author.id, f"Paid {user.name}", -amount)
            await self.db.log_transaction(user.id, f"Received from {ctx.author.name}", amount)
            
            await confirm_msg.edit(
                embed=create_success_embed(
                    "Payment Complete",
                    f"{ctx.author.mention} paid {user.mention} **⏣{format_number(amount)}**!"
                ),
                view=None
            )


async def setup(bot):
    await bot.add_cog(Economy(bot))
