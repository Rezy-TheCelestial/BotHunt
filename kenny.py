import os
import sys
import re
import json
import time
import asyncio
import logging
from random import randint
from pathlib import Path

from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError, PhoneCodeInvalidError, PhoneCodeExpiredError, FloodWaitError
from telethon.tl.types import PhotoStrippedSize

from pymongo import MongoClient
import certifi
from datetime import datetime, timezone, timedelta
import pytz

# Keep-alive server import
try:
    from keep_alive import keep_alive
    KEEP_ALIVE_AVAILABLE = True
except ImportError:
    print("⚠️ keep_alive.py not found - running without keep-alive server")
    KEEP_ALIVE_AVAILABLE = False

API_ID = 21453458
API_HASH = '565cac9ed11ff64ca7e2626f7b1b18b2'
BOT_TOKEN = '8275817464:AAGnjwnKXvJ9NrTNE4SEnsZAHs1gm1bLDP8'  
PASSWORD = "kennyurowner"
ADMIN_USER_ID = 5621201759
LOG_CHANNEL_ID = -1002835841460
CATCH_CHAT_ID = "@Hexamonbot"
CATCH_LIST = ["✨","Mewtwo","Eternatus","Xerneas","Yveltal","Zekrom","Dialga","Spectrier","Groudon","Kyurem","Kyogre","Marshadow","Solgaleo","Zacian","Zamazenta"]

AUTO_CATCH_2_LIST = ["Braixen","Delphox","Absol","Cloyster","Sandile","Krokorok","Krookodile","Ferroseed","Ferrothorn","Houndour","Houndoom","Vaporeon","Zoroark","Keldeo","Totodile","Croconaw","Feraligatr","Electrode","Mankey","Primeape","Annihilape","Torracat","Incineroar","Popplio","Brionne","Primarina","Toxapex","Shellder","Weedle","Kakuna","Swablu","Scraggy","Wimpod","Rhyperior","Rhydon","Shelmet","Accelgor","Vullaby","Mandibuzz","Litwick","Lampent","Chandelure","Toxticity","Helioptile","Heliolist","Rungerigus","Cofagrigus","Phantump","Trevenant","Kommo-o","Jangmo-o","Fennekin","Eevee","Buizel","Floatzel","Munchlax","Monferno","Ursaring","Prinplup","Glalie","Mamoswine","Abomasnow","Arceus","Scorbunny","Raboot","Grookey","Dottler","Consvisquire","Corvknight","Rookidee","Mudsdale","Wishiwashi","Boldore","Gigalith","Gurdurr","Flareon","Espeon","Glaceon","Leafeon","Umbreon","Sirfetch'd","Articuno","Arcanine","Zorua","Growlithe","Porygon","Staravia","Jolteon","Sneasler","Sneasel","Basculin","Ursaluna","Samurott","Voltorb","Raichu","Rufflet","Piplup","Infernape","Starly","Litten","Empoleon","Eiscue","Crustle","Dwebble","Decidueye","Quilava","Typhlosion","Shinx","Luxio","Luxray","Cyndaquil","Sylveon","Basculegion","Chimchar","Zapdos","Moltres","Mew","Raikou","Entei","Suicune","Lugia","Ho-Oh","Celebi","Regirock","Regice","Registeel","Latias","Latios","Rayquaza","Jirachi","Deoxys","Uxie","Mesprit","Azelf","Palkia","Heatran","Regigigas","Giratina","Cresselia","Darkrai","Shaymin","Victini","Cobalion","Terrakion","Virizion","Golurk","Golett","Tornadus","Thundurus","Reshiram","Landorus","Meloetta","Genesect","Zygarde","Diancie","Hoopa","Volcanion","Type: Null","Silvally","Tapu Koko","Tapu Lele","Tapu Bulu","Tapu Fini","Cosmog","Cosmoem","Lunala","Nihilego","Buzzwole","Pheromosa","Xurkitree","Celesteela","Kartana","Guzzlord","Necrozma","Magearna","Zeraora","Meltan","Melmetal","Kubfu","Urshifu","Regieleki","Regidrago","Glastrier","Calyrex","Abra","Kadabra","Alakazam","Sharpedo","Machop","Machoke","Machamp","Geodude","Graveler","Golem","Gastly","Haunter","Gengar","Dratini","Dragonair","Dragonite","Larvitar","Pupitar","Tyranitar","Bagon","Shelgon","Salamence","Beldum","Metang","Metagross","Gible","Gabite","Garchomp","Ralts","Kirlia","Gardevoir","Gallade","Magikarp","Gyarados","Charmander","Charmeleon","Charizard","Squirtle","Wartortle","Blastoise","Bulbasaur","Ivysaur","Venusaur","Treecko","Grovyle","Sceptile","Torchic","Combusken","Blaziken","Mudkip","Marshtomp","Swampert","Aron","Lairon","Aggron","Slowpoke","Slowbro","Slowking","Scyther","Scizor","Porygon2","Porygon-Z","Deino","Zweilous","Hydreigon","Axew","Fraxure","Haxorus","Goomy","Sliggoo","Goodra","Dreepy","Drakloak","Dragapult","Froakie","Frogadier","Greninja","Flabébé","Floette","Florges","Buneary","Lopunny","Riolu","Lucario","Slaking","Slakoth","Vigoroth","Mienfoo","Mienshao","Larvesta","Volcarona","Noibat","Noivern","Hakamo-o","Togepi","Togetic","Togekiss","Mareep","Flaaffy","Ampharos","Staryu","Starmie","Staraptor","Braviary","Bisharp","Kingambit","Tinkatink","Tinkatuff","Tinkaton","Fletchling","Fletchinder","Talonflame","Pawniard","Darumaka","Darmanitan","Litleo","Pyroar","Crabrawler","Crabominable","Rockruff","Lycanroc","Poipole","Naganadel","Stakataka","Blacephalon","Thwackey","Rillaboom","Cinderace","Sobble","Drizzile","Inteleon","Cramorant","Arrokuda","Barraskewda","Duraludon","Zarude","Venusaur","Beedrill","Pidgeot","Kangaskhan","Pinsir","Aerodactyl","Steelix","Heracross","Manectric","Camerupt","Altaria","Banette","Glalie","Abomasnow","Audino","Golisopod","✨"]

SAFARI_POKE_LIST = [
    "Mewtwo", "Ho-Oh", "Lugia", "Kyogre", "Groudon", "Jirachi", "Deoxys", "Arceus", "Dialga", "Palkia",
    "Giratina", "Regigigas", "Heatran", "Genesect", "Kyurem", "Reshiram", "Zekrom", "Victini", "Cobalion",
    "Meloetta", "Hoopa", "Diancie", "Zygarde", "Volcanion", "Necrozma", "Zeraora", "Marshadow", "Magearna",
    "Pheromosa", "Buzzwole", "Guzzlord", "Kubfu", "Glastrier", "Spectrier", "Zacian", "Zamazenta", "Eternatus",
    "Celebi","✨", "Rayquaza", "Shaymin", "Yveltal", "Xerneas", "Cosmog", "Cosmoem", "Solgaleo", "Lunala"
]

LEGENDARY_POKEMON = [
    "Mewtwo", "Ho-Oh", "Lugia", "Kyogre", "Groudon", "Jirachi", "Deoxys", "Arceus", "Dialga", "Palkia",
    "Giratina", "Regigigas", "Heatran", "Genesect", "Kyurem", "Reshiram", "Zekrom", "Victini", "Cobalion",
    "Meloetta", "Hoopa", "Diancie", "Zygarde", "Volcanion", "Necrozma", "Zeraora", "Marshadow", "Magearna",
    "Pheromosa", "Buzzwole", "Guzzlord", "Kubfu", "Glastrier", "Spectrier", "Zacian", "Zamazenta", "Eternatus",
    "Celebi", "Rayquaza", "Shaymin", "Yveltal", "Xerneas", "Cosmog", "Cosmoem", "Solgaleo", "Lunala",
    "Articuno", "Zapdos", "Moltres", "Raikou", "Entei", "Suicune", "Regirock", "Regice", "Registeel",
    "Latias", "Latios", "Darkrai", "Cresselia", "Uxie", "Mesprit", "Azelf", "Tornadus", "Thundurus",
    "Landorus", "Tapu Koko", "Tapu Lele", "Tapu Bulu", "Tapu Fini", "Nihilego", "Kartana", "Celesteela",
    "Xurkitree", "Guzzlord", "Meltan", "Melmetal", "Urshifu", "Regieleki", "Regidrago", "Calyrex"
]

POKEMON_NATURES = {
    "page1": {
        "title": "🌙 Best Natures For Non-Legendary Pokemon (Page 1)",
        "image": "https://postimg.cc/cvRp7h2N",
        "content": {
            "KANTO": {
                "Venusaur": "Sassy, Modest, Quiet",
                "Charizard [X,Y]": "Timid, Jolly",
                "Blastoise": "Sassy, Modest, Bold",
                "Beedrill": "Jolly, Adamant",
                "Pidgeot [Mega]": "Timid, Modest",
                "Arcanine": "Jolly, Adamant",
                "Alakazam [Mega]": "Timid, Modest",
                "Slowbro [Mega]": "Bold, Modest, Quiet, Relaxed",
                "Gengar [Mega]": "Timid, Modest",
                "Electrode": "Timid, Modest",
                "Kangaskhan [Mega]": "Adamant",
                "Pinsir [Mega]": "Adamant",
                "Gyarados [Mega]": "Adamant, Sassy",
                "Vaporeon": "Modest, Calm, Bold",
                "Jolteon": "Timid",
                "Flareon": "Adamant, Impish, Careful",
                "Aerodactyl": "Jolly, Adamant",
                "Snorlax": "Careful, Adamant",
                "Dragonite": "Adamant, Impish",
                "Lapras": "Modest, Quiet, Sassy, Calm",
                "Dugtrio": "Jolly"
            },
            "JOHTO": {
                "Typhlosion": "Timid",
                "Feraligatr": "Adamant, Impish",
                "Ampharos [Mega]": "Modest, Calm, Bold",
                "Scizor [Mega]": "Adamant, Impish",
                "Heracross": "Adamant, Jolly",
                "Espeon": "Timid",
                "Houndoom [Mega]": "Modest",
                "Tyranitar": "Adamant, Impish"
            }
        }
    },
    "page2": {
        "title": "🌙 Best Natures For Some Non-Legendary Pokemons (Page 2)",
        "image": "https://graph.org/file/81c916256eae182bd514a.jpg",
        "content": {
            "HOENN": {
                "Sceptile [mega]": "timid",
                "Blaziken [mega]": "adamant, jolly",
                "Swampert": "adamant",
                "Ludicolo": "sassy, calm",
                "Gardevoir": "modest, timid",
                "Slaking": "adamant, jolly with focus punch",
                "Ninjask": "jolly",
                "Aggron": "impish, adamant",
                "Camerupt": "modest, bold, calm",
                "Altaria": "modest, bold",
                "Salamence": "jolly, adamant",
                "Metagross": "adamant, jolly, impish",
                "Gallade": "jolly",
                "Sharpedo [mega]": "adamant, jolly",
                "Sableye [mega]": "sassy, relaxed",
                "Mawile [mega]": "adamant, impish",
                "Manectric [mega]": "timid, modest",
                "Banette [mega]": "adamant",
                "Absol": "jolly, adamant"
            },
            "SINNOH": {
                "Infernape": "adamant, jolly",
                "Empoleon": "sassy, calm, modest",
                "Steelix": "impish, adamant, relaxed, brave",
                "Lopunny": "adamant, jolly",
                "Medicham": "adamant, jolly",
                "Garchomp": "adamant",
                "Lucario": "adamant, jolly",
                "Leafeon": "adamant, impish, jolly",
                "Glaceon": "modest, calm, bold",
                "Rhyperior": "adamant, impish, relaxed, brave",
                "Porygon-Z": "timid, modest",
                "Weavile": "jolly, adamant"
            }
        }
    },
    "page3": {
        "title": "🌙 Best Natures For Some Non-Legendary Pokemons (Page 3)",
        "image": "https://graph.org/file/2ac0b8e945b8cb4faf239.jpg",
        "content": {
            "UNOVA": {
                "Gigalith": "impish, adamant",
                "Excadrill": "adamant",
                "Conkeldurr": "adamant, impish",
                "Scolipede": "adamant, jolly",
                "Krookodile": "adamant, jolly",
                "Darmanitan [zen]": "modest, bold, calm",
                "Scrafty": "adamant",
                "Cofagrigus": "bold, relaxed, sassy, calm",
                "Archeops": "adamant, jolly",
                "Escavalier": "adamant",
                "Haxorus": "adamant",
                "Beartic": "adamant",
                "Accelgor": "timid, modest",
                "Mienshao": "adamant, jolly",
                "Golurk": "adamant",
                "Bisharp": "adamant, impish",
                "Volcarona": "modest",
                "Crustle": "adamant, impish",
                "Druddigon": "adamant"
            },
            "KALOS": {
                "Chesnaught": "adamant, impish but flying 4x",
                "Greninja": "timid, jolly",
                "Tyrantrum": "adamant, impish",
                "Goodra": "sassy, careful, adamant",
                "Avalugg": "impish, adamant",
                "Florges": "sassy, modest, calm, quiet",
                "Sylveon": "modest, calm, bold",
                "Hawlucha": "jolly"
            },
            "ALOLA": {
                "Decidueye": "modest, sassy, quiet, calm",
                "Incineroar": "adamant",
                "Primarina": "sassy, quiet, modest, calm",
                "Vikavolt": "modest, quiet",
                "Lycanroc [dusk]": "adamant, jolly",
                "Mudsdale": "adamant, impish",
                "Passimian": "adamant, impish",
                "Golisopod": "adamant, impish",
                "Kommo-o": "adamant, careful, impish"
            }
        }
    },
    "legendary_page1": {
        "title": "☀️ Best Natures For Legendary Pokes (Page 1)",
        "image": "https://graph.org/file/ad5bb0c9de6a42fb2c8d6.jpg",
        "content": {
            "Normal Mewtwo/Mega Mewtwo Y": "Modest and Timid",
            "Mega Mewtwo X": "Adamant and Jolly",
            "Mew": "Modest and Timid",
            "Articuno": "Careful",
            "Zapdos": "Modest",
            "Moltres": "Modest",
            "Celebi": "Modest and Quite",
            "Ho-oH": "Careful and Adamant",
            "Lugia": "Careful and Jolly",
            "Raikou": "Timid",
            "Entei": "Adamant",
            "Suicune": "Careful",
            "Jirachi": "Modest",
            "Groudon": "Adamant",
            "Kyogre": "Modest",
            "Rayquaza": "Adamant",
            "Deoxys Normal Form": "Timid and Modest",
            "Deoxys Attack Form": "Modest",
            "Deoxys Defence Form": "Relaxed",
            "Deoxys Speed Form": "Timid"
        }
    },
    "legendary_page2": {
        "title": "☀️ Best Natures For Legendary Pokes (Page 2)",
        "image": "https://graph.org/file/ad5bb0c9de6a42fb2c8d6.jpg",
        "content": {
            "Regirock": "Relaxed",
            "Registeel": "Sassy,Relaxed",
            "Regice": "Calm , Careful",
            "Latias": "Calm",
            "Latios": "Modest",
            "Arceus": "Modest and Timid",
            "Dialga": "Modest",
            "Giratina": "Brave and Adamant",
            "Palkia": "Modest and Timid",
            "Regigigas": "Jolly and Adamant",
            "Darkrai": "Modest and Timid",
            "Reshiram": "Modest",
            "Zekrom": "Adamant",
            "Black Kyurem": "Adamant",
            "White Kyurem": "Modest",
            "Victini": "Adamant",
            "Normal Kyurem": "Adamant and Modest"
        }
    },
    "legendary_page3": {
        "title": "☀️ Best Natures For Legendary Pokes (Page 3)",
        "image": "https://graph.org/file/ad5bb0c9de6a42fb2c8d6.jpg",
        "content": {
            "Hoopa Confined": "Modest and Quite",
            "Hoopa Unbound": "Modest and Quite",
            "Diancie": "Relaxed and Sassy",
            "Volcanion": "Modest",
            "Xerneas and Yveltal": "Modest If you are training spa, Adamant if you are training Attack",
            "Zygarde 10%": "Jolly",
            "Zygarde 100%": "Adamant and Careful",
            "Ultra Necrozma": "Modest and Timid",
            "Dusk Mane Necrozma": "Adamant and Brave",
            "Dawn Wings Necrozma": "Quite and Modest",
            "Normal Necrozma": "Modest and Quite",
            "Solgaleo": "Adamant",
            "Lunala": "Modest",
            "Zeraora": "Jolly",
            "Marshadow": "Adamant and Jolly",
            "Pheromosa": "Jolly"
        }
    }
}

MONGO_URI = "mongodb+srv://pokemon_bot_user:PokemonBot2024!Secure@cluster0pokemon-bot-clu.iveqoue.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0pokemon-bot-cluster"
DB_NAME = "pokemon_guess_bot"
USERS_COLL = "Authusers"
ACCOUNTS_COLL = "Accounts"
USER_SETTINGS_COLL = "UserSettings"
BANNED_USERS_COLL = "BannedUsers"
BOT_STATS_COLL = "BotStats"
USER_STATS_COLL = "UserStats"
ACCOUNT_FINDINGS_COLL = "AccountFindings"
GENERAL_USERS_COLL = "Users"

SESSION_NAME = "hexamon_bot_telethon"
SESSIONS_DIR = "saitama"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

os.makedirs("cache", exist_ok=True)
os.makedirs("saitama", exist_ok=True)

try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    client.admin.command('ping')  
    db = client[DB_NAME]
    print("✅ MongoDB connection successful!")
    
    users_col = db[USERS_COLL]
    accounts_col = db[ACCOUNTS_COLL]
    user_settings_col = db[USER_SETTINGS_COLL]
    banned_users_col = db[BANNED_USERS_COLL]
    bot_stats_col = db[BOT_STATS_COLL]
    user_stats_col = db[USER_STATS_COLL]
    account_findings_col = db[ACCOUNT_FINDINGS_COLL]
    general_users_col = db[GENERAL_USERS_COLL]
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("🔄 Using fallback mode - bot will run with limited functionality")
    
    class FallbackCollection:
        def find_one(self, *args, **kwargs): return None
        def find(self, *args, **kwargs): return []
        def update_one(self, *args, **kwargs): return None
        def insert_one(self, *args, **kwargs): return None
        def delete_one(self, *args, **kwargs): return None
        def count_documents(self, *args, **kwargs): return 0
    
    users_col = FallbackCollection()
    accounts_col = FallbackCollection()
    user_settings_col = FallbackCollection()
    banned_users_col = FallbackCollection()
    bot_stats_col = FallbackCollection()
    user_stats_col = FallbackCollection()
    account_findings_col = FallbackCollection()
    general_users_col = FallbackCollection()
hunt_status = {}
bot_start_time = time.time()  
def load_authorized_users():
    try:
        docs = list(users_col.find({}, {"_id": 0, "user_id": 1}))
        authorized_users = set()
        
        for d in docs:
            user_id = d.get("user_id")
            if user_id is not None:
                if isinstance(user_id, list):
                    if user_id and isinstance(user_id[0], int):
                        authorized_users.add(user_id[0])
                        users_col.update_one({"user_id": user_id}, {"$set": {"user_id": user_id[0]}})
                elif isinstance(user_id, int):
                    authorized_users.add(user_id)
                else:
                    try:
                        authorized_users.add(int(user_id))
                        users_col.update_one({"user_id": user_id}, {"$set": {"user_id": int(user_id)}})
                    except (ValueError, TypeError):
                        print(f"Warning: Invalid user_id format in database: {user_id}")
        
        return authorized_users
    except Exception as e:
        print(f"Warning: Could not load authorized users: {e}")
        return set()

def save_authorized_user(uid: int):
    try:
        users_col.update_one({"user_id": uid}, {"$set": {"user_id": uid}}, upsert=True)
    except Exception as e:
        print(f"Warning: Could not save authorized user: {e}")

AUTHORIZED_USERS = load_authorized_users()
if ADMIN_USER_ID not in AUTHORIZED_USERS:
    AUTHORIZED_USERS.add(ADMIN_USER_ID)
    save_authorized_user(ADMIN_USER_ID)

def authorized_only(func):
    async def wrapper(event):
        if not is_bot_command(event):
            return
            
        uid = event.sender_id
        if uid not in AUTHORIZED_USERS:
            await event.reply("❌ You are not authorized to use this command.")
            return
        if is_user_banned(uid):
            await event.reply("❌ You have been banned from using this bot.")
            return
        return await func(event)
    return wrapper

def is_user_banned(user_id: int) -> bool:
    """Check if a user is banned."""
    return banned_users_col.find_one({"user_id": user_id}) is not None

def is_authorized(user_id: int) -> bool:
    """Check if user is authorized."""
    return user_id in AUTHORIZED_USERS and not is_user_banned(user_id)

def is_bot_command(event) -> bool:
    """Check if the command is meant for this bot."""
    text = event.message.text or ""
    
    if not text.startswith('/'):
        return False
    
    if '@' in text:
        command_part = text.split()[0]  
        if '@' in command_part:
            bot_mention = command_part.split('@')[1]
            return bot_mention.lower() in ['hexa_mine_bot']
    
    return True

def get_user_ball_type(user_id: int) -> str:
    """Get user's preferred ball type."""
    settings = get_user_settings(user_id)
    return settings.get('ball_type', 'Ultra Ball')

def ban_user(user_id: int, reason: str = "No reason provided"):
    """Ban a user."""
    banned_users_col.update_one(
        {"user_id": user_id}, 
        {"$set": {"user_id": user_id, "reason": reason, "banned_at": time.time()}}, 
        upsert=True
    )

def unban_user(user_id: int):
    """Unban a user."""
    banned_users_col.delete_one({"user_id": user_id})

def get_user_settings(user_id: int) -> dict:
    """Get user settings or create default ones."""
    settings = user_settings_col.find_one({"user_id": user_id})
    if not settings:
        default_settings = {
            "user_id": user_id,
            "ball_type": "Ultra Ball",
            "auto_catch_1_list": CATCH_LIST.copy(),
            "auto_catch_2_list": AUTO_CATCH_2_LIST.copy(),
            "auto_catch_1_min_balls": 10,
            "auto_catch_2_min_balls": 200,
            "auto_buy_balls": True,
            "max_balls_to_buy": 50,
            "private_group_id": None,
            "created_at": time.time()
        }
        user_settings_col.insert_one(default_settings)
        return default_settings
    return settings

def update_user_settings(user_id: int, updates: dict):
    """Update user settings."""
    user_settings_col.update_one(
        {"user_id": user_id}, 
        {"$set": {**updates, "updated_at": time.time()}}, 
        upsert=True
    )

def add_pokemon_to_list(user_id: int, pokemon_name: str, list_type: str) -> bool:
    """Add pokemon to user's catch list."""
    settings = get_user_settings(user_id)
    list_key = f"auto_catch_{list_type}_list"
    
    if list_key not in settings:
        return False
    
    if pokemon_name not in settings[list_key]:
        settings[list_key].append(pokemon_name)
        update_user_settings(user_id, {list_key: settings[list_key]})
        return True
    return False

def remove_pokemon_from_list(user_id: int, pokemon_name: str, list_type: str) -> bool:
    """Remove pokemon from user's catch list."""
    settings = get_user_settings(user_id)
    list_key = f"auto_catch_{list_type}_list"
    
    if list_key not in settings:
        return False
    
    if pokemon_name in settings[list_key]:
        settings[list_key].remove(pokemon_name)
        update_user_settings(user_id, {list_key: settings[list_key]})
        return True
    return False

def generate_account_id():
    """Generate a unique account ID."""
    import random
    import string
    while True:
        account_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        if not accounts_col.find_one({"account_id": account_id}):
            return account_id

def migrate_existing_accounts():
    """Assign Account IDs to existing accounts that don't have them."""
    try:
        accounts_without_id = accounts_col.find({"account_id": {"$exists": False}})
        updated_count = 0
        
        for account in accounts_without_id:
            account_id = generate_account_id()
            accounts_col.update_one(
                {"_id": account["_id"]}, 
                {"$set": {"account_id": account_id}}
            )
            updated_count += 1
            print(f"✅ Assigned Account ID '{account_id}' to phone {account.get('phone', 'Unknown')}")
        
        if updated_count > 0:
            print(f"🔄 Migration complete: {updated_count} accounts updated with Account IDs")
        else:
            print("✅ All accounts already have Account IDs")
            
    except Exception as e:
        print(f"❌ Error during account migration: {e}")

def get_utc_time():
    """Get current UTC time."""
    return datetime.now(UTC)

def is_guess_limit_reached(message_text):
    """Check if guess limit is reached based on message content."""
    return "guessed in" in message_text and "+5 💵" not in message_text

def is_daily_hunt_limit_reached(message_text):
    """Check if daily hunt limit is reached."""
    return "Daily hunt limit reached" in message_text

async def smart_sequence_manager(client, phone, user_id):
    """Manage the smart sequence for a single account."""
    print(f"🤖 [{phone}] Starting smart sequence manager")
    
    while phone in smart_sequence_tasks:
        try:
            current_time = get_utc_time()
            
            if phone not in account_states:
                account_states[phone] = {
                    "state": "waiting",
                    "next_action_time": current_time.replace(hour=13, minute=0, second=0, microsecond=0),  
                    "daily_stats": {"tms": 0, "pokes": 0, "shinies": 0}
                }
            
            state = account_states[phone]
            
            if current_time >= state["next_action_time"]:
                if state["state"] == "waiting":
                    if current_time.hour == 12 and current_time.minute >= 55:
                        await generate_daily_logs()
                    
                    await start_guess_for_account(client, phone, user_id)
                    state["state"] = "guessing"
                    
                elif state["state"] == "safari_wait":
                    await start_auto_catch_for_account(client, phone, user_id)
                    state["state"] = "catching"
            
            await asyncio.sleep(30)
            
        except asyncio.CancelledError:
            print(f"🛑 [{phone}] Smart sequence manager cancelled")
            break
        except Exception as e:
            print(f"❌ [{phone}] Error in smart sequence manager: {e}")
            await asyncio.sleep(60)  

async def start_guess_for_account(client, phone, user_id):
    """Start guessing for a specific account."""
    try:
        account = accounts_col.find_one({"phone": phone})
        if not account:
            return
        
        chat_id = account['chat_id']
        
        task = asyncio.create_task(smart_guessing_logic(client, chat_id, phone, user_id))
        account_tasks[phone] = task
        accounts_col.update_one({"phone": phone}, {"$set": {"active": True}})
        
        print(f"🎯 [{phone}] Started auto guess at {get_utc_time()}")
        
    except Exception as e:
        print(f"❌ [{phone}] Error starting guess: {e}")

async def start_safari_for_account(client, phone, user_id):
    """Start safari for a specific account."""
    try:
        account = accounts_col.find_one({"phone": phone})
        if not account:
            return
        
        chat_id = account['chat_id']
        
        task = asyncio.create_task(smart_safari_logic(client, chat_id, phone, user_id))
        safari_tasks[phone] = task
        accounts_col.update_one({"phone": phone}, {"$set": {"active": True}})
        
        print(f"🦁 [{phone}] Started auto safari at {get_utc_time()}")
        
    except Exception as e:
        print(f"❌ [{phone}] Error starting safari: {e}")

async def start_auto_catch_for_account(client, phone, user_id):
    """Start auto catch for a specific account."""
    try:
        task = asyncio.create_task(smart_auto_catch_logic(client, phone, user_id))
        auto_catch_tasks[phone] = task
        accounts_col.update_one({"phone": phone}, {"$set": {"active": True}})
        
        print(f"🎣 [{phone}] Started auto catch at {get_utc_time()}")
        
    except Exception as e:
        print(f"❌ [{phone}] Error starting auto catch: {e}")

async def smart_guessing_logic(client, chat_id, phone, user_id):
    """Smart guessing logic that detects limit and switches to safari."""
    print(f"🎯 [{phone}] Starting smart guessing logic")
    
    monitoring = True
    
    async def check_guess_result(event):
        nonlocal monitoring
        if not monitoring:
            return
            
        message_text = event.message.text or ''
        
        if is_guess_limit_reached(message_text):
            print(f"🚫 [{phone}] Guess limit reached, switching to safari")
            monitoring = False
            
            if phone in account_tasks:
                try:
                    account_tasks[phone].cancel()
                    del account_tasks[phone]
                except:
                    pass
            
            if phone in account_states:
                account_states[phone]["state"] = "safari"
            
            await start_safari_for_account(client, phone, user_id)
    
    client.add_event_handler(check_guess_result, events.NewMessage(chats=chat_id, pattern="guessed in", incoming=True))
    
    try:
        await guessing_logic(client, chat_id, phone)
    except asyncio.CancelledError:
        print(f"🛑 [{phone}] Smart guessing cancelled")
    finally:
        monitoring = False
        try:
            client.remove_event_handler(check_guess_result)
        except:
            pass

async def smart_safari_logic(client, chat_id, phone, user_id):
    """Smart safari logic that schedules auto catch after completion."""
    print(f"🦁 [{phone}] Starting smart safari logic")
    
    monitoring = True
    
    async def check_safari_completion(event):
        nonlocal monitoring
        if not monitoring:
            return
            
        message_text = event.message.text or ''
        text_l = message_text.lower()
        
        if ("you have run out of safari balls" in text_l and "are now exiting" in text_l) or "you were kicked" in text_l:
            print(f"✅ [{phone}] Safari completed, scheduling auto catch in 10 minutes")
            monitoring = False
            
            if phone in safari_tasks:
                try:
                    safari_tasks[phone].cancel()
                    del safari_tasks[phone]
                except:
                    pass
            
            import random
            wait_minutes = random.randint(10, 20)
            next_time = get_utc_time() + timedelta(minutes=wait_minutes)
            print(f"⏰ [{phone}] Scheduled auto catch in {wait_minutes} minutes")
            if phone in account_states:
                account_states[phone]["state"] = "safari_wait"
                account_states[phone]["next_action_time"] = next_time
    
    client.add_event_handler(check_safari_completion, events.NewMessage(chats=chat_id, incoming=True))
    
    try:
        await safari_logic(client, chat_id, phone, user_id)
    except asyncio.CancelledError:
        print(f"🛑 [{phone}] Smart safari cancelled")
    finally:
        monitoring = False
        try:
            client.remove_event_handler(check_safari_completion)
        except:
            pass

async def smart_auto_catch_logic(client, phone, user_id):
    """Smart auto catch logic that detects daily limit and completes the day."""
    print(f"🎣 [{phone}] Starting smart auto catch logic")
    
    monitoring = True
    
    async def check_daily_limit(event):
        nonlocal monitoring
        if not monitoring:
            return
            
        message_text = event.message.text or ''
        
        if is_daily_hunt_limit_reached(message_text):
            print(f"🏁 [{phone}] Daily hunt limit reached, completing day")
            monitoring = False
            
            if phone in auto_catch_tasks:
                try:
                    auto_catch_tasks[phone].cancel()
                    del auto_catch_tasks[phone]
                except:
                    pass
            
            if phone in account_states:
                account_states[phone]["state"] = "completed"
                daily_logs["completed_accounts"] += 1
                
                tomorrow = get_utc_time() + timedelta(days=1)
                next_time = tomorrow.replace(hour=13, minute=0, second=0, microsecond=0)
                account_states[phone]["next_action_time"] = next_time
                account_states[phone]["state"] = "waiting"
                
                print(f"📅 [{phone}] Scheduled for next day at {next_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    client.add_event_handler(check_daily_limit, events.NewMessage(chats=CATCH_CHAT_ID, incoming=True))
    
    try:
        await auto_catch_logic_with_list(client, phone, CATCH_LIST, get_user_ball_type(user_id), 50)
    except asyncio.CancelledError:
        print(f"🛑 [{phone}] Smart auto catch cancelled")
    finally:
        monitoring = False
        try:
            client.remove_event_handler(check_daily_limit)
        except:
            pass

async def start_smart_sequence_all(event, user_id, accounts):
    """Start smart sequence for all accounts."""
    try:
        account_clients = await get_account_clients(user_id)
        if not account_clients:
            await event.edit("❌ No active clients found. Please log in to your accounts first.")
            return

        started_count = 0
        failed_accounts = []

        for account in accounts:
            phone = account['phone']
            
            if phone not in account_clients:
                failed_accounts.append(phone)
                continue

            client_obj = account_clients[phone]
            
            try:
                if not client_obj.is_connected():
                    await client_obj.connect()
                
                if not await client_obj.is_user_authorized():
                    failed_accounts.append(phone)
                    continue

                task = asyncio.create_task(smart_sequence_manager(client_obj, phone, user_id))
                smart_sequence_tasks[phone] = task
                started_count += 1
                
                print(f"🤖 [{phone}] Smart sequence started")

            except Exception as e:
                print(f"Error starting smart sequence for {phone}: {e}")
                failed_accounts.append(phone)

        daily_logs["tms"] = 0
        daily_logs["pokes"] = 0
        daily_logs["shinies"] = 0
        daily_logs["completed_accounts"] = 0

        success_msg = f"🤖 **Smart Sequence Started**\n\n"
        success_msg += f"✅ **Started:** {started_count} accounts\n"
        
        if failed_accounts:
            success_msg += f"❌ **Failed:** {len(failed_accounts)} accounts\n"
        
        success_msg += f"\n📅 **Schedule:**\n"
        success_msg += f"🎯 **1:00 PM UTC** - Auto Guess starts\n"
        success_msg += f"🦁 **After guess limit** - Auto Safari\n"
        success_msg += f"🎣 **Safari + 10min** - Auto Catch\n"
        success_msg += f"🔄 **Repeats daily** until stopped\n\n"
        success_msg += f"⏰ **Current UTC Time:** {get_utc_time().strftime('%H:%M:%S')}"

        await event.edit(success_msg)

    except Exception as e:
        await event.edit(f"❌ Error starting smart sequence: {str(e)}")
        print(f"Error in start_smart_sequence_all: {e}")

async def generate_daily_logs():
    """Generate and send daily logs before starting new day."""
    try:
        current_time = get_utc_time()
        
        today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_start_str = today_start.isoformat()
        
        today_tms = account_findings_col.count_documents({
            "item_type": "tm",
            "timestamp": {"$gte": today_start_str}
        })
        
        today_shinies = account_findings_col.count_documents({
            "item_type": "shiny", 
            "timestamp": {"$gte": today_start_str}
        })
        
        today_pokes = account_findings_col.count_documents({
            "item_type": "pokemon",
            "timestamp": {"$gte": today_start_str}
        })
        
        completed_accounts = len([phone for phone, state in account_states.items() 
                                if state.get("state") == "completed"])
        
        log_msg = (
            f"📊 **Daily Logs - {current_time.strftime('%Y-%m-%d')}**\n\n"
            f"💿 **Total TMs found:** `{today_tms}`\n"
            f"🐾 **Total Pokes Caught:** `{today_pokes}`\n"
            f"✨ **Total Shinies Caught:** `{today_shinies}`\n\n"
            f"✅ **Total accounts that finished Today's task:** `{completed_accounts}`\n\n"
            f"⏰ **Generated at:** `{current_time.strftime('%H:%M:%S UTC')}`"
        )
        
        await bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="markdown")
        print(f"📊 Daily logs generated and sent")
        
    except Exception as e:
        print(f"❌ Error generating daily logs: {e}")

def get_bot_stats():
    """Get bot statistics."""
    total_users = users_col.count_documents({})
    total_accounts = accounts_col.count_documents({})
    active_accounts = accounts_col.count_documents({"active": True})
    banned_users = banned_users_col.count_documents({})
    
    total_shinies = account_findings_col.count_documents({"item_type": "shiny"})
    total_legendaries = account_findings_col.count_documents({"item_type": "pokemon", "item_name": {"$in": LEGENDARY_POKEMON}})
    total_mega_stones = account_findings_col.count_documents({"item_name": {"$regex": ".*Mega Stone.*", "$options": "i"}})
    total_tms = account_findings_col.count_documents({"item_type": "tm"})
    
    uptime = time.time() - bot_start_time
    uptime_hours = int(uptime // 3600)
    uptime_minutes = int((uptime % 3600) // 60)
    
    return {
        "total_users": total_users,
        "total_accounts": total_accounts,
        "active_accounts": active_accounts,
        "banned_users": banned_users,
        "uptime_hours": uptime_hours,
        "uptime_minutes": uptime_minutes,
        "total_shinies": total_shinies,
        "total_legendaries": total_legendaries,
        "total_mega_stones": total_mega_stones,
        "total_tms": total_tms
    }

def record_account_finding(phone: str, user_id: int, item_type: str, item_name: str, account_username: str = "Unknown"):
    """Record when an account finds something special."""
    utc_time = get_utc_time()
    finding = {
        "phone": phone,
        "user_id": user_id,
        "account_username": account_username,
        "item_type": item_type,  
        "item_name": item_name,
        "timestamp": utc_time.isoformat(),
        "date": utc_time.strftime('%Y-%m-%d %H:%M:%S UTC')
    }
    account_findings_col.insert_one(finding)
    
    if item_type == "tm":
        daily_logs["tms"] += 1
    elif item_type == "shiny":
        daily_logs["shinies"] += 1
    elif item_type == "pokemon":
        daily_logs["pokes"] += 1

def get_user_account_stats(user_id: int):
    """Get statistics for all accounts owned by a user."""
    user_accounts = list(accounts_col.find({"user_id": user_id}))
    phone_numbers = [acc["phone"] for acc in user_accounts]
    
    if not phone_numbers:
        return {
            "total_accounts": 0,
            "shinies": 0,
            "tms": 0,
            "mega_stones": 0,
            "pokemon_caught": 0,
            "poke_dollars": 0,
            "findings": []
        }
    
    findings = list(account_findings_col.find({"phone": {"$in": phone_numbers}}))
    
    stats = {
        "total_accounts": len(user_accounts),
        "shinies": len([f for f in findings if f["item_type"] == "shiny"]),
        "tms": len([f for f in findings if f["item_type"] == "tm"]),
        "mega_stones": len([f for f in findings if f["item_type"] == "mega_stone"]),
        "pokemon_caught": len([f for f in findings if f["item_type"] == "pokemon"]),
        "poke_dollars": sum([int(f.get("item_name", "0")) for f in findings if f["item_type"] == "pd"]),
        "findings": findings[-10:]  
    }
    
    return stats

bot = TelegramClient(SESSION_NAME, API_ID, API_HASH).start(bot_token=BOT_TOKEN)

account_clients = {}   
account_tasks = {}     
auto_catch_tasks = {}  
safari_tasks = {}      
daily_limits = {}      
limit_timers = {}      
login_states = {}      
giveme_states = {}     
hunt_status = {}     

smart_sequence_tasks = {}  
account_states = {}  
daily_logs = {"tms": 0, "pokes": 0, "shinies": 0, "completed_accounts": 0}
UTC = pytz.UTC

@bot.on(events.NewMessage(pattern=r'^\.giveme\s+(\d+)$'))
async def giveme_cmd(event):
    """Admin command to make all accounts send /give {amount}"""
    if not is_bot_command(event):
        return
    if event.sender_id != ADMIN_USER_ID:
        return

    try:
        amount = int(event.pattern_match.group(1))
    except (ValueError, IndexError):
        await event.reply("❌ Invalid format. Use: .giveme <amount>")
        return

    accounts = list(accounts_col.find({}, {"phone": 1, "session_string": 1, "chat_id": 1}))
    if not accounts:
        await event.reply("❌ No accounts found in database.")
        return

    account_clients = await get_account_clients()  

    successful_sends, failed_sends = 0, 0
    await event.reply(f"🎯 Sending /give {amount} from {len(accounts)} accounts...")

    for acc in accounts:
        phone = acc.get("phone")
        chat_id = acc.get("chat_id")
        client = account_clients.get(phone)
        try:
            if client is None:
                client = await ensure_user_client(phone, acc.get("session_string"))

            if not client.is_connected():
                await client.connect()
            if not await client.is_user_authorized():
                await event.reply(f"⚠️ Unauthorized session: {phone}")
                failed_sends += 1
                continue

            try:
                entity = await client.get_entity(chat_id)
            except Exception:
                entity = chat_id

            success = await send_give_with_confirmation(client, entity, amount, phone)
            if success:
                successful_sends += 1
            else:
                failed_sends += 1

            await asyncio.sleep(3)

        except FloodWaitError as fw:
            failed_sends += 1
            print(f"FloodWait for {phone}: {fw}")
            await asyncio.sleep(fw.seconds)
        except Exception as e:
            failed_sends += 1
            print(f"Failed to send from {phone}: {e}")

    summary = (
        f"✅ Give command completed!\n"
        f"📤 Successful: {successful_sends}\n"
        f"❌ Failed: {failed_sends}\n"
        f"💰 Amount: {amount}"
    )
    await event.reply(summary)


@bot.on(events.NewMessage(pattern=r'^/msend\s+(.+?)(?:\s+([a-z0-9]{6}))?$'))
async def msend_cmd(event):
    """Admin command to make accounts send custom messages in the group"""
    if not is_bot_command(event):
        return
    if event.sender_id != ADMIN_USER_ID:
        return

    if event.is_private:
        await event.reply("❌ This command must be used in a group!")
        return

    message_to_send = event.pattern_match.group(1).strip()
    account_id = event.pattern_match.group(2)
    group_id = event.chat_id
    
    if not message_to_send:
        await event.reply("❌ Invalid format. Use: /msend <message> [account_id]")
        return

    if account_id:
        account = accounts_col.find_one({"account_id": account_id})
        if not account:
            await event.reply(f"❌ Account with ID '{account_id}' not found.")
            return
        
        accounts = [account]
        await event.reply(f"📤 Sending '{message_to_send}' from account {account_id} to this group...")
    else:
        accounts = list(accounts_col.find({}, {"phone": 1, "session_string": 1, "account_id": 1}))
        if not accounts:
            await event.reply("❌ No accounts found in database.")
            return
        
        await event.reply(f"📤 Sending '{message_to_send}' from {len(accounts)} accounts to this group...")

    account_clients = await get_account_clients()
    successful_sends, failed_sends = 0, 0

    for acc in accounts:
        phone = acc.get("phone")
        acc_id = acc.get("account_id", "unknown")
        client = account_clients.get(phone)
        
        try:
            if client is None:
                client = await ensure_user_client(phone, acc.get("session_string"))

            if not client.is_connected():
                await client.connect()
            if not await client.is_user_authorized():
                print(f"⚠️ Unauthorized session: {acc_id}")
                failed_sends += 1
                continue

            await client.send_message(group_id, message_to_send)
            print(f"✅ [{acc_id}] Sent to group: {message_to_send}")
            successful_sends += 1

            if not account_id:  
                await asyncio.sleep(randint(1, 2))

        except FloodWaitError as fw:
            failed_sends += 1
            print(f"FloodWait for {acc_id}: {fw}")
            await asyncio.sleep(fw.seconds)
        except Exception as e:
            failed_sends += 1
            print(f"Failed to send from {acc_id}: {e}")

    summary = (
        f"✅ Message send completed!\n"
        f"📤 Successful: {successful_sends}\n"
        f"❌ Failed: {failed_sends}\n"
        f"💬 Message: '{message_to_send}'"
    )
    await event.reply(summary)


@bot.on(events.NewMessage(pattern=r'^/giveme\s+(\d+)$'))
@authorized_only
async def user_giveme_start(event):
    uid = event.sender_id
    try:
        amount = int(event.pattern_match.group(1))
    except Exception:
        await event.reply("❌ Usage: /giveme <amount>")
        return
    if not is_private_event(event):
        group_id = event.chat_id
        if uid == ADMIN_USER_ID:
            accounts = list(accounts_col.find({}, {"phone": 1, "session_string": 1}))
            clients = await get_account_clients()  
        else:
            accounts = list(accounts_col.find({"user_id": uid}, {"phone": 1, "session_string": 1}))
            clients = await get_account_clients(uid)
        if not accounts:
            await event.reply("❌ No accounts available.")
            return

        await event.reply(f"🎯 Sending /give {amount} here from {len(accounts)} account(s)...")
        sent, failed = 0, 0
        for acc in accounts:
            phone = acc.get("phone")
            client = clients.get(phone)
            try:
                if client is None:
                    client = await ensure_user_client(phone, acc.get("session_string"))
                if not client.is_connected():
                    await client.connect()
                if not await client.is_user_authorized():
                    failed += 1
                    continue
                try:
                    entity = await client.get_entity(group_id)
                except Exception:
                    entity = group_id
                
                success = await send_give_with_confirmation(client, entity, amount, phone, reply_to=event.message.id)
                if success:
                    sent += 1
                else:
                    failed += 1
                
                await asyncio.sleep(3)
                
            except FloodWaitError as fw:
                print(f"FloodWait for {phone}: {fw}")
                failed += 1
                await asyncio.sleep(fw.seconds)
            except Exception as e:
                print(f"Give from {phone} failed: {e}")
                failed += 1
        await event.reply(f"✅ Done. Successful: {sent} | Failed: {failed}")
        return

    giveme_states[uid] = {"amount": amount, "step": "group_id"}
    await event.reply("🔢 Enter the numeric group ID where your accounts should send /give.")

@bot.on(events.NewMessage(func=lambda e: True))
async def user_giveme_flow(event):
    uid = event.sender_id
    state = giveme_states.get(uid)
    if not state:
        return
    text = (event.raw_text or "").strip()
    if text.startswith('/'):
        return
    if state.get("step") != "group_id":
        return
    try:
        group_id = int(text)
    except ValueError:
        await event.reply("❌ Invalid group ID. Please enter a numeric ID.")
        return

    giveme_states.pop(uid, None)

    accounts = list(accounts_col.find({"user_id": uid}, {"phone": 1, "session_string": 1}))
    if not accounts:
        await event.reply("❌ You have no logged-in accounts.")
        return

    clients = await get_account_clients(uid)

    sent, failed = 0, 0
    amount = state.get("amount", 0)
    await event.reply(f"🎯 Sending /give {amount} to {group_id} from {len(accounts)} of your accounts...")

    for acc in accounts:
        phone = acc.get("phone")
        client = clients.get(phone)
        try:
            if client is None:
                client = await ensure_user_client(phone, acc.get("session_string"))
            if not client.is_connected():
                await client.connect()
            if not await client.is_user_authorized():
                failed += 1
                continue
            try:
                entity = await client.get_entity(group_id)
            except Exception:
                entity = group_id
            
            success = await send_give_with_confirmation(client, entity, amount, phone)
            if success:
                sent += 1
            else:
                failed += 1
            
            await asyncio.sleep(3)
            
        except FloodWaitError as fw:
            print(f"FloodWait for {phone}: {fw}")
            failed += 1
            await asyncio.sleep(fw.seconds)
        except Exception as e:
            print(f"Give from {phone} failed: {e}")
            failed += 1

    await event.reply(f"✅ Done. Successful: {sent} | Failed: {failed}")

async def send_give_with_confirmation(client, entity, amount, phone, reply_to=None, max_retries=3):
    """Send /give command and wait for bot response. Handle different responses appropriately."""
    for attempt in range(max_retries):
        try:
            print(f"[{phone}] Attempt {attempt + 1}: Sending /give {amount}")
            
            if reply_to:
                await client.send_message(entity, f"/give {amount}", reply_to=reply_to)
            else:
                await client.send_message(entity, f"/give {amount}")
            
            response_received = False
            start_time = time.time()
            timeout = 15  
            
            while time.time() - start_time < timeout:
                try:
                    messages = await client.get_messages(entity, limit=5)
                    
                    for msg in messages:
                        if msg.text:
                            msg_text = msg.text.lower()
                            
                            if "poke dollars sent" in msg_text or "poke dollar sent" in msg_text:
                                print(f"[{phone}] ✅ Success: {msg.text}")
                                return True
                            
                            elif "not enough poke dollars" in msg_text or "insufficient" in msg_text:
                                print(f"[{phone}] 💰 Not enough Poke Dollars: {msg.text}")
                                return True  
                            
                            elif any(phrase in msg_text for phrase in [
                                "you don't have enough",
                                "insufficient funds",
                                "not enough money",
                                "balance too low"
                            ]):
                                print(f"[{phone}] 💰 Insufficient balance: {msg.text}")
                                return True  
                    
                    await asyncio.sleep(1)  
                    
                except Exception as e:
                    print(f"[{phone}] Error checking messages: {e}")
                    await asyncio.sleep(1)
            
            print(f"[{phone}] ⚠️ No response received in {timeout}s, attempt {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                await asyncio.sleep(3)  
                    
        except Exception as e:
            print(f"[{phone}] Error in attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(3)
    
    print(f"[{phone}] ❌ No valid response after {max_retries} attempts - skipping account")
    return False  

async def log_message(chat_id, msg):
    """Helper function to log messages to console and admin."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    console_msg = msg.encode('ascii', 'ignore').decode('ascii')
    log_msg = f"[{timestamp}] [Chat {chat_id}] {console_msg}"
    print(log_msg)
    try:
        telegram_log_msg = f"[{timestamp}] [Chat {chat_id}] {msg}"
        await bot.send_message(LOG_CHANNEL_ID, telegram_log_msg)
    except:
        pass

def is_private_event(event):
    """Return True if message is from a private chat to the bot."""
    return event.is_private

async def send_to_admin(text):
    try:
        msg = await bot.send_message(ADMIN_USER_ID, text)
        return msg
    except Exception:
        logger.exception("Failed to notify admin")
        return None


def safe_text(text):
    """Send plain text without relying on HTML parsing — Telethon send_message default is plain text."""
    return text

async def is_task_running(task):
    """Check if an asyncio task is still running."""
    return task and not task.done()

async def notify_account_owner(phone, message):
    """Notify the account owner with a message and pin it."""
    try:
        account = accounts_col.find_one({"phone": phone})
        if not account:
            return
        
        user_id = account.get("user_id")
        if not user_id:
            return
        
        try:
            account_client = account_clients.get(phone)
            account_username = "Unknown"
            account_name = phone
            
            if account_client:
                try:
                    me = await account_client.get_me()
                    account_username = getattr(me, 'username', 'Unknown') or 'Unknown'
                    account_name = getattr(me, 'first_name', phone) or phone
                except:
                    pass
        except:
            account_username = "Unknown"
            account_name = phone
        
        item_type = "pokemon"
        item_name = message
        
        if "shiny" in message.lower() or "✨" in message:
            item_type = "shiny"
        elif "tm" in message.lower():
            item_type = "tm"
        elif "mega stone" in message.lower():
            item_type = "mega_stone"
        elif "poke dollars" in message.lower() or "pd" in message.lower():
            item_type = "pd"
        
        record_account_finding(phone, user_id, item_type, item_name, account_username)
        
        notification = (
            f"🚨 **SPECIAL ITEM FOUND!** 🚨\n\n"
            f"**Account Name:** `{account_name}`\n"
            f"**Account Username:** @{account_username}\n"
            f"**Account ID:** `{phone}`\n\n"
            f"**The item they found:** {message}\n\n"
            f"⚡ **Check your account immediately!**"
        )
        
        msg = await bot.send_message(user_id, notification, parse_mode="markdown")
        try:
            await msg.pin()
        except Exception as pin_error:
            print(f"Could not pin notification for {phone}: {pin_error}")
        
    except Exception as e:
        print(f"Error notifying account owner for {phone}: {e}")

async def get_account_clients(user_id: int | None = None):
    global account_clients
    account_clients = {k: v for k, v in account_clients.items() if hasattr(v, 'is_connected') and v.is_connected()}
    
    query = {} if user_id is None else {"user_id": user_id}
    accounts = list(accounts_col.find(query))
    for acc in accounts:
        phone, session_string = acc['phone'], acc['session_string']
        if phone not in account_clients:
            try:
                client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
                await client.connect()
                if not await client.is_user_authorized():
                    await client.start()
                account_clients[phone] = client
            except Exception as e:
                print(f"Failed to start client for {phone}: {str(e)}")
    
    return account_clients

@bot.on(events.NewMessage(pattern=r'^/start$'))
async def start_handler(event):
    if not is_bot_command(event):
        return
    if not is_private_event(event):
        return  
    user = await event.get_sender()
    user_id = user.id
    first_name = user.first_name or "Not provided"
    username = f"@{user.username}" if getattr(user, 'username', None) else "Not provided"

    general_users_col.update_one({"user_id": user_id}, {"$set": {"user_id": user_id, "username": user.username or str(user_id)}}, upsert=True)

    info_text = (
        f"User {username} started the bot\n"
        f"Name: {first_name}\n"
        f"Username: {username}\n"
        f"User ID: {user_id}"
    )
    reply_msg = await event.reply(info_text)
    
    try:
        await reply_msg.pin()
    except Exception as e:
        print(f"Could not pin message for {username}: {e}")

    if user_id not in AUTHORIZED_USERS:
        admin_text = (
            f"🔔 UNAUTHORIZED USER STARTED BOT\n"
            f"User {username} started the bot\n"
            f"Name: {first_name}\n"
            f"Username: {username}\n"
            f"User ID: {user_id}\n\n"
            f"Use /auth add {user_id} to authorize the user."
        )
        admin_msg = await send_to_admin(admin_text)
        try:
            if admin_msg:
                await admin_msg.pin()
        except Exception as e:
            print(f"Could not pin admin notification: {e}")
            
        await event.reply("ℹ️ Your details were sent to the admin for approval.")
    else:
        welcome_msg = await event.reply("👋 Welcome! Use /help to see commands.")
            
        print(f"Authorized user {username} ({user_id}) started the bot")

@bot.on(events.NewMessage(pattern=r'^/help$'))
@authorized_only
async def help_handler(event):
    msg = (
        "🔐 **Account Management:**\n"
        "/login - Add a new account (private chat)\n"
        "/accounts - List your accounts (with Account IDs)\n"
        "/naccounts - List accounts with phone numbers (password)\n"
        "/get_strings - Export session strings (password)\n"
        "/logout <phone> - Log out and remove account\n\n"
        "🎮 **Bot Control:**\n"
        "/solo_start <account_id> - Start single account by ID\n"
        "/solo_stop <account_id> - Stop single account by ID\n"
        "/startall - Choose mode for all accounts\n"
        "/stopall - Stop all activities\n\n"
        "🤖 **Smart Sequence (UTC Timezone):**\n"
        "/startall → 🔄 Smart Sequence - Automated daily cycle\n"
        "/smart_status - Check smart sequence status\n"
        "/safari_status - Check safari completion status\n"
        "• **1:00 PM UTC** - Auto Guess starts\n"
        "• **Guess limit reached** → Auto Safari\n"
        "• **Safari + 10-20min** → Auto Catch\n"
        "• **Daily hunt limit** → Wait for next day\n\n"
        "💰 **Commands:**\n"
        "/giveme <amount> - Send /give to all accounts\n"
        "/giveme <amount> <account_id> - Send /give to specific account\n\n"
        "⚙️ **Settings & Lists:**\n"
        "/mysettings - Manage ball type & pokemon lists\n"
        "/list - View auto catch lists\n"
        "/addpoke <pokemon> - Add pokemon to Auto Catch 1 list\n"
        "/addpoke2 <pokemon> - Add pokemon to Auto Catch 2 list\n"
        "/rpoke <pokemon> - Remove pokemon from any list\n\n"
        "📚 **Information:**\n"
        "/bestnature_0l - Pokemon nature guide\n\n"
        "📊 **Statistics:**\n"
        "/leaderboard - Show top accounts by catches\n"
        "/stats <account_id> - Show detailed account statistics\n\n"
        "💬 **Communication:**\n"
        "/report <message> - Report to admins\n\n"
        "👑 **Admin Only:**\n"
        "/auth - User authorization\n"
        "/ban <user> - Ban user\n"
        "/unban <user> - Unban user\n"
        "/broad <message> - Broadcast message\n"
        "/msg <user> <message> - Private message\n"
        "/msend <message> [account_id] - Make accounts send message in group\n"
        "/statics - Show bot statistics and findings\n"
    )
    await event.reply(msg, parse_mode="markdown")


@bot.on(events.NewMessage(pattern=r'^/mysettings$'))
@authorized_only
async def mysettings_handler(event):
    """Show user settings with inline buttons."""
    user_id = event.sender_id
    settings = get_user_settings(user_id)
    
    buttons = [
        [Button.inline(f"🏀 Ball Type: {settings['ball_type']}", b"change_ball_type")],
        [Button.inline("🎯 Auto Catch 1 (Rare/Legendaries)", b"manage_catch_1")],
        [Button.inline("🎪 Auto Catch 2 (Tour Helpers)", b"manage_catch_2")],
        [Button.inline("⚙️ Ball Settings", b"ball_settings")],
        [Button.inline("🏠 Private Group Settings", b"private_group_settings")],
        [Button.inline("🔄 Reset to Defaults", b"reset_settings")]
    ]
    
    auto_buy_status = "✅ Enabled" if settings.get('auto_buy_balls', True) else "❌ Disabled"
    private_group = settings.get('private_group_id')
    group_status = f"`{private_group}`" if private_group else "❌ Not Set"
    
    msg = (
        "⚙️ **Your Settings**\n\n"
        f"🏀 **Ball Type:** `{settings['ball_type']}`\n"
        f"🎯 **Auto Catch 1:** {len(settings.get('auto_catch_1_list', []))} Pokemon\n"
        f"🎪 **Auto Catch 2:** {len(settings.get('auto_catch_2_list', []))} Pokemon\n"
        f"🔢 **Auto Catch 1 Min Balls:** {settings.get('auto_catch_1_min_balls', 10)}\n"
        f"🔢 **Auto Catch 2 Min Balls:** {settings.get('auto_catch_2_min_balls', 200)}\n"
        f"🛒 **Auto Buy Balls:** {auto_buy_status}\n"
        f"📦 **Max Balls to Buy:** {settings.get('max_balls_to_buy', 50)}\n"
        f"🏠 **Private Group:** {group_status}\n\n"
        "Select an option to modify:"
    )
    
    await event.respond(msg, buttons=buttons, parse_mode="markdown")

@bot.on(events.CallbackQuery(pattern=b"^(change_ball_type|manage_catch_1|manage_catch_2|ball_settings|private_group_settings|reset_settings)$"))
async def settings_callback_handler(event):
    """Handle settings callback buttons."""
    user_id = event.sender_id
    action = event.data.decode()
    
    if action == "change_ball_type":
        buttons = [
            [Button.inline("🔴 Regular Ball", b"set_ball_Regular Ball")],
            [Button.inline("🔵 Great Ball", b"set_ball_Great Ball")],
            [Button.inline("🟡 Ultra Ball", b"set_ball_Ultra Ball")],
            [Button.inline("🟢 Level Ball", b"set_ball_Level Ball")],
            [Button.inline("⚡ Fast Ball", b"set_ball_Fast Ball")],
            [Button.inline("🔄 Repeat Ball", b"set_ball_Repeat Ball")],
            [Button.inline("🪺 Nest Ball", b"set_ball_Nest Ball")],
            [Button.inline("🕸️ Net Ball", b"set_ball_Net Ball")],
            [Button.inline("⚡ Quick Ball", b"set_ball_Quick Ball")],
            [Button.inline("⚫ Master Ball", b"set_ball_Master Ball")],
            [Button.inline("🔙 Back", b"back_to_settings")]
        ]
        await event.edit("🏀 **Choose Ball Type:**", buttons=buttons, parse_mode="markdown")
    
    elif action == "manage_catch_1":
        settings = get_user_settings(user_id)
        pokemon_list = settings.get('auto_catch_1_list', [])
        
        buttons = [
            [Button.inline("➕ Add Pokemon", b"add_to_catch_1")],
            [Button.inline("➖ Remove Pokemon", b"remove_from_catch_1")],
            [Button.inline("📋 View List", b"view_catch_1")],
            [Button.inline("🔙 Back", b"back_to_settings")]
        ]
        
        msg = (
            "🎯 **Auto Catch 1 Management**\n"
            "*(Rare Pokemon & Legendaries)*\n\n"
            f"📊 **Current Count:** {len(pokemon_list)} Pokemon\n\n"
            "Choose an action:"
        )
        await event.edit(msg, buttons=buttons, parse_mode="markdown")
    
    elif action == "manage_catch_2":
        settings = get_user_settings(user_id)
        pokemon_list = settings.get('auto_catch_2_list', [])
        
        buttons = [
            [Button.inline("➕ Add Pokemon", b"add_to_catch_2")],
            [Button.inline("➖ Remove Pokemon", b"remove_from_catch_2")],
            [Button.inline("📋 View List", b"view_catch_2")],
            [Button.inline("🔙 Back", b"back_to_settings")]
        ]
        
        msg = (
            "🎪 **Auto Catch 2 Management**\n"
            "*(Tour Helper Pokemon)*\n\n"
            f"📊 **Current Count:** {len(pokemon_list)} Pokemon\n\n"
            "Choose an action:"
        )
        await event.edit(msg, buttons=buttons, parse_mode="markdown")
    
    elif action == "ball_settings":
        settings = get_user_settings(user_id)
        auto_buy_status = "✅ Enabled" if settings.get('auto_buy_balls', True) else "❌ Disabled"
        
        buttons = [
            [Button.inline(f"🔢 Auto Catch 1 Min: {settings.get('auto_catch_1_min_balls', 10)}", b"set_catch1_min")],
            [Button.inline(f"🔢 Auto Catch 2 Min: {settings.get('auto_catch_2_min_balls', 200)}", b"set_catch2_min")],
            [Button.inline(f"🛒 Auto Buy: {auto_buy_status}", b"toggle_auto_buy")],
            [Button.inline(f"📦 Max Buy: {settings.get('max_balls_to_buy', 50)}", b"set_max_buy")],
            [Button.inline("🔙 Back", b"back_to_settings")]
        ]
        
        msg = (
            "⚙️ **Ball Settings**\n\n"
            f"🔢 **Auto Catch 1 Min Balls:** {settings.get('auto_catch_1_min_balls', 10)}\n"
            f"🔢 **Auto Catch 2 Min Balls:** {settings.get('auto_catch_2_min_balls', 200)}\n"
            f"🛒 **Auto Buy Balls:** {auto_buy_status}\n"
            f"📦 **Max Balls to Buy:** {settings.get('max_balls_to_buy', 50)}\n\n"
            "💡 **Info:**\n"
            "• Auto Catch 1: Minimum balls needed to start rare Pokemon hunting\n"
            "• Auto Catch 2: Minimum balls needed to start tour helper hunting\n"
            "• Auto Buy: Automatically purchase balls when running low\n"
            "• Max Buy: Maximum balls to purchase at once"
        )
        await event.edit(msg, buttons=buttons, parse_mode="markdown")
    
    elif action == "private_group_settings":
        settings = get_user_settings(user_id)
        current_group = settings.get('private_group_id')
        
        buttons = [
            [Button.inline("🔧 Set Private Group", b"set_private_group")],
            [Button.inline("❌ Remove Private Group", b"remove_private_group")],
            [Button.inline("🔙 Back", b"back_to_settings")]
        ]
        
        group_text = f"`{current_group}`" if current_group else "❌ Not Set"
        
        msg = (
            "🏠 **Private Group Settings**\n\n"
            f"📍 **Current Group:** {group_text}\n\n"
            "💡 **How to setup:**\n"
            "1. Create a private group\n"
            "2. Add this bot to the group\n"
            "3. Make the bot admin\n"
            "4. Send `/setgroup` in that group\n"
            "5. Use `/giveme` command in that group\n\n"
            "Choose an action:"
        )
        await event.edit(msg, buttons=buttons, parse_mode="markdown")
    
    elif action == "reset_settings":
        buttons = [
            [Button.inline("✅ Yes, Reset All", b"confirm_reset")],
            [Button.inline("❌ Cancel", b"back_to_settings")]
        ]
        await event.edit(
            "⚠️ **Reset Settings**\n\n"
            "This will reset all your settings to default values.\n"
            "Are you sure?", 
            buttons=buttons, 
            parse_mode="markdown"
        )

@bot.on(events.CallbackQuery(pattern=b"^set_ball_"))
async def set_ball_type_handler(event):
    """Handle ball type selection."""
    user_id = event.sender_id
    ball_type = event.data.decode().replace("set_ball_", "")
    
    update_user_settings(user_id, {"ball_type": ball_type})
    
    await event.edit(
        f"✅ **Ball Type Updated**\n\n"
        f"🏀 New ball type: `{ball_type}`", 
        buttons=[[Button.inline("🔙 Back to Settings", b"back_to_settings")]], 
        parse_mode="markdown"
    )

@bot.on(events.CallbackQuery(pattern=b"^(set_catch1_min|set_catch2_min|toggle_auto_buy|set_max_buy)$"))
async def ball_settings_handler(event):
    """Handle ball settings changes."""
    user_id = event.sender_id
    action = event.data.decode()
    
    if action == "toggle_auto_buy":
        settings = get_user_settings(user_id)
        current_status = settings.get('auto_buy_balls', True)
        new_status = not current_status
        update_user_settings(user_id, {"auto_buy_balls": new_status})
        
        status_text = "✅ Enabled" if new_status else "❌ Disabled"
        await event.edit(
            f"✅ **Auto Buy Updated**\n\n"
            f"🛒 Auto Buy Balls: {status_text}", 
            buttons=[[Button.inline("🔙 Back to Ball Settings", b"ball_settings")]], 
            parse_mode="markdown"
        )
    
    elif action in ["set_catch1_min", "set_catch2_min", "set_max_buy"]:
        if action == "set_catch1_min":
            buttons = [
                [Button.inline("5 Balls", b"update_catch1_min_5")],
                [Button.inline("10 Balls", b"update_catch1_min_10")],
                [Button.inline("20 Balls", b"update_catch1_min_20")],
                [Button.inline("50 Balls", b"update_catch1_min_50")],
                [Button.inline("🔙 Back", b"ball_settings")]
            ]
            await event.edit("🔢 **Set Auto Catch 1 Minimum Balls:**", buttons=buttons, parse_mode="markdown")
        
        elif action == "set_catch2_min":
            buttons = [
                [Button.inline("100 Balls", b"update_catch2_min_100")],
                [Button.inline("200 Balls", b"update_catch2_min_200")],
                [Button.inline("300 Balls", b"update_catch2_min_300")],
                [Button.inline("500 Balls", b"update_catch2_min_500")],
                [Button.inline("🔙 Back", b"ball_settings")]
            ]
            await event.edit("🔢 **Set Auto Catch 2 Minimum Balls:**", buttons=buttons, parse_mode="markdown")
        
        elif action == "set_max_buy":
            buttons = [
                [Button.inline("25 Balls", b"update_max_buy_25")],
                [Button.inline("50 Balls", b"update_max_buy_50")],
                [Button.inline("100 Balls", b"update_max_buy_100")],
                [Button.inline("200 Balls", b"update_max_buy_200")],
                [Button.inline("🔙 Back", b"ball_settings")]
            ]
            await event.edit("📦 **Set Maximum Balls to Buy:**", buttons=buttons, parse_mode="markdown")

@bot.on(events.CallbackQuery(pattern=b"^(set_private_group|remove_private_group)$"))
async def private_group_handler(event):
    """Handle private group settings."""
    user_id = event.sender_id
    action = event.data.decode()
    
    if action == "set_private_group":
        await event.edit(
            "🏠 **Set Private Group**\n\n"
            "To set your private group:\n\n"
            "1️⃣ Create a private group\n"
            "2️⃣ Add this bot to the group\n"
            "3️⃣ Make the bot admin\n"
            "4️⃣ Send `/setgroup` in that group\n\n"
            "💡 **Note:** The group will be automatically set when you use `/setgroup` command in your group.",
            buttons=[[Button.inline("🔙 Back", b"private_group_settings")]],
            parse_mode="markdown"
        )
    
    elif action == "remove_private_group":
        update_user_settings(user_id, {"private_group_id": None})
        await event.edit(
            "✅ **Private Group Removed**\n\n"
            "Your private group has been removed from settings.",
            buttons=[[Button.inline("🔙 Back to Settings", b"back_to_settings")]],
            parse_mode="markdown"
        )

@bot.on(events.CallbackQuery(pattern=b"^update_(catch1_min|catch2_min|max_buy)_"))
async def update_ball_values_handler(event):
    """Handle ball value updates."""
    user_id = event.sender_id
    data = event.data.decode()
    
    if "catch1_min" in data:
        value = int(data.split("_")[-1])
        update_user_settings(user_id, {"auto_catch_1_min_balls": value})
        await event.edit(
            f"✅ **Auto Catch 1 Minimum Updated**\n\n"
            f"🔢 New minimum: {value} balls", 
            buttons=[[Button.inline("🔙 Back to Ball Settings", b"ball_settings")]], 
            parse_mode="markdown"
        )
    
    elif "catch2_min" in data:
        value = int(data.split("_")[-1])
        update_user_settings(user_id, {"auto_catch_2_min_balls": value})
        await event.edit(
            f"✅ **Auto Catch 2 Minimum Updated**\n\n"
            f"🔢 New minimum: {value} balls", 
            buttons=[[Button.inline("🔙 Back to Ball Settings", b"ball_settings")]], 
            parse_mode="markdown"
        )
    
    elif "max_buy" in data:
        value = int(data.split("_")[-1])
        update_user_settings(user_id, {"max_balls_to_buy": value})
        await event.edit(
            f"✅ **Max Buy Amount Updated**\n\n"
            f"📦 New maximum: {value} balls", 
            buttons=[[Button.inline("🔙 Back to Ball Settings", b"ball_settings")]], 
            parse_mode="markdown"
        )

@bot.on(events.CallbackQuery(pattern=b"^(back_to_settings|confirm_reset)$"))
async def settings_navigation_handler(event):
    """Handle settings navigation."""
    user_id = event.sender_id
    action = event.data.decode()
    
    if action == "back_to_settings":
        settings = get_user_settings(user_id)
        
        buttons = [
            [Button.inline(f"🏀 Ball Type: {settings['ball_type']}", b"change_ball_type")],
            [Button.inline("🎯 Auto Catch 1 (Rare/Legendaries)", b"manage_catch_1")],
            [Button.inline("🎪 Auto Catch 2 (Tour Helpers)", b"manage_catch_2")],
            [Button.inline("⚙️ Ball Settings", b"ball_settings")],
            [Button.inline("🏠 Private Group Settings", b"private_group_settings")],
            [Button.inline("🔄 Reset to Defaults", b"reset_settings")]
        ]
        
        auto_buy_status = "✅ Enabled" if settings.get('auto_buy_balls', True) else "❌ Disabled"
        private_group = settings.get('private_group_id')
        group_status = f"`{private_group}`" if private_group else "❌ Not Set"
        
        msg = (
            "⚙️ **Your Settings**\n\n"
            f"🏀 **Ball Type:** `{settings['ball_type']}`\n"
            f"🎯 **Auto Catch 1:** {len(settings.get('auto_catch_1_list', []))} Pokemon\n"
            f"🎪 **Auto Catch 2:** {len(settings.get('auto_catch_2_list', []))} Pokemon\n"
            f"🔢 **Auto Catch 1 Min Balls:** {settings.get('auto_catch_1_min_balls', 10)}\n"
            f"🔢 **Auto Catch 2 Min Balls:** {settings.get('auto_catch_2_min_balls', 200)}\n"
            f"🛒 **Auto Buy Balls:** {auto_buy_status}\n"
            f"📦 **Max Balls to Buy:** {settings.get('max_balls_to_buy', 50)}\n"
            f"🏠 **Private Group:** {group_status}\n\n"
            "Select an option to modify:"
        )
        
        await event.edit(msg, buttons=buttons, parse_mode="markdown")
    
    elif action == "confirm_reset":
        default_settings = {
            "ball_type": "Ultra Ball",
            "auto_catch_1_list": CATCH_LIST.copy(),
            "auto_catch_2_list": AUTO_CATCH_2_LIST.copy(),
            "auto_catch_1_min_balls": 10,
            "auto_catch_2_min_balls": 200,
            "auto_buy_balls": True,
            "max_balls_to_buy": 50,
            "private_group_id": None
        }
        update_user_settings(user_id, default_settings)
        
        await event.edit(
            "✅ **Settings Reset**\n\n"
            "All settings have been reset to default values.", 
            buttons=[[Button.inline("🔙 Back to Settings", b"back_to_settings")]], 
            parse_mode="markdown"
        )

@bot.on(events.NewMessage(pattern=r'^/list$'))
@authorized_only
async def list_handler(event):
    """Show auto catch lists."""
    buttons = [
        [Button.inline("🎯 Auto Catch 1 (Rare/Legendaries)", b"show_list_1")],
        [Button.inline("🎪 Auto Catch 2 (Tour Helpers)", b"show_list_2")]
    ]
    
    try:
        await event.respond('https://postimg.cc/cvRp7h2N')
    except:
        pass  
    
    msg = (
        "📋 **Pokemon Lists**\n\n"
        "Choose which list to view:"
    )
    
    await event.respond(msg, buttons=buttons, parse_mode="markdown")

@bot.on(events.CallbackQuery(pattern=b"^show_list_"))
async def show_list_handler(event):
    """Handle list display buttons."""
    user_id = event.sender_id
    list_num = event.data.decode().split("_")[-1]
    
    settings = get_user_settings(user_id)
    pokemon_list = settings.get(f'auto_catch_{list_num}_list', [])
    
    page = 0
    items_per_page = 20
    total_pages = (len(pokemon_list) + items_per_page - 1) // items_per_page
    
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(pokemon_list))
    page_items = pokemon_list[start_idx:end_idx]
    
    list_name = "Rare/Legendaries" if list_num == "1" else "Tour Helpers"
    
    msg = (
        f"📋 **Auto Catch {list_num} - {list_name}**\n\n"
        f"📊 **Total:** {len(pokemon_list)} Pokemon\n"
        f"📄 **Page:** {page + 1}/{max(1, total_pages)}\n\n"
    )
    
    if page_items:
        for i, pokemon in enumerate(page_items, start_idx + 1):
            msg += f"<blockquote>{i:2d}. {pokemon}</blockquote>\n"
    else:
        msg += "*No Pokemon in this list*"
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(Button.inline("⬅️ Previous", f"view_catch_{list_num}_page_{page-1}".encode()))
    if page < total_pages - 1:
        nav_buttons.append(Button.inline("➡️ Next", f"view_catch_{list_num}_page_{page+1}".encode()))
    
    buttons = []
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.extend([
        [
            Button.inline("➕ Add Pokemon", f"add_to_catch_{list_num}".encode()),
            Button.inline("➖ Remove Pokemon", f"remove_from_catch_{list_num}".encode())
        ],
        [Button.inline("🔙 Back to Lists", b"back_to_lists")]
    ])
    
    await event.edit(msg, buttons=buttons, parse_mode="html")

@bot.on(events.CallbackQuery(pattern=b"^back_to_lists$"))
async def back_to_lists_handler(event):
    """Go back to list selection."""
    buttons = [
        [Button.inline("🎯 Auto Catch 1 (Rare/Legendaries)", b"show_list_1")],
        [Button.inline("🎪 Auto Catch 2 (Tour Helpers)", b"show_list_2")]
    ]
    
    msg = (
        "📋 **Pokemon Lists**\n\n"
        "Choose which list to view:"
    )
    
    await event.edit(msg, buttons=buttons, parse_mode="markdown")

@bot.on(events.CallbackQuery(pattern=b"^(view_catch_1|view_catch_2)$"))
async def view_catch_list_handler(event):
    """Handle view list from mysettings."""
    user_id = event.sender_id
    action = event.data.decode()
    
    list_num = "1" if action == "view_catch_1" else "2"
    settings = get_user_settings(user_id)
    pokemon_list = settings.get(f'auto_catch_{list_num}_list', [])
    
    page = 0
    items_per_page = 20
    total_pages = (len(pokemon_list) + items_per_page - 1) // items_per_page
    
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(pokemon_list))
    page_items = pokemon_list[start_idx:end_idx]
    
    list_name = "Rare/Legendaries" if list_num == "1" else "Tour Helpers"
    
    msg = (
        f"📋 **Auto Catch {list_num} - {list_name}**\n\n"
        f"📊 **Total:** {len(pokemon_list)} Pokemon\n"
        f"📄 **Page:** {page + 1}/{max(1, total_pages)}\n\n"
    )
    
    if page_items:
        for i, pokemon in enumerate(page_items, start_idx + 1):
            msg += f"`{i:2d}.` {pokemon}\n"
    else:
        msg += "*No Pokemon in this list*"
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(Button.inline("⬅️ Previous", f"view_catch_{list_num}_page_{page-1}".encode()))
    if page < total_pages - 1:
        nav_buttons.append(Button.inline("➡️ Next", f"view_catch_{list_num}_page_{page+1}".encode()))
    
    buttons = []
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.extend([
        [
            Button.inline("➕ Add Pokemon", f"add_to_catch_{list_num}".encode()),
            Button.inline("➖ Remove Pokemon", f"remove_from_catch_{list_num}".encode())
        ],
        [Button.inline("🔙 Back to Settings", b"back_to_settings")]
    ])
    
    await event.edit(msg, buttons=buttons, parse_mode="markdown")

@bot.on(events.CallbackQuery(pattern=b"^view_catch_[12]_page_"))
async def view_catch_page_handler(event):
    """Handle pagination for view catch lists from mysettings."""
    user_id = event.sender_id
    data = event.data.decode()
    
    parts = data.split("_")
    list_num = parts[2]
    page = int(parts[4])
    
    settings = get_user_settings(user_id)
    pokemon_list = settings.get(f'auto_catch_{list_num}_list', [])
    
    items_per_page = 20
    total_pages = (len(pokemon_list) + items_per_page - 1) // items_per_page
    
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, len(pokemon_list))
    page_items = pokemon_list[start_idx:end_idx]
    
    list_name = "Rare/Legendaries" if list_num == "1" else "Tour Helpers"
    
    msg = (
        f"📋 **Auto Catch {list_num} - {list_name}**\n\n"
        f"📊 **Total:** {len(pokemon_list)} Pokemon\n"
        f"📄 **Page:** {page + 1}/{max(1, total_pages)}\n\n"
    )
    
    if page_items:
        for i, pokemon in enumerate(page_items, start_idx + 1):
            msg += f"`{i:2d}.` {pokemon}\n"
    else:
        msg += "*No Pokemon in this list*"
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(Button.inline("⬅️ Previous", f"view_catch_{list_num}_page_{page-1}".encode()))
    if page < total_pages - 1:
        nav_buttons.append(Button.inline("➡️ Next", f"view_catch_{list_num}_page_{page+1}".encode()))
    
    buttons = []
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.extend([
        [
            Button.inline("➕ Add Pokemon", f"add_to_catch_{list_num}".encode()),
            Button.inline("➖ Remove Pokemon", f"remove_from_catch_{list_num}".encode())
        ],
        [Button.inline("🔙 Back to Settings", b"back_to_settings")]
    ])
    
    await event.edit(msg, buttons=buttons, parse_mode="markdown")

@bot.on(events.CallbackQuery(pattern=b"^(add_to_catch_1|add_to_catch_2|remove_from_catch_1|remove_from_catch_2)$"))
async def pokemon_management_handler(event):
    """Handle add/remove pokemon buttons."""
    user_id = event.sender_id
    action = event.data.decode()
    
    if action.startswith("add_to_catch_"):
        list_num = action.split("_")[-1]
        await event.edit(
            f"➕ **Add Pokemon to Auto Catch {list_num}**\n\n"
            f"Please use the command:\n"
            f"`/addpoke <pokemon_name>`\n\n"
            f"Example: `/addpoke Pikachu`",
            buttons=[[Button.inline("🔙 Back to Settings", b"back_to_settings")]],
            parse_mode="markdown"
        )
    
    elif action.startswith("remove_from_catch_"):
        list_num = action.split("_")[-1]
        await event.edit(
            f"➖ **Remove Pokemon from Auto Catch {list_num}**\n\n"
            f"Please use the command:\n"
            f"`/rpoke <pokemon_name>`\n\n"
            f"Example: `/rpoke Pikachu`",
            buttons=[[Button.inline("🔙 Back to Settings", b"back_to_settings")]],
            parse_mode="markdown"
        )


async def show_status_page(event, user_id, page=0):
    """Show account status with pagination."""
    accounts = list(accounts_col.find({"user_id": user_id}))
    if not accounts:
        await event.reply("❌ No accounts found.")
        return

    items_per_page = 10
    total_accounts = len(accounts)
    total_pages = (total_accounts + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, total_accounts)
    page_accounts = accounts[start_idx:end_idx]

    global account_tasks, auto_catch_tasks
    msg = f"📊 **Your Account Status**\n\n"
    msg += f"📱 **Total:** {total_accounts} accounts\n"
    msg += f"📄 **Page:** {page + 1}/{total_pages}\n\n"
    
    for i, acc in enumerate(page_accounts, start_idx + 1):
        phone = acc['phone']
        is_guessing = phone in account_tasks and not account_tasks[phone].done()
        is_catching = phone in auto_catch_tasks and not auto_catch_tasks[phone].done()

        if is_guessing:
            status = "🎯 Guessing"
        elif is_catching:
            status = "🎣 Catching"
        else:
            status = "❌ Inactive"
            
        msg += f"`{i:2d}.` **Phone:** `{phone}`\n**Status:** {status}\n\n"

    buttons = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(Button.inline("⬅️ Previous", f"status_page_{page-1}".encode()))
    if page < total_pages - 1:
        nav_buttons.append(Button.inline("➡️ Next", f"status_page_{page+1}".encode()))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([Button.inline("🔄 Refresh", b"refresh_status")])
    
    try:
        if hasattr(event, 'edit') and hasattr(event, 'message') and event.message:
            await event.edit(msg, buttons=buttons, parse_mode="markdown")
        else:
            await event.respond(msg, buttons=buttons, parse_mode="markdown")
    except Exception as e:
        print(f"Error in show_status_page: {e}")
        await event.respond(msg, buttons=buttons, parse_mode="markdown")

@bot.on(events.CallbackQuery(pattern=b"^status_page_"))
async def status_page_handler(event):
    """Handle status pagination."""
    uid = event.sender_id
    page = int(event.data.decode().split("_")[-1])
    await show_status_page(event, uid, page)

@bot.on(events.CallbackQuery(pattern=b"^refresh_status$"))
async def refresh_status_handler(event):
    """Refresh status list."""
    uid = event.sender_id
    await show_status_page(event, uid, 0)


@bot.on(events.NewMessage(pattern=r'^/addpoke\s+(.+)$'))
@authorized_only
async def addpoke_handler(event):
    """Add pokemon to user's active list."""
    user_id = event.sender_id
    pokemon_name = event.pattern_match.group(1).strip().title()
    
    settings = get_user_settings(user_id)
    list1 = settings.get('auto_catch_1_list', [])
    list2 = settings.get('auto_catch_2_list', [])
    
    if pokemon_name in list1:
        await event.reply(f"❌ <blockquote>{pokemon_name}</blockquote> is already in your **Auto Catch 1** list!", parse_mode="html")
        return
    elif pokemon_name in list2:
        await event.reply(f"❌ <blockquote>{pokemon_name}</blockquote> is already in your **Auto Catch 2** list!", parse_mode="html")
        return
    
    success = add_pokemon_to_list(user_id, pokemon_name, "1")
    
    if success:
        await event.reply(f"✅ Added <blockquote>{pokemon_name}</blockquote> to **Auto Catch 1** list!", parse_mode="html")
    else:
        await event.reply(f"❌ Failed to add <blockquote>{pokemon_name}</blockquote> to the list!", parse_mode="html")

@bot.on(events.NewMessage(pattern=r'^/addpoke2\s+(.+)$'))
@authorized_only
async def addpoke2_handler(event):
    """Add pokemon to user's Auto Catch 2 list."""
    user_id = event.sender_id
    pokemon_name = event.pattern_match.group(1).strip().title()
    
    settings = get_user_settings(user_id)
    list1 = settings.get('auto_catch_1_list', [])
    list2 = settings.get('auto_catch_2_list', [])
    
    if pokemon_name in list1:
        await event.reply(f"❌ <blockquote>{pokemon_name}</blockquote> is already in your **Auto Catch 1** list!", parse_mode="html")
        return
    elif pokemon_name in list2:
        await event.reply(f"❌ <blockquote>{pokemon_name}</blockquote> is already in your **Auto Catch 2** list!", parse_mode="html")
        return
    
    success = add_pokemon_to_list(user_id, pokemon_name, "2")
    
    if success:
        await event.reply(f"✅ Added <blockquote>{pokemon_name}</blockquote> to **Auto Catch 2** list!", parse_mode="html")
    else:
        await event.reply(f"❌ Failed to add <blockquote>{pokemon_name}</blockquote> to the list!", parse_mode="html")

@bot.on(events.NewMessage(pattern=r'^/rpoke\s+(.+)$'))
@authorized_only
async def rpoke_handler(event):
    """Remove pokemon from user's active list."""
    user_id = event.sender_id
    pokemon_name = event.pattern_match.group(1).strip().title()
    
    settings = get_user_settings(user_id)
    list1 = settings.get('auto_catch_1_list', [])
    list2 = settings.get('auto_catch_2_list', [])
    
    if pokemon_name not in list1 and pokemon_name not in list2:
        await event.reply(f"❌ <blockquote>{pokemon_name}</blockquote> is not found in any of your lists!", parse_mode="html")
        return
    
    success1 = remove_pokemon_from_list(user_id, pokemon_name, "1")
    success2 = remove_pokemon_from_list(user_id, pokemon_name, "2")
    
    if success1:
        await event.reply(f"✅ Removed <blockquote>{pokemon_name}</blockquote> from **Auto Catch 1** list!", parse_mode="html")
    elif success2:
        await event.reply(f"✅ Removed <blockquote>{pokemon_name}</blockquote> from **Auto Catch 2** list!", parse_mode="html")
    else:
        await event.reply(f"❌ Failed to remove <blockquote>{pokemon_name}</blockquote> from the lists!", parse_mode="html")

@bot.on(events.NewMessage(pattern=r'^/ban\s+(.+)$'))
async def ban_handler(event):
    """Ban a user (owner only)."""
    if not is_bot_command(event):
        return
    if event.sender_id != ADMIN_USER_ID:
        await event.reply("❌ Only owner can ban users.")
        return
    
    target = event.pattern_match.group(1).strip()
    
    try:
        user_id = int(target)
    except ValueError:
        user_doc = users_col.find_one({"username": target.replace("@", "")})
        if not user_doc:
            await event.reply(f"❌ User `{target}` not found in database.")
            return
        user_id = user_doc["user_id"]
    
    if user_id == ADMIN_USER_ID:
        await event.reply("❌ Cannot ban the owner!")
        return
    
    if is_user_banned(user_id):
        await event.reply(f"❌ User `{target}` is already banned.")
        return
    
    ban_user(user_id, f"Banned by owner via /ban command")
    await event.reply(f"✅ User `{target}` (ID: {user_id}) has been banned.")

@bot.on(events.NewMessage(pattern=r'^/unban\s+(.+)$'))
async def unban_handler(event):
    """Unban a user (owner only)."""
    if not is_bot_command(event):
        return
    if event.sender_id != ADMIN_USER_ID:
        await event.reply("❌ Only owner can unban users.")
        return
    
    target = event.pattern_match.group(1).strip()
    
    try:
        user_id = int(target)
    except ValueError:
        user_doc = users_col.find_one({"username": target.replace("@", "")})
        if not user_doc:
            await event.reply(f"❌ User `{target}` not found in database.")
            return
        user_id = user_doc["user_id"]
    
    if not is_user_banned(user_id):
        await event.reply(f"❌ User `{target}` is not banned.")
        return
    
    unban_user(user_id)
    await event.reply(f"✅ User `{target}` (ID: {user_id}) has been unbanned.")

@bot.on(events.NewMessage(pattern=r'^/broad\s+(.+)$'))
async def broadcast_handler(event):
    """Broadcast message to all users (owner only)."""
    if not is_bot_command(event):
        return
    if event.sender_id != ADMIN_USER_ID:
        await event.reply("❌ Only owner can broadcast messages.")
        return
    
    message = event.pattern_match.group(1).strip()
    
    all_users = list(users_col.find({}))
    sent_count = 0
    failed_count = 0
    
    broadcast_msg = (
        "📢 **BROADCAST MESSAGE**\n\n"
        f"{message}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "*This is an official broadcast from the bot owner.*"
    )
    
    await event.reply(f"📡 Broadcasting to {len(all_users)} users...")
    
    for user in all_users:
        try:
            user_id = user["user_id"]
            if not is_user_banned(user_id):
                await bot.send_message(user_id, broadcast_msg, parse_mode="markdown")
                sent_count += 1
                await asyncio.sleep(0.1)  
        except Exception as e:
            failed_count += 1
            print(f"Failed to send broadcast to {user.get('user_id', 'unknown')}: {e}")
    
    await event.reply(
        f"✅ **Broadcast Complete**\n\n"
        f"📤 **Sent:** {sent_count}\n"
        f"❌ **Failed:** {failed_count}",
        parse_mode="markdown"
    )

@bot.on(events.NewMessage(pattern=r'^/msg\s+(\S+)\s+(.+)$'))
async def private_message_handler(event):
    """Send private message to user (owner only)."""
    if not is_bot_command(event):
        return
    if event.sender_id != ADMIN_USER_ID:
        await event.reply("❌ Only owner can send private messages.")
        return
    
    target = event.pattern_match.group(1).strip()
    message = event.pattern_match.group(2).strip()
    
    try:
        user_id = int(target)
    except ValueError:
        user_doc = users_col.find_one({"username": target.replace("@", "")})
        if not user_doc:
            await event.reply(f"❌ User `{target}` not found in database.")
            return
        user_id = user_doc["user_id"]
    
    try:
        private_msg = (
            "💌 **PRIVATE MESSAGE**\n\n"
            f"{message}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "*This is a private message from the bot owner.*"
        )
        
        await bot.send_message(user_id, private_msg, parse_mode="markdown")
        await event.reply(f"✅ Private message sent to `{target}` (ID: {user_id})")
    except Exception as e:
        await event.reply(f"❌ Failed to send message to `{target}`: {str(e)}")

@bot.on(events.NewMessage(pattern=r'^/report\s+(.+)$'))
@authorized_only
async def report_handler(event):
    """Send report to admins."""
    user_id = event.sender_id
    message = event.pattern_match.group(1).strip()
    
    user_info = users_col.find_one({"user_id": user_id})
    username = user_info.get("username", "Unknown") if user_info else "Unknown"
    
    report_msg = (
        "📋 **USER REPORT**\n\n"
        f"👤 **From:** @{username} (ID: {user_id})\n"
        f"📝 **Message:** {message}\n\n"
        f"🕐 **Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    
    try:
        await bot.send_message(ADMIN_USER_ID, report_msg, parse_mode="markdown")
        await event.reply("✅ Your report has been sent to the admins. Thank you!")
    except Exception as e:
        await event.reply("❌ Failed to send report. Please try again later.")
        print(f"Failed to send report: {e}")

@bot.on(events.NewMessage(pattern=r'^/leaderboard$'))
@authorized_only
async def leaderboard_handler(event):
    """Show leaderboard of top accounts by catches and findings."""
    try:
        findings = list(account_findings_col.find({}))
        
        if not findings:
            await event.reply("📊 No data available for leaderboard yet.")
            return
        
        account_stats = {}
        
        for finding in findings:
            phone = finding.get("phone", "Unknown")
            item_type = finding.get("item_type", "unknown")
            
            account_info = accounts_col.find_one({"phone": phone})
            if account_info:
                account_id = account_info.get("account_id", "unknown")
                account_name = account_info.get("name", "Unknown")
            else:
                account_id = "unknown"
                account_name = "Unknown"
            
            if phone not in account_stats:
                account_stats[phone] = {
                    "account_id": account_id,
                    "account_name": account_name,
                    "legendaries": 0,
                    "shinies": 0,
                    "tms": 0,
                    "mega_stones": 0,
                    "key_stones": 0,
                    "total_score": 0
                }
            
            if item_type == "legendary":
                account_stats[phone]["legendaries"] += 1
                account_stats[phone]["total_score"] += 10  
            elif item_type == "shiny":
                account_stats[phone]["shinies"] += 1
                account_stats[phone]["total_score"] += 20  
            elif item_type == "tm":
                account_stats[phone]["tms"] += 1
                account_stats[phone]["total_score"] += 2   
            elif item_type == "mega_stone":
                account_stats[phone]["mega_stones"] += 1
                account_stats[phone]["total_score"] += 15  
            elif item_type == "key_stone":
                account_stats[phone]["key_stones"] += 1
                account_stats[phone]["total_score"] += 5   
        
        sorted_accounts = sorted(account_stats.items(), key=lambda x: x[1]["total_score"], reverse=True)
        
        if not sorted_accounts:
            await event.reply("📊 No accounts with recorded findings yet.")
            return
        
        leaderboard_msg = "🏆 **ACCOUNT LEADERBOARD** 🏆\n\n"
        leaderboard_msg += "📊 **Ranking by Total Score:**\n"
        leaderboard_msg += "*(Shiny=20pts, Mega Stone=15pts, Legendary=10pts, Key Stone=5pts, TM=2pts)*\n\n"
        
        for i, (phone, stats) in enumerate(sorted_accounts[:10], 1):  
            if i == 1:
                rank_emoji = "🥇"
            elif i == 2:
                rank_emoji = "🥈"
            elif i == 3:
                rank_emoji = "🥉"
            else:
                rank_emoji = f"{i}."
            
            leaderboard_msg += f"{rank_emoji} **{stats['account_name']}** (`{stats['account_id']}`)\n"
            leaderboard_msg += f"   📊 **Score:** {stats['total_score']} pts\n"
            
            findings_list = []
            if stats['shinies'] > 0:
                findings_list.append(f"✨{stats['shinies']}")
            if stats['legendaries'] > 0:
                findings_list.append(f"🔥{stats['legendaries']}")
            if stats['mega_stones'] > 0:
                findings_list.append(f"💎{stats['mega_stones']}")
            if stats['key_stones'] > 0:
                findings_list.append(f"🗝️{stats['key_stones']}")
            if stats['tms'] > 0:
                findings_list.append(f"💿{stats['tms']}")
            
            if findings_list:
                leaderboard_msg += f"   🎯 {' | '.join(findings_list)}\n\n"
            else:
                leaderboard_msg += f"   🎯 No findings yet\n\n"
        
        if len(sorted_accounts) > 10:
            leaderboard_msg += f"*... and {len(sorted_accounts) - 10} more accounts*\n\n"
        
        leaderboard_msg += "💡 **Use `/stats <account_id>` for detailed account statistics**"
        
        await event.reply(leaderboard_msg, parse_mode="markdown")
        
    except Exception as e:
        await event.reply("❌ Error generating leaderboard. Please try again later.")
        print(f"Leaderboard error: {e}")

@bot.on(events.NewMessage(pattern=r'^/stats\s+([a-z0-9]{6})$'))
@authorized_only
async def stats_handler(event):
    """Show detailed stats for a specific account."""
    account_id = event.pattern_match.group(1).lower()
    
    try:
        account_info = accounts_col.find_one({"account_id": account_id})
        if not account_info:
            await event.reply(f"❌ Account with ID '{account_id}' not found.")
            return
        
        phone = account_info.get("phone")
        account_name = account_info.get("name", "Unknown")
        
        account_username = "Unknown"
        try:
            account_clients = await get_account_clients()
            if phone in account_clients:
                client = account_clients[phone]
                if client and client.is_connected():
                    me = await client.get_me()
                    account_username = getattr(me, 'username', 'Unknown')
                    if account_username:
                        account_username = f"@{account_username}"
        except:
            pass
        
        findings = list(account_findings_col.find({"phone": phone}).sort("timestamp", -1))
        
        if not findings:
            stats_msg = (
                f"📊 **ACCOUNT STATISTICS**\n\n"
                f"👤 **Account Name:** `{account_name}`\n"
                f"📱 **Account Username:** {account_username}\n"
                f"🆔 **Account ID:** `{account_id}`\n\n"
                f"📈 **Total Findings:** 0\n\n"
                f"🎯 No findings recorded yet for this account."
            )
            await event.reply(stats_msg, parse_mode="markdown")
            return
        
        stats = {
            "legendaries": [],
            "shinies": [],
            "tms": [],
            "mega_stones": [],
            "key_stones": []
        }
        
        for finding in findings:
            item_type = finding.get("item_type", "unknown")
            item_name = finding.get("item_name", "Unknown")
            timestamp = finding.get("timestamp", "Unknown")
            
            try:
                if isinstance(timestamp, str):
                    date_obj = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    date_obj = timestamp
                formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
            except:
                formatted_date = "Unknown Date"
            
            finding_entry = f"{item_name} - {formatted_date}"
            
            if item_type == "legendary":
                stats["legendaries"].append(finding_entry)
            elif item_type == "shiny":
                stats["shinies"].append(finding_entry)
            elif item_type == "tm":
                stats["tms"].append(finding_entry)
            elif item_type == "mega_stone":
                stats["mega_stones"].append(finding_entry)
            elif item_type == "key_stone":
                stats["key_stones"].append(finding_entry)
        
        total_score = (len(stats["shinies"]) * 20 + 
                      len(stats["legendaries"]) * 10 + 
                      len(stats["mega_stones"]) * 15 + 
                      len(stats["key_stones"]) * 5 + 
                      len(stats["tms"]) * 2)
        
        stats_msg = (
            f"📊 **ACCOUNT STATISTICS**\n\n"
            f"👤 **Account Name:** `{account_name}`\n"
            f"📱 **Account Username:** {account_username}\n"
            f"🆔 **Account ID:** `{account_id}`\n\n"
            f"📈 **Total Score:** {total_score} points\n"
            f"🎯 **Total Findings:** {len(findings)}\n\n"
        )
        
        if stats["shinies"]:
            stats_msg += f"✨ **Shiny Pokemon ({len(stats['shinies'])}):**\n"
            for shiny in stats["shinies"][:10]:  
                stats_msg += f"   • {shiny}\n"
            if len(stats["shinies"]) > 10:
                stats_msg += f"   *... and {len(stats['shinies']) - 10} more*\n"
            stats_msg += "\n"
        
        if stats["legendaries"]:
            stats_msg += f"🔥 **Legendary Pokemon ({len(stats['legendaries'])}):**\n"
            for legendary in stats["legendaries"][:10]:  
                stats_msg += f"   • {legendary}\n"
            if len(stats["legendaries"]) > 10:
                stats_msg += f"   *... and {len(stats['legendaries']) - 10} more*\n"
            stats_msg += "\n"
        
        if stats["mega_stones"]:
            stats_msg += f"💎 **Mega Stones ({len(stats['mega_stones'])}):**\n"
            for stone in stats["mega_stones"][:10]:
                stats_msg += f"   • {stone}\n"
            if len(stats["mega_stones"]) > 10:
                stats_msg += f"   *... and {len(stats['mega_stones']) - 10} more*\n"
            stats_msg += "\n"
        
        if stats["key_stones"]:
            stats_msg += f"🗝️ **Key Stones ({len(stats['key_stones'])}):**\n"
            for stone in stats["key_stones"][:10]:
                stats_msg += f"   • {stone}\n"
            if len(stats["key_stones"]) > 10:
                stats_msg += f"   *... and {len(stats['key_stones']) - 10} more*\n"
            stats_msg += "\n"
        
        if stats["tms"]:
            stats_msg += f"💿 **TMs Found:** {len(stats['tms'])}\n\n"
        
        if not any(stats.values()):
            stats_msg += "🎯 No findings recorded yet for this account."
        
        await event.reply(stats_msg, parse_mode="markdown")
        
    except Exception as e:
        await event.reply("❌ Error retrieving account statistics. Please try again later.")
        print(f"Stats error: {e}")

@bot.on(events.NewMessage(pattern=r'^/bestnature_(0l|6l)$'))
@authorized_only
async def bestnature_handler(event):
    """Show Pokemon nature guide with pagination."""
    command_type = event.pattern_match.group(1)
    
    if command_type == "0l":
        buttons = [
            [Button.inline("🌙 Non-Legendary Page 1", b"nature_page1")],
            [Button.inline("🌙 Non-Legendary Page 2", b"nature_page2")],
            [Button.inline("🌙 Non-Legendary Page 3", b"nature_page3")]
        ]
        
        msg = (
            "📚 **Pokemon Nature Guide - Non-Legendary**\n\n"
            "Select a page to view the best natures for non-legendary Pokemon:\n\n"
            "*Note: These are recommended natures. Other natures may also work well.*"
        )
    else:
        buttons = [
            [Button.inline("☀️ Legendary Page 1", b"nature_legendary_page1")],
            [Button.inline("☀️ Legendary Page 2", b"nature_legendary_page2")],
            [Button.inline("☀️ Legendary Page 3", b"nature_legendary_page3")]
        ]
        
        msg = (
            "📚 **Pokemon Nature Guide - Legendary**\n\n"
            "Select a page to view the best natures for legendary Pokemon:\n\n"
            "*Note: These are recommended natures. Other natures may also work well.*"
        )
    
    await event.respond(msg, buttons=buttons, parse_mode="markdown")

@bot.on(events.CallbackQuery(pattern=b"^nature_"))
async def nature_page_handler(event):
    """Handle nature page navigation."""
    page_key = event.data.decode().replace("nature_", "")
    
    if page_key not in POKEMON_NATURES:
        await event.answer("❌ Page not found!", alert=True)
        return
    
    page_data = POKEMON_NATURES[page_key]
    
    await event.respond(page_data.get('image', 'https://postimg.cc/cvRp7h2N'))
    
    msg = f"{page_data['title']}\n\n"
    
    if isinstance(page_data['content'], dict):
        if 'KANTO' in page_data['content'] or 'HOENN' in page_data['content'] or 'SINNOH' in page_data['content']:  
            for region, pokemon_data in page_data['content'].items():
                msg += f"**?? {region} REGION**\n"
                msg += "━━━━━━━━━━━━━━━━━━━━\n"
                
                if isinstance(pokemon_data, dict):
                    for pokemon, nature in pokemon_data.items():
                        nature_clean = nature.replace("'", "").replace('"', '')
                        msg += f"• **{pokemon}:** <blockquote>{nature_clean}</blockquote>\n"
                else:
                    msg += f"• {pokemon_data}\n"
                msg += "\n"
        else:  
            for pokemon, nature in page_data['content'].items():
                nature_clean = nature.replace("'", "").replace('"', '')
                msg += f"• **{pokemon}:** <blockquote>{nature_clean}</blockquote>\n"
    
    msg += "\n*Note: These Best Natures Are According To Me. There Are Other Good Natures too..*"
    
    all_pages = list(POKEMON_NATURES.keys())
    current_idx = all_pages.index(page_key)
    
    nav_buttons = []
    if current_idx > 0:
        prev_page = all_pages[current_idx - 1]
        nav_buttons.append(Button.inline("⬅️ Previous", f"nature_{prev_page}".encode()))
    if current_idx < len(all_pages) - 1:
        next_page = all_pages[current_idx + 1]
        nav_buttons.append(Button.inline("➡️ Next", f"nature_{next_page}".encode()))
    
    buttons = []
    if nav_buttons:
        buttons.append(nav_buttons)
    buttons.append([Button.inline("🔙 Back to Guide", b"back_to_nature_guide")])
    
    await event.edit(msg, buttons=buttons, parse_mode="markdown")

@bot.on(events.CallbackQuery(pattern=b"^back_to_nature_guide$"))
async def back_to_nature_guide_handler(event):
    """Go back to nature guide main menu."""
    buttons = [
        [Button.inline("🌙 Non-Legendary Page 1", b"nature_page1")],
        [Button.inline("🌙 Non-Legendary Page 2", b"nature_page2")],
        [Button.inline("🌙 Non-Legendary Page 3", b"nature_page3")],
        [Button.inline("☀️ Legendary Page 1", b"nature_legendary_page1")],
        [Button.inline("☀️ Legendary Page 2", b"nature_legendary_page2")],
        [Button.inline("☀️ Legendary Page 3", b"nature_legendary_page3")]
    ]
    
    msg = (
        "📚 **Pokemon Nature Guide**\n\n"
        "Select a page to view the best natures for Pokemon:\n\n"
        "🌙 **Non-Legendary Pokemon** - Regular Pokemon natures\n"
        "☀️ **Legendary Pokemon** - Legendary Pokemon natures\n\n"
        "*Note: These are recommended natures. Other natures may also work well.*"
    )
    
    await event.edit(msg, buttons=buttons, parse_mode="markdown")

@bot.on(events.NewMessage(pattern=r'^/setgroup$'))
@authorized_only
async def setgroup_handler(event):
    """Set private group for /giveme command."""
    if event.is_private:
        await event.reply("❌ This command must be used in a group!")
        return
    
    user_id = event.sender_id
    group_id = event.chat_id
    
    update_user_settings(user_id, {"private_group_id": group_id})
    
    await event.reply(
        f"✅ **Private Group Set!**\n\n"
        f"📍 **Group ID:** `{group_id}`\n"
        f"🎯 **Usage:** You can now use `/giveme` command in this group!\n\n"
        f"💡 **Tip:** Make sure the bot is admin in this group for best results.",
        parse_mode="markdown"
    )

@bot.on(events.NewMessage(pattern=r'^/statics$'))
async def statics_handler(event):
    """Show bot statistics (owner only)."""
    if not is_bot_command(event):
        return
    if event.sender_id != ADMIN_USER_ID:
        await event.reply("❌ Only owner can view bot statistics.")
        return
    
    stats = get_bot_stats()
    
    msg = (
        f"🤖 **Bot Statistics**\n\n"
        f"👥 **Total Users:** `{stats['total_users']}`\n"
        f"📱 **Total Accounts:** `{stats['total_accounts']}`\n"
        f"🟢 **Active Accounts:** `{stats['active_accounts']}`\n"
        f"🚫 **Banned Users:** `{stats['banned_users']}`\n"
        f"⏰ **Uptime:** `{stats['uptime_hours']}h {stats['uptime_minutes']}m`\n"
        f"⚡ **Bot Speed:** `Fast`\n"
        f"🔧 **Currently Active:** `{stats['active_accounts']}` accounts\n\n"
        f"**Total rare items found:**\n"
        f"**Shinies:** `{stats['total_shinies']}`\n"
        f"**Legendaries:** `{stats['total_legendaries']}`\n"
        f"**Mega Stone:** `{stats['total_mega_stones']}`\n"
        f"**TM:** `{stats['total_tms']}`"
    )
    
    await event.reply(msg, parse_mode="markdown")

@bot.on(events.NewMessage(pattern=r'^/refreshbot$'))
async def refreshbot_handler(event):
    """Refresh bot data (owner only)."""
    if not is_bot_command(event):
        return
    if event.sender_id != ADMIN_USER_ID:
        await event.reply("❌ Only owner can refresh bot data.")
        return
    
    global account_clients, account_tasks, auto_catch_tasks, daily_limits, limit_timers, hunt_status
    
    for phone, task in list(account_tasks.items()):
        if task and not task.done():
            task.cancel()
    
    for phone, task in list(auto_catch_tasks.items()):
        if task and not task.done():
            task.cancel()
    
    account_clients.clear()
    account_tasks.clear()
    auto_catch_tasks.clear()
    daily_limits.clear()
    limit_timers.clear()
    hunt_status.clear()
    
    global AUTHORIZED_USERS
    AUTHORIZED_USERS = load_authorized_users()
    
    await event.reply(
        "🔄 **Bot Refreshed Successfully!**\n\n"
        "✅ **Cleared:**\n"
        "• All active tasks\n"
        "• Client connections\n"
        "• Daily limits\n"
        "• Hunt status\n\n"
        "✅ **Reloaded:**\n"
        "• Authorized users\n"
        "• Bot configurations\n\n"
        "🚀 **Bot is ready for fresh start!**",
        parse_mode="markdown"
    )

@bot.on(events.NewMessage(pattern=r'^/stats\s+(\d+)$'))
async def user_stats_handler(event):
    """Show user account statistics (owner only)."""
    if not is_bot_command(event):
        return
    if event.sender_id != ADMIN_USER_ID:
        await event.reply("❌ Only owner can view user statistics.")
        return
    
    target_user_id = int(event.pattern_match.group(1))
    
    user_info = users_col.find_one({"user_id": target_user_id})
    if not user_info:
        await event.reply(f"❌ User ID `{target_user_id}` not found in database.")
        return
    
    username = user_info.get('username', 'Unknown')
    stats = get_user_account_stats(target_user_id)
    
    msg = (
        f"📊 **Account Statistics**\n\n"
        f"👤 **User:** @{username} (ID: `{target_user_id}`)\n"
        f"📱 **Total Accounts:** `{stats['total_accounts']}`\n\n"
        f"🎯 **Findings Summary:**\n"
        f"✨ **Shinies Found:** `{stats['shinies']}`\n"
        f"💿 **TMs Found:** `{stats['tms']}`\n"
        f"💎 **Mega Stones Found:** `{stats['mega_stones']}`\n"
        f"🎮 **Pokemon Caught:** `{stats['pokemon_caught']}`\n"
        f"💰 **Poke Dollars Earned:** `{stats['poke_dollars']}`\n\n"
    )
    
    if stats['findings']:
        msg += "📋 **Recent Findings:**\n"
        for finding in stats['findings'][-5:]:  
            item_emoji = {
                'shiny': '✨',
                'tm': '💿',
                'mega_stone': '💎',
                'pokemon': '🎮',
                'pd': '💰'
            }.get(finding['item_type'], '📦')
            
            msg += f"{item_emoji} `{finding['item_name']}` - {finding['date']}\n"
    else:
        msg += "📋 **Recent Findings:** *No findings recorded*"
    
    await event.reply(msg, parse_mode="markdown")

@bot.on(events.NewMessage(pattern=r'^/auth(?:\s+.*)?$'))
async def auth_handler(event):
    if not is_bot_command(event):
        return
    if event.sender_id != ADMIN_USER_ID:
        await event.reply("❌ Only owner can manage auth.")
        return

    text = event.raw_text.strip()
    parts = text.split()
    if len(parts) < 2:
        await event.reply(
            "Usage:\n"
            "/auth add <user_id>\n"
            "/auth remove <user_id>\n"
            "/auth list"
        )
        return

    cmd = parts[1].lower()
    if cmd == "add" and len(parts) >= 3:
        try:
            uid = int(parts[2])
            if uid in AUTHORIZED_USERS:
                await event.reply(f"User {uid} is already authorized.")
            else:
                AUTHORIZED_USERS.add(uid)
                save_authorized_user(uid)
                await event.reply(f"✅ User {uid} has been authorized.")
        except Exception:
            await event.reply("❌ Invalid user ID format.")
    elif cmd == "remove" and len(parts) >= 3:
        try:
            uid = int(parts[2])
            if uid == ADMIN_USER_ID:
                await event.reply("❌ Cannot remove owner's authorization.")
            elif uid in AUTHORIZED_USERS:
                AUTHORIZED_USERS.remove(uid)
                db[USERS_COLL].delete_one({"user_id": uid})
                await event.reply(f"✅ User {uid} has been removed from authorized users.")
            else:
                await event.reply(f"❌ User {uid} is not in the authorized list.")
        except Exception:
            await event.reply("❌ Invalid user ID format.")
    elif cmd == "list":
        if not AUTHORIZED_USERS:
            await event.reply("🔐 **Authorized Users:** *None*")
            return
        
        users_list = "🔐 **Authorized Users:**\n\n"
        for uid in sorted(AUTHORIZED_USERS):
            first_name = "Unknown"
            username = "Unknown"
            
            try:
                user = await bot.get_entity(uid)
                first_name = getattr(user, 'first_name', 'Unknown')
                telegram_username = getattr(user, 'username', None)
                if telegram_username:
                    username = telegram_username
            except Exception as e:
                print(f"Could not get Telegram info for {uid}: {e}")
                
                user_info = general_users_col.find_one({"user_id": uid})
                if user_info:
                    stored_username = user_info.get('username', None)
                    if stored_username and stored_username != str(uid):
                        username = stored_username
            
            username_display = f"@{username}" if username != "Unknown" else "*Unknown*"
            name_display = f"`{first_name}`" if first_name != "Unknown" else "*Unknown*"
            
            users_list += f"👤 **Name:** {name_display}\n"
            users_list += f"📱 **Username:** {username_display}\n"
            users_list += f"🆔 **User ID:** `{uid}`\n\n"
        
        await event.reply(users_list, parse_mode="markdown")
    else:
        await event.reply("❌ Unknown /auth subcommand.")

@bot.on(events.NewMessage(pattern=r'^/login$'))
@authorized_only
async def login_start(event):
    if not is_private_event(event):
        await event.reply("Please run /login in a private chat with the bot.")
        return
    uid = event.sender_id
    login_states[uid] = {"step": "phone", "retry": 0}
    await event.reply("🔑 Please enter your phone number (with country code, e.g., +1234567890). Send /cancel to abort.")

@bot.on(events.NewMessage(pattern=r'^/cancel$'))
@authorized_only
async def cancel_all_processes(event):
    """Cancel all ongoing processes for the user."""
    uid = event.sender_id
    cancelled_processes = []
    
    login_state = login_states.pop(uid, None)
    if login_state:
        if login_state.get("tele_client"):
            try:
                await login_state["tele_client"].disconnect()
            except Exception:
                pass
        cancelled_processes.append("Login")
    
    giveme_state = giveme_states.pop(uid, None)
    if giveme_state:
        cancelled_processes.append("Give Me")
    
    if uid == ADMIN_USER_ID:
        cancelled_tasks = 0
        
        for phone, task in list(account_tasks.items()):
            if task and not task.done():
                task.cancel()
                cancelled_tasks += 1
        account_tasks.clear()
        
        for phone, task in list(auto_catch_tasks.items()):
            if task and not task.done():
                task.cancel()
                cancelled_tasks += 1
        auto_catch_tasks.clear()
        
        for phone, task in list(safari_tasks.items()):
            if task and not task.done():
                task.cancel()
                cancelled_tasks += 1
        safari_tasks.clear()
        
        hunt_status.clear()
        
        if cancelled_tasks > 0:
            cancelled_processes.append(f"All Account Tasks ({cancelled_tasks} tasks)")
            
    else:
        user_accounts = list(accounts_col.find({"user_id": uid}, {"phone": 1}))
        user_phones = [acc["phone"] for acc in user_accounts]
        cancelled_tasks = 0
        
        for phone in user_phones:
            if phone in account_tasks:
                task = account_tasks.pop(phone, None)
                if task and not task.done():
                    task.cancel()
                    cancelled_tasks += 1
            
            if phone in auto_catch_tasks:
                task = auto_catch_tasks.pop(phone, None)
                if task and not task.done():
                    task.cancel()
                    cancelled_tasks += 1
            
            if phone in safari_tasks:
                task = safari_tasks.pop(phone, None)
                if task and not task.done():
                    task.cancel()
                    cancelled_tasks += 1
            
            if phone in hunt_status:
                hunt_status[phone] = False
        
        if cancelled_tasks > 0:
            cancelled_processes.append(f"Your Account Tasks ({cancelled_tasks} tasks)")
    
    if cancelled_processes:
        processes_text = ", ".join(cancelled_processes)
        await event.reply(f"✅ Cancelled: {processes_text}")
    else:
        await event.reply("ℹ️ No active processes to cancel.")

@bot.on(events.NewMessage(func=lambda e: True))
async def login_flow_handler(event):
    uid = event.sender_id
    if uid not in login_states:
        return
    if uid != ADMIN_USER_ID:
        return

    state = login_states[uid]
    step = state.get("step")

    try:
        if step == "phone":
            text = (event.raw_text or "").strip()
    
            if text.startswith("/"):
                return

            phone = text

            tele_client = TelegramClient(StringSession(), API_ID, API_HASH)
            await tele_client.connect()
            try:
                sent = await tele_client.send_code_request(phone)
            except Exception as e:
                await tele_client.disconnect()
                login_states.pop(uid, None)
                await event.reply(f"❌ Error sending code: {e}")
                return

            state.update({"tele_client": tele_client, "phone": phone, "sent": sent, "step": "otp", "retry": 0})
            await event.reply("🔑 OTP sent. Please enter the 5-digit code you received (or send it separated by spaces).")
            return

        if step == "otp":
            otp_raw = event.raw_text.strip()
            otp = re.sub(r'\s+', '', otp_raw)
            if not re.fullmatch(r'\d{4,10}', otp):
                state['retry'] = state.get('retry', 0) + 1
                if state['retry'] >= 3:
                    login_states.pop(uid, None)
                    await event.reply("❌ Too many invalid attempts. Please restart with /login.")
                    if state.get("tele_client"):
                        await state["tele_client"].disconnect()
                    return
                await event.reply("❌ Invalid OTP format. Try again:")
                return

            tele_client = state.get("tele_client")
            sent = state.get("sent")
            if not tele_client or not sent:
                login_states.pop(uid, None)
                await event.reply("❌ Session expired. Please restart with /login.")
                return

            try:
                await tele_client.sign_in(phone=state['phone'], code=otp, phone_code_hash=sent.phone_code_hash)
                state['step'] = 'group_id'
                await event.reply(
                    "✅ Verification successful!\n"
                    "Now, please provide the numeric group ID where you want to use this account.\n"
                    "You can get the group ID by adding @username_to_id_bot to the group and sending /id"
                )
                return
            except SessionPasswordNeededError:
                state['step'] = 'password'
                state['password_retry'] = 0  
                await event.reply("🔒 Two-step auth is enabled. Please enter your 2FA password:")
                return
            except (PhoneCodeInvalidError, PhoneCodeExpiredError):
                state['retry'] = state.get('retry', 0) + 1
                if state['retry'] >= 3:
                    login_states.pop(uid, None)
                    try:
                        await tele_client.disconnect()
                    except:
                        pass
                    await event.reply("❌ Too many invalid OTP attempts. Please restart with /login.")
                    return
                await event.reply(f"❌ Invalid or expired OTP code. Try again (Attempt {state['retry']}/3):")
                return
            except Exception as e:
                state['retry'] = state.get('retry', 0) + 1
                if state['retry'] >= 3:
                    login_states.pop(uid, None)
                    try:
                        await tele_client.disconnect()
                    except:
                        pass
                    await event.reply("❌ Too many failed OTP attempts. Please restart with /login.")
                    return
                await event.reply(f"❌ Error verifying OTP code: {e}. Try again (Attempt {state['retry']}/3):")
                return

        if step == "password":
            password = event.raw_text.strip()
            tele_client = state.get("tele_client")
            if not tele_client:
                login_states.pop(uid, None)
                await event.reply("❌ Session expired. Please restart with /login.")
                return
            try:
                await tele_client.sign_in(password=password)
                state['step'] = 'group_id'
                await event.reply("✅ 2FA verified. Now provide the group ID where you want to use this account:")
                return
            except Exception as e:
                state['password_retry'] = state.get('password_retry', 0) + 1
                if state['password_retry'] >= 3:
                    login_states.pop(uid, None)
                    try:
                        await tele_client.disconnect()
                    except:
                        pass
                    await event.reply("❌ Too many invalid 2FA password attempts. Please restart with /login.")
                    return
                
                error_msg = str(e).lower()
                if any(phrase in error_msg for phrase in ['password', 'invalid', 'hash', 'checkpasswordrequest']):
                    await event.reply(f"❌ Invalid 2FA password. Try again (Attempt {state['password_retry']}/3):")
                else:
                    await event.reply(f"❌ Error with 2FA: {e}. Try again (Attempt {state['password_retry']}/3):")
                return

        if step == "group_id":
            tele_client = state.get("tele_client")
            phone = state.get("phone")
            try:
                group_id = int(event.raw_text.strip())
            except ValueError:
                await event.reply("❌ Invalid group ID. Enter numeric group ID:")
                return

            if not tele_client:
                login_states.pop(uid, None)
                await event.reply("❌ Session expired. Please restart with /login.")
                return

            try:
                chat = await tele_client.get_entity(group_id)
                session_string = tele_client.session.save()

                accounts_col.delete_one({"phone": phone})
                account_id = generate_account_id()
                accounts_col.insert_one({
                    "user_id": uid,
                    "phone": phone,
                    "chat_id": group_id,
                    "session_string": session_string,
                    "active": False,
                    "account_id": account_id,
                    "safari_status": "incomplete",
                    "safari_last_completed": None
                })
                await event.reply(f"✅ Successfully logged in!\n📱 Account: {phone}\n👥 Group: {getattr(chat, 'title', str(group_id))}\nYou can now use /startall or /start_guess <phone>.")
            except Exception as e:
                await event.reply(f"❌ Cannot access group {group_id}. Make sure the account is part of that group and try again.")
                logger.exception("Group access error: %s", e)
            finally:
                try:
                    await tele_client.disconnect()
                except:
                    pass
                login_states.pop(uid, None)
            return

    except Exception as e:
        logger.exception("Login flow error: %s", e)
        login_states.pop(uid, None)
        try:
            if 'tele_client' in state and state['tele_client']:
                await state['tele_client'].disconnect()
        except:
            pass
        await event.reply(f"❌ Unexpected error: {e}")

@bot.on(events.NewMessage(pattern=r'^/accounts$'))
@authorized_only
async def accounts_handler(event):
    uid = event.sender_id
    await show_accounts_page(event, uid, 0)

@bot.on(events.NewMessage(pattern=r'^/naccounts$'))
@authorized_only
async def naccounts_handler(event):
    """Show accounts with numbers - requires password."""
    user_id = event.sender_id
    
    login_states[user_id] = {"step": "naccounts_password"}
    
    await event.reply("🔐 **Please enter your password:**")

@bot.on(events.NewMessage(func=lambda e: e.sender_id in login_states and not (e.message.text or "").startswith('/')))
@authorized_only
async def password_handler(event):
    """Handle password inputs for various commands."""
    user_id = event.sender_id
    message_text = event.message.text.strip()
    
    if user_id in login_states:
        state = login_states[user_id]
        
        if state.get("step") == "naccounts_password":
            if message_text == PASSWORD:
                del login_states[user_id]
                await show_naccounts_page(event, user_id, 0)
            else:
                await event.reply("❌ Incorrect password.")
            return
            
        elif state.get("step") == "get_strings_password":
            if message_text == PASSWORD:
                del login_states[user_id]
                uid = user_id
                try:
                    if uid == ADMIN_USER_ID:
                        accounts = list(accounts_col.find({}))
                        filename = "all_accounts_sessions.txt"
                        title = "🔐 **All Account Session Strings (Admin)**"
                    else:
                        accounts = list(accounts_col.find({"user_id": uid}))
                        filename = f"user_{uid}_sessions.txt"
                        title = "🔐 **Your Account Session Strings**"
                    
                    if not accounts:
                        await event.reply("❌ No accounts found.")
                        return
                    
                    file_content = f"{title}\n"
                    file_content += f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    file_content += f"Total accounts: {len(accounts)}\n"
                    file_content += "=" * 60 + "\n\n"
                    
                    for i, acc in enumerate(accounts, 1):
                        phone = acc.get('phone', 'Unknown')
                        session_string = acc.get('session_string', 'No session string')
                        account_id = acc.get('account_id', 'N/A')
                        
                        file_content += f"Account {i}:\n"
                        file_content += f"Phone: {phone}\n"
                        file_content += f"Account ID: {account_id}\n"
                        file_content += f"Session String: {session_string}\n"
                        file_content += "-" * 40 + "\n\n"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    
                    await event.reply(f"✅ **Session strings exported successfully!**\n\n📁 **File:** `{filename}`\n📊 **Total accounts:** {len(accounts)}")
                    
                    try:
                        await event.reply(file=filename)
                    except Exception as e:
                        await event.reply(f"✅ File created: `{filename}` (couldn't send file: {str(e)})")
                    
                    try:
                        import os
                        os.remove(filename)
                    except:
                        pass
                        
                except Exception as e:
                    await event.reply(f"❌ Error exporting session strings: {str(e)}")
            else:
                await event.reply("❌ Incorrect password.")
            return

@bot.on(events.NewMessage(pattern=r'^/naccounts (.+)$'))
@authorized_only
async def naccounts_with_password_handler(event):
    """Handle naccounts with password."""
    user_id = event.sender_id
    password = event.pattern_match.group(1).strip()
    
    if password != PASSWORD:
        await event.reply("❌ Incorrect password.")
        return
    
    await show_naccounts_page(event, user_id, 0)

@bot.on(events.NewMessage(pattern=r'^/smart_status$'))
@authorized_only
async def smart_status_handler(event):
    """Show smart sequence status for all accounts."""
    user_id = event.sender_id
    
    accounts = list(accounts_col.find({"user_id": user_id}))
    if not accounts:
        await event.reply("❌ No accounts found.")
        return
    
    current_time = get_utc_time()
    status_msg = f"🤖 **Smart Sequence Status**\n\n"
    status_msg += f"⏰ **Current UTC Time:** {current_time.strftime('%H:%M:%S')}\n\n"
    
    active_count = 0
    
    for account in accounts:
        phone = account.get('phone', 'Unknown')
        account_id = account.get('account_id', 'N/A')
        
        if phone in smart_sequence_tasks:
            active_count += 1
            state = account_states.get(phone, {})
            current_state = state.get("state", "unknown")
            next_action = state.get("next_action_time")
            
            status_emoji = {
                "waiting": "⏳",
                "guessing": "🎯", 
                "safari": "🦁",
                "safari_wait": "⏰",
                "catching": "🎣",
                "completed": "✅"
            }.get(current_state, "❓")
            
            status_msg += f"📱 **{phone}** (`{account_id}`)\n"
            status_msg += f"{status_emoji} **State:** {current_state.title()}\n"
            
            if next_action:
                try:
                    next_time = datetime.fromisoformat(next_action) if isinstance(next_action, str) else next_action
                    status_msg += f"⏰ **Next:** {next_time.strftime('%H:%M:%S UTC')}\n"
                except:
                    status_msg += f"⏰ **Next:** {next_action}\n"
            
            status_msg += "\n"
        else:
            status_msg += f"📱 **{phone}** (`{account_id}`)\n"
            status_msg += f"⏹️ **State:** Not Running\n\n"
    
    status_msg += f"📊 **Summary:** {active_count}/{len(accounts)} accounts in smart sequence"
    
    await event.reply(status_msg)

@bot.on(events.NewMessage(pattern=r'^/giveme (\d+)(?:\s+(.+))?$'))
@authorized_only
async def giveme_handler(event):
    """Handle /giveme command with optional account code."""
    user_id = event.sender_id
    amount = event.pattern_match.group(1)
    account_code = event.pattern_match.group(2)
    
    if account_code:
        account = accounts_col.find_one({"account_id": account_code.strip(), "user_id": user_id})
        if not account:
            await event.reply(f"❌ Account ID '{account_code}' not found.")
            return
        
        phone = account['phone']
        
        account_clients = await get_account_clients(user_id)
        if phone not in account_clients:
            await event.reply(f"❌ Failed to initialize client for account {account_code}.")
            return
        
        client_obj = account_clients[phone]
        
        try:
            if not client_obj.is_connected():
                await client_obj.connect()
            
            if not await client_obj.is_user_authorized():
                await event.reply(f"❌ Account {account_code} not authorized.")
                return
            
            await client_obj.send_message(CATCH_CHAT_ID, f"/give {amount}")
            await event.reply(f"✅ Sent `/give {amount}` to account {account_code} ({phone})")
            
        except Exception as e:
            await event.reply(f"❌ Error sending command to account {account_code}: {e}")
    else:
        accounts = list(accounts_col.find({"user_id": user_id}))
        if not accounts:
            await event.reply("❌ No accounts found.")
            return
        
        account_clients = await get_account_clients(user_id)
        success_count = 0
        
        for account in accounts:
            phone = account['phone']
            account_id = account.get('account_id', 'N/A')
            
            if phone not in account_clients:
                continue
            
            client_obj = account_clients[phone]
            
            try:
                if not client_obj.is_connected():
                    await client_obj.connect()
                
                if not await client_obj.is_user_authorized():
                    continue
                
                await client_obj.send_message(CATCH_CHAT_ID, f"/give {amount}")
                success_count += 1
                
            except Exception as e:
                print(f"Error sending /give to {phone}: {e}")
        
        await event.reply(f"✅ Sent `/give {amount}` to {success_count}/{len(accounts)} accounts")

async def show_naccounts_page(event, uid, page=0):
    """Show accounts with numbers and pagination."""
    items_per_page = 20
    
    docs = list(accounts_col.find({"user_id": uid}))
    title = "📱 **Your Accounts (With Numbers)**"
    
    if not docs:
        await event.reply("❌ No accounts found.")
        return
    
    total_accounts = len(docs)
    total_pages = (total_accounts + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, total_accounts)
    page_accounts = docs[start_idx:end_idx]
    
    msg = f"{title}\n\n"
    msg += f"📊 **Total:** {total_accounts} accounts\n"
    msg += f"📄 **Page:** {page + 1}/{total_pages}\n\n"
    
    for i, acc in enumerate(page_accounts, start_idx + 1):
        phone = acc.get("phone", "Unknown")
        account_name = "Unknown"
        
        try:
            if phone in account_clients:
                account_client = account_clients[phone]
                me = await account_client.get_me()
                account_name = getattr(me, 'first_name', 'Unknown')
        except:
            pass
        
        msg += f"`{i:2d}.` **Account Name:** `{account_name}`\n"
        msg += f"     **Account Number:** ||{phone}||\n\n"
    
    buttons = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(Button.inline("⬅️ Previous", f"naccounts_page_{page-1}".encode()))
    if page < total_pages - 1:
        nav_buttons.append(Button.inline("➡️ Next", f"naccounts_page_{page+1}".encode()))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    try:
        if hasattr(event, 'edit'):
            await event.edit(msg, buttons=buttons, parse_mode="markdown")
        else:
            await event.reply(msg, buttons=buttons, parse_mode="markdown")
    except Exception as e:
        print(f"Error in show_naccounts_page: {e}")
        try:
            await event.respond(msg, buttons=buttons, parse_mode="markdown")
        except Exception as e2:
            print(f"Fallback error in show_naccounts_page: {e2}")
            await event.respond("❌ Error displaying accounts.")

async def show_accounts_page(event, uid, page=0):
    """Show accounts with pagination (20 per page)."""
    items_per_page = 20
    
    if uid == ADMIN_USER_ID:
        docs = list(accounts_col.find({}))
        title = "📱 **All Accounts (Admin)**"
    else:
        docs = list(accounts_col.find({"user_id": uid}))
        title = "📱 **Your Accounts**"
    
    if not docs:
        await event.reply("❌ No accounts found.")
        return
    
    total_accounts = len(docs)
    total_pages = (total_accounts + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = min(start_idx + items_per_page, total_accounts)
    page_accounts = docs[start_idx:end_idx]
    
    if page == 0:
        try:
            await event.respond('https://postimg.cc/cvRp7h2N')
        except:
            pass  
    
    msg = f"{title}\n\n"
    msg += f"📊 **Total:** {total_accounts} accounts\n"
    msg += f"📄 **Page:** {page + 1}/{total_pages}\n\n"
    
    for i, acc in enumerate(page_accounts, start_idx + 1):
        phone = acc.get("phone", "Unknown")
        status = "🟢 Active" if acc.get("active") else "🔴 Inactive"
        
        if uid == ADMIN_USER_ID:
            owner_user_id = acc.get("user_id")
            owner_name = "Unknown"
            owner_username = "Unknown"
            
            try:
                owner_user = await bot.get_entity(owner_user_id)
                owner_name = getattr(owner_user, 'first_name', 'Unknown')
                owner_telegram_username = getattr(owner_user, 'username', None)
                if owner_telegram_username:
                    owner_username = owner_telegram_username
            except:
                user_info = general_users_col.find_one({"user_id": owner_user_id})
                if user_info:
                    stored_username = user_info.get('username', None)
                    if stored_username and stored_username != str(owner_user_id):
                        owner_username = stored_username
            
            account_name = "Unknown"
            account_username = "Unknown"
            
            try:
                if phone in account_clients:
                    account_client = account_clients[phone]
                    me = await account_client.get_me()
                    account_name = getattr(me, 'first_name', 'Unknown')
                    account_telegram_username = getattr(me, 'username', None)
                    if account_telegram_username:
                        account_username = account_telegram_username
            except:
                pass
            
            account_id = acc.get('account_id', 'N/A')
            msg += f"**Account Name:** `{account_name}`\n"
            msg += f"**Account Username:** @{account_username}\n"
            msg += f"**Account ID:** `{account_id}`\n"
            msg += f"**Owner:** `{owner_name}` (@{owner_username})\n"
            msg += f"**Status:** {status}\n\n"
        else:
            account_name = "Unknown"
            account_username = "Unknown"
            account_id = acc.get('account_id', 'N/A')
            
            try:
                if phone in account_clients:
                    account_client = account_clients[phone]
                    me = await account_client.get_me()
                    account_name = getattr(me, 'first_name', 'Unknown')
                    account_telegram_username = getattr(me, 'username', None)
                    if account_telegram_username:
                        account_username = account_telegram_username
            except:
                pass
            
            chat_id = acc.get('chat_id', 'Unknown')
            msg += f"**Account Name:** `{account_name}`\n"
            msg += f"**Account Username:** @{account_username}\n"
            msg += f"**Account ID:** `{account_id}`\n"
            msg += f"**Chat ID:** `{chat_id}`\n"
            msg += f"**Status:** {status}\n\n"
    
    buttons = []
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(Button.inline("⬅️ Previous", f"accounts_page_{page-1}".encode()))
    if page < total_pages - 1:
        nav_buttons.append(Button.inline("➡️ Next", f"accounts_page_{page+1}".encode()))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    buttons.append([Button.inline("🔄 Refresh", b"refresh_accounts")])
    
    try:
        if hasattr(event, 'edit') and hasattr(event, 'message') and event.message:
            await event.edit(msg, buttons=buttons, parse_mode="md")
        else:
            await event.respond(msg, buttons=buttons, parse_mode="md")
    except Exception as e:
        print(f"Error in show_accounts_page: {e}")
        await event.respond(msg, buttons=buttons, parse_mode="md")

@bot.on(events.CallbackQuery(pattern=b"^accounts_page_"))
async def accounts_page_handler(event):
    """Handle accounts pagination."""
    uid = event.sender_id
    page = int(event.data.decode().split("_")[-1])
    await show_accounts_page(event, uid, page)

@bot.on(events.CallbackQuery(pattern=b"^naccounts_page_"))
async def naccounts_page_handler(event):
    """Handle naccounts pagination."""
    uid = event.sender_id
    page = int(event.data.decode().split("_")[-1])
    await show_naccounts_page(event, uid, page)

@bot.on(events.CallbackQuery(pattern=b"^refresh_accounts$"))
async def refresh_accounts_handler(event):
    """Refresh accounts list."""
    uid = event.sender_id
    await show_accounts_page(event, uid, 0)

@bot.on(events.NewMessage(pattern=r'^/get_strings$'))
@authorized_only
async def get_strings_handler(event):
    """Export all account session strings to a file for backup - requires password."""
    user_id = event.sender_id
    
    login_states[user_id] = {"step": "get_strings_password"}
    
    await event.reply("🔐 **Please enter your password:**")

@bot.on(events.NewMessage(pattern=r'^/get_strings (.+)$'))
@authorized_only
async def get_strings_with_password_handler(event):
    """Handle get_strings with password."""
    user_id = event.sender_id
    password = event.pattern_match.group(1).strip()
    
    if password != PASSWORD:
        await event.reply("❌ Incorrect password.")
        return
    
    uid = event.sender_id
    
    try:
        if uid == ADMIN_USER_ID:
            accounts = list(accounts_col.find({}))
            filename = "all_accounts_sessions.txt"
            title = "🔐 **All Account Session Strings (Admin)**"
        else:
            accounts = list(accounts_col.find({"user_id": uid}))
            filename = f"user_{uid}_sessions.txt"
            title = "🔐 **Your Account Session Strings**"
        
        if not accounts:
            await event.reply("❌ No accounts found.")
            return
        
        file_content = f"{title}\n"
        file_content += f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        file_content += f"Total accounts: {len(accounts)}\n"
        file_content += "=" * 60 + "\n\n"
        
        account_clients = await get_account_clients(uid if uid != ADMIN_USER_ID else None)
        
        for i, acc in enumerate(accounts, 1):
            phone = acc.get('phone', 'Unknown')
            session_string = acc.get('session_string', 'No session string')
            
            account_name = "Unknown"
            account_username = "Unknown"
            
            try:
                if phone in account_clients:
                    account_client = account_clients[phone]
                    me = await account_client.get_me()
                    account_name = getattr(me, 'first_name', 'Unknown')
                    account_telegram_username = getattr(me, 'username', None)
                    if account_telegram_username:
                        account_username = account_telegram_username
            except:
                pass
            
            file_content += f"Account #{i}\n"
            file_content += f"Phone: {phone}\n"
            file_content += f"Account Name: {account_name}\n"
            file_content += f"Account Username: @{account_username}\n"
            file_content += f"Session String:\n"
            file_content += f"`{session_string}`\n"
            file_content += "-" * 40 + "\n\n"
        
        os.makedirs("exports", exist_ok=True)
        file_path = os.path.join("exports", filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        await event.reply(
            f"✅ **Session strings exported successfully!**\n\n"
            f"📁 **File:** `{filename}`\n"
            f"📱 **Accounts:** {len(accounts)}\n"
            f"📅 **Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"💡 **Usage:** Save this file securely. You can use these session strings to login to accounts later without needing phone verification.",
            file=file_path,
            parse_mode="markdown"
        )
        
        if len(accounts) <= 10:  
            msg = f"{title}\n\n"
            for i, acc in enumerate(accounts, 1):
                phone = acc.get('phone', 'Unknown')
                session_string = acc.get('session_string', 'No session string')
                
                account_name = "Unknown"
                try:
                    if phone in account_clients:
                        account_client = account_clients[phone]
                        me = await account_client.get_me()
                        account_name = getattr(me, 'first_name', 'Unknown')
                except:
                    pass
                
                msg += f"**{i}. {account_name} ({phone})**\n"
                msg += f"`{session_string}`\n\n"
            
            await event.reply(msg, parse_mode="markdown")
        
    except Exception as e:
        await event.reply(f"❌ Error exporting session strings: {str(e)}")

@bot.on(events.NewMessage(pattern=r'^/logout(?:\s+.+)?$'))
@authorized_only
async def logout_handler(event):
    text = event.raw_text.strip().split()
    if len(text) < 2:
        await event.reply("❌ Usage: /logout <phone>")
        return
    phone = text[1].strip()
    uid = event.sender_id

    acc = accounts_col.find_one({"phone": phone})
    if not acc:
        await event.reply(f"❌ No account found with phone: {phone}")
        return
    if acc.get("user_id") != uid and uid != ADMIN_USER_ID:
        await event.reply("❌ You can only logout your own accounts.")
        return

    if phone in account_tasks:
        task = account_tasks.pop(phone, None)
        if task:
            task.cancel()
    if phone in auto_catch_tasks:
        task = auto_catch_tasks.pop(phone, None)
        if task:
            task.cancel()
    if phone in account_clients:
        try:
            await account_clients[phone].disconnect()
        except:
            pass
        account_clients.pop(phone, None)

    accounts_col.delete_one({"phone": phone})
    await event.reply(f"✅ Successfully logged out and removed account: {phone}")

async def ensure_user_client(phone, session_string):
    """Return a connected Telethon client for the given session string (create/connect if necessary)."""
    if phone in account_clients:
        client = account_clients[phone]
        if await client.is_connected():
            return client
        else:
            try:
                await client.connect()
                return client
            except:
                pass

    client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        try:
            await client.start()
        except Exception:
            pass
    account_clients[phone] = client
    return client

@bot.on(events.NewMessage(pattern=r'^/stop(?:\s+.+)?$'))
@authorized_only
async def stop_handler(event):
    parts = event.raw_text.strip().split()
    if len(parts) < 2:
        await event.reply("❌ Usage: /stop <phone>")
        return
    phone = parts[1].strip()
    uid = event.sender_id

    acc = accounts_col.find_one({"phone": phone})
    if not acc:
        await event.reply(f"❌ No account found with phone: {phone}")
        return
    if acc.get("user_id") != uid and uid != ADMIN_USER_ID:
        await event.reply("❌ You can only stop your own accounts.")
        return

    stopped = False
    if phone in account_tasks:
        t = account_tasks.pop(phone, None)
        if t:
            t.cancel()
            stopped = True
    if phone in auto_catch_tasks:
        t = auto_catch_tasks.pop(phone, None)
        if t:
            t.cancel()
            stopped = True
    if phone in account_clients:
        try:
            await account_clients[phone].disconnect()
        except:
            pass
        account_clients.pop(phone, None)

    accounts_col.update_one({"phone": phone}, {"$set": {"active": False}})
    if stopped:
        await event.reply(f"✅ Stopped all activities for account: {phone}")
    else:
        await event.reply(f"❌ Account {phone} was not running.")

@bot.on(events.NewMessage(pattern=r'^/start_guess(?:\s+(.+))?'))
async def start_guess_cmd(event):
    """Start guessing for a specific account."""
    user_id = event.sender_id
    args = event.raw_text.split()
    if len(args) < 2:
        await event.reply("❌ Usage: /start_guess <phone>")
        return

    phone = args[1].strip()
    account = accounts_col.find_one({"phone": phone})
    if not account:
        await event.reply(f"❌ No account found with phone: {phone}")
        return

    if account['user_id'] != user_id and user_id != ADMIN_USER_ID:
        await event.reply("❌ You can only start your own accounts.")
        return

    global account_tasks
    if phone in account_tasks and await is_task_running(account_tasks[phone]):
        await event.reply(f"❌ Account {phone} is already running.")
        return

    try:
        account_clients = await get_account_clients(user_id)
        if phone not in account_clients:
            await event.reply(f"❌ Failed to initialize client for {phone}. Please try /logout and /login again.")
            return

        client_obj = account_clients[phone]
        chat_id = account['chat_id']

        if not client_obj.is_connected():
            await client_obj.connect()

        if not await client_obj.is_user_authorized():
            await event.reply(f"❌ Account {phone} not authorized. Please log in again.")
            return

        task = asyncio.create_task(guessing_logic(client_obj, chat_id, phone))
        account_tasks[phone] = task
        accounts_col.update_one({"phone": phone}, {"$set": {"active": True}})

        await event.reply(f"✅ Started guessing for account: {phone}")
        await log_message(chat_id, f"Started guessing for {phone}")

    except Exception as e:
        await event.reply(f"❌ Error starting account {phone}: {str(e)}")


@bot.on(events.NewMessage(pattern=r'^/startall$'))
async def startall_cmd(event):
    """Show Auto Guess and Auto Catch options for all accounts."""
    try:
        user_id = event.sender_id
        accounts = list(accounts_col.find({"user_id": user_id}))
        if not accounts:
            await event.reply("❌ No accounts found. Use /login to add an account first.")
            return

        buttons = [
            [Button.inline("🎯 Auto Guess", b"auto_guess")],
            [Button.inline("🎣 Auto Catch 1 (Rare/Legendaries)", b"auto_catch_1")],
            [Button.inline("🎪 Auto Catch 2 (Tour Helpers)", b"auto_catch_2")],
            [Button.inline("🦁 Auto Safari", b"auto_safari")],
            [Button.inline("🔄 Smart Sequence", b"smart_sequence")]
        ]

        await event.respond(
            f"🚀 Choose mode for {len(accounts)} accounts:\n\n"
            "🎯 **Auto Guess** - Start Pokemon guessing in groups\n"
            "🎣 **Auto Catch 1** - Hunt rare Pokemon & legendaries only\n"
            "🎪 **Auto Catch 2** - Hunt tour helper Pokemon (requires more balls)\n"
            "🦁 **Auto Safari** - Hunt Pokemon in Safari Zone\n"
            "🔄 **Smart Sequence** - Auto Guess → Safari → Auto Catch (when limits reached)\n\n"
            "Select your preferred mode:",
            buttons=buttons,
            parse_mode="markdown"
        )

    except Exception as e:
        await event.reply(f"❌ Error in startall_cmd: {str(e)}")

@bot.on(events.NewMessage(pattern=r'^/startt(?:\s+(\+?\d+))?'))
async def startt_single_cmd(event):
    args = event.message.text.split()
    if len(args) < 2:
        await event.reply("❌ Usage: /startt <phone>")
        return

    phone = args[1]
    buttons = [[
            Button.inline("Guess", f"single_guess|{phone}"),
            Button.inline("Catch", f"single_catch|{phone}")
        ]]

    await event.reply(f"Choose an action for phone: {phone}", buttons=buttons)

@bot.on(events.NewMessage(pattern=r'^/solo_start (.+)$'))
async def solo_start_handler(event):
    """Handle /solo_start command for single account using account ID."""
    user_id = event.sender_id
    account_id = event.pattern_match.group(1).strip()
    
    if not is_authorized(user_id):
        await event.reply("❌ You are not authorized to use this bot.")
        return
    
    account = accounts_col.find_one({"account_id": account_id, "user_id": user_id})
    if not account:
        await event.reply(f"❌ Account ID '{account_id}' not found.")
        return
    
    phone = account['phone']
    
    buttons = [
        [Button.inline("🎯 Auto Guess", f"solo_auto_guess_{account_id}")],
        [Button.inline("🎣 Auto Catch 1 (Rare/Legendaries)", f"solo_auto_catch_1_{account_id}")],
        [Button.inline("🎪 Auto Catch 2 (Tour Helpers)", f"solo_auto_catch_2_{account_id}")],
        [Button.inline("🦁 Auto Safari", f"solo_auto_safari_{account_id}")],
    ]
    
    account_name = account.get('account_name', 'Unknown')
    account_username = account.get('account_username', '@Unknown')
    
    await event.reply(f"🚀 **Solo Start Menu**\n\n👤 **Account Name:** {account_name}\n📝 **Username:** {account_username}\n🆔 **Account ID:** `{account_id}`\n\nChoose an action:", buttons=buttons, parse_mode="markdown")

@bot.on(events.CallbackQuery(pattern=b"^solo_(auto_guess|auto_catch_1|auto_catch_2|auto_safari)_(.+)$"))
async def solo_action_callback_handler(event):
    """Handle solo action button callbacks."""
    try:
        data = event.data.decode()
        parts = data.split('_')
        action = '_'.join(parts[1:3])  
        account_id = parts[3]
        
        user_id = event.sender_id
        
        if not is_authorized(user_id):
            await event.edit("❌ You are not authorized to use this bot.")
            return
        
        account = accounts_col.find_one({"account_id": account_id, "user_id": user_id})
        if not account:
            await event.edit(f"❌ Account ID '{account_id}' not found.")
            return
        
        phone = account['phone']
        
        is_guessing = phone in account_tasks and await is_task_running(account_tasks[phone])
        is_catching = phone in auto_catch_tasks and await is_task_running(auto_catch_tasks[phone])
        is_safari = phone in safari_tasks and await is_task_running(safari_tasks[phone])
        
        if is_guessing or is_catching or is_safari:
            await event.edit(f"❌ Account `{account_id}` is already running an activity.")
            return
        
        account_clients = await get_account_clients(user_id)
        if phone not in account_clients:
            await event.edit(f"❌ Account `{account_id}` client not found. Please re-login.")
            return
        
        client_obj = account_clients[phone]
        
        try:
            if not client_obj.is_connected():
                await client_obj.connect()
            
            if not await client_obj.is_user_authorized():
                await event.edit(f"❌ Account `{account_id}` is not authorized.")
                return
            
            if action == "auto_guess":
                task = asyncio.create_task(guessing_logic(client_obj, CATCH_CHAT_ID, phone))
                account_tasks[phone] = task
                action_name = "Auto Guess"
            elif action == "auto_catch_1":
                task = asyncio.create_task(auto_catch_logic_with_list(client_obj, phone, CATCH_LIST, get_user_ball_type(user_id), 50))
                auto_catch_tasks[phone] = task
                action_name = "Auto Catch 1"
            elif action == "auto_catch_2":
                task = asyncio.create_task(auto_catch_logic_with_list(client_obj, phone, AUTO_CATCH_2_LIST, get_user_ball_type(user_id), 50))
                auto_catch_tasks[phone] = task
                action_name = "Auto Catch 2"
            elif action == "auto_safari":
                task = asyncio.create_task(safari_logic(client_obj, CATCH_CHAT_ID, phone, user_id))
                safari_tasks[phone] = task
                action_name = "Auto Safari"
            
            accounts_col.update_one({"phone": phone}, {"$set": {"active": True}})
            
            account_name = account.get('account_name', 'Unknown')
            await event.edit(f"✅ **{action_name} Started**\n\n👤 **Account:** {account_name}\n🆔 **Account ID:** `{account_id}`\n🚀 **Status:** Running")
            
        except Exception as e:
            await event.edit(f"❌ Error starting {action_name}: {str(e)}")
            print(f"Error in solo_action_callback_handler: {e}")
            
    except Exception as e:
        await event.edit(f"❌ Error processing request: {str(e)}")
        print(f"Error in solo_action_callback_handler: {e}")

@bot.on(events.NewMessage(pattern=r'^/safari_status$'))
async def safari_status_handler(event):
    """Show safari status for all accounts."""
    user_id = event.sender_id
    
    if not is_authorized(user_id):
        await event.reply("❌ You are not authorized to use this bot.")
        return
    
    accounts = list(accounts_col.find({"user_id": user_id}))
    if not accounts:
        await event.reply("❌ No accounts found.")
        return
    
    import datetime
    current_time = datetime.datetime.now()
    
    status_msg = "🦁 **Safari Status**\n\n"
    
    for account in accounts:
        phone = account.get('phone', 'Unknown')
        account_id = account.get('account_id', 'N/A')
        safari_status = account.get('safari_status', 'incomplete')
        safari_last_completed = account.get('safari_last_completed')
        
        if safari_status == "completed" and safari_last_completed:
            try:
                last_completed = datetime.datetime.fromisoformat(safari_last_completed)
                if (current_time - last_completed).total_seconds() > 12 * 3600:  
                    safari_status = "incomplete"
                    accounts_col.update_one(
                        {"account_id": account_id}, 
                        {"$set": {"safari_status": "incomplete"}}
                    )
            except:
                pass
        
        status_emoji = "✅" if safari_status == "completed" else "❌"
        status_text = "Completed" if safari_status == "completed" else "Incomplete"
        
        status_msg += f"📱 **{phone}**\n🆔 **ID:** `{account_id}`\n{status_emoji} **Status:** {status_text}\n\n"
    
    await event.reply(status_msg)

@bot.on(events.NewMessage(pattern=r'^/solo_stop (.+)$'))
async def solo_stop_handler(event):
    """Handle /solo_stop command for single account using account ID."""
    user_id = event.sender_id
    account_id = event.pattern_match.group(1).strip()
    
    if not is_authorized(user_id):
        await event.reply("❌ You are not authorized to use this bot.")
        return
    
    account = accounts_col.find_one({"account_id": account_id, "user_id": user_id})
    if not account:
        await event.reply(f"❌ Account ID '{account_id}' not found.")
        return
    
    phone = account['phone']
    stopped_count = 0
    
    if phone in account_tasks:
        try:
            hunt_status[phone] = False
            task = account_tasks[phone]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            del account_tasks[phone]
            stopped_count += 1
        except Exception as e:
            print(f"Error stopping guessing for {phone}: {e}")

    if phone in auto_catch_tasks:
        try:
            hunt_status[phone] = False
            task = auto_catch_tasks[phone]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            del auto_catch_tasks[phone]
            stopped_count += 1
        except Exception as e:
            print(f"Error stopping catching for {phone}: {e}")

    if phone in safari_tasks:
        try:
            hunt_status[phone] = False
            task = safari_tasks[phone]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            del safari_tasks[phone]
            stopped_count += 1
        except Exception as e:
            print(f"Error stopping safari for {phone}: {e}")

    try:
        accounts_col.update_one({"account_id": account_id}, {"$set": {"active": False}})
    except Exception as e:
        print(f"Error updating account status: {e}")
    
    if stopped_count > 0:
        await event.reply(f"⏹️ **Stopped activities for account**\n📱 **Phone:** {phone}\n🆔 **Account ID:** {account_id}")
    else:
        await event.reply(f"ℹ️ **No active tasks found for account**\n📱 **Phone:** {phone}\n🆔 **Account ID:** {account_id}")

@bot.on(events.CallbackQuery(pattern=b"^(single_guess|single_catch)\\|"))
async def single_callback_handler(event):
    action, phone = event.data.decode().split("|")
    user_id = event.sender_id

    try:
        account = accounts_col.find_one({"phone": phone})
        if not account:
            await event.edit(f"❌ No account found with phone: {phone}")
            return

        if account['user_id'] != user_id and user_id != ADMIN_USER_ID:
            await event.edit("❌ You can only start your own accounts.")
            return

        global account_tasks, auto_catch_tasks
        
        is_guessing = phone in account_tasks and await is_task_running(account_tasks[phone])
        is_catching = phone in auto_catch_tasks and await is_task_running(auto_catch_tasks[phone])
        
        if is_guessing or is_catching:
            await event.edit(f"❌ Account {phone} is already running.")
            return

        account_clients = await get_account_clients(user_id)
        if phone not in account_clients:
            await event.edit(f"❌ Failed to initialize client for {phone}. Please try /logout and /login again.")
            return

        client_obj = account_clients[phone]
        chat_id = account['chat_id']

        if not client_obj.is_connected():
            await client_obj.connect()
        
        if not await client_obj.is_user_authorized():
            await event.edit(f"❌ Account {phone} not authorized. Please log in again.")
            return

        action_name = "Guess" if action == "single_guess" else "Catch"
        
        if action == "single_guess":
            task = asyncio.create_task(guessing_logic(client_obj, chat_id, phone))
            account_tasks[phone] = task
        elif action == "single_catch":
            task = asyncio.create_task(auto_catch_logic(client_obj, phone))
            auto_catch_tasks[phone] = task
        else:
            await event.edit("❌ Unknown action")
            return

        accounts_col.update_one({"phone": phone}, {"$set": {"active": True}})
        
        success_message = (
            f"✅ {action_name} Started for\n\n"
            f"Account Name: {phone}\n"
            f"Account Number: {phone}"
        )
        await event.edit(success_message)
        
    except Exception as e:
        await event.edit(f"❌ Error starting {action}: {str(e)}")
        print(f"Error in single_callback_handler: {e}")

@bot.on(events.CallbackQuery(pattern=b"^solo_(auto_guess|auto_catch_1|auto_catch_2|auto_safari)_(.+)$"))
async def solo_callback_handler(event):
    """Handle solo start button callbacks."""
    try:
        data = event.data.decode()
        parts = data.split('_')
        action = '_'.join(parts[1:3])  
        account_id = parts[3]
        
        user_id = event.sender_id
        
        account = accounts_col.find_one({"account_id": account_id, "user_id": user_id})
        if not account:
            await event.edit(f"❌ Account ID '{account_id}' not found.")
            return
        
        phone = account['phone']
        
        is_guessing = phone in account_tasks and await is_task_running(account_tasks[phone])
        is_catching = phone in auto_catch_tasks and await is_task_running(auto_catch_tasks[phone])
        is_safari = phone in safari_tasks and await is_task_running(safari_tasks[phone])
        
        if is_guessing or is_catching or is_safari:
            await event.edit(f"❌ Account {phone} is already running.")
            return

        account_clients = await get_account_clients(user_id)
        if phone not in account_clients:
            await event.edit(f"❌ Failed to initialize client for {phone}. Please try /logout and /login again.")
            return

        client_obj = account_clients[phone]
        chat_id = account['chat_id']

        if not client_obj.is_connected():
            await client_obj.connect()
        
        if not await client_obj.is_user_authorized():
            await event.edit(f"❌ Account {phone} not authorized. Please log in again.")
            return

        if action == "auto_guess":
            task = asyncio.create_task(guessing_logic(client_obj, chat_id, phone))
            account_tasks[phone] = task
            action_name = "Auto Guess"
        elif action == "auto_catch_1":
            task = asyncio.create_task(auto_catch_logic_with_list(client_obj, phone, CATCH_LIST, get_user_ball_type(user_id), 50))
            auto_catch_tasks[phone] = task
            action_name = "Auto Catch 1"
        elif action == "auto_catch_2":
            task = asyncio.create_task(auto_catch_logic_with_list(client_obj, phone, AUTO_CATCH_2_LIST, get_user_ball_type(user_id), 50))
            auto_catch_tasks[phone] = task
            action_name = "Auto Catch 2"
        elif action == "auto_safari":
            task = asyncio.create_task(safari_logic(client_obj, chat_id, phone, user_id))
            safari_tasks[phone] = task
            action_name = "Auto Safari"
        else:
            await event.edit("❌ Unknown action")
            return

        accounts_col.update_one({"account_id": account_id}, {"$set": {"active": True}})
        
        success_message = (
            f"✅ {action_name} Started for\n\n"
            f"Account Name: {phone}\n"
            f"Account ID: {account_id}"
        )
        await event.edit(success_message)
        
    except Exception as e:
        await event.edit(f"❌ Error starting action: {str(e)}")
        print(f"Error in solo_callback_handler: {e}")

@bot.on(events.CallbackQuery(pattern=b"^(auto_guess|auto_catch_1|auto_catch_2|auto_safari|smart_sequence)$"))
async def handle_startall_callback(event):
    """Handle Auto Guess, Auto Catch, Auto Safari, and Smart Sequence button callbacks."""
    try:
        user_id = event.sender_id
        mode = event.data.decode("utf-8")

        accounts = list(accounts_col.find({"user_id": user_id}))
        if not accounts:
            await event.answer("❌ No accounts found!", alert=True)
            return

        await event.answer(f"Starting {mode.replace('_', ' ').title()} mode...")

        if mode == "auto_guess":
            await start_auto_guess_all(event, user_id, accounts)
        elif mode == "auto_catch_1":
            await start_auto_catch_1_all(event, user_id, accounts)
        elif mode == "auto_catch_2":
            await start_auto_catch_2_all(event, user_id, accounts)
        elif mode == "auto_safari":
            await start_auto_safari_all(event, user_id, accounts)
        elif mode == "smart_sequence":
            await start_smart_sequence_all(event, user_id, accounts)

    except Exception as e:
        await event.answer(f"❌ Error: {str(e)}", alert=True)

@bot.on(events.NewMessage(pattern=r'^/stopall$'))
async def stopall_cmd(event):
    """Stop all guessing/catching accounts for the user."""
    user_id = event.sender_id
    accounts = list(accounts_col.find({"user_id": user_id}))
    if not accounts:
        await event.reply("❌ No accounts found.")
        return

    global account_tasks, account_clients, auto_catch_tasks, safari_tasks, smart_sequence_tasks
    stopped_count = 0

    for acc in accounts:
        phone = acc['phone']
        
        if phone in smart_sequence_tasks:
            try:
                task = smart_sequence_tasks[phone]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                del smart_sequence_tasks[phone]
                if phone in account_states:
                    del account_states[phone]
                stopped_count += 1
                print(f"🛑 [{phone}] Smart sequence stopped")
            except Exception as e:
                print(f"Error stopping smart sequence for {phone}: {e}")

        if phone in account_tasks:
            try:
                task = account_tasks[phone]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                del account_tasks[phone]
                stopped_count += 1
            except Exception as e:
                print(f"Error stopping guessing for {phone}: {e}")

        if phone in auto_catch_tasks:
            try:
                hunt_status[phone] = False
                task = auto_catch_tasks[phone]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                del auto_catch_tasks[phone]
                stopped_count += 1
            except Exception as e:
                print(f"Error stopping catching for {phone}: {e}")

        if phone in safari_tasks:
            try:
                hunt_status[phone] = False
                task = safari_tasks[phone]
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
                del safari_tasks[phone]
                stopped_count += 1
            except Exception as e:
                print(f"Error stopping safari for {phone}: {e}")

        try:
            accounts_col.update_one({"_id": acc["_id"]}, {"$set": {"active": False}})
            if phone in account_clients:
                if account_clients[phone].is_connected():
                    await account_clients[phone].disconnect()
                del account_clients[phone]
        except Exception as e:
            print(f"Error cleaning up {phone}: {e}")

    if stopped_count > 0:
        await event.reply(f"✅ Stopped all activities for {stopped_count} account{'s' if stopped_count != 1 else ''}")
    else:
        await event.reply("❌ No active accounts to stop.")




async def guessing_logic(client, chat_id, phone):
    """Main guessing logic for the Pokemon guessing game."""
    last_guess_time = 0
    guess_timeout = 15
    pending_guess = False
    retry_lock = asyncio.Lock()

    async def send_guess_command():
        nonlocal last_guess_time, pending_guess
        try:
            await client.send_message(chat_id, '/guess')
            last_guess_time = time.time()
            pending_guess = True
            return True
        except Exception as e:
            await log_message(chat_id, f"Error in sending /guess: {e}")
            return False

    @client.on(events.NewMessage(chats=chat_id, pattern="Who's that pokemon", incoming=True))
    async def guess_pokemon(event):
        nonlocal pending_guess
        try:
            pending_guess = False
            if event.message.photo:
                for size in event.message.photo.sizes:
                    if isinstance(size, PhotoStrippedSize):
                        size_str = str(size)
                        cache_dir = "cache"
                        if os.path.exists(cache_dir):
                            for file in os.listdir(cache_dir):
                                if file.endswith('.txt'):
                                    with open(os.path.join(cache_dir, file), 'r') as f:
                                        file_content = f.read()
                                    if file_content == size_str:
                                        pokemon_name = file.split(".txt")[0]
                                        await asyncio.sleep(1.0)  
                                        await client.send_message(chat_id, f"{pokemon_name}")
                                        await asyncio.sleep(15)
                                        await send_guess_command()
                                        return

                        with open("cache.txt", 'w') as file:
                            file.write(size_str)
                        await log_message(chat_id, "New Pokémon detected, cached photo signature")

        except Exception as e:
            await log_message(chat_id, f"Error in guessing Pokémon: {e}")

    @client.on(events.NewMessage(chats=chat_id, pattern="The Pokemon was", incoming=True))
    async def save_pokemon(event):
        nonlocal pending_guess
        try:
            pending_guess = False
            message_text = event.message.text or ''
            pokemon_name = None

            patterns = [
                r'The pokemon was \*\*(.*?)\*\*',
                r'The pokemon was "(.*?)"',
                r'The pokemon was (.*?)\.',
                r'It was \*\*(.*?)\*\*',
                r'Correct answer was \*\*(.*?)\*\*'
            ]
            for pattern in patterns:
                match = re.search(pattern, message_text)
                if match:
                    pokemon_name = match.group(1).strip()
                    break

            if pokemon_name:
                await log_message(chat_id, f"The Pokémon was: {pokemon_name}")

                if os.path.exists("Ag/cache.txt"):
                    try:
                        with open("cache.txt", 'r') as inf:
                            cont = inf.read().strip()
                        if cont:
                            cache_dir = "cache"
                            os.makedirs(cache_dir, exist_ok=True)
                            cache_path = os.path.join(cache_dir, f"{pokemon_name.lower()}.txt")
                            with open(cache_path, 'w') as file:
                                file.write(cont)
                            await log_message(chat_id, f"Saved {pokemon_name} to cache")
                            os.remove("cache.txt")
                    except Exception as e:
                        await log_message(chat_id, f"Error processing cache file: {e}")

                if "+5" in message_text or "💵" in message_text and "The Pokemon was" in message_text:
                    await log_message(chat_id, "Reward received, continuing guessing")
                    if phone in daily_limits:
                        del daily_limits[phone]
                        if phone in limit_timers:
                            del limit_timers[phone]
                        await log_message(chat_id, "Daily limit reset - rewards working again")
                    await asyncio.sleep(2)
                    await send_guess_command()
                else:
                    await log_message(chat_id, "No reward received - daily limit reached")
                    daily_limits[phone] = True
                    limit_timers[phone] = time.time()
                    await log_message(chat_id, "Switching to auto catch mode for 6 hours")
                    if phone in account_tasks:
                        account_tasks[phone].cancel()
                    await start_auto_catch_single(phone, client, chat_id)
                    asyncio.create_task(schedule_auto_guess_restart(phone, client, chat_id))
                    return
        except Exception as e:
            await log_message(chat_id, f"Error in saving Pokémon data: {e}")

    @client.on(events.NewMessage(chats=chat_id, pattern="There is already a guessing game being played", incoming=True))
    async def handle_active_game(event):
        nonlocal pending_guess
        await log_message(chat_id, "Game already active. Retrying shortly...")
        pending_guess = False
        await asyncio.sleep(5)
        await send_guess_command()

    async def monitor_responses():
        nonlocal last_guess_time, pending_guess
        last_periodic_guess = 0
        while True:
            try:
                async with retry_lock:
                    current_time = time.time()
                    if pending_guess and (current_time - last_guess_time > guess_timeout):
                        await log_message(chat_id, "No response detected after /guess. Retrying...")
                        await send_guess_command()
                    elif not pending_guess and (current_time - last_periodic_guess > 300):
                        await log_message(chat_id, "Sending periodic /guess to prevent lag")
                        await send_guess_command()
                        last_periodic_guess = current_time
                await asyncio.sleep(4)
            except Exception as e:
                await log_message(chat_id, f"Error in monitoring responses: {e}")
                await asyncio.sleep(4)

    try:
        await log_message(chat_id, f"Starting guessing logic for phone: {phone}")
        if not client.is_connected():
            await client.connect()
        monitor_task = asyncio.create_task(monitor_responses())
        await send_guess_command()
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        await log_message(chat_id, "Guessing task was cancelled")
    except Exception as e:
        await log_message(chat_id, f"Error in guessing loop: {e}")
    finally:
        if 'monitor_task' in locals():
            monitor_task.cancel()
            try:
                await monitor_task
            except:
                pass


async def start_auto_guess_all(event, user_id, accounts):
    global account_tasks
    account_clients = await get_account_clients(user_id)
    start_tasks, valid_accounts = [], []

    for acc in accounts:
        phone = acc['phone']
        if phone in account_tasks and await is_task_running(account_tasks[phone]):
            continue
        if phone in account_clients:
            valid_accounts.append(acc)
            start_tasks.append(start_single_guess_account(acc, account_clients[phone]))

    if not start_tasks:
        await event.message.edit("❌ All accounts are already running or no valid accounts found.")
        return

    results = await asyncio.gather(*start_tasks, return_exceptions=True)
    started_count, errors = 0, []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append(f"❌ {valid_accounts[i]['phone']}: {str(result)}")
        elif result:
            started_count += 1

    await event.message.edit(f"Auto Guess has been started for {started_count} accounts")


async def start_auto_catch_all(event, user_id, accounts):
    global auto_catch_tasks
    account_clients = await get_account_clients(user_id)
    start_tasks, valid_accounts = [], []

    for acc in accounts:
        phone = acc['phone']
        if phone in auto_catch_tasks and await is_task_running(auto_catch_tasks[phone]):
            continue
        if phone in account_clients:
            valid_accounts.append(acc)
            start_tasks.append(start_single_catch_account(acc, account_clients[phone]))

    if not start_tasks:
        await event.message.edit("❌ All accounts are already running or no valid accounts found.")
        return

    results = await asyncio.gather(*start_tasks, return_exceptions=True)
    started_count, errors = 0, []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append(f"❌ {valid_accounts[i]['phone']}: {str(result)}")
        elif result:
            started_count += 1

    await event.message.edit(f"Auto Catch has been started for {started_count} accounts")

async def start_auto_catch_1_all(event, user_id, accounts):
    """Start Auto Catch 1 (Rare/Legendaries) for all user accounts."""
    global auto_catch_tasks
    account_clients = await get_account_clients(user_id)
    start_tasks, valid_accounts = [], []
    
    settings = get_user_settings(user_id)
    min_balls = settings.get('auto_catch_1_min_balls', 10)

    for acc in accounts:
        phone = acc['phone']
        if phone in auto_catch_tasks and await is_task_running(auto_catch_tasks[phone]):
            continue
        if phone in account_clients:
            valid_accounts.append(acc)
            start_tasks.append(start_single_catch_1_account(acc, account_clients[phone], min_balls))

    if not start_tasks:
        await event.message.edit("❌ All accounts are already running or no valid accounts found.")
        return

    results = await asyncio.gather(*start_tasks, return_exceptions=True)
    started_count, errors = 0, []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append(f"❌ {valid_accounts[i]['phone']}: {str(result)}")
        elif result:
            started_count += 1

    await event.message.edit(f"🎣 Auto Catch 1 (Rare/Legendaries) started for {started_count} accounts\nMin balls required: {min_balls}")

async def start_auto_catch_2_all(event, user_id, accounts):
    """Start Auto Catch 2 (Tour Helpers) for all user accounts."""
    global auto_catch_tasks
    account_clients = await get_account_clients(user_id)
    start_tasks, valid_accounts = [], []
    
    settings = get_user_settings(user_id)
    min_balls = settings.get('auto_catch_2_min_balls', 200)

    for acc in accounts:
        phone = acc['phone']
        if phone in auto_catch_tasks and await is_task_running(auto_catch_tasks[phone]):
            continue
        if phone in account_clients:
            valid_accounts.append(acc)
            start_tasks.append(start_single_catch_2_account(acc, account_clients[phone], min_balls))

    if not start_tasks:
        await event.message.edit("❌ All accounts are already running or no valid accounts found.")
        return

    results = await asyncio.gather(*start_tasks, return_exceptions=True)
    started_count, errors = 0, []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append(f"❌ {valid_accounts[i]['phone']}: {str(result)}")
        elif result:
            started_count += 1

    await event.message.edit(f"🎪 Auto Catch 2 (Tour Helpers) started for {started_count} accounts\nMin balls required: {min_balls}")

async def start_auto_safari_all(event, user_id, accounts):
    """Start Auto Safari for all user accounts."""
    global safari_tasks
    account_clients = await get_account_clients(user_id)
    start_tasks, valid_accounts = [], []

    for acc in accounts:
        phone = acc['phone']
        if phone in safari_tasks and await is_task_running(safari_tasks[phone]):
            continue
        if phone in account_clients:
            valid_accounts.append(acc)
            start_tasks.append(start_single_safari_account(acc, account_clients[phone], user_id))

    if not start_tasks:
        await event.message.edit("❌ All accounts are already running or no valid accounts found.")
        return

    results = await asyncio.gather(*start_tasks, return_exceptions=True)
    started_count, errors = 0, []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            errors.append(f"❌ {valid_accounts[i]['phone']}: {str(result)}")
        elif result:
            started_count += 1

    await event.message.edit(f"🦁 Auto Safari started for {started_count} accounts")

async def start_single_safari_account(account, client_obj, user_id):
    """Start Safari hunting for a single account."""
    phone = account['phone']
    chat_id = account['chat_id']
    acc_id = account['_id']
    
    try:
        global safari_tasks
        
        if not client_obj.is_connected():
            await client_obj.connect()
            
        if not await client_obj.is_user_authorized():
            raise Exception(f"Account {phone} not authorized")
        
        if phone in safari_tasks:
            task = safari_tasks[phone]
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=2.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
        
        task = asyncio.create_task(safari_logic(client_obj, chat_id, phone, user_id))
        safari_tasks[phone] = task
        accounts_col.update_one({"_id": acc_id}, {"$set": {"active": True}})
        
        await log_message(CATCH_CHAT_ID, f"Started Safari for {phone}")
        return True
        
    except Exception as e:
        print(f"Error starting Safari for {account['phone']}: {str(e)}")
        raise e

async def start_single_catch_1_account(account, client_obj, min_balls):
    """Start Auto Catch 1 for a single account."""
    try:
        phone = account['phone']
        acc_id = account['_id']
        
        global auto_catch_tasks
        
        if not client_obj.is_connected():
            await client_obj.connect()
            
        if not await client_obj.is_user_authorized():
            raise Exception(f"Account {phone} not authorized")
        
        if phone in auto_catch_tasks:
            task = auto_catch_tasks[phone]
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=2.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
        
        task = asyncio.create_task(auto_catch_1_logic(client_obj, phone, min_balls))
        auto_catch_tasks[phone] = task
        accounts_col.update_one({"_id": acc_id}, {"$set": {"active": True}})
        
        await log_message(CATCH_CHAT_ID, f"Started Auto Catch 1 for {phone}")
        return True
        
    except Exception as e:
        print(f"Error starting Auto Catch 1 for {account['phone']}: {str(e)}")
        raise e

async def start_single_catch_2_account(account, client_obj, min_balls):
    """Start Auto Catch 2 for a single account."""
    try:
        phone = account['phone']
        acc_id = account['_id']
        
        global auto_catch_tasks
        
        if not client_obj.is_connected():
            await client_obj.connect()
            
        if not await client_obj.is_user_authorized():
            raise Exception(f"Account {phone} not authorized")
        
        if phone in auto_catch_tasks:
            task = auto_catch_tasks[phone]
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=2.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
        
        task = asyncio.create_task(auto_catch_2_logic(client_obj, phone, min_balls))
        auto_catch_tasks[phone] = task
        accounts_col.update_one({"_id": acc_id}, {"$set": {"active": True}})
        
        await log_message(CATCH_CHAT_ID, f"Started Auto Catch 2 for {phone}")
        return True
        
    except Exception as e:
        print(f"Error starting Auto Catch 2 for {account['phone']}: {str(e)}")
        raise e

async def schedule_hunt_restart(phone, client, chat_id):
    """Schedule hunt restart after 6 hours when hunt limit resets."""
    try:
        await log_message(chat_id, f"Scheduled hunt restart for {phone} in 6 hours")
        
        await asyncio.sleep(21600)
        
        await log_message(chat_id, f"6 hours passed, hunt limit should be reset for {phone}")
        
        if phone in account_tasks:
            account_tasks[phone].cancel()
            del account_tasks[phone]
        
        await start_auto_catch_single(phone, client, chat_id)
        
    except Exception as e:
        await log_message(chat_id, f"Error in scheduled hunt restart for {phone}: {e}")

async def schedule_auto_guess_restart(phone, client, chat_id):
    """Schedule auto guess restart after 6 hours when daily limit resets."""
    try:
        await log_message(chat_id, f"Scheduled auto guess restart for {phone} in 6 hours")
        
        await asyncio.sleep(21600)
        
        if phone in daily_limits:
            await log_message(chat_id, f"6 hours passed, restarting auto guess for {phone}")
            
            if phone in auto_catch_tasks:
                auto_catch_tasks[phone].cancel()
                del auto_catch_tasks[phone]
            
            del daily_limits[phone]
            if phone in limit_timers:
                del limit_timers[phone]
            
            task = asyncio.create_task(guessing_logic(client, chat_id, phone))
            account_tasks[phone] = task
            
            await log_message(chat_id, f"Auto guess restarted for {phone}")
        
    except Exception as e:
        await log_message(chat_id, f"Error in scheduled restart for {phone}: {e}")

async def start_auto_catch_single(phone, client, chat_id):
    """Start auto catch for a single account when daily limit is reached."""
    try:
        await log_message(chat_id, f"Starting auto catch for {phone}")
        
        task = asyncio.create_task(auto_catch_logic(client, phone))
        auto_catch_tasks[phone] = task
        
        await log_message(chat_id, f"Auto catch started for {phone}")
        
    except Exception as e:
        await log_message(chat_id, f"Error starting auto catch for {phone}: {e}")

async def start_single_guess_account(account, client_obj):
    """Start guessing for a single account (helper function for concurrent execution)."""
    try:
        phone = account['phone']
        chat_id = account['chat_id']
        acc_id = account['_id']
        
        global account_tasks
        
        if not client_obj.is_connected():
            await client_obj.connect()
            
        if not await client_obj.is_user_authorized():
            raise Exception(f"Account {phone} not authorized")
        
        if phone in account_tasks:
            task = account_tasks[phone]
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=2.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
        
        task = asyncio.create_task(guessing_logic(client_obj, chat_id, phone))
        account_tasks[phone] = task
        accounts_col.update_one({"_id": acc_id}, {"$set": {"active": True}})
        
        await log_message(chat_id, f"Started guessing for {phone}")
        return True
        
    except Exception as e:
        print(f"Error starting {account['phone']}: {str(e)}")
        raise e

async def start_single_catch_account(account, client_obj):
    """Start catching for a single account (helper function for concurrent execution)."""
    try:
        phone = account['phone']
        acc_id = account['_id']
        
        global auto_catch_tasks
        
        if not client_obj.is_connected():
            await client_obj.connect()
            
        if not await client_obj.is_user_authorized():
            raise Exception(f"Account {phone} not authorized")
        
        if phone in auto_catch_tasks:
            task = auto_catch_tasks[phone]
            if not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=2.0)
                except (asyncio.CancelledError, asyncio.TimeoutError):
                    pass
        
        task = asyncio.create_task(auto_catch_logic(client_obj, phone))
        auto_catch_tasks[phone] = task
        accounts_col.update_one({"_id": acc_id}, {"$set": {"active": True}})
        
        await log_message(CATCH_CHAT_ID, f"Started auto catch for {phone}")
        return True
        
    except Exception as e:
        print(f"Error starting catch for {account['phone']}: {str(e)}")
        raise e

import re
from telethon.errors import FloodWaitError

async def auto_catch_logic(client, phone):
    """Auto catch logic for Pokemon hunting with inventory check."""
    global hunt_status
    hunt_status[phone] = True
    user_notify_chat_id = -1002835841460
    
    account = accounts_col.find_one({"phone": phone})
    if not account:
        return
    
    user_id = account.get("user_id")
    user_settings = get_user_settings(user_id) if user_id else {}
    selected_ball_type = user_settings.get('ball_type', 'Ultra Ball')
    catch_list = user_settings.get('auto_catch_1_list', CATCH_LIST)

    async def check_inventory(initial=False):
        """Check selected ball type and Poke Dollars, buy if needed."""
        try:
            try:
                entity = await client.get_entity(CATCH_CHAT_ID)
            except Exception:
                entity = CATCH_CHAT_ID

            await client.send_message(entity, "/myinventory")
            await asyncio.sleep(3)

            try:
                msgs = await client.get_messages(entity, limit=5)
            except Exception:
                msgs = []
            inv_msg = next((m for m in msgs if "Poke Dollars" in (m.text or "")), None)

            if inv_msg is None:
                try:
                    await client.send_message(entity, "/start")
                    await asyncio.sleep(2)
                    await client.send_message(entity, "/myinventory")
                    await asyncio.sleep(3)
                    msgs = await client.get_messages(entity, limit=5)
                    inv_msg = next((m for m in msgs if "Poke Dollars" in (m.text or "")), None)
                except Exception:
                    inv_msg = None
            if inv_msg is None:
                await log_message(user_notify_chat_id, f"⚠️ [{phone}] Inventory not found, proceeding with hunt anyway.")
                return True

            text = inv_msg.text

            ball_patterns = {
                "Regular Ball": r"Poke Balls:\s*(\d+)",
                "Great Ball": r"Great Balls:\s*(\d+)",
                "Ultra Ball": r"Ultra Balls:\s*(\d+)",
                "Level Ball": r"Level Balls:\s*(\d+)",
                "Fast Ball": r"Fast Balls:\s*(\d+)",
                "Repeat Ball": r"Repeat Balls:\s*(\d+)",
                "Nest Ball": r"Nest Balls:\s*(\d+)",
                "Net Ball": r"Net Balls:\s*(\d+)",
                "Quick Ball": r"Quick Balls:\s*(\d+)",
                "Master Ball": r"Master Balls:\s*(\d+)"
            }
            
            pattern = ball_patterns.get(selected_ball_type, r"Ultra Balls:\s*(\d+)")
            ball_match = re.search(pattern, text)
            ball_count = int(ball_match.group(1)) if ball_match else 0

            money_match = re.search(r"Poke Dollars.*?:\s*([\d,]+)", text)
            money = int(money_match.group(1).replace(",", "")) if money_match else 0

            print(f"[{phone}] Inventory → {selected_ball_type}={ball_count}, Money={money}")

            min_balls = user_settings.get('auto_catch_1_min_balls', 10)
            if ball_count < min_balls:
                buy_command = "/buy ultra 10"  
                if "Ultra" in selected_ball_type:
                    buy_command = "/buy ultra 10"
                elif "Great" in selected_ball_type:
                    buy_command = "/buy great 10"
                elif "Regular" in selected_ball_type or "Poke" in selected_ball_type:
                    buy_command = "/buy poke 10"
                
                await client.send_message(entity, buy_command)
                await asyncio.sleep(2)
                await client.send_message(user_notify_chat_id,
                                          f"💰 [{phone}] Bought 10 {selected_ball_type} (Before: {ball_count})")
            else:
                if initial:
                    await client.send_message(user_notify_chat_id,
                                              f"✅ [{phone}] Ready to hunt using {selected_ball_type} → Count={ball_count}, Money={money}")
            return True
        except Exception as e:
            print(f"[{phone}] Error checking inventory: {e}")
            return True

    async def send_hunt():
        """Send /hunt repeatedly until stopped."""
        try:
            entity = await client.get_entity(CATCH_CHAT_ID)
        except Exception:
            entity = CATCH_CHAT_ID
        while hunt_status.get(phone, False):
            try:
                await client.send_message(entity, "/hunt")
                await asyncio.sleep(randint(1, 2))
            except FloodWaitError as e:
                print(f"[{phone}] Flood wait: sleeping {e.seconds}s")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"[{phone}] Error in send_hunt: {e}")
                await asyncio.sleep(10)

    @client.on(events.NewMessage(chats=CATCH_CHAT_ID, incoming=True))
    async def battle_handler(event):
        if not hunt_status.get(phone, False):
            return
        try:
            msg_text = event.message.text or ""
            
            if "Daily hunt limit reached" in msg_text:
                hunt_status[phone] = False
                await log_message(user_notify_chat_id,
                                  f"⏹️ [{phone}] Daily hunt limit reached. Auto catch stopped.")
                return
            
            if "TM" in msg_text and re.search(r'TM\d+', msg_text):
                tm_match = re.search(r'TM(\d+)', msg_text)
                tm_number = tm_match.group(1) if tm_match else "Unknown"
                await notify_account_owner(phone, f"TM{tm_number}")
                await log_message(user_notify_chat_id, f"🎯 [{phone}] TM{tm_number} found!")
            
            if "Mega Stone found!" in msg_text:
                stone_match = re.search(r'(\w+)\s*Mega Stone found!', msg_text)
                stone_name = stone_match.group(1) if stone_match else "Unknown"
                await notify_account_owner(phone, f"{stone_name} Mega Stone")
                await log_message(user_notify_chat_id, f"💎 [{phone}] {stone_name} Mega Stone found!")
            
            pokemon_match = re.search(r'A wild (.*?) appeared!', msg_text)
            pokemon_name = pokemon_match.group(1) if pokemon_match else ""
            
            is_shiny = "✨" in msg_text
            is_in_catch_list = any(item in msg_text for item in catch_list)
            
            if is_shiny or is_in_catch_list or any(item in pokemon_name for item in catch_list):
                hunt_status[phone] = False
                
                if is_shiny:
                    await notify_account_owner(phone, f"Shiny {pokemon_name}")
                    await log_message(user_notify_chat_id, f"✨ [{phone}] Shiny {pokemon_name} found! Starting catch sequence...")
                else:
                    await notify_account_owner(phone, f"Legendary {pokemon_name}")
                    await log_message(user_notify_chat_id, f"🔥 [{phone}] Legendary {pokemon_name} found! Starting catch sequence...")
                
                msg = event.message
                await asyncio.sleep(1)
                
                for attempt in range(15):  
                    try:
                        await msg.click(text="Battle")
                        await asyncio.sleep(0.3)
                        break  
                    except Exception as e:
                        print(f"[{phone}] Battle click attempt {attempt+1} failed: {e}")
                        await asyncio.sleep(0.2)
                
                return
            
            if msg_text.startswith("Battle begins"):
                msg = event.message
                await asyncio.sleep(1)
                
                ball_button_text = selected_ball_type.replace(" Ball", " Balls")  
                if selected_ball_type == "Regular Ball":
                    ball_button_text = "Poke Balls"
                
                for attempt in range(6):
                    try:
                        await msg.click(text=ball_button_text)
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        print(f"[{phone}] {ball_button_text} click {attempt+1} failed: {e}")
                        try:
                            await msg.click(text="Poke Balls")
                            await asyncio.sleep(0.5)
                        except:
                            break
        except Exception as e:
            print(f"[{phone}] Error in battle_handler: {e}")

    @client.on(events.MessageEdited(chats=CATCH_CHAT_ID))
    async def catch_handler(event):
        if not hunt_status.get(phone, False):
            return
        try:
            msg_text = event.message.text or ""
            
            if "Daily hunt limit reached" in msg_text:
                hunt_status[phone] = False
                await log_message(user_notify_chat_id,
                                  f"⏹️ [{phone}] Daily hunt limit reached. Auto catch stopped.")
                return
            
            msg = event.message
            
            if "Poke Balls" in msg_text and msg.buttons:
                available_labels = []
                try:
                    if msg.buttons:
                        for row in msg.buttons:
                            for btn in row:
                                t = getattr(btn, 'text', '') or ''
                                if t:
                                    available_labels.append(t)
                except Exception:
                    pass

                def find_label(names: list[str]) -> str | None:
                    low = [t.lower() for t in available_labels]
                    for name in names:
                        name_low = name.lower()
                        for idx, t in enumerate(low):
                            if name_low in t:
                                return available_labels[idx]
                    return None

                ball_type_names = {
                    "Regular Ball": ["Poke", "Poke Ball", "POKE", "POKE BALL"],
                    "Great Ball": ["Great", "Great Ball", "GREAT", "GREAT BALL"],
                    "Ultra Ball": ["Ultra", "Ultra Ball", "ULTRA", "ULTRA BALL"],
                    "Level Ball": ["Level", "Level Ball", "LEVEL", "LEVEL BALL"],
                    "Fast Ball": ["Fast", "Fast Ball", "FAST", "FAST BALL"],
                    "Repeat Ball": ["Repeat", "Repeat Ball", "REPEAT", "REPEAT BALL"],
                    "Nest Ball": ["Nest", "Nest Ball", "NEST", "NEST BALL"],
                    "Net Ball": ["Net", "Net Ball", "NET", "NET BALL"],
                    "Quick Ball": ["Quick", "Quick Ball", "QUICK", "QUICK BALL"],
                    "Master Ball": ["Master", "Master Ball", "MASTER", "MASTER BALL"]
                }
                
                selected_names = ball_type_names.get(selected_ball_type, ["Ultra", "Ultra Ball", "ULTRA", "ULTRA BALL"])
                target = find_label(selected_names)

                if target:
                    for attempt in range(27):
                        try:
                            await msg.click(text=target)
                            await asyncio.sleep(0.3)
                        except Exception as e:
                            print(f"[{phone}] {target} click {attempt+1} failed: {e}")
                            await asyncio.sleep(0.1)
                return
            
            if msg_text.startswith("Wild"):
                ball_button_text = selected_ball_type.replace(" Ball", " Balls")  
                if selected_ball_type == "Regular Ball":
                    ball_button_text = "Poke Balls"
                
                for attempt in range(9):
                    try:
                        await msg.click(text=ball_button_text)
                        await asyncio.sleep(0.3)
                    except Exception as e:
                        print(f"[{phone}] {ball_button_text} click {attempt+1} failed: {e}")
                        try:
                            await msg.click(text="Poke Balls")
                            await asyncio.sleep(0.3)
                        except:
                            break
                
                for attempt in range(27):
                    try:
                        await msg.click(text=ball_button_text)
                        await asyncio.sleep(0.2)
                    except Exception as e:
                        print(f"[{phone}] {ball_button_text} click {attempt+1} failed: {e}")
                        try:
                            await msg.click(text="Poke Balls")
                            await asyncio.sleep(0.2)
                        except:
                            break
                return
            
            if any(k in msg_text for k in ["fled", "fainted", "caught"]):
                if "fled" in msg_text:
                    print(f"[{phone}] Pokemon fled - checking inventory and buying balls if needed")
                    await asyncio.sleep(1)
                    
                    try:
                        entity = await client.get_entity(CATCH_CHAT_ID)
                    except Exception:
                        entity = CATCH_CHAT_ID
                    
                    await client.send_message(entity, "/myinventory")
                    await asyncio.sleep(3)
                    
                    try:
                        msgs = await client.get_messages(entity, limit=5)
                        inv_msg = next((m for m in msgs if "Poke Dollars" in (m.text or "")), None)
                        
                        if inv_msg:
                            text = inv_msg.text
                            ball_patterns = {
                                "Regular Ball": r"Poke Balls:\s*(\d+)",
                                "Great Ball": r"Great Balls:\s*(\d+)",
                                "Ultra Ball": r"Ultra Balls:\s*(\d+)",
                                "Level Ball": r"Level Balls:\s*(\d+)",
                                "Fast Ball": r"Fast Balls:\s*(\d+)",
                                "Repeat Ball": r"Repeat Balls:\s*(\d+)",
                                "Nest Ball": r"Nest Balls:\s*(\d+)",
                                "Net Ball": r"Net Balls:\s*(\d+)",
                                "Quick Ball": r"Quick Balls:\s*(\d+)",
                                "Master Ball": r"Master Balls:\s*(\d+)"
                            }
                            
                            pattern = ball_patterns.get(selected_ball_type, r"Ultra Balls:\s*(\d+)")
                            ball_match = re.search(pattern, text)
                            ball_count = int(ball_match.group(1)) if ball_match else 0
                            
                            min_balls = user_settings.get('auto_catch_1_min_balls', 10)
                            if ball_count < min_balls:
                                buy_command = "/buy ultra 50"
                                if "Ultra" in selected_ball_type:
                                    buy_command = "/buy ultra 50"
                                elif "Great" in selected_ball_type:
                                    buy_command = "/buy great 50"
                                elif "Regular" in selected_ball_type or "Poke" in selected_ball_type:
                                    buy_command = "/buy poke 50"
                                elif "Repeat" in selected_ball_type:
                                    buy_command = "/buy repeat 50"
                                
                                await client.send_message(entity, buy_command)
                                await asyncio.sleep(2)
                                await log_message(user_notify_chat_id, f"💰 [{phone}] Pokemon fled! Bought 50 {selected_ball_type} (Had: {ball_count})")
                            else:
                                print(f"[{phone}] Ball count OK: {ball_count} {selected_ball_type}")
                    except Exception as e:
                        print(f"[{phone}] Error checking inventory after flee: {e}")
                
                if "caught" in msg_text:
                    if "TM" in msg_text and re.search(r'TM\d+', msg_text):
                        tm_match = re.search(r'TM(\d+)', msg_text)
                        tm_number = tm_match.group(1) if tm_match else "Unknown"
                        await notify_account_owner(phone, f"TM{tm_number} (Successfully Caught)")
                    
                    for poke in catch_list:
                        if poke.lower() in msg_text.lower():
                            pokemon_caught = poke
                            break
                    
                    try:
                        account_info = accounts_col.find_one({"phone": phone})
                        account_name = "Unknown"
                        account_username = "Unknown"
                        
                        if phone in account_clients:
                            account_client = account_clients[phone]
                            me = await account_client.get_me()
                            account_name = getattr(me, 'first_name', 'Unknown')
                            account_telegram_username = getattr(me, 'username', None)
                            if account_telegram_username:
                                account_username = account_telegram_username
                    except:
                        pass
                    
                    import datetime
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    log_msg = (
                        f"🆕 **NEW LOG**\n\n"
                        f"**Account Name:** `{account_name}`\n"
                        f"**Account Username:** @{account_username}\n\n"
                        f"**Item Found:** `{pokemon_caught}`\n"
                        f"**Status:** ✅ Normal Hunt\n"
                        f"**Time:** `{current_time}`"
                    )
                    
                    try:
                        sent_msg = await bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="markdown")
                        if "caught" in msg_text.lower() and any(legendary.lower() in pokemon_caught.lower() for legendary in LEGENDARY_POKEMON):
                            await sent_msg.pin()
                            print(f"📌 [{phone}] Pinned legendary catch: {pokemon_caught}")
                        else:
                            print(f"📝 [{phone}] Logged catch: {pokemon_caught}")
                    except Exception as e:
                        print(f"Error sending log: {e}")
                    
                    await notify_account_owner(phone, f"Caught {pokemon_caught}")
                
                if "tm" in msg_text.lower():
                    try:
                        account_info = accounts_col.find_one({"phone": phone})
                        account_name = "Unknown"
                        account_username = "Unknown"
                        
                        if phone in account_clients:
                            account_client = account_clients[phone]
                            me = await account_client.get_me()
                            account_name = getattr(me, 'first_name', 'Unknown')
                            account_telegram_username = getattr(me, 'username', None)
                            if account_telegram_username:
                                account_username = account_telegram_username
                    except:
                        pass
                    
                    import datetime
                    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    log_msg = (
                        f"🆕 **NEW LOG**\n\n"
                        f"**Account Name:** `{account_name}`\n"
                        f"**Account Username:** @{account_username}\n\n"
                        f"**Item Found:** `TM`\n"
                        f"**Status:** 💿 Normal Hunt\n"
                        f"**Time:** `{current_time}`"
                    )
                    
                    try:
                        sent_msg = await bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="markdown")
                        await sent_msg.pin()
                        print(f"📌 [{phone}] Pinned TM find")
                        
                        account = accounts_col.find_one({"phone": phone})
                        user_id = account.get("user_id", 0) if account else 0
                        record_account_finding(phone, user_id, "tm", "TM", account_username)
                    except Exception as e:
                        print(f"Error sending/pinning TM log: {e}")
                
                if "key stone" in msg_text.lower():
                    try:
                        account_info = accounts_col.find_one({"phone": phone})
                        account_name = "Unknown"
                        account_username = "Unknown"
                        
                        if phone in account_clients:
                            account_client = account_clients[phone]
                            me = await account_client.get_me()
                            account_name = getattr(me, 'first_name', 'Unknown')
                            account_telegram_username = getattr(me, 'username', None)
                            if account_telegram_username:
                                account_username = account_telegram_username
                    except:
                        pass
                    
                    log_msg = (
                        f"🆕 **NEW LOG**\n\n"
                        f"**Account Name:** `{account_name}`\n"
                        f"**Account Username:** @{account_username}\n\n"
                        f"**Item Found:** `Key Stone`\n"
                        f"**Status:** 💎 Normal Catch"
                    )
                    
                    try:
                        sent_msg = await bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="markdown")
                        print(f"📝 [{phone}] Logged Key Stone find (not pinned)")
                    except Exception as e:
                        print(f"Error sending Key Stone log: {e}")
                
                await asyncio.sleep(randint(2, 3))
                if hunt_status.get(phone, False):
                    try:
                        entity = await client.get_entity(CATCH_CHAT_ID)
                    except Exception:
                        entity = CATCH_CHAT_ID
                    await client.send_message(entity, "/hunt")
        except Exception as e:
            print(f"[{phone}] Error in catch_handler: {e}")

    try:
        await log_message(CATCH_CHAT_ID, f"🚀 Starting auto catch for {phone}")

        if not client.is_connected():
            await client.connect()

        ok = await check_inventory(initial=True)
        if not ok:
            hunt_status[phone] = False
            return

        hunt_task = asyncio.create_task(send_hunt())

        while hunt_status.get(phone, False):
            await asyncio.sleep(60)

    except Exception as e:
        await log_message(CATCH_CHAT_ID, f"❌ Fatal error in auto_catch_logic for {phone}: {e}")
    finally:
        hunt_status[phone] = False
        if 'hunt_task' in locals():
            hunt_task.cancel()
            try:
                await hunt_task
            except:
                pass

async def auto_catch_1_logic(client, phone, min_balls):
    """Auto catch logic for Pokemon hunting (Auto Catch 1 - Rare/Legendaries)."""
    global hunt_status
    hunt_status[phone] = True
    user_notify_chat_id = -1002835841460
    
    account = accounts_col.find_one({"phone": phone})
    if not account:
        return
    
    user_id = account.get("user_id")
    user_settings = get_user_settings(user_id) if user_id else {}
    selected_ball_type = user_settings.get('ball_type', 'Ultra Ball')
    catch_list = user_settings.get('auto_catch_1_list', CATCH_LIST)

    async def check_inventory(initial=False):
        """Check selected ball type and Poke Dollars, buy if needed."""
        try:
            try:
                entity = await client.get_entity(CATCH_CHAT_ID)
            except Exception:
                entity = CATCH_CHAT_ID

            await client.send_message(entity, "/myinventory")
            await asyncio.sleep(3)

            try:
                msgs = await client.get_messages(entity, limit=5)
            except Exception:
                msgs = []
            inv_msg = next((m for m in msgs if "Poke Dollars" in (m.text or "")), None)

            if inv_msg is None:
                await log_message(user_notify_chat_id, f"⚠️ [{phone}] Inventory not found, proceeding with hunt anyway.")
                return True

            text = inv_msg.text

            ball_patterns = {
                "Regular Ball": r"Poke Balls:\s*(\d+)",
                "Great Ball": r"Great Balls:\s*(\d+)",
                "Ultra Ball": r"Ultra Balls:\s*(\d+)",
                "Level Ball": r"Level Balls:\s*(\d+)",
                "Fast Ball": r"Fast Balls:\s*(\d+)",
                "Repeat Ball": r"Repeat Balls:\s*(\d+)",
                "Nest Ball": r"Nest Balls:\s*(\d+)",
                "Net Ball": r"Net Balls:\s*(\d+)",
                "Quick Ball": r"Quick Balls:\s*(\d+)",
                "Master Ball": r"Master Balls:\s*(\d+)"
            }
            
            pattern = ball_patterns.get(selected_ball_type, r"Ultra Balls:\s*(\d+)")
            ball_match = re.search(pattern, text)
            ball_count = int(ball_match.group(1)) if ball_match else 0

            if ball_count < min_balls:
                hunt_status[phone] = False
                await log_message(user_notify_chat_id, f"⚠️ [{phone}] Not enough {selected_ball_type} ({ball_count}/{min_balls}). Auto Catch 1 stopped.")
                return False

            return True
        except Exception as e:
            print(f"[{phone}] Error checking inventory: {e}")
            return True

    if not await check_inventory(initial=True):
        return

    await auto_catch_logic(client, phone)

async def auto_catch_2_logic(client, phone, min_balls):
    """Auto catch logic for Pokemon hunting (Auto Catch 2 - Tour Helpers)."""
    global hunt_status
    hunt_status[phone] = True
    user_notify_chat_id = -1002835841460
    
    account = accounts_col.find_one({"phone": phone})
    if not account:
        return
    
    user_id = account.get("user_id")
    user_settings = get_user_settings(user_id) if user_id else {}
    selected_ball_type = user_settings.get('ball_type', 'Ultra Ball')
    catch_list = user_settings.get('auto_catch_2_list', AUTO_CATCH_2_LIST)

    async def check_inventory(initial=False):
        """Check selected ball type and Poke Dollars, buy if needed."""
        try:
            try:
                entity = await client.get_entity(CATCH_CHAT_ID)
            except Exception:
                entity = CATCH_CHAT_ID

            await client.send_message(entity, "/myinventory")
            await asyncio.sleep(3)

            try:
                msgs = await client.get_messages(entity, limit=5)
            except Exception:
                msgs = []
            inv_msg = next((m for m in msgs if "Poke Dollars" in (m.text or "")), None)

            if inv_msg is None:
                await log_message(user_notify_chat_id, f"⚠️ [{phone}] Inventory not found, proceeding with hunt anyway.")
                return True

            text = inv_msg.text

            ball_patterns = {
                "Regular Ball": r"Poke Balls:\s*(\d+)",
                "Great Ball": r"Great Balls:\s*(\d+)",
                "Ultra Ball": r"Ultra Balls:\s*(\d+)",
                "Level Ball": r"Level Balls:\s*(\d+)",
                "Fast Ball": r"Fast Balls:\s*(\d+)",
                "Repeat Ball": r"Repeat Balls:\s*(\d+)",
                "Nest Ball": r"Nest Balls:\s*(\d+)",
                "Net Ball": r"Net Balls:\s*(\d+)",
                "Quick Ball": r"Quick Balls:\s*(\d+)",
                "Master Ball": r"Master Balls:\s*(\d+)"
            }
            
            pattern = ball_patterns.get(selected_ball_type, r"Ultra Balls:\s*(\d+)")
            ball_match = re.search(pattern, text)
            ball_count = int(ball_match.group(1)) if ball_match else 0

            if ball_count < min_balls:
                hunt_status[phone] = False
                await log_message(user_notify_chat_id, f"⚠️ [{phone}] Not enough {selected_ball_type} ({ball_count}/{min_balls}). Auto Catch 2 stopped.")
                return False

            return True
        except Exception as e:
            print(f"[{phone}] Error checking inventory: {e}")
            return True

    if not await check_inventory(initial=True):
        return

    await auto_catch_logic_with_list(client, phone, catch_list, selected_ball_type, min_balls)

async def auto_catch_logic_with_list(client, phone, catch_list, selected_ball_type, min_balls):
    """Auto catch logic with exact hunting script implementation."""
    global hunt_status
    hunt_status[phone] = True
    user_notify_chat_id = -1002835841460
    
    account_info = accounts_col.find_one({"phone": phone})
    account_id = account_info.get("account_id", "unknown") if account_info else "unknown"

    async def check_inventory_and_buy():
        try:
            entity = await client.get_entity(CATCH_CHAT_ID)
            await client.send_message(entity, "/myinventory")
            await asyncio.sleep(1)
            
            msgs = await client.get_messages(entity, limit=5)
            inv_msg = next((m for m in msgs if "Poke Dollars" in (m.text or "")), None)
            
            if inv_msg:
                text = inv_msg.text
                ball_patterns = {
                    "Regular Ball": r"Poke Balls:\s*(\d+)",
                    "Great Ball": r"Great Balls:\s*(\d+)",
                    "Ultra Ball": r"Ultra Balls:\s*(\d+)",
                    "Level Ball": r"Level Balls:\s*(\d+)",
                    "Fast Ball": r"Fast Balls:\s*(\d+)",
                    "Repeat Ball": r"Repeat Balls:\s*(\d+)",
                    "Nest Ball": r"Nest Balls:\s*(\d+)",
                    "Net Ball": r"Net Balls:\s*(\d+)",
                    "Quick Ball": r"Quick Balls:\s*(\d+)",
                    "Master Ball": r"Master Balls:\s*(\d+)"
                }
                
                pattern = ball_patterns.get(selected_ball_type, r"Ultra Balls:\s*(\d+)")
                ball_match = re.search(pattern, text)
                ball_count = int(ball_match.group(1)) if ball_match else 0
                
                if ball_count < min_balls:
                    buy_command = "/buy ultra 50"
                    if "Ultra" in selected_ball_type:
                        buy_command = "/buy ultra 50"
                    elif "Great" in selected_ball_type:
                        buy_command = "/buy great 50"
                    elif "Regular" in selected_ball_type or "Poke" in selected_ball_type:
                        buy_command = "/buy poke 50"
                    elif "Repeat" in selected_ball_type:
                        buy_command = "/buy repeat 50"
                    
                    await client.send_message(entity, buy_command)
                    await asyncio.sleep(2)
                    await log_message(user_notify_chat_id, f"💰 [{account_id}] Bought 50 {selected_ball_type} (Had: {ball_count})")
                    return True
                else:
                    print(f"[{account_id}] Ball count OK: {ball_count} {selected_ball_type}")
                    return True
        except Exception as e:
            print(f"[{account_id}] Error checking inventory: {e}")
            return False
    
    if not await check_inventory_and_buy():
        hunt_status[phone] = False
        return

    @client.on(events.NewMessage(chats=CATCH_CHAT_ID, incoming=True))
    async def hunt_handler(event):
        if not hunt_status.get(phone, False):
            return
        
        text = event.message.text or ""
        message = await client.get_messages(CATCH_CHAT_ID, ids=event.message.id)
        
        if "Daily hunt limit reached" in text:
            hunt_status[phone] = False
            await log_message(user_notify_chat_id, f"⏹️ [{account_id}] Daily hunt limit reached. Auto catch stopped.")
            return
        
        if "✨" in text or "A shiny" in text:
            if "A wild" in text and "(Lv." in text and "has appeared!" in text:
                pokemon_match = re.search(r'A wild (.*?) \(Lv\. \d+\) has appeared!', text)
                pokemon_name = pokemon_match.group(1) if pokemon_match else "Unknown Shiny"
                
                await log_shiny_found_channel_only(phone, pokemon_name, text)
                
                print(f"[{account_id}] ✨ SHINY FOUND! Attempting to catch: {pokemon_name}")
                
                while True:
                    try:
                        await message.click(text="Battle")
                        await asyncio.sleep(0.1)
                        print(f"[{account_id}] Battle clicked")
                    except Exception as e:
                        print(f"[{account_id}] Battle button not found, moving to battle: {e}")
                        break
                
                return
            else:
                print(f"[{account_id}] Expert trainer shiny found - skipping")
                await asyncio.sleep(randint(2, 5))
                try:
                    entity = await client.get_entity(CATCH_CHAT_ID)
                    x = await client.send_message(entity, "/hunt")
                    try:
                        async with client.conversation('@Hexamonbot') as conv:
                            await conv.get_response(x.id)
                    except:
                        await asyncio.sleep(2)
                        await client.send_message(entity, "/hunt")
                except Exception as e:
                    print(f"[{account_id}] Error after expert shiny: {e}")
                return
        
        if "TM" in text:
            print(f"[{account_id}] TM found: {text}")
            await asyncio.sleep(randint(2, 3))
            try:
                entity = await client.get_entity(CATCH_CHAT_ID)
                x = await client.send_message(entity, "/hunt")
                try:
                    async with client.conversation('@Hexamonbot') as conv:
                        await conv.get_response(x.id)
                except:
                    await asyncio.sleep(2)
                    await client.send_message(entity, "/hunt")
            except Exception as e:
                print(f"[{account_id}] Error after TM: {e}")
            return
        
        if "A wild" in text and "(Lv." in text and "has appeared!" in text:
            pokemon_match = re.search(r'A wild (.*?) \(Lv\. \d+\) has appeared!', text)
            pokemon_name = pokemon_match.group(1) if pokemon_match else ""
            
            is_legendary_pokemon = any(legendary.lower() in pokemon_name.lower() for legendary in LEGENDARY_POKEMON)
            
            if any(item in pokemon_name for item in catch_list) or is_legendary_pokemon:
                print(f"[{account_id}] Target Pokemon found: {pokemon_name}")
                
                while True:
                    try:
                        await message.click(text="Battle")
                        await asyncio.sleep(0.1)
                        print(f"[{account_id}] Battle clicked")
                    except Exception as e:
                        print(f"[{account_id}] Battle button not found, moving to battle: {e}")
                        break
                
                return
            else:
                await asyncio.sleep(randint(2, 5))
                try:
                    entity = await client.get_entity(CATCH_CHAT_ID)
                    x = await client.send_message(entity, "/hunt")
                    try:
                        async with client.conversation('@Hexamonbot') as conv:
                            await conv.get_response(x.id)
                    except:
                        await asyncio.sleep(2)
                        await client.send_message(entity, "/hunt")
                except Exception as e:
                    print(f"[{account_id}] Error after wild: {e}")
                return
        
        if "An expert" in text:
            print(f"[{account_id}] Expert trainer found - skipping")
            await asyncio.sleep(randint(2, 5))
            try:
                entity = await client.get_entity(CATCH_CHAT_ID)
                x = await client.send_message(entity, "/hunt")
                try:
                    async with client.conversation('@Hexamonbot') as conv:
                        await conv.get_response(x.id)
                except:
                    await asyncio.sleep(2)
                    await client.send_message(entity, "/hunt")
            except Exception as e:
                print(f"[{account_id}] Error after expert: {e}")
            return

    @client.on(events.NewMessage(chats=CATCH_CHAT_ID, incoming=True))
    async def battle_begins_handler(event):
        if not hunt_status.get(phone, False):
            return
        
        text = event.message.text or ""
        if text.startswith("Battle begins"):
            print(f"[{account_id}] Battle begins: {text}")
            message = await client.get_messages(CATCH_CHAT_ID, ids=event.message.id)
            await asyncio.sleep(1)
            
            while True:
                try:
                    await message.click(text="Poke Balls")
                    await asyncio.sleep(0.1)
                    print(f"[{account_id}] Poke Balls clicked")
                except Exception as e:
                    print(f"[{account_id}] Poke Balls button not found: {e}")
                    break

    @client.on(events.MessageEdited(chats=CATCH_CHAT_ID))
    async def catch_handler(event):
        if not hunt_status.get(phone, False):
            return
        
        text = event.message.text or ""
        message = await client.get_messages(CATCH_CHAT_ID, ids=event.message.id)
        
        while True:
            try:
                await message.click(text="Poke Balls")
                await asyncio.sleep(0.1)
                print(f"[{account_id}] Poke Balls clicked")
            except Exception as e:
                print(f"[{account_id}] Poke Balls button not found: {e}")
                break
        
        while True:
            try:
                await message.click(text="Ultra")
                await asyncio.sleep(0.1)
                print(f"[{account_id}] Ultra clicked")
            except Exception as e:
                print(f"[{account_id}] Ultra button not found: {e}")
                break
        
        if any(keyword in text for keyword in ['fled', 'fainted', 'caught']):
            if 'caught' in text:
                await log_catch_result(phone, text, catch_list)
            
            await asyncio.sleep(randint(2, 5))
            try:
                entity = await client.get_entity(CATCH_CHAT_ID)
                x = await client.send_message(entity, "/hunt")
                try:
                    async with client.conversation('@Hexamonbot') as conv:
                        await conv.get_response(x.id)
                except:
                    await asyncio.sleep(2)
                    await client.send_message(entity, "/hunt")
            except Exception as e:
                print(f"[{account_id}] Error after battle end: {e}")
    
    async def log_shiny_found_channel_only(phone, pokemon_name, message_text):
        try:
            account_info = accounts_col.find_one({"phone": phone})
            account_name = "Unknown"
            account_username = "Unknown"
            account_id = account_info.get("account_id", "unknown") if account_info else "unknown"
            
            if phone in account_clients:
                account_client = account_clients[phone]
                me = await account_client.get_me()
                account_name = getattr(me, 'first_name', 'Unknown')
                account_telegram_username = getattr(me, 'username', None)
                if account_telegram_username:
                    account_username = account_telegram_username
        except:
            pass
        
        import datetime
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_msg = (
            f"🆕 **NEW LOG**\n\n"
            f"**Account Name:** `{account_name}`\n"
            f"**Account Username:** @{account_username}\n"
            f"**Account ID:** `{account_id}`\n\n"
            f"**Item Found:** `✨ Shiny {pokemon_name}`\n"
            f"**Status:** ✨ Shiny Found\n"
            f"**Time:** `{current_time}`"
        )
        
        try:
            sent_msg = await bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="markdown")
            await sent_msg.pin()  
            print(f"📌 [{account_id}] Pinned shiny found: {pokemon_name}")
        except Exception as e:
            print(f"Error sending shiny log: {e}")

    async def log_shiny_found(phone, pokemon_name, message_text):
        try:
            account_info = accounts_col.find_one({"phone": phone})
            account_name = "Unknown"
            account_username = "Unknown"
            account_id = account_info.get("account_id", "unknown") if account_info else "unknown"
            
            if phone in account_clients:
                account_client = account_clients[phone]
                me = await account_client.get_me()
                account_name = getattr(me, 'first_name', 'Unknown')
                account_telegram_username = getattr(me, 'username', None)
                if account_telegram_username:
                    account_username = account_telegram_username
        except:
            pass
        
        import datetime
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_msg = (
            f"🆕 **NEW LOG**\n\n"
            f"**Account Name:** `{account_name}`\n"
            f"**Account Username:** @{account_username}\n"
            f"**Account ID:** `{account_id}`\n\n"
            f"**Item Found:** `✨ Shiny {pokemon_name}`\n"
            f"**Status:** ✨ Shiny Found\n"
            f"**Time:** `{current_time}`"
        )
        
        try:
            sent_msg = await bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="markdown")
            await sent_msg.pin()  
            print(f"📌 [{account_id}] Pinned shiny found: {pokemon_name}")
            
            
        except Exception as e:
            print(f"Error sending shiny log: {e}")
    
    async def log_catch_result(phone, message_text, catch_list):
        if "caught" not in message_text.lower():
            return
            
        try:
            pokemon_caught = "Unknown Pokemon"
            
            import re
            
            catch_patterns = [
                r"You caught (?:a )?(.+?)!",
                r"(.+?) was caught!",
                r"Caught (?:a )?(.+?)!",
                r"Successfully caught (?:a )?(.+?)!"
            ]
            
            for pattern in catch_patterns:
                match = re.search(pattern, message_text, re.IGNORECASE)
                if match:
                    pokemon_caught = match.group(1).strip()
                    break
            
            if pokemon_caught == "Unknown Pokemon":
                for poke in catch_list:
                    if poke.lower() in message_text.lower():
                        pokemon_caught = poke
                        break
            
            if pokemon_caught == "Unknown Pokemon":
                for legendary in LEGENDARY_POKEMON:
                    if legendary.lower() in message_text.lower():
                        pokemon_caught = legendary
                        break
            
            account_info = accounts_col.find_one({"phone": phone})
            account_name = "Unknown"
            account_username = "Unknown"
            account_id = account_info.get("account_id", "unknown") if account_info else "unknown"
            
            if phone in account_clients:
                account_client = account_clients[phone]
                me = await account_client.get_me()
                account_name = getattr(me, 'first_name', 'Unknown')
                account_telegram_username = getattr(me, 'username', None)
                if account_telegram_username:
                    account_username = account_telegram_username
        except:
            pass
        
        import datetime
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        is_shiny = "✨" in message_text or "shiny" in message_text.lower()
        is_legendary = any(legendary.lower() in pokemon_caught.lower() for legendary in LEGENDARY_POKEMON)
        
        log_msg = (
            f"🆕 **NEW LOG**\n\n"
            f"**Account Name:** `{account_name}`\n"
            f"**Account Username:** @{account_username}\n"
            f"**Account ID:** `{account_id}`\n\n"
            f"**Item Found:** `{pokemon_caught}`\n"
            f"**Status:** ✅ Caught\n"
            f"**Time:** `{current_time}`"
        )
        
        try:
            sent_msg = await bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="markdown")
            
            if is_shiny or is_legendary:
                await sent_msg.pin()
                print(f"📌 [{account_id}] Pinned catch: {pokemon_caught}")
            else:
                print(f"📝 [{account_id}] Logged catch: {pokemon_caught}")
            
            account = accounts_col.find_one({"phone": phone})
            user_id = account.get("user_id", 0) if account else 0
            
            if is_shiny:
                record_account_finding(phone, user_id, "shiny", pokemon_caught, account_username)
                print(f"📊 [{account_id}] Recorded shiny catch in database: {pokemon_caught}")
            elif is_legendary:
                record_account_finding(phone, user_id, "legendary", pokemon_caught, account_username)
                print(f"📊 [{account_id}] Recorded legendary catch in database: {pokemon_caught}")
                
        except Exception as e:
            print(f"Error sending catch log: {e}")
    
    try:
        await log_message(user_notify_chat_id, f"🚀 [{account_id}] Auto catch started using {selected_ball_type}")
        
        entity = await client.get_entity(CATCH_CHAT_ID)
        x = await client.send_message(entity, "/hunt")
        try:
            async with client.conversation('@Hexamonbot') as conv:
                await conv.get_response(x.id)
        except:
            await asyncio.sleep(2)
            await client.send_message(entity, "/hunt")
        
        for i in range(1, 10000):
            if not hunt_status.get(phone, False):
                break
            await asyncio.sleep(randint(1000, 1020))
            if hunt_status.get(phone, False):
                await client.send_message(entity, "/hunt")

    except Exception as e:
        await log_message(user_notify_chat_id, f"❌ Fatal error in auto_catch_logic for [{account_id}]: {e}")
    finally:
        hunt_status[phone] = False
    


async def safari_logic(client, chat_id, phone, user_id):
    """Safari hunting logic for Pokemon."""
    global hunt_status
    hunt_status[phone] = True
    hunt_watchdog = None
    
    safari_chat_id = CATCH_CHAT_ID  
    
    safari_poke_list = SAFARI_POKE_LIST

    async def send_hunt():
        nonlocal hunt_watchdog
        try:
            entity = await client.get_entity(safari_chat_id)
        except Exception:
            entity = safari_chat_id
        await client.send_message(entity, "/hunt")
        print(f"🔁 [{phone}] Sent /hunt")
        if hunt_watchdog:
            hunt_watchdog.cancel()
        hunt_watchdog = asyncio.create_task(hunt_timeout())

    async def hunt_timeout():
        try:
            await asyncio.sleep(10)
            if hunt_status.get(phone, False):
                await send_hunt()
        except asyncio.CancelledError:
            pass

    print(f"🔰 [{phone}] Entering Safari Zone...")
    while True:
        try:
            entity = await client.get_entity(safari_chat_id)
        except Exception:
            entity = safari_chat_id
        await client.send_message(entity, "/enter")
        print(f"🚪 [{phone}] Sent /enter")
        await asyncio.sleep(5)

        last_msg = await client.get_messages(entity, limit=1)
        if last_msg:
            text = last_msg[0].text.lower()
            if "entry fee deducted" in text or "you are already in the" in text:
                print(f"✅ [{phone}] Already or just entered Safari Zone.")
                break
            if "you have already played the safari game today" in text:
                print(f"📛 [{phone}] Safari already played today. Stopping.")
                hunt_status[phone] = False
                return

    await send_hunt()

    @client.on(events.NewMessage(chats=safari_chat_id, incoming=True))
    async def wild_handler(event):
        if not hunt_status.get(phone, False):
            return

        text = event.message.text
        message = await client.get_messages(safari_chat_id, ids=event.message.id)

        if "✨ shiny pokémon found!" in text.lower():
            try:
                account_name = "Unknown"
                account_username = "Unknown"
                
                if phone in account_clients:
                    account_client = account_clients[phone]
                    me = await account_client.get_me()
                    account_name = getattr(me, 'first_name', 'Unknown')
                    account_telegram_username = getattr(me, 'username', None)
                    if account_telegram_username:
                        account_username = account_telegram_username
            except:
                pass
            
            import datetime
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            log_msg = (
                f"🆕 **NEW LOG**\\n\\n"
                f"**Account Name:** `{account_name}`\\n"
                f"**Account Username:** @{account_username}\\n\\n"
                f"**Item Found:** `✨ Shiny Pokemon`\\n"
                f"**Status:** ✨ In Safari\\n"
                f"**Time:** `{current_time}`"
            )
            
            try:
                sent_msg = await bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="markdown")
                await sent_msg.pin()
            except Exception as e:
                print(f"Error sending/pinning shiny log: {e}")
            
            await notify_account_owner(phone, f"✨ Shiny Pokemon found in Safari! {text}")
            print(f"✨ [{phone}] Shiny found. Stopping safari.")
            hunt_status[phone] = False
            return

        if "daily hunt limit reached" in text.lower():
            await notify_account_owner(phone, f"⚡ Daily hunt limit reached: {text}")
            print(f"📛 [{phone}] Daily hunt limit reached. Stopping safari.")
            hunt_status[phone] = False
            return

        text_l = text.lower()

        if ("you have run out of safari balls" in text_l and "are now exiting" in text_l) or "you were kicked" in text_l:
            await notify_account_owner(phone, f"⚕️ Successfully completed safari 🎉 -- {text}")
            print(f"🛑 [{phone}] Kicked or safari balls ended. Stopping safari.")
            
            import datetime
            current_time = datetime.datetime.now().isoformat()
            accounts_col.update_one(
                {"phone": phone}, 
                {"$set": {
                    "safari_status": "completed",
                    "safari_last_completed": current_time
                }}
            )
            
            hunt_status[phone] = False
            return

        if text.startswith("A wild"):
            if hunt_watchdog:
                hunt_watchdog.cancel()

            matched = False
            for poke in safari_poke_list:
                if poke in text:
                    matched = True
                    try:
                        await message.click(text="Engage")
                        await message.click(text="Engage")
                        await message.click(text="Engage")
                        print(f"✅ [{phone}] Engaged with: {poke}")
                    except Exception as e:
                        print(f"❌ [{phone}] Could not click Engage: {e}")
                    break

            if not matched:
                print(f"⏩ [{phone}] No matching Pokémon, skipping.")
                await asyncio.sleep(randint(2, 4))
                if hunt_status.get(phone, False):
                    await send_hunt()

    @client.on(events.NewMessage(chats=safari_chat_id, incoming=True))
    async def ball_handler(event):
        text = event.message.text.lower()
        message = await client.get_messages(safari_chat_id, ids=event.message.id)

        if "wild" in text:
            try:
                await message.click(text="Throw ball")
                await message.click(text="Throw ball")
                await message.click(text="Throw ball")
                print(f"🎯 [{phone}] Threw ball.")
            except Exception as e:
                print(f"❌ [{phone}] Throw ball not found: {e}")

    @client.on(events.MessageEdited(chats=safari_chat_id))
    async def retry_throw_handler(event):
        text = event.message.text.lower()
        message = await client.get_messages(safari_chat_id, ids=event.message.id)

        if "safari ball failed" in text:
            try:
                await message.click(text="Throw ball")
                await asyncio.sleep(0.5)
                await message.click(text="Throw ball")
                await asyncio.sleep(0.5)
                await message.click(text="Throw ball")
                print(f"🔁 [{phone}] Retried: Throw ball clicked again.")
            except Exception as e:
                print(f"❌ [{phone}] Failed to retry Throw ball: {e}")

        if any(word in text for word in ["caught", "fled", "fainted", "tm", "an expert trainer", "key stone", "mega stone found"]):
            if "caught" in text:
                pokemon_caught = "Unknown Pokemon"
                
                for poke in safari_poke_list:
                    if poke.lower() in text.lower():
                        pokemon_caught = poke
                        break
                
                try:
                    account_name = "Unknown"
                    account_username = "Unknown"
                    
                    if phone in account_clients:
                        account_client = account_clients[phone]
                        me = await account_client.get_me()
                        account_name = getattr(me, 'first_name', 'Unknown')
                        account_telegram_username = getattr(me, 'username', None)
                        if account_telegram_username:
                            account_username = account_telegram_username
                except:
                    pass
                
                import datetime
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                log_msg = (
                    f"🆕 **NEW LOG**\\n\\n"
                    f"**Account Name:** `{account_name}`\\n"
                    f"**Account Username:** @{account_username}\\n\\n"
                    f"**Item Found:** `{pokemon_caught}`\\n"
                    f"**Status:** ✅ In Safari\\n"
                    f"**Time:** `{current_time}`"
                )
                
                try:
                    sent_msg = await bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="markdown")
                    if any(legendary.lower() in pokemon_caught.lower() for legendary in LEGENDARY_POKEMON):
                        await sent_msg.pin()
                        print(f"📌 [{phone}] Pinned legendary catch: {pokemon_caught}")
                    else:
                        print(f"📝 [{phone}] Logged non-legendary catch: {pokemon_caught}")
                except Exception as e:
                    print(f"Error sending log: {e}")
                
                await notify_account_owner(phone, f"🎉 Safari Catch: {pokemon_caught} has been caught!")
            
            if "tm" in text.lower():
                try:
                    account_name = "Unknown"
                    account_username = "Unknown"
                    
                    if phone in account_clients:
                        account_client = account_clients[phone]
                        me = await account_client.get_me()
                        account_name = getattr(me, 'first_name', 'Unknown')
                        account_telegram_username = getattr(me, 'username', None)
                        if account_telegram_username:
                            account_username = account_telegram_username
                except:
                    pass
                
                import datetime
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                log_msg = (
                    f"🆕 **NEW LOG**\\n\\n"
                    f"**Account Name:** `{account_name}`\\n"
                    f"**Account Username:** @{account_username}\\n\\n"
                    f"**Item Found:** `TM`\\n"
                    f"**Status:** 💿 In Safari\\n"
                    f"**Time:** `{current_time}`"
                )
                
                try:
                    sent_msg = await bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="markdown")
                    print(f"📝 [{phone}] Logged TM find (not pinned)")
                except Exception as e:
                    print(f"Error sending TM log: {e}")
            
            if "key stone" in text.lower():
                try:
                    account_name = "Unknown"
                    account_username = "Unknown"
                    
                    if phone in account_clients:
                        account_client = account_clients[phone]
                        me = await account_client.get_me()
                        account_name = getattr(me, 'first_name', 'Unknown')
                        account_telegram_username = getattr(me, 'username', None)
                        if account_telegram_username:
                            account_username = account_telegram_username
                except:
                    pass
                
                import datetime
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                log_msg = (
                    f"🆕 **NEW LOG**\\n\\n"
                    f"**Account Name:** `{account_name}`\\n"
                    f"**Account Username:** @{account_username}\\n\\n"
                    f"**Item Found:** `Key Stone`\\n"
                    f"**Status:** 💎 In Safari\\n"
                    f"**Time:** `{current_time}`"
                )
                
                try:
                    sent_msg = await bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="markdown")
                    print(f"📝 [{phone}] Logged Key Stone find (not pinned)")
                except Exception as e:
                    print(f"Error sending Key Stone log: {e}")
            
            if "mega stone found" in text.lower():
                try:
                    import re
                    mega_stone_match = re.search(r'(\w+)\s+Mega Stone found!', text)
                    mega_stone_name = mega_stone_match.group(1) if mega_stone_match else "Unknown Mega Stone"
                    
                    account_name = "Unknown"
                    account_username = "Unknown"
                    
                    if phone in account_clients:
                        account_client = account_clients[phone]
                        me = await account_client.get_me()
                        account_name = getattr(me, 'first_name', 'Unknown')
                        account_telegram_username = getattr(me, 'username', None)
                        if account_telegram_username:
                            account_username = account_telegram_username
                except:
                    pass
                
                import datetime
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                log_msg = (
                    f"🆕 **NEW LOG**\\\\n\\\\n"
                    f"**Account Name:** `{account_name}`\\\\n"
                    f"**Account Username:** @{account_username}\\\\n\\\\n"
                    f"**Item Found:** `{mega_stone_name}`\\\\n"
                    f"**Status:** 💎 In Safari\\\\n"
                    f"**Time:** `{current_time}`"
                )
                
                try:
                    sent_msg = await bot.send_message(LOG_CHANNEL_ID, log_msg, parse_mode="markdown")
                    await sent_msg.pin()
                    print(f"📌 [{phone}] Pinned Mega Stone find: {mega_stone_name}")
                    
                    account = accounts_col.find_one({"phone": phone})
                    user_id = account.get("user_id", 0) if account else 0
                    record_account_finding(phone, user_id, "mega_stone", mega_stone_name, account_username)
                except Exception as e:
                    print(f"Error sending/pinning Mega Stone log: {e}")
            
            await asyncio.sleep(randint(2, 3))
            if hunt_status.get(phone, False):
                await send_hunt()

    try:
        print(f"🦁 [{phone}] Starting safari logic")
        while hunt_status.get(phone, False):
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        print(f"🛑 [{phone}] Safari task was cancelled")
        hunt_status[phone] = False
    except Exception as e:
        print(f"❌ [{phone}] Error in safari logic: {e}")
        hunt_status[phone] = False
    finally:
        if hunt_watchdog:
            hunt_watchdog.cancel()

if __name__ == "__main__":
    print("=" * 50)
    print("         TELETHON BOT STARTING")
    print("=" * 50)
    admin_display_list = [str(ADMIN_USER_ID)]
    print(f"Admins: {', '.join(admin_display_list)}")
    print("=" * 50)

    async def startup_notification():
        migrate_existing_accounts()
        
        await log_message(LOG_CHANNEL_ID, "🚀 Bot started successfully with Telethon")
        startup_msg = await send_to_admin("🚀 BOT HAS STARTED\n\nThe Pokemon bot is now online and ready to use!")
    
    async def startup_with_scheduler():
        await startup_notification()
        
        async def daily_log_scheduler():
            """Schedule daily logs at 12:55 PM UTC."""
            while True:
                try:
                    current_time = get_utc_time()
                    if current_time.hour == 12 and current_time.minute == 55:
                        await generate_daily_logs()
                        await asyncio.sleep(3600)  
                    else:
                        await asyncio.sleep(60)  
                except Exception as e:
                    print(f"❌ Error in daily log scheduler: {e}")
                    await asyncio.sleep(300)  
        
        asyncio.create_task(daily_log_scheduler())
    
    # Start keep-alive server if available
    if KEEP_ALIVE_AVAILABLE:
        keep_alive()
        print("🌐 Keep-alive server started successfully!")
    
    bot.loop.run_until_complete(startup_with_scheduler())

    bot.run_until_disconnected()

    try:
        bot.loop.run_until_complete(log_message(LOG_CHANNEL_ID, "🛑 Bot stopped"))
    except:
        pass