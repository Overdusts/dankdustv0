"""
Database management using aiosqlite
"""

import aiosqlite
import logging
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime

from utils.config import Config

logger = logging.getLogger('EconomyBot.Database')


class Database:
    """Async database handler for the economy bot"""
    
    def __init__(self, db_path: str = "economy.db"):
        self.db_path = db_path
        self.conn: Optional[aiosqlite.Connection] = None
        
    async def connect(self) -> aiosqlite.Connection:
        """Get database connection"""
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_path)
            self.conn.row_factory = aiosqlite.Row
        return self.conn
        
    async def close(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
            self.conn = None
            
    async def setup(self):
        """Initialize database tables"""
        conn = await self.connect()
        
        # levels table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS levels (
                user_id INTEGER PRIMARY KEY,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                rebirth_level INTEGER DEFAULT 0
            )
        ''')
        
        # balances table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS balances (
                user_id INTEGER PRIMARY KEY,
                wallet INTEGER DEFAULT 0,
                bank INTEGER DEFAULT 0,
                inventory INTEGER DEFAULT 0,
                net_worth INTEGER DEFAULT 0
            )
        ''')
        
        # badges table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS badges (
                user_id INTEGER,
                badge_name TEXT,
                PRIMARY KEY (user_id, badge_name)
            )
        ''')
        
        # cooldowns table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS cooldowns (
                user_id INTEGER PRIMARY KEY,
                beg_cooldown REAL DEFAULT 0,
                search_cooldown REAL DEFAULT 0,
                fetch_cooldown REAL DEFAULT 0,
                fish_cooldown REAL DEFAULT 0,
                hunt_cooldown REAL DEFAULT 0,
                stake_cooldown REAL DEFAULT 0,
                dice_cooldown REAL DEFAULT 0
            )
        ''')
        
        # inventory table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                user_id INTEGER,
                item_id TEXT,
                quantity INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, item_id)
            )
        ''')
        
        # shop items table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS shop_items (
                id TEXT PRIMARY KEY,
                name TEXT,
                price INTEGER
            )
        ''')
        
        # currency log table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS currencylog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT,
                amount INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # stock price table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS stock_price (
                item_id TEXT PRIMARY KEY,
                price INTEGER
            )
        ''')
        
        # boosts table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS boosts (
                user_id INTEGER PRIMARY KEY,
                boost_factor INTEGER,
                expiration_time INTEGER
            )
        ''')
        
        # lottery table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS lottery (
                user_id INTEGER PRIMARY KEY,
                tickets INTEGER DEFAULT 0
            )
        ''')
        
        await conn.commit()
        
        # initialize shop items
        await self.init_shop_items()
        
        # initialize stock price
        await conn.execute(
            "INSERT OR IGNORE INTO stock_price (item_id, price) VALUES (?, ?)",
            ('stock', Config.STOCK_INITIAL_PRICE)
        )
        await conn.commit()
        
        logger.info("Database setup complete")
        
    async def init_shop_items(self):
        """Initialize shop items in database"""
        conn = await self.connect()
        
        for item_id, item_data in Config.SHOP_ITEMS.items():
            if item_data['price'] is not None:
                await conn.execute(
                    "INSERT OR REPLACE INTO shop_items (id, name, price) VALUES (?, ?, ?)",
                    (item_id, item_data['name'], item_data['price'])
                )
                
        await conn.commit()
        
    # user management
    async def ensure_user(self, user_id: int):
        """Ensure user exists in all tables"""
        conn = await self.connect()
        
        await conn.execute(
            "INSERT OR IGNORE INTO balances (user_id) VALUES (?)",
            (user_id,)
        )
        await conn.execute(
            "INSERT OR IGNORE INTO levels (user_id) VALUES (?)",
            (user_id,)
        )
        await conn.execute(
            "INSERT OR IGNORE INTO cooldowns (user_id) VALUES (?)",
            (user_id,)
        )
        
        await conn.commit()
        
    # balance operations
    async def get_balance(self, user_id: int) -> Dict[str, int]:
        """Get user's balance info"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        async with conn.execute(
            "SELECT wallet, bank FROM balances WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            
        return {
            'wallet': row['wallet'] if row else 0,
            'bank': row['bank'] if row else 0
        }
        
    async def add_coins(self, user_id: int, amount: int, location: str = 'wallet'):
        """Add coins to user's wallet or bank"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        await conn.execute(
            f"UPDATE balances SET {location} = {location} + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await conn.commit()
        
    async def remove_coins(self, user_id: int, amount: int, location: str = 'wallet') -> bool:
        """Remove coins from user's wallet or bank. Returns True if successful."""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        # check if user has enough
        balance = await self.get_balance(user_id)
        if balance[location] < amount:
            return False
            
        await conn.execute(
            f"UPDATE balances SET {location} = {location} - ? WHERE user_id = ?",
            (amount, user_id)
        )
        await conn.commit()
        return True
        
    async def get_net_worth(self, user_id: int) -> int:
        """Calculate user's total net worth"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        # get wallet balance
        balance = await self.get_balance(user_id)
        wallet = balance['wallet']
        
        # calculate inventory worth
        async with conn.execute('''
            SELECT SUM(
                CASE 
                    WHEN inventory.item_id = 'stock' THEN 
                        (SELECT price FROM stock_price WHERE item_id = 'stock') * quantity
                    ELSE 
                        shop_items.price * quantity
                END
            ) as inventory_worth
            FROM inventory
            LEFT JOIN shop_items ON inventory.item_id = shop_items.id
            WHERE inventory.user_id = ?
        ''', (user_id,)) as cursor:
            row = await cursor.fetchone()
            inventory_worth = row['inventory_worth'] if row and row['inventory_worth'] else 0
            
        return wallet + inventory_worth
        
    # inventory operations
    async def get_inventory(self, user_id: int) -> List[Tuple[str, int]]:
        """Get user's inventory"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        async with conn.execute(
            "SELECT item_id, quantity FROM inventory WHERE user_id = ? AND quantity > 0 ORDER BY quantity DESC",
            (user_id,)
        ) as cursor:
            return await cursor.fetchall()
            
    async def get_item_quantity(self, user_id: int, item_id: str) -> int:
        """Get quantity of specific item"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        async with conn.execute(
            "SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?",
            (user_id, item_id)
        ) as cursor:
            row = await cursor.fetchone()
            return row['quantity'] if row else 0
            
    async def add_item(self, user_id: int, item_id: str, quantity: int = 1):
        """Add item to user's inventory"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        await conn.execute('''
            INSERT INTO inventory (user_id, item_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, item_id) DO UPDATE SET
            quantity = quantity + ?
        ''', (user_id, item_id, quantity, quantity))
        
        await conn.commit()
        
    async def remove_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        """Remove item from user's inventory. Returns True if successful."""
        current_quantity = await self.get_item_quantity(user_id, item_id)
        
        if current_quantity < quantity:
            return False
            
        conn = await self.connect()
        await conn.execute(
            "UPDATE inventory SET quantity = quantity - ? WHERE user_id = ? AND item_id = ?",
            (quantity, user_id, item_id)
        )
        await conn.commit()
        return True
        
    # level operations
    async def get_level_data(self, user_id: int) -> Dict[str, int]:
        """Get user's level data"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        async with conn.execute(
            "SELECT level, experience, rebirth_level FROM levels WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            
        return {
            'level': row['level'] if row else 1,
            'experience': row['experience'] if row else 0,
            'rebirth_level': row['rebirth_level'] if row else 0
        }
        
    async def add_experience(self, user_id: int, amount: int = 1):
        """Add experience to user"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        await conn.execute(
            "UPDATE levels SET experience = experience + ? WHERE user_id = ?",
            (amount, user_id)
        )
        await conn.commit()
        
    async def set_level(self, user_id: int, level: int):
        """Set user's level"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        await conn.execute(
            "UPDATE levels SET level = ? WHERE user_id = ?",
            (level, user_id)
        )
        await conn.commit()
        
    # cooldown operations
    async def get_cooldown(self, user_id: int, command: str) -> float:
        """Get cooldown for a specific command"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        async with conn.execute(
            f"SELECT {command}_cooldown FROM cooldowns WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[f'{command}_cooldown'] if row else 0
            
    async def set_cooldown(self, user_id: int, command: str, timestamp: float):
        """Set cooldown for a specific command"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        await conn.execute(
            f"UPDATE cooldowns SET {command}_cooldown = ? WHERE user_id = ?",
            (timestamp, user_id)
        )
        await conn.commit()
        
    # badge operations
    async def get_badges(self, user_id: int) -> List[str]:
        """Get user's badges"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        async with conn.execute(
            "SELECT badge_name FROM badges WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [row['badge_name'] for row in rows]
            
    async def add_badge(self, user_id: int, badge_name: str):
        """Add badge to user"""
        conn = await self.connect()
        
        await conn.execute(
            "INSERT OR IGNORE INTO badges (user_id, badge_name) VALUES (?, ?)",
            (user_id, badge_name)
        )
        await conn.commit()
        
    async def remove_badge(self, user_id: int, badge_name: str):
        """Remove badge from user"""
        conn = await self.connect()
        
        await conn.execute(
            "DELETE FROM badges WHERE user_id = ? AND badge_name = ?",
            (user_id, badge_name)
        )
        await conn.commit()
        
    # stock operations
    async def get_stock_price(self) -> int:
        """Get current stock price"""
        conn = await self.connect()
        
        async with conn.execute(
            "SELECT price FROM stock_price WHERE item_id = 'stock'"
        ) as cursor:
            row = await cursor.fetchone()
            return row['price'] if row else Config.STOCK_INITIAL_PRICE
            
    async def set_stock_price(self, price: int):
        """Update stock price"""
        conn = await self.connect()
        
        await conn.execute(
            "UPDATE stock_price SET price = ? WHERE item_id = 'stock'",
            (price,)
        )
        await conn.commit()
        
    # leaderboard operations
    async def get_leaderboard(self, limit: int = 10) -> List[Tuple[int, int]]:
        """Get top users by net worth"""
        conn = await self.connect()
        
        async with conn.execute('''
            SELECT 
                user_id,
                wallet + COALESCE((
                    SELECT SUM(
                        CASE 
                            WHEN inventory.item_id = 'stock' THEN 
                                (SELECT price FROM stock_price WHERE item_id = 'stock') * quantity
                            ELSE 
                                shop_items.price * quantity
                        END
                    )
                    FROM inventory
                    LEFT JOIN shop_items ON inventory.item_id = shop_items.id
                    WHERE inventory.user_id = balances.user_id
                ), 0) as net_worth
            FROM balances
            ORDER BY net_worth DESC
            LIMIT ?
        ''', (limit,)) as cursor:
            return await cursor.fetchall()
            
    async def get_item_leaderboard(self, item_id: str, limit: int = 5) -> List[Tuple[int, int]]:
        """Get top holders of a specific item"""
        conn = await self.connect()
        
        async with conn.execute('''
            SELECT user_id, quantity
            FROM inventory
            WHERE item_id = ?
            ORDER BY quantity DESC
            LIMIT ?
        ''', (item_id, limit)) as cursor:
            return await cursor.fetchall()
            
    # boost operations
    async def get_boost(self, user_id: int) -> Optional[Tuple[int, int]]:
        """Get user's active boost (factor, expiration_time)"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        async with conn.execute(
            "SELECT boost_factor, expiration_time FROM boosts WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return (row['boost_factor'], row['expiration_time'])
        return None
        
    async def set_boost(self, user_id: int, boost_factor: int, expiration_time: int):
        """Set or update user's boost"""
        await self.ensure_user(user_id)
        conn = await self.connect()
        
        await conn.execute('''
            INSERT INTO boosts (user_id, boost_factor, expiration_time)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            boost_factor = ?, expiration_time = ?
        ''', (user_id, boost_factor, expiration_time, boost_factor, expiration_time))
        
        await conn.commit()
        
    async def remove_boost(self, user_id: int):
        """Remove user's boost"""
        conn = await self.connect()
        
        await conn.execute(
            "DELETE FROM boosts WHERE user_id = ?",
            (user_id,)
        )
        await conn.commit()
        
    # utility functions
    async def log_transaction(self, user_id: int, action: str, amount: int):
        """Log a currency transaction"""
        conn = await self.connect()
        
        await conn.execute(
            "INSERT INTO currencylog (user_id, action, amount) VALUES (?, ?, ?)",
            (user_id, action, amount)
        )
        await conn.commit()
        
    async def get_currency_log(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's recent currency transactions"""
        conn = await self.connect()
        
        async with conn.execute('''
            SELECT action, amount, timestamp
            FROM currencylog
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
            
    async def wipe_user(self, user_id: int):
        """Completely wipe a user's data"""
        conn = await self.connect()
        
        await conn.execute("DELETE FROM inventory WHERE user_id = ?", (user_id,))
        await conn.execute("UPDATE balances SET wallet = 0, bank = 0 WHERE user_id = ?", (user_id,))
        await conn.execute("DELETE FROM badges WHERE user_id = ?", (user_id,))
        await conn.execute("DELETE FROM boosts WHERE user_id = ?", (user_id,))
        
        await conn.commit()
