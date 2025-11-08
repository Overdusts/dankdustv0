# Discord Economy Bot

A feature-rich Discord economy bot with leveling, gambling, fighting, stock market, lottery system, and more!

## Features

### 💰 Economy System
- **Wallet & Bank**: Store and manage your coins
- **Inventory System**: Collect and trade items
- **Net Worth Tracking**: Track your total wealth
- **Currency Logging**: Audit trail for all transactions

### 🎮 Gambling & Games
- **Blackjack**: Classic card game with betting
- **Dice Betting**: Roll dice against the bot
- **Stake**: Gamble for loot boxes and coins
- **Fighting System**: Wager coins or items in PvP battles
- **Lottery**: Enter tickets for a chance to win the jackpot

### 📈 Progression
- **Leveling System**: Gain XP from using commands
- **Rebirth System**: Prestige for additional rewards
- **Level Rewards**: Unlock items and coins as you level up
- **XP Boosts**: Temporary multipliers for faster leveling
- **Badges**: Earn special badges for achievements

### 🎣 Grinding Commands
- **Beg**: Simple way to earn starting coins
- **Search**: Find coins and items in different locations
- **Fetch**: Retrieve items like a good doggy
- **Fish**: Catch fish of varying sizes and values
- **Hunt**: Hunt for coins and rare items

### 🏪 Shop & Trading
- **Dynamic Shop**: Buy items with varying prices
- **Stock Market**: Invest in stocks with fluctuating prices
- **Item Trading**: Pay other users with coins or items
- **Item Usage**: Use consumable items for effects

### 🛠️ Admin Tools
- **User Management**: Add/remove coins and items
- **Leaderboards**: View top users (public & admin)
- **Wipe Command**: Reset user data
- **Level Management**: Set user levels manually
- **Dupe Detection**: Find users with negative balances

## Setup

### Prerequisites
- Python 3.9 or higher
- Discord Bot Token ([Get one here](https://discord.com/developers/applications))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/discord-economy-bot.git
cd discord-economy-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure the bot**
```bash
cp .env.example .env
```

Edit `.env` and add your bot token:
```env
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_guild_id_here
```

4. **Run the bot**
```bash
python main.py
```

## Configuration

### Environment Variables

- `DISCORD_TOKEN`: Your Discord bot token (required)
- `GUILD_ID`: Your Discord server ID for slash command sync (optional)
- `PREFIX`: Command prefix (default: `,`)
- `ADMIN_IDS`: Comma-separated list of admin user IDs

### Database

The bot uses SQLite by default. The database file `economy.db` will be created automatically on first run.

## Commands

### Economy Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `bal` / `/balance` | Check your balance | `bal [@user]` |
| `pay` / `/pay` | Send coins/items to someone | `pay @user 1000` |
| `inv` / `/inventory` | View your inventory | `inv [@user]` |
| `shop` / `/shop` | Browse the shop | `shop` |
| `buy` / `/buy` | Purchase items | `buy <item> <amount>` |
| `sell` / `/sell` | Sell items | `sell <item> <amount>` |
| `item` / `/item` | View item details | `item <item_id>` |
| `use` / `/use` | Use an item | `use <item> [amount]` |

### Grinding Commands

| Command | Description | Cooldown |
|---------|-------------|----------|
| `beg` / `/beg` | Beg for coins | 60s |
| `search` / `/search` | Search locations for loot | 60s |
| `fetch` / `/fetch` | Fetch like a dog | 75s |
| `fish` / `/fish` | Go fishing | 60s |
| `hunt` / `/hunt` | Hunt for rewards | 60s |

### Gambling Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `bj` / `/blackjack` | Play blackjack | `bj 1000` |
| `bet` / `/bet` | Dice gambling | `bet 1000` or `bet max` |
| `stake` / `/stake` | Stake gambling | `stake` |
| `fight` / `/fight` | Challenge someone | `fight @user [wager]` |
| `lottery` / `/lottery` | View/enter lottery | `lottery buy 10` |

### Progression Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `profile` / `/profile` | View your profile | `profile [@user]` |
| `progress` / `/progress` | Check level progress | `progress` |
| `lb` / `/leaderboard` | View top users | `lb` |
| `itemlb` / `/itemleaderboard` | Top item holders | `itemlb <item>` |

### Utility Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `help` / `/help` | Show help message | `help` |
| `loottable` / `/loottable` | View drop rates | `loottable search` |
| `currencylog` / `/currencylog` | View transaction history | `currencylog` |

### Admin Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `add` | Add coins/items to user | `add <user_id> <amount> [item]` |
| `remove` | Remove coins/items | `remove <user_id> <amount> [item]` |
| `setlevel` | Set user level | `setlevel <user_id> <level>` |
| `wipe` | Wipe user data | `wipe <user_id>` |
| `adminleaderboard` | Admin leaderboard | `adminleaderboard` |
| `showdupers` | Find suspicious accounts | `showdupers` |
| `restart` | Restart the bot | `restart` |

## Item System

### Shop Items

- **Mohamed ki beard** (⏣10,000): Basic collectible
- **Sarthak** (⏣100,000): Mid-tier item
- **Doggy** (⏣300,000): Pet item
- **Sunny** (⏣500,000): Rare collectible
- **SKULL SKELETON** (⏣1,000,000): Epic item
- **Xily ka banana** (⏣10,000,000): Legendary item
- **Mohamed's Pyramid** (⏣911,000): Special structure
- **God Box** (⏣40,000,000): Legendary loot box
- **Stock** (Variable): Investment item with dynamic pricing

### Loot Boxes

- **Rare Loot Box**: 50% nothing, 30% beard, 15% Sarthak, 5% Doggy
- **Legendary Loot Box**: 50% Sarthak, 30% nothing, 15% Sunny, 5% Skull
- **Best Loot Box**: 30% Skull, 20% nothing, 20% 2x boxes, 10% banana, 1% bolb
- **God Box**: 50% eNicx, 50% nothing

### Special Items

- **Stocks**: Dynamic pricing, fluctuates every 2-5 minutes
- **Kuppy**: Timeout other users for 5 minutes
- **Robert's Leash**: Timeout specific user
- **Nicx Crown**: 1% chance to upgrade to Enchanted Nicx Crown
- **Sunny's Tren**: 48-hour 2x XP boost

## Leveling System

### Level Rewards

- **Level 1**: 50,000 coins
- **Level 3**: 100,000 coins
- **Level 5**: Grass
- **Level 8**: Nicx Crown
- **Level 10**: 2x Best Loot Box
- **Level 12**: 10x Kuppy, 2x Best Loot Box, Nicx Crown
- **Level 14**: Banana
- **Level 15**: God Box
- **Level 17**: Bolb
- **Level 18**: 2x God Box
- **Level 19**: Enchanted Nicx Crown
- **Level 20**: 50,000,000 coins + Bolb
- **Level 21**: 25,000,000 coins + Sunny's Tren
- **Level 22+**: Scaling coin rewards (150M base × 1.2^level)

### Badges

- **Godzilla**: Net worth ≥ 250,000,000
- **Platinum Godzilla**: Net worth ≥ 1,000,000,000

## Search Locations

Different locations have unique loot tables:

- **outside**: Low risk, 5% chance for Sunny
- **mohamedhouse**: 20% beard, 5% legendary box
- **mountain**: 20% rare box
- **dog**: 5% Kuppy, 1% best box
- **grass**: 2% grass
- **pyramid**: 2% pyramid or Nicx Crown
- **gbroad**: 1% Sunny/best box/Nicx Crown
- **delhi**: High risk! 10% lose half wallet, 10% Sunny
- **fighthub**: 30% egirl, 10% beard, 1% any loot box

## Stock Market

The stock market updates every 2-5 minutes with price changes of ±30,000 coins. 

- Buy when prices are high (>10k minimum)
- Sell strategically for profit
- If stock hits 0, all stocks are deleted!

## Lottery System

- Ticket price: 10,000 coins each
- Lottery runs for 1 hour after first purchase
- Winner takes the entire pool
- Initial pool: 100,000 coins

## Fighting System

Challenge other users to fights:
- **Punch**: 1-15 damage, 100% hit rate
- **Kick**: 5-32 damage, 60% hit rate (40% self-damage)
- **Run**: Surrender and lose wager

Wager coins or items in fights!

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Security

- Never commit your `.env` file or bot token
- Use environment variables for sensitive data
- Keep your bot token private
- Regularly update dependencies

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, join our Discord server or open an issue on GitHub.

## Acknowledgments

- Original concept and features from the legacy bot
- Built with discord.py 2.x
- Uses aiosqlite for async database operations

---

Made with ❤️ for Discord communities
