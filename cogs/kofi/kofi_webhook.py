import discord
from discord.ext import commands
import asyncio
import json
import logging
import os
import sys
import threading
import datetime
import importlib
from flask import Flask, request, jsonify
import requests
import io
from config.settings import (
    KOFI_WEBHOOK_PORT,
    KOFI_VERIFICATION_TOKEN,
    KOFI_CHANNEL_ID,
    KOFI_LANGUAGE,
)
from cogs.helpers.logger import logger

# Silence Flask's startup banner
cli = importlib.import_module("flask.cli")
cli.show_server_banner = lambda *args, **kwargs: None


# Configure Flask to use our logger
class FlaskHandler(logging.Handler):
    def emit(self, record):
        # Skip Werkzeug's internal logs about requests
        if record.name == "werkzeug" and record.msg.startswith("127.0.0.1"):
            return
        if record.name == "werkzeug" and "Running on" in str(record.msg):
            # Clean up the Flask startup message
            msg = record.msg
            if isinstance(msg, str):
                if "WARNING:" in msg:
                    logger.warning(f"Flask: {msg.replace('WARNING: ', '')}")
                elif "* Running on" in msg:
                    host_info = msg.replace("* Running on ", "").strip()
                    logger.info(f"Ko-fi webhook listening on {host_info}")
                else:
                    logger.info(f"Flask: {msg}")
            return
        logger.log(record.levelno, f"Flask: {record.getMessage()}")


# Create a filter to ignore common port scanning requests
class IgnoreScansFilter(logging.Filter):
    def filter(self, record):
        log_message = record.getMessage()
        # Skip common port scanning errors
        if any(
            pattern in log_message
            for pattern in [
                "Bad HTTP/0.9 request type",
                "Failed to decode",
                "Bad request syntax",
                "Bad request version",
                "Received invalid data",
                "Invalid HTTP request",
                "Malformed HTTP request",
            ]
        ):
            return False
        return True


# Translations for multiple languages
TRANSLATIONS = {
    "en": {
        # Types
        "Donation": "Donation",
        "Subscription": "Subscription",
        "Commission": "Commission",
        "Shop Order": "Shop Order",
        # Field names
        "From": "From",
        "Type": "Type",
        "Amount": "Amount",
        "Membership Tier": "Membership Tier",
        "First Payment": "First Payment",
        "Date": "Date",
        "Transaction ID": "Transaction ID",
        "Message": "Message",
        # Status messages
        "Yes": "Yes",
        "Renewal": "Renewal",
        "Anonymous": "Anonymous",
        # UI messages
        "New {KOFI_NAME} Support Received!": "New {KOFI_NAME} Support Received!",
        "has subscribed to the": "has subscribed to the",
        "tier!": "tier!",
        "Thanks for the support!": "Thanks for the support!",
        "{KOFI_NAME} Support": "{KOFI_NAME} Support",
        "CustomMessage": "Thanks for the support! Your donation helps keep our community and services running.",
        "CustomFooter": "{KOFI_NAME} Support",
    },
    "de": {
        # Types
        "Donation": "Spende",
        "Subscription": "Abo",
        "Commission": "Auftrag",
        "Shop Order": "Bestellung",
        # Field names
        "From": "Von",
        "Type": "Typ",
        "Amount": "Betrag",
        "Membership Tier": "Mitgliedsstufe",
        "First Payment": "Erste Zahlung",
        "Date": "Datum",
        "Transaction ID": "Transaktions-ID",
        "Message": "Nachricht",
        # Status messages
        "Yes": "Ja",
        "Renewal": "Verlängerung",
        "Anonymous": "Anonym",
        # UI messages
        "New {KOFI_NAME} Support Received!": "Neue {KOFI_NAME} Spende erhalten!",
        "has subscribed to the": "hat die",
        "tier!": "Stufe abonniert!",
        "Thanks for the support!": "Vielen Dank für die Unterstützung!",
        "{KOFI_NAME} Support": "{KOFI_NAME} Support",
        "CustomMessage": "Vielen Dank für die Unterstützung! Deine Spende hilft uns, unsere Community und Dienste am Laufen zu halten.",
        "CustomFooter": "{KOFI_NAME} Support",
    },
    "fr": {
        # Types
        "Donation": "Don",
        "Subscription": "Abonnement",
        "Commission": "Commission",
        "Shop Order": "Commande",
        # Field names
        "From": "De",
        "Type": "Type",
        "Amount": "Montant",
        "Membership Tier": "Niveau d'adhésion",
        "First Payment": "Premier paiement",
        "Date": "Date",
        "Transaction ID": "ID de transaction",
        "Message": "Message",
        # Status messages
        "Yes": "Oui",
        "Renewal": "Renouvellement",
        "Anonymous": "Anonyme",
        # UI messages
        "New {KOFI_NAME} Support Received!": "Nouveau soutien {KOFI_NAME} reçu !",
        "has subscribed to the": "a souscrit au niveau",
        "tier!": "!",
        "Thanks for the support!": "Merci pour le soutien !",
        "{KOFI_NAME} Support": "Support {KOFI_NAME}",
        "CustomMessage": "Merci pour votre soutien! Votre don nous aide à maintenir notre communauté et nos services.",
        "CustomFooter": "Support {KOFI_NAME}",
    },
}

# Default configuration
DEFAULT_CONFIG = {
    "kofi_name": "Ko-fi",
    "kofi_logo": "https://storage.ko-fi.com/cdn/brandasset/kofi_s_logo_nolabel.png",
    "webhook_username": "Ko-fi Supporter Alert",
    "language": "en",
    "verification_token": "",
    "channel_id": None,
    "port": 3033,
}


class KofiWebhook(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Configure Flask logging
        self.configure_flask_logging()

        self.app = Flask(__name__)
        self.thread = None

        # Load configuration
        self.config = self.load_config()

        # Log configuration
        logger.info("Ko-fi configuration loaded:")
        logger.info(f"  → Ko-Fi Language: '{self.config['language']}'")
        logger.info(f"  → Ko-Fi Name: '{self.config['kofi_name']}'")
        logger.info(f"  → Ko-Fi Port: '{self.config['port']}'")
        logger.info(
            f"  → Ko-Fi Token: {'[REDACTED]' if self.config['verification_token'] else 'NOT SET - REQUIRED'}"
        )
        logger.info(f"  → Ko-Fi Channel ID: '{self.config['channel_id']}'")
        print("---------------------------------------------")
        # Setup Flask routes
        self.setup_routes()

    def configure_flask_logging(self):
        """Configure Flask's logging to suppress common port scanning errors"""
        # Suppress Flask/Werkzeug logging
        werkzeug_logger = logging.getLogger("werkzeug")
        werkzeug_logger.setLevel(logging.ERROR)

        # Apply the filter to ignore scan attempts
        werkzeug_logger.addFilter(IgnoreScansFilter())

        # Also apply the filter to the root logger to catch any forwarded messages
        logging.getLogger().addFilter(IgnoreScansFilter())

    def load_config(self):
        """Load configuration from environment or settings"""
        config = DEFAULT_CONFIG.copy()

        # Try to load from settings
        try:
            config["port"] = KOFI_WEBHOOK_PORT
            config["verification_token"] = KOFI_VERIFICATION_TOKEN
            config["channel_id"] = KOFI_CHANNEL_ID
            config["language"] = KOFI_LANGUAGE.lower()

            # Try to load optional settings
            try:
                from config.settings import (
                    KOFI_NAME,
                    KOFI_LOGO,
                    KOFI_CUSTOM_MESSAGE,
                    KOFI_CUSTOM_FOOTER,
                )

                # Load basic settings
                if "KOFI_NAME" in locals() and KOFI_NAME:
                    config["kofi_name"] = KOFI_NAME
                if "KOFI_LOGO" in locals() and KOFI_LOGO:
                    config["kofi_logo"] = KOFI_LOGO

                # If custom messages are defined, override the translations
                if "KOFI_CUSTOM_MESSAGE" in locals() and KOFI_CUSTOM_MESSAGE:
                    lang = config["language"]
                    if lang in TRANSLATIONS:
                        TRANSLATIONS[lang]["CustomMessage"] = KOFI_CUSTOM_MESSAGE

                # If custom footer is defined, override the translations
                if "KOFI_CUSTOM_FOOTER" in locals() and KOFI_CUSTOM_FOOTER:
                    lang = config["language"]
                    if lang in TRANSLATIONS:
                        TRANSLATIONS[lang]["CustomFooter"] = KOFI_CUSTOM_FOOTER

            except ImportError:
                pass  # Optional settings not defined

        except:
            logger.warning("Could not load all Ko-fi settings from config.settings")

        return config

    def setup_routes(self):
        """Set up Flask routes for the webhook"""
        app = self.app

        @app.route("/")
        def home():
            """Root endpoint"""
            return jsonify(
                {
                    "message": f"{self.config['kofi_name']} to Discord webhook service is online!",
                    "language": self.config["language"],
                }
            )

        @app.route("/health")
        def health():
            """Health check endpoint"""
            return jsonify(
                {
                    "status": "OK",
                    "message": f"{self.config['kofi_name']} to Discord webhook service is running",
                }
            )

        @app.route("/webhook", methods=["GET", "POST"])
        def webhook():
            """Ko-fi webhook endpoint"""
            # For GET requests (browser access), show a friendly message
            if request.method == "GET":
                return jsonify(
                    {
                        "status": "active",
                        "message": f"{self.config['kofi_name']} webhook endpoint is active and waiting for POST requests from Ko-fi",
                        "hint": "This endpoint only processes POST requests from Ko-fi's notification system",
                    }
                )

            # Process POST requests (from Ko-fi)
            try:
                logger.debug(
                    f"Received webhook request with Content-Type: {request.content_type}"
                )

                # Get data from the request based on content type
                data = None

                # Handle application/json content type
                if request.is_json:
                    payload = request.json
                    data = payload.get("data")
                    logger.debug("Processing JSON payload")

                # Handle form data (application/x-www-form-urlencoded)
                elif request.form:
                    data = request.form.get("data")
                    logger.debug("Processing form data payload")

                # Handle raw data as a fallback
                elif request.data:
                    try:
                        # Try to parse raw data as JSON
                        payload = json.loads(request.data.decode("utf-8"))
                        data = payload.get("data")
                        logger.debug("Processing raw data as JSON")
                    except:
                        # If parsing fails, try to use the raw data as-is
                        data = request.data.decode("utf-8")
                        logger.debug("Processing raw data as string")

                if not data:
                    logger.error("No data provided in webhook request")
                    logger.debug(
                        f"Request details - Form: {request.form}, Data: {request.data}, JSON: {request.is_json}"
                    )
                    return jsonify({"success": False, "error": "No data provided"}), 400

                # Parse the Ko-fi data (Ko-fi sends data as a string that needs to be parsed)
                kofi_data = data
                if isinstance(data, str):
                    try:
                        kofi_data = json.loads(data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing Ko-fi data: {e}")
                        return (
                            jsonify(
                                {"success": False, "error": f"Invalid JSON: {str(e)}"}
                            ),
                            400,
                        )

                logger.info(f"Received Ko-fi Donation webhook")
                logger.debug(f"Received Ko-fi data: {kofi_data}")

                # Verify the token if configured
                if (
                    self.config["verification_token"]
                    and kofi_data.get("verification_token")
                    != self.config["verification_token"]
                ):
                    logger.warning("Invalid verification token received")
                    return (
                        jsonify(
                            {"success": False, "error": "Invalid verification token"}
                        ),
                        401,
                    )

                # Process the Ko-fi data
                asyncio.run_coroutine_threadsafe(
                    self.process_kofi_data(kofi_data), self.bot.loop
                )

                return jsonify({"success": True})

            except Exception as e:
                logger.error(f"Error processing webhook: {str(e)}")
                return jsonify({"success": False, "error": str(e)}), 500

    def t(self, key):
        """Get translation with variable replacement"""
        lang = self.config["language"].lower()
        if lang not in TRANSLATIONS:
            lang = "en"  # Fall back to English

        # Handle CustomMessage and CustomFooter specially to allow overrides from settings
        if key in ["CustomMessage", "CustomFooter"]:
            try:
                # Try to import custom message settings
                if key == "CustomMessage":
                    from config.settings import KOFI_CUSTOM_MESSAGE

                    if "KOFI_CUSTOM_MESSAGE" in locals() and KOFI_CUSTOM_MESSAGE:
                        return KOFI_CUSTOM_MESSAGE
                elif key == "CustomFooter":
                    from config.settings import KOFI_CUSTOM_FOOTER

                    if "KOFI_CUSTOM_FOOTER" in locals() and KOFI_CUSTOM_FOOTER:
                        return KOFI_CUSTOM_FOOTER
            except ImportError:
                pass

        # Get translation from the dictionary
        text = TRANSLATIONS[lang].get(key, TRANSLATIONS["en"].get(key, key))
        return text.replace("{KOFI_NAME}", self.config["kofi_name"])

    def format_date(self, timestamp):
        """Format timestamp nicely based on language"""
        try:
            date = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

            if self.config["language"] == "de":
                return date.strftime("%A, %d. %B %Y, %H:%M Uhr")
            elif self.config["language"] == "fr":
                return date.strftime("%A %d %B %Y, %H:%M")
            else:
                return date.strftime("%A, %B %d, %Y at %I:%M %p")
        except:
            return timestamp or "Unknown date"

    def get_type_emoji(self, type_str):
        """Get appropriate emoji for different transaction types"""
        if not type_str:
            return "<:donation:1364168027716976731>"

        type_lower = type_str.lower()

        if type_lower in ["donation", "spende", "don"]:
            return "<:donation:1364168027716976731>"
        elif type_lower in ["subscription", "abo", "abonnement"]:
            return "🏆"
        elif type_lower in ["commission", "auftrag"]:
            return "🎨"
        elif type_lower in ["shop order", "bestellung", "commande"]:
            return "🛍️"
        else:
            return "<:donation:1364168027716976731>"

    def get_color(self, data):
        """Get color based on transaction type or tier"""
        # Ko-fi Blue: #29ABE0 = 2743264 in decimal
        if data.get("tier_name"):
            tier_name = data["tier_name"].lower()

            if tier_name == "bronze":
                return 0xCD7F32  # Bronze color
            elif tier_name == "silver":
                return 0xC0C0C0  # Silver color
            elif tier_name == "gold":
                return 0xFFD700  # Gold color
            elif tier_name == "platinum":
                return 0xE5E4E2  # Platinum color
            else:
                return 0x29ABE0  # Ko-fi blue

        # Handle different language types
        type_lower = data.get("type", "").lower()

        if type_lower in ["donation", "spende", "don"]:
            return 0x29ABE0  # Ko-fi blue
        elif type_lower in ["subscription", "abo", "abonnement"]:
            return 0x8A2BE2  # Purple
        elif type_lower in ["commission", "auftrag"]:
            return 0xFF69B4  # Pink
        elif type_lower in ["shop order", "bestellung", "commande"]:
            return 0x32CD32  # Green
        else:
            return 0x29ABE0  # Ko-fi blue default

    async def process_kofi_data(self, kofi_data):
        """Process Ko-fi data and send Discord message"""
        try:
            # Get channel
            channel_id = self.config["channel_id"]
            if not channel_id:
                logger.error("No channel ID configured for Ko-fi notifications")
                return

            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                logger.error(f"Could not find channel with ID {channel_id}")
                return

            # Determine if it's a subscription
            is_subscription = (
                kofi_data.get("type") == "Subscription"
                or kofi_data.get("type") == "Abo"
                or kofi_data.get("is_subscription_payment")
            )

            # Get translated type
            translated_type = self.t(kofi_data.get("type", "Donation"))

            # Get current language
            lang = self.config["language"]

            # Create embed
            embed = discord.Embed(
                title=f"{self.get_type_emoji(kofi_data.get('type'))} {self.t('New {KOFI_NAME} Support Received!')}",
                color=self.get_color(kofi_data),
            )

            # Set thumbnail
            embed.set_thumbnail(url=self.config["kofi_logo"])

            # Add message or default text to description
            if kofi_data.get("message") and kofi_data["message"].strip():
                embed.description = f"\"{kofi_data['message']}\""
            elif is_subscription:
                embed.description = f"**{kofi_data.get('from_name', self.t('Anonymous'))}** {self.t('has subscribed to the')} {kofi_data.get('tier_name', '')} {self.t('tier!')} 🎉"
            else:
                # Use custom message if available
                embed.description = self.t("CustomMessage")

            # Set footer and timestamp
            footer_text = self.t("CustomFooter").replace(
                "{KOFI_NAME}", self.config["kofi_name"]
            )
            embed.set_footer(text=footer_text, icon_url=self.config["kofi_logo"])
            embed.timestamp = datetime.datetimezone.utc()

            # Add main fields
            embed.add_field(
                name=self.t("From"),
                value=kofi_data.get("from_name", self.t("Anonymous")),
                inline=True,
            )
            embed.add_field(name=self.t("Type"), value=translated_type, inline=True)

            # Amount with currency
            if kofi_data.get("amount"):
                embed.add_field(
                    name=self.t("Amount"),
                    value=f"{kofi_data['amount']} {kofi_data.get('currency', 'USD')}",
                    inline=True,
                )

            # Add subscription-specific fields
            if is_subscription:
                # Add tier name if available
                if kofi_data.get("tier_name"):
                    embed.add_field(
                        name=self.t("Membership Tier"),
                        value=kofi_data["tier_name"],
                        inline=True,
                    )

                # Show if this is first payment
                if "is_first_subscription_payment" in kofi_data:
                    embed.add_field(
                        name=self.t("First Payment"),
                        value=(
                            f"{self.t('Yes')} ✨"
                            if kofi_data["is_first_subscription_payment"]
                            else f"{self.t('Renewal')} 🔄"
                        ),
                        inline=True,
                    )

            # Format and add timestamp
            if kofi_data.get("timestamp"):
                embed.add_field(
                    name=self.t("Date"),
                    value=self.format_date(kofi_data["timestamp"]),
                    inline=False,
                )

            # Add transaction ID for reference
            if kofi_data.get("kofi_transaction_id"):
                embed.add_field(
                    name=self.t("Transaction ID"),
                    value=kofi_data["kofi_transaction_id"],
                    inline=False,
                )

            # Add message as separate field if not used in description
            if (
                kofi_data.get("message")
                and kofi_data["message"].strip()
                and is_subscription
            ):
                embed.add_field(
                    name=self.t("Message"), value=kofi_data["message"], inline=False
                )

            # Send the message
            await channel.send(embed=embed)
            logger.info(f"Sent Ko-fi notification to channel {channel.name}")

        except Exception as e:
            logger.error(f"Error processing Ko-fi data: {str(e)}")

    def start_webhook_server(self):
        """Start the Flask server in a separate thread"""

        # Create a /dev/null stream for Flask to log to
        class NullStream:
            def write(self, *args, **kwargs):
                pass

            def flush(self, *args, **kwargs):
                pass

        def run_app():
            try:
                # Save old stdout/stderr
                old_stdout = sys.stdout
                old_stderr = sys.stderr

                # Replace with our null stream to silence Flask
                sys.stdout = NullStream()
                sys.stderr = NullStream()

                try:
                    # Run Flask with all output silenced
                    logger.info(
                        f"Starting Ko-fi webhook server on port {self.config['port']}"
                    )
                    self.app.run(
                        host="0.0.0.0", port=self.config["port"], use_reloader=False
                    )
                finally:
                    # Restore stdout/stderr no matter what
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

            except Exception as e:
                logger.error(f"Error running Flask app: {str(e)}")

        self.thread = threading.Thread(target=run_app)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"Ko-fi webhook started")
        logger.info(f"Ko-fi webhook service up and running")

    @commands.Cog.listener()
    async def on_ready(self):
        """Start the webhook server when the bot is ready"""
        if not self.thread or not self.thread.is_alive():
            self.start_webhook_server()
            logger.debug("Ko-fi webhook server started (or restarted)")

    @commands.command(name="kofitest", help="Test the Ko-fi integration")
    @commands.has_permissions(administrator=True)
    async def kofitest(self, ctx):
        """Test the Ko-fi integration by sending a sample notification"""
        try:
            # Create sample Ko-fi data
            kofi_data = {
                "type": "Donation",
                "from_name": "Test User",
                "message": "This is a test donation!",
                "amount": "5.00",
                "currency": "USD",
                "kofi_transaction_id": "TEST123",
                "timestamp": datetime.datetime.utcnow().isoformat(),
            }

            # Process the sample data
            await self.process_kofi_data(kofi_data)

            await ctx.send("Ko-fi test notification sent!")
        except Exception as e:
            logger.error(f"Error sending test notification: {str(e)}")
            await ctx.send(f"Error sending test notification: {str(e)}")


async def setup(bot):
    """Setup function to add the cog."""
    await bot.add_cog(KofiWebhook(bot))
    logger.debug("KofiWebhook cog loaded.")
