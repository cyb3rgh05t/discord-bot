import logging
import discord
import psutil
import shutil
import platform
import sqlite3
from datetime import datetime
from discord.ext import commands, tasks
from config.settings import SYSTEM_CHANNEL_ID
from cogs.helpers.logger import logger

DATABASE_PATH = "databases/system_info.db"  # Path to your SQLite database


class SystemInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_index = 0
        self.status_array = []
        self.db_path = DATABASE_PATH
        self.init_db()

    def init_db(self):
        """Initialize the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS system_info_message (
                guild_id INTEGER PRIMARY KEY,
                message_id INTEGER
            )
            """
        )
        conn.commit()
        conn.close()

    def get_stored_message_id(self, guild_id):
        """Retrieve the stored system message ID for a guild."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT message_id FROM system_info_message WHERE guild_id = ?",
            (guild_id,),
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def store_message_id(self, guild_id, message_id):
        """Store or update the system message ID for a guild."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO system_info_message (guild_id, message_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET message_id = excluded.message_id
            """,
            (guild_id, message_id),
        )
        conn.commit()
        conn.close()

    def get_cpu_usage(self):
        """Retrieve CPU usage percentage."""
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self):
        """Retrieve memory usage in MB."""
        memory = psutil.virtual_memory()
        return memory.used / (1024 * 1024), memory.total / (1024 * 1024)

    def get_disk_usage(self):
        """Retrieve disk usage statistics."""
        disk = shutil.disk_usage("/")
        return disk.used / (1024 * 1024 * 1024), disk.total / (1024 * 1024 * 1024)

    def get_network_stats(self):
        """Retrieve network statistics."""
        stats = psutil.net_io_counters()
        return stats.bytes_sent, stats.bytes_recv

    def check_sqlite_connection(self):
        """Check the connection status of the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return "Online"
        except sqlite3.Error as e:
            logger.error(f"SQLite connection error: {e}")
            return "Offline"

    def create_embed(self):
        """Create the embed for system information."""
        memory_used, memory_total = self.get_memory_usage()
        disk_used, disk_total = self.get_disk_usage()
        network_sent, network_recv = self.get_network_stats()
        cpu_info = platform.processor()
        sqlite_status = self.check_sqlite_connection()

        embed = discord.Embed(
            title="StreamNet Plex Server | Information",
            color=discord.Color.dark_gray(),
            timestamp=datetime.utcnow(),
        )
        embed.add_field(
            name="<:icon_reply:1312507800689311854> System",
            value=(
                f"**• CPU**: {cpu_info}\n"
                f"**• Memory Available**: {memory_total:.1f} MB\n"
                f"**• Memory Used**: {memory_used:.1f} MB\n"
                f"**• Disk Used**: {disk_used:.1f} GB/{disk_total:.1f} GB"
            ),
            inline=False,
        )
        embed.add_field(
            name="<:icon_reply:1312507800689311854> Network",
            value=(
                f"**• Sent**: {network_sent / (1024 * 1024):.1f} MB\n"
                f"**• Received**: {network_recv / (1024 * 1024):.1f} MB"
            ),
            inline=False,
        )
        embed.add_field(
            name="<:icon_reply:1312507800689311854> Database",
            value=f"**• SQLite Status**: {sqlite_status}",
            inline=False,
        )
        embed.set_footer(text="System Information")
        return embed

    async def send_or_update_message(self, channel):
        """Send a new message or update the existing one with system information."""
        embed = self.create_embed()
        guild_id = channel.guild.id
        guild_name = channel.guild.name
        message_id = self.get_stored_message_id(guild_id)

        if message_id:
            try:
                message = await channel.fetch_message(message_id)
                await message.edit(embed=embed)
                logger.debug(
                    f"Updated system info message for guild '{guild_name}' (ID: {guild_id})."
                )
            except discord.NotFound:
                logger.warning(
                    f"Message with ID {message_id} not found, sending a new one."
                )
                message = await channel.send(embed=embed)
                self.store_message_id(guild_id, message.id)
        else:
            message = await channel.send(embed=embed)
            self.store_message_id(guild_id, message.id)

    @tasks.loop(seconds=120)
    async def init_status_task(self):
        """Update the status every 2 minutes."""
        await self.update_status()
        channel = self.bot.get_channel(SYSTEM_CHANNEL_ID)
        if channel:
            await self.send_or_update_message(channel)
        else:
            logger.error(f"System channel with ID {SYSTEM_CHANNEL_ID} not found.")

    async def update_status(self):
        """Rotate and update bot's status messages."""
        if not self.status_array:
            memory_used, memory_total = self.get_memory_usage()
            cpu_usage = self.get_cpu_usage()
            self.status_array = [
                f"RAM: {memory_used:.1f}MB/{memory_total:.1f}MB",
                f"CPU: {cpu_usage:.1f}%",
                "StreamNet Server",
            ]

        status = self.status_array[self.status_index]
        if self.bot.is_ready():
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching, name=status
                ),
                status=discord.Status.online,
            )
        self.status_index = (self.status_index + 1) % len(self.status_array)

    @commands.Cog.listener()
    async def on_ready(self):
        """Send or update system information in the specific channel."""
        logger.info("SystemInfo cog is ready.")
        self.init_status_task.start()


async def setup(bot):
    """Setup function to add the cog."""
    await bot.add_cog(SystemInfo(bot))
    logger.debug("SystemInfo cog loaded.")
