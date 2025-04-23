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
        """Initialize the SQLite database with migration support."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='system_info_message'"
        )
        table_exists = cursor.fetchone() is not None

        if table_exists:
            # Check if channel_id column exists
            cursor.execute("PRAGMA table_info(system_info_message)")
            columns = [info[1] for info in cursor.fetchall()]

            if "channel_id" not in columns:
                logger.info(
                    "Migrating system_info_message table to add channel_id column"
                )
                # SQLite has limited ALTER TABLE support, so we use a transaction to recreate the table
                cursor.execute("BEGIN TRANSACTION")
                try:
                    # Create new table with all columns
                    cursor.execute(
                        """
                        CREATE TABLE system_info_message_new (
                            guild_id INTEGER PRIMARY KEY,
                            message_id INTEGER,
                            channel_id INTEGER
                        )
                    """
                    )

                    # Copy data from old table to new table
                    cursor.execute(
                        """
                        INSERT INTO system_info_message_new (guild_id, message_id)
                        SELECT guild_id, message_id FROM system_info_message
                    """
                    )

                    # Drop old table
                    cursor.execute("DROP TABLE system_info_message")

                    # Rename new table to old table name
                    cursor.execute(
                        "ALTER TABLE system_info_message_new RENAME TO system_info_message"
                    )

                    cursor.execute("COMMIT")
                    logger.info("Migration completed successfully")
                except Exception as e:
                    cursor.execute("ROLLBACK")
                    logger.error(f"Migration failed: {e}")
        else:
            # Create the table if it doesn't exist
            cursor.execute(
                """
                CREATE TABLE system_info_message (
                    guild_id INTEGER PRIMARY KEY,
                    message_id INTEGER,
                    channel_id INTEGER
                )
            """
            )

        conn.commit()
        conn.close()

    def get_stored_message_id(self, guild_id, channel_id=None):
        """Retrieve the stored system message ID for a guild."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            if channel_id:
                # Try querying with channel_id first (if column exists)
                try:
                    cursor.execute(
                        "SELECT message_id FROM system_info_message WHERE guild_id = ? AND channel_id = ?",
                        (guild_id, channel_id),
                    )
                    result = cursor.fetchone()
                    if result:
                        return result[0]
                except sqlite3.OperationalError:
                    # Channel_id column might not exist yet
                    pass

            # Fall back to just guild_id (existing behavior)
            cursor.execute(
                "SELECT message_id FROM system_info_message WHERE guild_id = ?",
                (guild_id,),
            )
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()

    def store_message_id(self, guild_id, message_id, channel_id=None):
        """Store or update the system message ID for a guild."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if channel_id column exists
            has_channel_id = True
            try:
                cursor.execute("PRAGMA table_info(system_info_message)")
                columns = [info[1] for info in cursor.fetchall()]
                has_channel_id = "channel_id" in columns
            except Exception:
                has_channel_id = False

            if channel_id and has_channel_id:
                # If we have a channel_id and the column exists
                cursor.execute(
                    "SELECT COUNT(*) FROM system_info_message WHERE guild_id = ?",
                    (guild_id,),
                )
                exists = cursor.fetchone()[0] > 0

                if exists:
                    # Update existing record
                    cursor.execute(
                        "UPDATE system_info_message SET message_id = ?, channel_id = ? WHERE guild_id = ?",
                        (message_id, channel_id, guild_id),
                    )
                else:
                    # Insert new record with channel_id
                    cursor.execute(
                        "INSERT INTO system_info_message (guild_id, message_id, channel_id) VALUES (?, ?, ?)",
                        (guild_id, message_id, channel_id),
                    )
            else:
                # Original behavior - if channel_id is not supported
                cursor.execute(
                    """
                    INSERT INTO system_info_message (guild_id, message_id)
                    VALUES (?, ?)
                    ON CONFLICT(guild_id) DO UPDATE SET message_id = excluded.message_id
                    """,
                    (guild_id, message_id),
                )

            conn.commit()
        except Exception as e:
            logger.error(f"Error storing message ID: {e}")
        finally:
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
        """Create a beautifully styled embed for system information."""
        try:
            # Gather system information
            memory_used, memory_total = self.get_memory_usage()
            disk_used, disk_total = self.get_disk_usage()
            network_sent, network_recv = self.get_network_stats()
            cpu_usage = self.get_cpu_usage()
            cpu_info = platform.processor()
            sqlite_status = self.check_sqlite_connection()

            # Calculate usage percentages
            memory_percent = (
                (memory_used / memory_total) * 100 if memory_total > 0 else 0
            )
            disk_percent = (disk_used / disk_total) * 100 if disk_total > 0 else 0

            # Progress bar function
            def get_progress_bar(percent, length=10):
                filled = int(percent * length / 100)
                bar = "█" * filled + "" * (length - filled)
                return bar

            # Format file sizes
            def format_size(size_mb):
                if size_mb > 1024:
                    return f"{size_mb/1024:.2f} GB"
                else:
                    return f"{size_mb:.2f} MB"

            # Status indicators
            def get_status_emoji(percent):
                if percent < 60:
                    return "<:icon_online:993231898291736576>"  # Green/Good
                elif percent < 85:
                    return "<:icon_connecting:993232321685762048>"  # Orange/Warning
                else:
                    return "<:icon_offline:993232252647514152>"  # Red/Critical

            # Create embed with a dark theme
            embed = discord.Embed(
                title="StreamNet Plex Server",
                description="Real-time system monitoring information",
                color=0xE5A209,  # Dark theme color
                timestamp=datetime.utcnow(),
            )
            embed.add_field(
                name="",
                value="",
                inline=False,
            )

            # Add CPU field with progress bar
            cpu_bar = get_progress_bar(cpu_usage)
            cpu_emoji = get_status_emoji(cpu_usage)
            embed.add_field(
                name="CPU Usage",
                value=f"\n<:icon_reply:993231553083736135> {cpu_emoji} `{cpu_bar}` **{cpu_usage:.1f}%**\n"
                f"<:icon_reply:993231553083736135> Processor: {cpu_info.split()[0] if len(cpu_info.split()) > 0 else 'Unknown'}\n",
                inline=False,
            )
            embed.add_field(
                name="",
                value="",
                inline=False,
            )

            # Add Memory field with progress bar
            memory_bar = get_progress_bar(memory_percent)
            memory_emoji = get_status_emoji(memory_percent)
            embed.add_field(
                name="Memory Usage",
                value=f"\n<:icon_reply:993231553083736135> {memory_emoji} `{memory_bar}` **{memory_percent:.1f}%**\n"
                f"<:icon_reply:993231553083736135> Used: {format_size(memory_used)} / Total: {format_size(memory_total)}\n",
                inline=False,
            )
            embed.add_field(
                name="",
                value="",
                inline=False,
            )

            # Add Disk field with progress bar
            disk_bar = get_progress_bar(disk_percent)
            disk_emoji = get_status_emoji(disk_percent)
            embed.add_field(
                name="Disk Usage",
                value=f"\n<:icon_reply:993231553083736135> {disk_emoji} `{disk_bar}` **{disk_percent:.1f}%**\n"
                f"<:icon_reply:993231553083736135> Used: {disk_used:.2f} GB / Total: {disk_total:.2f} GB\n",
                inline=False,
            )
            embed.add_field(
                name="",
                value="",
                inline=False,
            )

            # Add Network field
            embed.add_field(
                name="Network Transfer",
                value=f"\n<:icon_reply:993231553083736135> ⬆️ Sent: {network_sent / (1024 * 1024):.2f} MB\n"
                f"<:icon_reply:993231553083736135> ⬇️ Received: {network_recv / (1024 * 1024):.2f} MB\n",
                inline=False,
            )
            embed.add_field(
                name="",
                value="",
                inline=False,
            )

            # Add Database Status
            db_emoji = (
                "<:icon_online:993231898291736576>"
                if sqlite_status == "Online"
                else "<:icon_offline:993232252647514152>"
            )
            embed.add_field(
                name="Database Status",
                value=f"<:icon_reply:993231553083736135> {db_emoji} **{sqlite_status}**",
                inline=False,
            )
            embed.add_field(
                name="",
                value="",
                inline=False,
            )

            # Add system uptime if available
            try:
                uptime_seconds = int(float(open("/proc/uptime").read().split()[0]))
                days, remainder = divmod(uptime_seconds, 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)

                uptime_str = ""
                if days > 0:
                    uptime_str += f"{days}d "
                if hours > 0 or days > 0:
                    uptime_str += f"{hours}h "
                if minutes > 0 or hours > 0 or days > 0:
                    uptime_str += f"{minutes}m "
                uptime_str += f"{seconds}s"

                embed.add_field(
                    name="System Uptime",
                    value=f"\n<:icon_reply:993231553083736135> **{uptime_str}**",
                    inline=False,
                )
                embed.add_field(
                    name="",
                    value="",
                    inline=False,
                )
            except:
                # Uptime might not be available on all systems (especially Windows)
                try:
                    # For Windows systems
                    import ctypes

                    class LASTINPUTINFO(ctypes.Structure):
                        _fields_ = [
                            ("cbSize", ctypes.c_uint),
                            ("dwTime", ctypes.c_uint),
                        ]

                    GetTickCount = ctypes.windll.kernel32.GetTickCount
                    GetTickCount.restype = ctypes.c_uint

                    uptime_ms = GetTickCount()
                    uptime_seconds = uptime_ms // 1000

                    days, remainder = divmod(uptime_seconds, 86400)
                    hours, remainder = divmod(remainder, 3600)
                    minutes, seconds = divmod(remainder, 60)

                    uptime_str = ""
                    if days > 0:
                        uptime_str += f"{days}d "
                    if hours > 0 or days > 0:
                        uptime_str += f"{hours}h "
                    if minutes > 0 or hours > 0 or days > 0:
                        uptime_str += f"{minutes}m "
                    uptime_str += f"{seconds}s"

                    embed.add_field(
                        name="System Uptime",
                        value=f"\n<:icon_reply:993231553083736135> **{uptime_str}**",
                        inline=False,
                    )
                    embed.add_field(
                        name="",
                        value="",
                        inline=False,
                    )
                except:
                    pass

            embed.set_thumbnail(
                url="https://cdn.discordapp.com/emojis/1033460420587049021.png"
            )

            # Set footer with last updated time
            embed.set_footer(text="Last Updated")

            return embed
        except Exception as e:
            logger.error(f"Error creating embed: {e}")
            # Fallback to simple embed if anything goes wrong
            embed = discord.Embed(
                title="StreamNet Server Status",
                description="System monitoring information",
                color=discord.Color.dark_gray(),
                timestamp=datetime.utcnow(),
            )
            embed.add_field(
                name="System",
                value="Error fetching detailed stats. Check server logs.",
                inline=False,
            )
            return embed

    async def send_or_update_message(self, channel, specific_message_id=None):
        """Send a new message or update the existing one with system information."""
        embed = self.create_embed()
        guild_id = channel.guild.id
        guild_name = channel.guild.name

        # If a specific message ID is provided, use that
        if specific_message_id:
            message_id = specific_message_id
        else:
            # Otherwise check if we have a stored message for this channel
            message_id = self.get_stored_message_id(guild_id, channel.id)

            # If no channel-specific message, fall back to guild-level message
            if not message_id:
                message_id = self.get_stored_message_id(guild_id)

        if message_id:
            try:
                message = await channel.fetch_message(message_id)
                await message.edit(embed=embed)
                logger.debug(f"Updated system info message in channel #{channel.name}")
                return message
            except discord.NotFound:
                logger.warning(
                    f"Message with ID {message_id} not found in channel #{channel.name}, sending a new one."
                )
                message = await channel.send(embed=embed)
                self.store_message_id(guild_id, message.id, channel.id)
                logger.info(
                    f"Created new system info message in channel #{channel.name}"
                )
                return message
            except Exception as e:
                logger.error(f"Error updating message in channel #{channel.name}: {e}")
                message = await channel.send(embed=embed)
                self.store_message_id(guild_id, message.id, channel.id)
                logger.info(
                    f"Created new system info message in channel #{channel.name} after error"
                )
                return message
        else:
            message = await channel.send(embed=embed)
            self.store_message_id(guild_id, message.id, channel.id)
            logger.info(
                f"Created initial system info message in channel #{channel.name}"
            )
            return message

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

    @commands.command(name="serverinfo", help="Create or update server info message")
    @commands.has_permissions(administrator=True)
    async def serverinfo(self, ctx):
        """Create or update a server info message in the current channel."""
        try:
            message = await self.send_or_update_message(ctx.channel)
            logger.info(f"Created/updated server info in channel {ctx.channel.name}")

            # Send a confirmation message that will be deleted after a short delay
            confirm_msg = await ctx.send(
                "Server info message created/updated successfully!"
            )
            await confirm_msg.delete(delay=5)

        except Exception as e:
            logger.error(f"Error creating server info message: {e}")
            await ctx.send(f"Error creating server info message: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        """Send or update system information in the specific channel."""
        logger.debug("SystemInfo cog is ready.")

        # Log the channel where we'll be updating info
        channel = self.bot.get_channel(SYSTEM_CHANNEL_ID)
        if channel:
            logger.info(f"System channel found #{channel.name}")
        else:
            logger.error(
                f"System channel with ID {SYSTEM_CHANNEL_ID} not found. Cannot start system info updates."
            )

        self.init_status_task.start()


async def setup(bot):
    """Setup function to add the cog."""
    await bot.add_cog(SystemInfo(bot))
    logger.debug("SystemInfo cog loaded.")
