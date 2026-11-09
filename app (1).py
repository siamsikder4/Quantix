import requests
import time
import json
import os
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
import threading
import random
import re
import html
import pyotp
from collections import Counter 
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from datetime import datetime 
from urllib.parse import urljoin

# ==========================================
# Configuration (Token & Owner ID)
# ==========================================
TOKEN = "8849255377:AAGAHkJ1zfH9J5yv7XP1MXvaSYDL7lO0ANg"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = 8271633124
BOT_USERNAME = "@Quaantix_bot"
DB_FILE = "bot_data.json"
db_lock = threading.RLock()

# ==========================================
# Premium Emoji Database
# ==========================================
PEM = {
    "ok": '<tg-emoji emoji-id="5987557149360792425">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id="5420130255174145507">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id="5336944168944047463">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5353032893096567467">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id="5987786010988125765">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id="5352721946054268944">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5352597830089347330">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id="5987664755471425123">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id="5987641605597699007">💸</tg-emoji>',
    "gift": '<tg-emoji emoji-id="5420396762189831222">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id="5420155432272438703">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id="5420517437885943844">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id="5422557736330106570">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id="5353001161878182134">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id="5987629038523392103">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5353022963132174959">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id="5337132498965010628">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id="5303214794336125778">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "star": '<tg-emoji emoji-id="5352552689983067014">✨</tg-emoji>',
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>'
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5240241223632954241", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5334590977837403844", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "5337172996211648018", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "5336850036145823599",
    "⚠️": "5336944168944047463", "🔥": "5987918111297249544", "💸": "5987641605597699007",
    "🥚": "5348390922507817684", "👨‍⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "5987610583048919551", "🔢": "5303214794336125778", "👤": "5987786010988125765",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5987872202391821841",
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "5987557149360792425",
    "1️⃣": "5988081676536784112", "2️⃣": "5988017797488189036", "3️⃣": "5987563664826179813",
    "4️⃣": "5987589486169563440", "5️⃣": "5987874216731484188", "6️⃣": "5988082947847105873",
    "7️⃣": "5987860253792804740", "8️⃣": "5987741549486678919", "9️⃣": "5987626998413927947",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5987955490397626603", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "5420130255174145507", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "5987751449386296261", "🗑": "5422557736330106570", "🎁": "5420396762189831222",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "5988050370520161591",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "5192812028632274956", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5303214794336125778", "📈": "5987664755471425123",
    "🔔": "5352980533150259581", "🏦": "5987641605597699007", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604", "🔍": "5463352748751753567",
    "🔑": "5197288647275071607"
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": "══════════════\n   📊 𝗡𝗨𝗠𝗕𝗘𝗥 𝗕𝗢𝗧\n══════════════\n🚀 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗢𝗨𝗥 𝗙𝗔𝗠𝗜𝗟𝗬\n━━━━━━━━━━━━━\n✅ 𝗖𝗛𝗢𝗢𝗦𝗘 𝗔𝗡 𝗢𝗣𝗧𝗜𝗢𝗡 𝗕𝗘𝗟𝗢𝗪\n𝗧𝗢 𝗖𝗢𝗡𝗧𝗜𝗡𝗨𝗘 𝗨𝗦𝗜𝗡𝗚 𝗧𝗛𝗘 𝗕𝗢𝗧.\n━━━━━━━━━━━━━\n💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗢𝗧𝗣 𝗦𝗘𝗥𝗩𝗜𝗖𝗘", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []}, 
    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": "🎁 𝚁𝙴𝙵𝙴𝚁𝚁𝙰𝙻 𝙿𝚁𝙾𝙶𝚁𝙰𝙼\n━━━━━━━━━━━━━━━━━━\n🔗 𝚈𝙾𝚄𝚁 𝙸𝙽𝚅𝙸𝚃𝙴 𝙻𝙸𝙽𝙺:\n\n<code>{ref_link}</code>\n━━━━━━━━━━━━━━━━━━\n<blockquote>💬 𝚁𝙴𝙵𝙴𝚁𝚁𝙰𝙻 𝙾𝚃𝙿 : {total_otp}</blockquote>\n<blockquote><tg-emoji emoji-id=\"5420145051336485498\">👥</tg-emoji> 𝚃𝙾𝚃𝙰𝙻 𝙸𝙽𝚅𝙸𝚃𝙴𝚂 : {total_ref}</blockquote>\n<blockquote>💸 𝚁𝙴𝚆𝙰𝚁𝙳 𝙿𝙴𝚁 𝙸𝙽𝚅𝙸𝚃𝙴 : {ref_reward} 𝚃𝙺</blockquote>\n━━━━━━━━━━━━━━━━━━\n💎 𝙸𝙽𝚅𝙸𝚃 𝙼𝙾𝚁𝙴 • 𝙴𝙰𝚁𝙽 𝙼𝙾𝚁𝙴", "buttons": []},
    "withdrawal": {"text": "➖➖➖➖➖➖➖➖\n《 😒 𝙼𝚈 𝙸𝙽𝙵𝙾 》\n➖➖➖➖➖➖➖➖\n<blockquote>🆔 𝚄𝚂𝙴𝚁 𝙸𝙳 : <code>{user_id}</code></blockquote>\n<blockquote>🔥 𝙾𝚃𝙿 𝚁𝙴𝙲𝙴𝙸𝚅𝙴𝙳 : {total_otp} 𝚃𝙾𝚃𝙰𝙻 </blockquote>\n<blockquote>🫂 𝚃𝙾𝚃𝙰𝙻 𝚁𝙴𝙵𝙴𝚁 : {total_ref}</blockquote>\n<blockquote>📅 𝙱𝙰𝙻𝙰𝙽𝙲𝙴 : {bal}৳</blockquote>\n<blockquote><tg-emoji emoji-id=\"5987961773934780806\">💬</tg-emoji> 𝚆𝚂 𝙰𝙳𝙳𝙴𝙳 : 0 𝚃𝙾𝚃𝙰𝙻</blockquote>\n➖➖➖➖➖➖➖➖", "buttons": []}
}

# ==========================================
# Firebase Setup
# ==========================================
db = None

def init_firebase():
    global db
    key_file = "firebase_key.json" if os.path.exists("firebase_key.json") else ("firebase_credentials.json" if os.path.exists("firebase_credentials.json") else None)
    if key_file:
        try:
            with open(key_file, "r", encoding='utf-8') as f:
                cred_dict = json.load(f)
            
            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                
            db = firestore.client()
            print(f"✅ Firebase Connected Successfully using {key_file}!")
            return True
        except Exception as e:
            print(f"❌ Firebase Error: {e}")
            db = None
            return False
    else:
        print("⚠️ No Firebase Key found. Bot running in Local Mode.")
        return False

init_firebase()

bot_settings = {
    "admins": [OWNER_ID],
    "panels": [], 
    "fw_groups": [], 
    "otp_link": "https://t.me/your_otp_group",
    "withdraw_on": True,
    "min_withdraw": 30.0,
    "otp_reward": 0.1,
    "refer_reward": 0.2,
    "cooldown": 10,
    "num_req": 3,
    "num_share": 1, 
    "support_link": "https://t.me/your_support",
    "w_methods": ["bKash", "Nagad"],
    "w_group": "", 
    "otp_channel_link": "https://t.me/EliteEarningLab",
    
    "fj_on": False,
    "fj_channels": [], 
    "stex_keys": [], 
    "voltx_keys": [],
    "zenex_keys": [],
    "mino_keys": [],
    "search_countries": [],
    "stex_services": {},
    "voltx_services": {},
    "zenex_services": {},
    "mino_services": {},
    "ws_checker_on": True,
    "ws_checker_services": [],
    "ws_checker_files": [],
    "master_api_url": "https://bot.orabitsms.site/api",
    "master_api_key": "",
"premium_flags": {
        "1": {"char": "🇺🇸", "iso": "US", "name": "USA/Canada", "id": "5913463998522592692"},
        "380": {"char": "🇺🇦", "iso": "UA", "name": "Ukraine", "id": "5911406692007941050"},
        "48": {"char": "🇵🇱", "iso": "PL", "name": "Poland", "id": "5913550391789752571"},
        "7": {"char": "🇰🇿", "iso": "KZ", "name": "Kazakhstan", "id": "5913724621433082323"},
        "86": {"char": "🇨🇳", "iso": "CN", "name": "China", "id": "5913779335021466780"},
        "994": {"char": "🇦🇿", "iso": "AZ", "name": "Azerbaijan", "id": "5911197578640233518"},
        "374": {"char": "🇦🇲", "iso": "AM", "name": "Armenia", "id": "5913272455866093666"},
        "79": {"char": "🇷🇺", "iso": "RU", "name": "Russia", "id": "5913274246867456342"},
        "998": {"char": "🇺🇿", "iso": "UZ", "name": "Uzbekistan", "id": "5911051846104912282"},
        "49": {"char": "🇩🇪", "iso": "DE", "name": "Germany", "id": "5911096835887337583"},
        "81": {"char": "🇯🇵", "iso": "JP", "name": "Japan", "id": "5913293711659241040"},
        "90": {"char": "🇹🇷", "iso": "TR", "name": "Turkey", "id": "5910995113881901195"},
        "375": {"char": "🇧🇾", "iso": "BY", "name": "Belarus", "id": "5911011185649521599"},
        "44": {"char": "🇬🇧", "iso": "GB", "name": "United Kingdom", "id": "5913443365499703513"},
        "91": {"char": "🇮🇳", "iso": "IN", "name": "India", "id": "5913754823643107921"},
        "55": {"char": "🇧🇷", "iso": "BR", "name": "Brazil", "id": "5911148568768418614"},
        "260": {"char": "🇿🇲", "iso": "ZM", "name": "Zambia", "id": "5913564754160389778"},
        "967": {"char": "🇾🇪", "iso": "YE", "name": "Yemen", "id": "5913346492512341993"},
        "84": {"char": "🇻🇳", "iso": "VN", "name": "Vietnam", "id": "5913428887164949581"},
        "379": {"char": "🇻🇦", "iso": "VA", "name": "Vatican City", "id": "5911211932420938860"},
        "678": {"char": "🇻🇺", "iso": "VU", "name": "Vanuatu", "id": "5913511535220625585"},
        "598": {"char": "🇺🇾", "iso": "UY", "name": "Uruguay", "id": "5913623088406204470"},
        "971": {"char": "🇦🇪", "iso": "AE", "name": "UAE", "id": "5913726554168365343"},
        "256": {"char": "🇺🇬", "iso": "UG", "name": "Uganda", "id": "5913488939397681980"},
        "993": {"char": "🇹🇲", "iso": "TM", "name": "Turkmenistan", "id": "5913315521503170180"},
        "216": {"char": "🇹🇳", "iso": "TN", "name": "Tunisia", "id": "5911332947419468671"},
        "228": {"char": "🇹🇬", "iso": "TG", "name": "Togo", "id": "5913423260757790970"},
        "66": {"char": "🇹🇭", "iso": "TH", "name": "Thailand", "id": "5913617968805187987"},
        "255": {"char": "🇹🇿", "iso": "TZ", "name": "Tanzania", "id": "5911418949844603556"},
        "992": {"char": "🇹🇯", "iso": "TJ", "name": "Tajikistan", "id": "5911287639809463107"},
        "41": {"char": "🇨🇭", "iso": "CH", "name": "Switzerland", "id": "5913271227505448072"},
        "46": {"char": "🇸🇪", "iso": "SE", "name": "Sweden", "id": "5911156510162949403"},
        "268": {"char": "🇸🇿", "iso": "SZ", "name": "Eswatini", "id": "5913374525763883286"},
        "597": {"char": "🇸🇷", "iso": "SR", "name": "Suriname", "id": "5913275539652611719"},
        "249": {"char": "🇸🇩", "iso": "SD", "name": "Sudan", "id": "5911387497799094470"},
        "34": {"char": "🇪🇸", "iso": "ES", "name": "Spain", "id": "5911193287967904547"},
        "94": {"char": "🇱🇰", "iso": "LK", "name": "Sri Lanka", "id": "5911293163137406640"},
        "211": {"char": "🇸🇸", "iso": "SS", "name": "South Sudan", "id": "5911406262511211744"},
        "27": {"char": "🇿🇦", "iso": "ZA", "name": "South Africa", "id": "5911203119148044594"},
        "252": {"char": "🇸🇴", "iso": "SO", "name": "Somala", "id": "5911397852965244436"},
        "677": {"char": "🇸🇧", "iso": "SB", "name": "Solomon Islands", "id": "5911482712929080608"},
        "386": {"char": "🇸🇮", "iso": "SI", "name": "Slovenia", "id": "5913431983836368644"},
        "421": {"char": "🇸🇰", "iso": "SK", "name": "Slovakia", "id": "5913751666842145020"},
        "65": {"char": "🇸🇬", "iso": "SG", "name": "Singapore", "id": "5911531460808051849"},
        "232": {"char": "🇸🇱", "iso": "SL", "name": "Sierra Leone", "id": "5911210450657218661"},
        "248": {"char": "🇸🇨", "iso": "SC", "name": "Seychelles", "id": "5911185183364616913"},
        "381": {"char": "🇷🇸", "iso": "RS", "name": "Serbia", "id": "5913592598433369871"},
        "221": {"char": "🇸🇳", "iso": "SN", "name": "Senegal", "id": "5910995302860461643"},
        "239": {"char": "🇸🇹", "iso": "ST", "name": "Sao Tome", "id": "5913574331937462345"},
        "378": {"char": "🇸🇲", "iso": "SM", "name": "San Marino", "id": "5913587968458625465"},
        "685": {"char": "🇼🇸", "iso": "WS", "name": "Samoa", "id": "5913325971158602854"},
        "970": {"char": "🇵🇸", "iso": "PS", "name": "Palestine", "id": "5913684768431541668"},
        "250": {"char": "🇷🇼", "iso": "RW", "name": "Rwanda", "id": "5911455229433352234"},
        "40": {"char": "🇷🇴", "iso": "RO", "name": "Romania", "id": "5913460373570195273"},
        "974": {"char": "🇶🇦", "iso": "QA", "name": "Qatar", "id": "5911260864983339619"},
        "351": {"char": "🇵🇹", "iso": "PT", "name": "Portugal", "id": "5911023653939581472"},
        "63": {"char": "🇵🇭", "iso": "PH", "name": "Philippines", "id": "5911268638874145162"},
        "51": {"char": "🇵🇪", "iso": "PE", "name": "Peru", "id": "5911207993935925780"},
        "595": {"char": "🇵🇾", "iso": "PY", "name": "Paraguay", "id": "5911014265141072316"},
        "675": {"char": "🇵🇬", "iso": "PG", "name": "Papua", "id": "5911107251183030903"},
        "507": {"char": "🇵🇦", "iso": "PA", "name": "Panama", "id": "5913428968769327174"},
        "680": {"char": "🇵🇼", "iso": "PW", "name": "Palau", "id": "5911283903187915549"},
        "92": {"char": "🇵🇰", "iso": "PK", "name": "Pakistan", "id": "5913705895375672082"},
        "968": {"char": "🇴🇲", "iso": "OM", "name": "Oman", "id": "5913570801474343473"},
        "47": {"char": "🇳🇴", "iso": "NO", "name": "Norway", "id": "5913617397574537046"},
        "234": {"char": "🇳🇬", "iso": "NG", "name": "Nigeria", "id": "5911143844304393105"},
        "227": {"char": "🇳🇪", "iso": "NE", "name": "Niger", "id": "5911270086278124251"},
        "64": {"char": "🇳🇿", "iso": "NZ", "name": "New Zealand", "id": "5913640044937089340"},
        "31": {"char": "🇳🇱", "iso": "NL", "name": "Netherlands", "id": "5913367645226275100"},
        "977": {"char": "🇳🇵", "iso": "NP", "name": "Nepal", "id": "5913496520014958723"},
        "264": {"char": "🇳🇦", "iso": "NA", "name": "Namibia", "id": "5911108535378252443"},
        "258": {"char": "🇲🇿", "iso": "MZ", "name": "Mozambique", "id": "5911333419865871464"},
        "212": {"char": "🇲🇦", "iso": "MA", "name": "Morocco", "id": "5911482111633658301"},
        "382": {"char": "🇲🇪", "iso": "ME", "name": "Montenegro", "id": "5913239436157522151"},
        "976": {"char": "🇲🇳", "iso": "MN", "name": "Mongolia", "id": "5911041383564580038"},
        "377": {"char": "🇲🇨", "iso": "MC", "name": "Monaco", "id": "5911245347266500057"},
        "373": {"char": "🇲🇩", "iso": "MD", "name": "Moldova", "id": "5913456847402045950"},
        "960": {"char": "🇲🇻", "iso": "MV", "name": "Maldives", "id": "5913501399097806832"},
        "223": {"char": "🇲🇱", "iso": "ML", "name": "Mali", "id": "5911305266355245916"},
        "356": {"char": "🇲🇹", "iso": "MT", "name": "Malta", "id": "5911023714069123567"},
        "596": {"char": "🇲🇶", "iso": "MQ", "name": "Martinique", "id": "5911378005921370347"},
        "692": {"char": "🇲🇭", "iso": "MH", "name": "Marshall Islands", "id": "5913235935759175692"},
        "230": {"char": "🇲🇺", "iso": "MU", "name": "Mauritius", "id": "5913291113204027321"},
        "52": {"char": "🇲🇽", "iso": "MX", "name": "Mexico", "id": "5913687302462246518"},
        "691": {"char": "🇫🇲", "iso": "FM", "name": "Micronesia", "id": "5911271104185373336"},
        "60": {"char": "🇲🇾", "iso": "MY", "name": "Malaysia", "id": "5913654360063087453"},
        "254": {"char": "🇰🇪", "iso": "KE", "name": "Kenya", "id": "5911154710571651231"},
        "261": {"char": "🇲🇬", "iso": "MG", "name": "Madagascar", "id": "5913766918271012920"},
        "389": {"char": "🇲🇰", "iso": "MK", "name": "North Macedonia", "id": "5913394029210374721"},
        "352": {"char": "🇱🇺", "iso": "LU", "name": "Luxembourg", "id": "5913390842344640293"},
        "370": {"char": "🇱🇹", "iso": "LT", "name": "Lithuania", "id": "5911172315642597775"},
        "423": {"char": "🇱🇮", "iso": "LI", "name": "Liechtenstein", "id": "5911166650580734660"},
        "218": {"char": "🇱🇾", "iso": "LY", "name": "Libya", "id": "5911236989260140996"},
        "231": {"char": "🇱🇷", "iso": "LR", "name": "Liberia", "id": "5913324167272337727"},
        "686": {"char": "🇰🇮", "iso": "KI", "name": "Kiribati", "id": "5911294443037660118"},
        "383": {"char": "🇽🇰", "iso": "XK", "name": "Kosovo", "id": "5911433681582429010"},
        "965": {"char": "🇰🇼", "iso": "KW", "name": "Kuwait", "id": "5913290705182134003"},
        "996": {"char": "🇰🇬", "iso": "KG", "name": "Kyrgyzstan", "id": "5911202161370337549"},
        "856": {"char": "🇱🇦", "iso": "LA", "name": "Laos", "id": "5913718526874489279"},
        "371": {"char": "🇱🇻", "iso": "LV", "name": "Latvia", "id": "5913738489882480243"},
        "961": {"char": "🇱🇧", "iso": "LB", "name": "Lebanon", "id": "5911504273664905447"},
        "266": {"char": "🇱🇸", "iso": "LS", "name": "Lesotho", "id": "5911059881988723711"},
        "62": {"char": "🇮🇩", "iso": "ID", "name": "Indonesia", "id": "5913479361620611038"},
        "98": {"char": "🇮🇷", "iso": "IR", "name": "Iran", "id": "5911308891307643032"},
        "964": {"char": "🇮🇶", "iso": "IQ", "name": "Iraq", "id": "5911382442622587735"},
        "353": {"char": "🇮🇪", "iso": "IE", "name": "Ireland", "id": "5913440715504881532"},
        "972": {"char": "🇮🇱", "iso": "IL", "name": "Israel", "id": "5911471936856134692"},
        "39": {"char": "🇮🇹", "iso": "IT", "name": "Italy", "id": "5913688444923547525"},
        "962": {"char": "🇯🇴", "iso": "JO", "name": "Jordan", "id": "5913234136167878475"},
        "354": {"char": "🇮🇸", "iso": "IS", "name": "Iceland", "id": "5911047899029967246"},
        "36": {"char": "🇭🇺", "iso": "HU", "name": "Hungary", "id": "5913767635530551104"},
        "504": {"char": "🇭🇳", "iso": "HN", "name": "Honduras", "id": "5911406889576436289"},
        "509": {"char": "🇭🇹", "iso": "HT", "name": "Haiti", "id": "5913459789454643194"},
        "592": {"char": "🇬🇾", "iso": "GY", "name": "Guyana", "id": "5913579412883771480"},
        "245": {"char": "🇬🇼", "iso": "GW", "name": "Bissau", "id": "5911398694778836149"},
        "224": {"char": "🇬🇳", "iso": "GN", "name": "Guinea", "id": "5913471858312744319"},
        "502": {"char": "🇬🇹", "iso": "GT", "name": "Guatemala", "id": "5913324858762072330"},
        "30": {"char": "🇬🇷", "iso": "GR", "name": "Greece", "id": "5911210399117611448"},
        "233": {"char": "🇬🇭", "iso": "GH", "name": "Ghana", "id": "5913391155877252952"},
        "995": {"char": "🇬🇪", "iso": "GE", "name": "Georgia", "id": "5913434771270144023"},
        "220": {"char": "🇬🇲", "iso": "GM", "name": "Gambia", "id": "5913657267755945883"},
        "241": {"char": "🇬🇦", "iso": "GA", "name": "Gabon", "id": "5911037896051137264"},
        "33": {"char": "🇫🇷", "iso": "FR", "name": "France", "id": "5913605586414473124"},
        "358": {"char": "🇫🇮", "iso": "FI", "name": "Finland", "id": "5911041344909873378"},
        "679": {"char": "🇫🇯", "iso": "FJ", "name": "Fiji", "id": "5911393832875856716"},
        "251": {"char": "🇪🇹", "iso": "ET", "name": "Ethiopia", "id": "5911078333168227043"},
        "670": {"char": "🇹🇱", "iso": "TL", "name": "Timor-Leste", "id": "5911141915864076479"},
        "593": {"char": "🇪🇨", "iso": "EC", "name": "Ecuador", "id": "5911273865849347408"},
        "20": {"char": "🇪🇬", "iso": "EG", "name": "Egypt", "id": "5913694831539916769"},
        "503": {"char": "🇸🇻", "iso": "SV", "name": "El Salvador", "id": "5913238624408703010"},
        "372": {"char": "🇪🇪", "iso": "EE", "name": "Estonia", "id": "5910986042910969906"},
        "253": {"char": "🇩🇯", "iso": "DJ", "name": "Djibouti", "id": "5911407709915190157"},
        "45": {"char": "🇩🇰", "iso": "DK", "name": "Denmark", "id": "5911206009661034712"},
        "357": {"char": "🇨🇾", "iso": "CY", "name": "Cyprus", "id": "5911023550860366409"},
        "385": {"char": "🇭🇷", "iso": "HR", "name": "Croatia", "id": "5913692684056269311"},
        "506": {"char": "🇨🇷", "iso": "CR", "name": "Costa Rica", "id": "5911261745451635030"},
        "242": {"char": "🇨🇬", "iso": "CG", "name": "Congo", "id": "5911338788574990168"},
        "243": {"char": "🇨🇩", "iso": "CD", "name": "DR Congo", "id": "5913770362834783827"},
        "269": {"char": "🇰🇲", "iso": "KM", "name": "Comoros", "id": "5911338582416560604"},
        "855": {"char": "🇰🇭", "iso": "KH", "name": "Cambodia", "id": "5913699998385573485"},
        "237": {"char": "🇨🇲", "iso": "CM", "name": "Cameroon", "id": "5911172109484167745"},
        "238": {"char": "🇨🇻", "iso": "CV", "name": "Cape Verde", "id": "5913571501554012193"},
        "236": {"char": "🇨🇫", "iso": "CF", "name": "CAR", "id": "5913443245240619222"},
        "235": {"char": "🇹🇩", "iso": "TD", "name": "Chad", "id": "5913299849167507310"},
        "420": {"char": "🇨🇿", "iso": "CZ", "name": "Czechia", "id": "5911198691036764307"},
        "56": {"char": "🇨🇱", "iso": "CL", "name": "Chile", "id": "5911470957603592832"},
        "57": {"char": "🇨🇴", "iso": "CO", "name": "Colombia", "id": "5913773060074246009"},
        "257": {"char": "🇧🇮", "iso": "BI", "name": "Burundi", "id": "5913766441529642752"},
        "267": {"char": "🇧🇼", "iso": "BW", "name": "Botswana", "id": "5911513782722499475"},
        "387": {"char": "🇧🇦", "iso": "BA", "name": "Bosnia", "id": "5913700002680541032"},
        "591": {"char": "🇧🇴", "iso": "BO", "name": "Bolivia", "id": "5913638795101606133"},
        "975": {"char": "🇧🇹", "iso": "BT", "name": "Bhutan", "id": "5913236734623093021"},
        "229": {"char": "🇧🇯", "iso": "BJ", "name": "Benin", "id": "5913735869952430547"},
        "54": {"char": "🇦🇷", "iso": "AR", "name": "Argentina", "id": "5913573356979884082"},
        "61": {"char": "🇦🇺", "iso": "AU", "name": "Australia", "id": "5913632326880858455"},
        "43": {"char": "🇦🇹", "iso": "AT", "name": "Austria", "id": "5911338831524664592"},
        "973": {"char": "🇧🇭", "iso": "BH", "name": "Bahrain", "id": "5913581663446634403"},
        "880": {"char": "🇧🇩", "iso": "BD", "name": "Bangladesh", "id": "5911365056594973179"},
        "32": {"char": "🇧🇪", "iso": "BE", "name": "Belgium", "id": "5913529642802745141"},
        "501": {"char": "🇧🇿", "iso": "BZ", "name": "Belize", "id": "5913355005137522807"},
        "244": {"char": "🇦🇴", "iso": "AO", "name": "Angola", "id": "5913753316109586411"},
        "376": {"char": "🇦🇩", "iso": "AD", "name": "Andorra", "id": "5911314702398396902"},
        "213": {"char": "🇩🇿", "iso": "DZ", "name": "Algeria", "id": "5913782968563800236"},
        "355": {"char": "🇦🇱", "iso": "AL", "name": "Albania", "id": "5911357458797826163"},
        "93": {"char": "🇦🇫", "iso": "AF", "name": "Afghanistan", "id": "5913492040364068694"},
        "263": {"char": "🇿🇼", "iso": "ZW", "name": "Zimbabwe", "id": "5911092502265336396"},
        "53": {"char": "🇨🇺", "iso": "CU", "name": "Cuba", "id": "5431551436502611633"},
        "850": {"char": "🇰🇵", "iso": "KP", "name": "North Korea", "id": "5434142701941437163"},
        "58": {"char": "🇻🇪", "iso": "VE", "name": "Venezuela", "id": "5434009132753499322"},
        "963": {"char": "🇸🇾", "iso": "SY", "name": "Syria", "id": "5433910876786670092"},
        "95": {"char": "🇲🇲", "iso": "MM", "name": "Myanmar", "id": "5433666360003540231"},
        "505": {"char": "🇳🇮", "iso": "NI", "name": "Nicaragua", "id": "5334807849418003620"},
        "82": {"char": "🇰🇷", "iso": "KR", "name": "South Korea", "id": "5913371673905598425"},
        "240": {"char": "🇬🇶", "iso": "GQ", "name": "Equatorial", "id": "5911306279967529251"},
        "299": {"char": "🇬🇱", "iso": "GL", "name": "Greenland", "id": "5292014752283774878"},
        "298": {"char": "🇫🇴", "iso": "FO", "name": "Faroe Islands", "id": "5296469342039327674"},
        "225": {"char": "🇨🇮", "iso": "CI", "name": "Ivory Coast", "id": "5222233374948602940"},
        "673": {"char": "🇧🇳", "iso": "BN", "name": "Brunei", "id": "5911336409163109113"},
        "359": {"char": "🇧🇬", "iso": "BG", "name": "Bulgaria", "id": "5294329219965272288"},
        "226": {"char": "🇧🇫", "iso": "BF", "name": "Burkina Faso", "id": "5913407764515786948"},
        "291": {"char": "🇪🇷", "iso": "ER", "name": "Eritrea", "id": "5433723401464198287"},
        "265": {"char": "🇲🇼", "iso": "MW", "name": "Malawi", "id": "5433968339154122439"},
        "222": {"char": "🇲🇷", "iso": "MR", "name": "Mauritania", "id": "5433859405898594234"},
        "674": {"char": "🇳🇷", "iso": "NR", "name": "Nauru", "id": "5434131139889478358"},
        "966": {"char": "🇸🇦", "iso": "SA", "name": "Saudi Arabia", "id": "4985897134424328239"},
        "676": {"char": "🇹🇴", "iso": "TO", "name": "Tonga", "id": "5433640100573491806"},
        "688": {"char": "🇹🇻", "iso": "TV", "name": "Tuvalu", "id": "5433684690923961019"},
        "886": {"char": "🇹🇼", "iso": "TW", "name": "Taiwan", "id": "5366187256937726720"},
        "852": {"char": "🇭🇰", "iso": "HK", "name": "Hong Kong", "id": "5292166459118606932"},
        "853": {"char": "🇲🇴", "iso": "MO", "name": "Macau", "id": "6323557758096377611"}
    },    "premium_apps": {
        "FACEBOOK": {"char": "📘", "id": "5987710801815805371", "name": "Facebook"},
        "WHATSAPP": {"char": "💬", "id": "5987961773934780806", "name": "WhatsApp"},
        "TELEGRAM": {"char": "✈️", "id": "5987728952347599001", "name": "Telegram"},
        "WHATSAPP BUSINESSES": {"char": "💼", "id": "5987624163735510516", "name": "WhatsApp Businesses"},
        "IMO": {"char": "💭", "id": "5420159924808231804", "name": "Imo"},
        "INSTAGRAM": {"char": "📸", "id": "5985673990885089081", "name": "Instagram"},
        "APPLE": {"char": "🍎", "id": "5987724223588605235", "name": "Apple"},
        "GOOGLE": {"char": "🔍", "id": "5987804986153640201", "name": "Google"},
        "MICROSOFT": {"char": "🪟", "id": "5985736658752904860", "name": "Microsoft"},
        "OTHER": {"char": "📶", "id": "5987629038523392103", "name": "Other"},
        "TEAMS": {"char": "🧑‍🤝‍🧑", "id": "5987665940882398070", "name": "Teams"},
        "TIKTOK": {"char": "🎵", "id": "5987609011090891923", "name": "Tiktok"},
        "BKASH": {"char": "🏦", "id": "5987604149187911152", "name": "Bkash"},
        "ROCKET": {"char": "🚀", "id": "5987837649379927880", "name": "Rocket"},
        "BYBIT": {"char": "📈", "id": "5987883326357119136", "name": "Bybit"},
        "BINANCE": {"char": "💱", "id": "5987692299096694475", "name": "Binance"},
        "MELBET": {"char": "🌟", "id": "5337102391244263212", "name": "Melbet"},
        "SNAPCHAT": {"char": "👻", "id": "5987559176585357589", "name": "Snapchat"},
        "UBER": {"char": "🚗", "id": "5298715455316303708", "name": "Uber"},
        "PAYPAL": {"char": "💵", "id": "5776103539872896061", "name": "PayPal"},
        "DISCORD": {"char": "🎬", "id": "5987802542317248814", "name": "Discord"},
        "AMAZON": {"char": "🌟", "id": "5987887904792256874", "name": "Amazon"},
        "VIBER": {"char": "💜", "id": "5987569523161571161", "name": "Viber"},
        "LINKEDIN": {"char": "💼", "id": "5987627999141306054", "name": "Linkedin"},
        "LINE": {"char": "🔒", "id": "5987622492993233094", "name": "Line"},
        "WECHAT": {"char": "🌟", "id": "5987972635907071188", "name": "Wechat"},
        "TWITTER": {"char": "🐦", "id": "5987739968938713086", "name": "Twitter"},
        "REDDIT": {"char": "👽", "id": "5987861684016914044", "name": "Reddit"},
        "PINTEREST": {"char": "📌", "id": "5345799562579688546", "name": "Pinterest"},
        "TWITCH": {"char": "🎮", "id": "5233333563306301418", "name": "Twitch"},
        "ZOOM": {"char": "📹", "id": "5881799193219043268", "name": "Zoom"},
        "SIGNAL": {"char": "💬", "id": "5293998404404272267", "name": "Signal"},
        "SLACK": {"char": "💻", "id": "4994972469040251302", "name": "Slack"},
        "SKYPE": {"char": "☎️", "id": "4992613535562334989", "name": "Skype"},
        "NETFLIX": {"char": "🎥", "id": "5987993840160612808", "name": "Netflix"},
        "SPOTIFY": {"char": "🎵", "id": "5346074681004801565", "name": "Spotify"},
        "AMAZON PRIME": {"char": "📺", "id": "5346056560537779652", "name": "Amazon Prime"},
        "HOICHOI": {"char": "🍿", "id": "6104822598493801746", "name": "Hoichoi"},
        "DARAZ": {"char": "📦", "id": "5336879280578138635", "name": "Daraz"},
        "FOODPANDA": {"char": "🐼", "id": "5336879280578138635", "name": "Foodpanda"},
        "PATHAO": {"char": "🛵", "id": "5336879280578138635", "name": "Pathao"},
        "ALIEXPRESS": {"char": "🛒", "id": "5988091215659147405", "name": "AliExpress"},
        "SHOPEE": {"char": "🛍️", "id": "5336879280578138635", "name": "Shopee"},
        "PAYONEER": {"char": "💳", "id": "5336879280578138635", "name": "Payoneer"},
        "WISE": {"char": "🦉", "id": "5336879280578138635", "name": "Wise"},
        "CHATGPT": {"char": "🤖", "id": "5987580771680918123", "name": "ChatGPT"},
        "NOTION": {"char": "📓", "id": "5336879280578138635", "name": "Notion"},
        "GITHUB": {"char": "🐙", "id": "5987807747817611113", "name": "GitHub"},
        "CANVA": {"char": "🖌️", "id": "6100366144722438297", "name": "Canva"},
        "FIGMA": {"char": "🎨", "id": "5336879280578138635", "name": "Figma"},
        "UPWORK": {"char": "💼", "id": "5336879280578138635", "name": "Upwork"},
        "FIVERR": {"char": "🟢", "id": "5336879280578138635", "name": "Fiverr"},
        "YAHOO": {"char": "🌐", "id": "5336879280578138635", "name": "Yahoo"},
        "DROPBOX": {"char": "☁️", "id": "5336879280578138635", "name": "Dropbox"},
        "COURSERA": {"char": "📚", "id": "5336879280578138635", "name": "Coursera"},
        "DUOLINGO": {"char": "🗣️", "id": "5336879280578138635", "name": "Duolingo"},
        "HSBC": {"char": "💄", "id": "5402185559688912571", "name": "Hsbc"},
        "1XBET": {"char": "👌", "id": "6210530664295434942", "name": "1Xbet"}
    },
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy()
}

FS_KEYS = [
    "admins", "panels", "fw_groups", "otp_link", "withdraw_on", 
    "min_withdraw", "otp_reward", "refer_reward", "cooldown", 
    "num_req", "num_share", "support_link", "w_methods", "w_group", "otp_channel_link", "stex_keys", "voltx_keys", "search_countries", "stex_services", "voltx_services",
    "fj_on", "fj_channels", "voltx_auto", "stex_auto", "zenex_auto", "zenex_keys", "zenex_services", "zenex_search_countries",
    "mino_auto", "mino_keys", "mino_services", "mino_search_countries",
    "ws_checker_on", "tg_checker_on", "ws_checker_services", "ws_checker_files", "tg_checker_services", "tg_checker_files",
    "master_api_key", "premium_flags", "premium_apps"
]

number_batches = {}
used_numbers_list = []
stex_assigned_numbers = {} 
voltx_assigned_numbers = {}
zenex_assigned_numbers = {}
mino_assigned_numbers = {}
ws_linked_numbers = {} # Store linked WhatsApp numbers -> user ID
STEX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tness/@public/api"
VOLTX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
ZENEX_BASE_URL = "https://api.zenexnetwork.com"
MINO_BASE_URL = "https://minosms.com"
total_uploaded_stats = 0
total_assigned_stats = 0
processed_otps = set() 
recent_traffic = []
user_banned_cache = {}

# Active HTTP sessions for Auto Captcha Panels
panel_sessions = {}

# 🌟 sAjaxSource (AJAX/DataTable) এবং Fallback HTML Parser Helper Function
def fetch_cpt_panel_cdrs(p, session, check_url):
    res = session.get(check_url, timeout=15)
    html_text = res.text
    
    # সেশন শেষ হয়েছে বা লগইন পেজে রিডাইরেক্ট করেছে কি না তা সঠিকভাবে চেক করা
    is_session_expired = False
    if res.status_code in (401, 403):
        is_session_expired = True
    elif ('type="password"' in html_text or "type='password'" in html_text) and ('<form' in html_text):
        is_session_expired = True
    elif any(x in html_text for x in ["Sign in to your account", "Please sign in to continue", "User Login", "Login to your account"]):
        if 'logout' not in html_text.lower() and 'cdrs' not in html_text.lower() and 'smscdrstats' not in html_text.lower():
            is_session_expired = True

    if is_session_expired:
        raise Exception("Session expired")
        
    soup = BeautifulSoup(html_text, 'html.parser')
    s_ajax_source = ""
    for script in soup.find_all("script"):
        script_text = script.string or ""
        match = re.search(r'sAjaxSource":\s*"([^"]+)"', script_text)
        if match:
            s_ajax_source = match.group(1)
            break
            
    results = []
    
    n_col_name = p.get("num_col_name", "number").lower()
    m_col_name = p.get("msg_col_name", "message").lower()
    n_idx = int(p.get("num_col_idx", 1)) - 1 if p.get("num_col_idx") else 1
    m_idx = int(p.get("msg_col_idx", 2)) - 1 if p.get("msg_col_idx") else 2

    # ৫.১ যদি sAjaxSource AJAX লিংক পাওয়া যায়
    if s_ajax_source:
        baseUrl = p.get("login_url", "").split("/client")[0].split("/login")[0].strip()
        if not baseUrl.startswith("http"):
            baseUrl = "http://" + baseUrl
            
        full_ajax_url = ""
        if s_ajax_source.startswith("http"):
            full_ajax_url = s_ajax_source
        elif s_ajax_source.startswith("/"):
            full_ajax_url = f"{baseUrl}{s_ajax_source}"
        else:
            last_slash_idx = check_url.rfind("/")
            current_dir = check_url[:last_slash_idx]
            full_ajax_url = f"{current_dir}/{s_ajax_source}"

        if "iDisplayLength" not in full_ajax_url:
            # 250 এর জায়গায় 10000 করে দেওয়া হলো যাতে সব মেসেজ ফেচ করতে পারে
            query_params = "sEcho=1&iColumns=7&iDisplayStart=0&iDisplayLength=10000&sSearch=&iSortingCols=1&iSortCol_0=0&sSortDir_0=desc"
            divider = "&" if "?" in full_ajax_url else "?"
            full_ajax_url += f"{divider}{query_params}"

        ajax_headers = {
            "Referer": check_url,
            "X-Requested-With": "XMLHttpRequest"
        }
        
        ajax_res = session.get(full_ajax_url, headers=ajax_headers, timeout=15)
        data_dict = ajax_res.json()
        rows = data_dict.get("aaData", [])
        for row_val in rows:
            if not isinstance(row_val, list):
                continue
                
            if len(row_val) < max(n_idx, m_idx) + 1:
                continue
                
            num_val = row_val[n_idx] if (0 <= n_idx < len(row_val)) else row_val[2]
            msg_val = row_val[m_idx] if (0 <= m_idx < len(row_val)) else row_val[4]
            
            clean_num = re.sub(r'\D', '', str(num_val))
            msg_str = str(msg_val).strip()
            if clean_num and 5 <= len(clean_num) <= 18 and len(msg_str) > 4:
                otp = extract_otp_code(msg_str) or "FULL_SMS"
                results.append({"number": clean_num, "message": msg_str, "otp": otp})
                    
    else:
        # ৫.২ ডাইরেক্ট HTML টেবিল থেকে রিড করার ব্যাকআপ লজিক
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if not rows: continue
            
            final_n_idx = n_idx
            final_m_idx = m_idx
            
            header_cells = rows[0].find_all(['th', 'td'])
            for i, cell in enumerate(header_cells):
                c_text = cell.get_text(strip=True).lower()
                if n_col_name in c_text: final_n_idx = i
                if m_col_name in c_text: final_m_idx = i

            for row in rows:
                cols = row.find_all(['td', 'th'])
                if all(c.name == 'th' for c in cols): continue
                
                if len(cols) > max(final_n_idx, final_m_idx):
                    num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                    msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                    
                    clean_num = re.sub(r'\D', '', num_text)
                    if clean_num and 5 <= len(clean_num) <= 18 and len(msg_text) > 4:
                        otp = extract_otp_code(msg_text) or "FULL_SMS"
                        results.append({"number": clean_num, "message": msg_text, "otp": otp})
                            
    return results, html_text

# Track active number sessions to expire them automatically
user_active_sessions = {}

assigned_number_rates = {}

def load_db():
    global bot_settings, number_batches, used_numbers_list, total_uploaded_stats, total_assigned_stats, recent_traffic, stex_assigned_numbers, voltx_assigned_numbers, zenex_assigned_numbers, mino_assigned_numbers, ws_linked_numbers, processed_otps, assigned_number_rates
    
    loaded_from_local = False
    
    # ১. প্রথমে Local DB লোড করবে (এটি সবচেয়ে আপডেট থাকে, তাই Key হারাবে না)
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                saved_settings = data.get("bot_settings", {})
                for key, val in saved_settings.items():
                    if key == "custom_messages":
                        for m_key, m_val in val.items():
                            bot_settings["custom_messages"][m_key] = m_val
                    else:
                        bot_settings[key] = val
                        
                for m_key, m_val in DEFAULT_CUSTOM_MESSAGES.items():
                    if m_key not in bot_settings["custom_messages"]:
                        bot_settings["custom_messages"][m_key] = m_val
                        
                number_batches = data.get("number_batches", {})
                used_numbers_list = data.get("used_numbers_list", [])
                total_uploaded_stats = data.get("total_uploaded_stats", 0)
                total_assigned_stats = data.get("total_assigned_stats", 0)
                recent_traffic = data.get("recent_traffic", [])
                stex_assigned_numbers = data.get("stex_assigned_numbers", {})
                voltx_assigned_numbers = data.get("voltx_assigned_numbers", {})
                zenex_assigned_numbers = data.get("zenex_assigned_numbers", {})
                mino_assigned_numbers = data.get("mino_assigned_numbers", {})
                ws_linked_numbers = data.get("ws_linked_numbers", {})
                processed_otps = set(data.get("processed_otps", []))
                assigned_number_rates = data.get("assigned_number_rates", {})
                loaded_from_local = True
            print("✅ Local Stock/UI DB Loaded Successfully!")
        except Exception as e:
            print(f"❌ Error loading local DB: {e}")

    # ২. এরপর Firestore থেকে শুধু মিসিং ডেটা লোড করবে (Local ডেটা ওভাররাইট করবে না)
    if db:
        try:
            doc = db.collection('settings').document('bot_config').get()
            if doc.exists:
                fs_data = doc.to_dict()
                for k in FS_KEYS:
                    # যদি Local-এ ডেটা না থাকে (ফাঁকা থাকে), তবেই শুধুমাত্র Firestore থেকে আনবে
                    if k in fs_data and (not loaded_from_local or bot_settings.get(k) in [None, [], ""]):
                        bot_settings[k] = fs_data[k]
                print("✅ Config Synced with Firestore!")
            else:
                fs_data = {k: bot_settings[k] for k in FS_KEYS if k in bot_settings}
                db.collection('settings').document('bot_config').set(fs_data)
                print("✅ Firestore Config Initialized!")
        except Exception as e:
            print(f"❌ Error loading from Firestore: {e}")

def save_local_db():
    local_data = {
        "bot_settings": bot_settings,
        "number_batches": number_batches,
        "used_numbers_list": used_numbers_list,
        "total_uploaded_stats": total_uploaded_stats,
        "total_assigned_stats": total_assigned_stats,
        "recent_traffic": recent_traffic,
        "stex_assigned_numbers": stex_assigned_numbers,
        "voltx_assigned_numbers": voltx_assigned_numbers,
        "zenex_assigned_numbers": zenex_assigned_numbers,
        "mino_assigned_numbers": mino_assigned_numbers,
        "ws_linked_numbers": ws_linked_numbers,
        "processed_otps": list(processed_otps),
        "assigned_number_rates": assigned_number_rates
    }
    with db_lock:
        try:
            # Atomic Write: প্রথমে .tmp ফাইলে সেভ করবে, তারপর মেইন ফাইলে রিপ্লেস করবে
            temp_file = DB_FILE + ".tmp"
            with open(temp_file, "w", encoding='utf-8') as f:
                json.dump(local_data, f, indent=4)
            os.replace(temp_file, DB_FILE)
        except Exception as e:
            pass

def _sync_fs():
    if not db: return
    fs_data = {k: bot_settings[k] for k in FS_KEYS if k in bot_settings}
    try:
        db.collection('settings').document('bot_config').set(fs_data)
    except: pass

def save_db():
    # 🌟 Local এবং Firestore দুটোই এখন Background-এ সেভ হবে, তাই বাটন ক্লিক চোখের পলকে রেসপন্স করবে!
    threading.Thread(target=save_local_db).start()
    threading.Thread(target=_sync_fs).start()

load_db()

user_states = {}
temp_data = {}
user_cooldowns = {}
pending_withdrawals = {}

# ==========================================
# Telegram API & Helpers
# ==========================================
tg_session = requests.Session() # 🌟 Keep-Alive Connection (Makes bot 10x faster)

def api_call(method, payload=None):
    url = f"{BASE_URL}/{method}"
    try:
        # 🌟 Added timeout to prevent hanging!
        res = tg_session.post(url, json=payload, timeout=15)
        return res.json()
    except Exception as e:
        return {}

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendMessage", payload)

def send_photo(chat_id, photo_url_or_file_id, caption="", reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "photo": photo_url_or_file_id, "caption": caption, "parse_mode": parse_mode}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendPhoto", payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("editMessageText", payload)

def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def answer_callback(callback_id, text="", show_alert=False):
    api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text, "show_alert": show_alert})

def send_document(chat_id, filename, text_content):
    url = f"{BASE_URL}/sendDocument"
    files = {'document': (filename, text_content)}
    data = {'chat_id': chat_id}
    try: requests.post(url, data=data, files=files)
    except: pass

# 🌟 Local User List to completely remove Firebase Read Costs!
all_known_users = set()

def sync_users_list():
    global all_known_users
    try:
        if os.path.exists("users_list.json"):
            with open("users_list.json", "r") as f:
                all_known_users = set(json.load(f))
        if not all_known_users and db:
            for doc in db.collection('users').select([]).stream():
                all_known_users.add(doc.id)
            with open("users_list.json", "w") as f:
                json.dump(list(all_known_users), f)
    except: pass

threading.Thread(target=sync_users_list, daemon=True).start()

def _save_users_list():
    try:
        with open("users_list.json", "w") as f:
            json.dump(list(all_known_users), f)
    except: pass

def register_user_local(uid):
    uid_str = str(uid)
    if uid_str not in all_known_users:
        all_known_users.add(uid_str)
        # 🌟 Non-blocking background save (Prevents lag)
        threading.Thread(target=_save_users_list, daemon=True).start()

def broadcast_copymessage(from_chat_id, msg_id):
    users = list(all_known_users)
    url = f"{BASE_URL}/copyMessage"
    results = {"success": 0, "failed": 0}
    b_session = requests.Session()
    
    def send_single(user_id):
        try:
            payload = {"chat_id": user_id, "from_chat_id": from_chat_id, "message_id": msg_id}
            res = b_session.post(url, json=payload, timeout=5).json()
            if res.get("ok"): results["success"] += 1
            else: results["failed"] += 1
        except:
            results["failed"] += 1

    # 🌟 15x Fast Multi-threading for Broadcast 
    with ThreadPoolExecutor(max_workers=15) as executor:
        executor.map(send_single, users)
        
    send_message(from_chat_id, render_body_text(f"📢 <b>Broadcast Completed!</b>\n✅ Success: {results['success']}\n❌ Failed: {results['failed']}\n👥 Total Sent: {len(users)}"))

def render_body_text(text):
    if not text: return str(text)
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', str(text))
    for i in range(len(parts)):
        if not parts[i].startswith('<tg-emoji'):
            for normal_emj, prem_id in GLOBAL_BODY_EMOJIS.items():
                if normal_emj in parts[i]:
                    parts[i] = parts[i].replace(normal_emj, f'<tg-emoji emoji-id="{prem_id}">{normal_emj}</tg-emoji>')
    return "".join(parts)

def extract_premium_html(msg):
    text = msg.get("text", msg.get("caption", ""))
    entities = msg.get("entities", msg.get("caption_entities", []))
    if not entities: return text
    try:
        b_text = text.encode('utf-16-le')
        c_entities = [e for e in entities if e.get("type") == "custom_emoji"]
        c_entities.sort(key=lambda x: x["offset"], reverse=True)
        for ent in c_entities:
            offset = ent["offset"] * 2
            length = ent["length"] * 2
            eid = ent["custom_emoji_id"]
            emoji_char = b_text[offset:offset+length].decode('utf-16-le')
            html_tag = f'<tg-emoji emoji-id="{eid}">{emoji_char}</tg-emoji>'
            replacement = html_tag.encode('utf-16-le')
            b_text = b_text[:offset] + replacement + b_text[offset+length:]
        return b_text.decode('utf-16-le')
    except Exception as e:
        return text 

def get_flag_info_from_num(num):
    clean = num.replace("+", "").replace(" ", "")
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            data = bot_settings["premium_flags"][code]
            return data["char"], data.get("iso", "XX"), data.get("id")
    return "🌍", "XX", None

def get_flag_and_code(num):
    char, iso, _ = get_flag_info_from_num(num)
    return char, iso

def get_flag_info_html(num_or_iso, return_full_name=False):
    if len(num_or_iso) == 2:
        for code, data in bot_settings.get("premium_flags", {}).items():
            if data.get("iso") == num_or_iso:
                eid = data.get("id")
                char = data.get("char")
                name = data.get("name", num_or_iso)
                if return_full_name: return name
                if eid: return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                return char
        if return_full_name: return num_or_iso
        return "🌍"
        
    char, _, eid = get_flag_info_from_num(num_or_iso)
    if return_full_name:
        for code, data in bot_settings.get("premium_flags", {}).items():
            clean = num_or_iso.replace("+", "").replace(" ", "")
            if clean.startswith(code): return data.get("name", num_or_iso)
        return num_or_iso
        
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
    return char

def mask_number(num):
    clean = num.replace("+", "").replace(" ", "")
    if len(clean) > 6: return f"{clean[:3]}DXA{clean[-3:]}"
    elif len(clean) > 2: return f"{clean[:1]}DXA{clean[-1:]}"
    return clean

# 🌟 WhatsApp Checker API Helper 🌟
def is_checker_api_valid():
    if not bot_settings.get("ws_checker_on", False):
        return False
    api_url = bot_settings.get("master_api_url", "https://bot.orabitsms.site/api")
    api_key = bot_settings.get("master_api_key", "").strip()
    if not api_key:
        return False
    try:
        res = requests.get(f"{api_url}/user-status", params={"apiKey": api_key}, timeout=8)
        if res.status_code != 200:
            return False
        data = res.json()
        if isinstance(data, dict):
            if data.get("success") is False or data.get("error"):
                return False
            if "ActiveSessions" in data or data.get("success") is True:
                return True
        return False
    except Exception:
        return False

def check_whatsapp_numbers(phones_list, user_id):
    """
    ইউজারের লিংক করা নম্বরগুলো (senders) দিয়ে phones_list এর নম্বরগুলো চেক করবে।
    পার্সোনাল সিস্টেম: ইউজারের নিজস্ব সেন্ডার না থাকলে চেক করবে না।
    """
    results = {}
    for p in phones_list:
        clean_p = p.replace("+", "").replace(" ", "")
        results[clean_p] = "Unknown"

    if not bot_settings.get("ws_checker_on", False):
        return results

    api_key = bot_settings.get("master_api_key", "")
    if not api_key:
        return results

    # 🌟 শুধু ইউজারের নিজের কানেক্ট করা নাম্বার (Sender) খুঁজবে
    user_senders = [phone for phone, uid in ws_linked_numbers.items() if str(uid) == str(user_id)]
    
    # 🌟 ইউজারের নিজস্ব সেন্ডার না থাকলে চেক স্কিপ করবে (পার্সোনাল সিস্টেম)
    if not user_senders:
        return results

    checker_url = "https://bot.orabitsms.site/api/check-whatsapp-batch"
    
    # অ্যাডমিনের ডক অনুযায়ী হেডার সেট করা হলো
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    clean_phones = [p.replace("+", "").replace(" ", "") for p in phones_list]
    
    # 🌟 অ্যাডমিনের ডক অনুযায়ী পেলোডে phones এবং senders দেওয়া হলো
    payload = {
        "apiKey": api_key,
        "phones": clean_phones,
        "sender": user_senders[0],
        "senders": user_senders
    }

    try:
        res = requests.post(checker_url, json=payload, headers=headers, timeout=25)
        
        if res.status_code == 200:
            data = res.json()
            
            # 🟢 Good Numbers (notActive in WhatsApp)
            for item in data.get("notActive", []):
                phones = item.get("phone", []) if isinstance(item, dict) else [item]
                if not isinstance(phones, list):
                    phones = [phones]
                for ph in phones:
                    clean_ph = re.sub(r'\D', '', str(ph))
                    if clean_ph:
                        results[clean_ph] = "Good"

            # 🚫 Bad Numbers (active in WhatsApp)
            for item in data.get("active", []):
                phones = item.get("phone", []) if isinstance(item, dict) else [item]
                if not isinstance(phones, list):
                    phones = [phones]
                for ph in phones:
                    clean_ph = re.sub(r'\D', '', str(ph))
                    if clean_ph:
                        results[clean_ph] = "Bad"
    except Exception as e:
        pass 

    return results

def format_checker_button(display_num, clean_num, ws_results, tg_results=None):
    ws_stat = ws_results.get(clean_num, "Unknown")

    emojis = ""
    if ws_stat == "Good":
        emojis += "🟢"
    elif ws_stat == "Bad":
        emojis += "🚫"

    if ws_stat == "Bad":
        btn_style = "danger"
    elif ws_stat == "Good":
        btn_style = "success"
    else:
        btn_style = "primary"

    btn_text = f"{display_num} {emojis}" if emojis else f"{display_num}"
    return btn_text, btn_style

def get_number_reward_rate(num, owner_id=None):
    clean_n = re.sub(r'\D', '', str(num))
    if not clean_n:
        return float(bot_settings.get("otp_reward", 0.0))
    # ১. সরাসরি assigned_number_rates এ চেক (+ সহ এবং + ছাড়া)
    for k in (str(num).strip(), f"+{clean_n}", clean_n):
        if k in assigned_number_rates:
            return float(assigned_number_rates[k])
    # ২. ইউজারের অ্যাক্টিভ সেশনে থাকা নাম্বারের সাথে মিলিয়ে চেক (প্যানেল থেকে কান্ট্রি কোড ছাড়া নাম্বার আসলে)
    if owner_id and owner_id in user_active_sessions:
        for act_num in user_active_sessions[owner_id].get("nums", []):
            act_clean = re.sub(r'\D', '', str(act_num))
            if act_clean and (act_clean == clean_n or (len(act_clean) >= 8 and len(clean_n) >= 8 and (act_clean.endswith(clean_n[-8:]) or clean_n.endswith(act_clean[-8:])))):
                for k in (str(act_num).strip(), f"+{act_clean}", act_clean):
                    if k in assigned_number_rates:
                        return float(assigned_number_rates[k])
    # ৩. শেষের ৮ ডিজিট দিয়ে assigned_number_rates এ চেক
    if len(clean_n) >= 8:
        for k, r_val in assigned_number_rates.items():
            k_clean = re.sub(r'\D', '', str(k))
            if k_clean and (k_clean == clean_n or (len(k_clean) >= 8 and (k_clean.endswith(clean_n[-8:]) or clean_n.endswith(k_clean[-8:])))):
                return float(r_val)
    # ৪. number_batches এ চেক (যদি নাম্বার এখনও কোনো ফাইলের ব্যাচে থাকে)
    for b_data in number_batches.values():
        if "rate" in b_data:
            for n_obj in b_data.get("numbers", []):
                b_clean = re.sub(r'\D', '', str(n_obj.get("num", "")))
                if b_clean and (b_clean == clean_n or (len(b_clean) >= 8 and len(clean_n) >= 8 and (b_clean.endswith(clean_n[-8:]) or clean_n.endswith(b_clean[-8:])))):
                    return float(b_data["rate"])
    return float(bot_settings.get("otp_reward", 0.0))

def build_live_number_text(prem_app_html, app_full_name, country_emoji_html, country_full_name, iso_code, run_ws=False, run_tg=False, nums=None):
    rate_val = bot_settings.get("otp_reward", 0.0)
    if nums and len(nums) > 0:
        rate_val = get_number_reward_rate(nums[0])
    try:
        f_rate = float(rate_val)
        rate_str = str(int(f_rate)) if f_rate.is_integer() else str(f_rate)
    except:
        rate_str = str(rate_val)
    return (f" {country_emoji_html} COUNTRY: {str(country_full_name).upper()} [ {iso_code} ] \n"
            f"{prem_app_html} SERVICE : {str(app_full_name).upper()}\n"
            f"💳 OTP RATE : ৳{rate_str} TK\n")

def strip_country_code(num_str):
    clean = re.sub(r'\D', '', str(num_str))
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code) and len(clean) > len(code):
            return clean[len(code):]
    return clean

LANG_MAP = {
    "#EN": "English", "#BN": "Bengali", "#AR": "Arabic", "#HI": "Hindi", 
    "#PA": "Punjabi", "#GU": "Gujarati", "#OR": "Odia", "#TA": "Tamil", 
    "#TE": "Telugu", "#KN": "Kannada", "#ML": "Malayalam", "#SI": "Sinhala", 
    "#TH": "Thai", "#LO": "Lao", "#BO": "Tibetan", "#MY": "Burmese", 
    "#AM": "Amharic", "#KM": "Khmer", "#KA": "Georgian", "#HY": "Armenian", 
    "#HE": "Hebrew", "#EL": "Greek", "#RU": "Russian", "#ZH": "Chinese", 
    "#JA": "Japanese", "#KO": "Korean", "#ID": "Indonesian", "#MS": "Malay", 
    "#VN": "Vietnamese", "#TL": "Filipino", "#ES": "Spanish", "#PT": "Portuguese", 
    "#FR": "French", "#DE": "German", "#IT": "Italian", "#PL": "Polish", 
    "#TR": "Turkish", "#NL": "Dutch", "#SV": "Swedish", "#DA": "Danish", 
    "#NO": "Norwegian", "#FI": "Finnish", "#CS": "Czech", "#SK": "Slovak", 
    "#HU": "Hungarian", "#RO": "Romanian", "#HR": "Croatian", "#BG": "Bulgarian", 
    "#UK": "Ukrainian", "#SW": "Swahili", "#AF": "Afrikaans"
}

# ==========================================
# 🌟 ADVANCED SERVICE & LANGUAGE DETECTION
# ==========================================

SERVICE_SMS_KEYWORDS = {
    # 🟢 Social Media & Chat (Added Arabic Keywords)
    "whatsapp": ["whatsapp", "whatsa", "whatsap", "whats", "whatsapp business", "whatsapp me", "whatsapp code", "whatsap", "واتساب", "واتساپ", "واٹس ایپ", "व्हाट्सएप", "वाट्सएप", "वॉट्सऐप", "व्हाट्सप्प", "হোয়াটসঅ্যাপ", "হোটসঅ্যাপ", "ватсап", "уотсап", "вотсап", "ватс апп", "వాట్సాప్", "വാട്‌സ്ആപ്പ്", "வாட்ஸ்அப்", "ವಾಟ್ಸಾಪ್", "વોટ્સએપ", "ਵਟਸਐਪ", "ହ୍ଵାଟସ୍ ଆପ୍", "වට්ස්ඇප්", "วอตส์แอปป์", "วอทส์แอพ", "ဝက်စ်အက်ပ်", "វ៉តសាប់", "ວອດແອັບ", "ワッツアップ", "왓츠앱", "whatsapp的", "whatsapp验证码", "וואטסאפ", "γουάτσαπ", "ዋትስአፕ", "ვოთსאფი", "վոթսափ"],
    "facebook": ["facebook", "fb", "meta", "fbook", "fb code", "facebook code", "فيسبوك", "فيس بوك"],
    "instagram": ["instagram", "insta", "ig", "ig code", "instagram code", "انستغرام", "انستقرام"],
    "telegram": ["telegram", "tg", "tele", "telegram code", "tg code", "t.me", "تيليجرام", "تليجرام"],
    "tiktok": ["tiktok", "tik tok", "tikvideo", "tiktok code", "tik code", "تيك توك"],
    "snapchat": ["snapchat", "snap", "snap code", "سناب شات"],
    "twitter": ["twitter", "x.com", "x code", "twitter code", "تويتر"],
    "discord": ["discord", "discord code", "ديسكورد"],
    "viber": ["viber", "viber code", "فايبر"],
    "line": ["line", "line code", "line verification", "لاين"],
    "wechat": ["wechat", "we chat", "wechat code", "وي تشات"],
    "signal": ["signal", "signal code", "سيجنال"],
    "linkedin": ["linkedin", "linked in", "لينكد إن"],
    "imo": ["imo", "imo code", "imo verification", "ايمو"],
    "kakaotalk": ["kakao", "kakaotalk", "كاكاو"],
    "qq": ["qq", "tencent qq"],
    "vk": ["vk", "vkontakte"],

    # 🔵 Tech & Mail
    "google": ["google", "gmail", "youtube", "g-", "google voice", "جوجل", "غوغل"],
    "microsoft": ["microsoft", "ms", "outlook", "live.com", "hotmail"],
    "apple": ["apple", "icloud", "itunes", "apple id"],
    "yahoo": ["yahoo", "yahoo code", "ymail"],
    "protonmail": ["proton", "protonmail"],
    
    # 💰 Crypto & Trading
    "binance": ["binance", "bnb", "binances"],
    "coinbase": ["coinbase"],
    "okx": ["okx", "okex"],
    "kucoin": ["kucoin"],
    "bybit": ["bybit"],
    "huobi": ["huobi", "htx"],
    "mexc": ["mexc"],
    "trustwallet": ["trust wallet", "trustwallet"],

    # 💳 Finance & Wallets
    "bkash": ["bkash", "b-kash", "bkash code"],
    "nagad": ["nagad", "nagad code"],
    "rocket": ["rocket", "dutch bangla"],
    "upay": ["upay", "upay code"],
    "paypal": ["paypal", "pay pal"],
    "paytm": ["paytm"],
    "cashapp": ["cash app", "cashapp"],
    "wise": ["wise", "transferwise"],

    # 🛒 E-commerce & Delivery
    "amazon": ["amazon", "amzn", "amazon code"],
    "ebay": ["ebay"],
    "aliexpress": ["aliexpress", "ali express"],
    "alibaba": ["alibaba"],
    "daraz": ["daraz", "daraz code"],
    "foodpanda": ["foodpanda", "food panda"],
    "uber": ["uber", "uber code", "uber verification", "uber eats"],
    "pathao": ["pathao", "pathao ride"],

    # 🎮 Gaming & Entertainment
    "netflix": ["netflix", "netflix code"],
    "spotify": ["spotify", "spotify code"],
    "steam": ["steam", "steam guard"],
    "epicgames": ["epic games", "epicgames"],
    "roblox": ["roblox", "roblox code"],
    "riotgames": ["riot", "riot games", "valorant", "league of legends"],
    "garena": ["garena", "free fire", "freefire"],
    "playstation": ["playstation", "psn"],

    # 🎲 Betting & Casino
    "1xbet": ["1xbet", "1x bet"],
    "melbet": ["melbet", "melbet code"],
    "linebet": ["linebet"],
    "bet365": ["bet365"],
    "megapari": ["megapari"],

    # ❤️ Dating
    "tinder": ["tinder", "tinder code"],
    "bumble": ["bumble"],
    "badoo": ["badoo"]
}

def detect_service(text):
    text_lower = str(text).lower()
    for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return service_key.upper()
    return None

def get_service_info_html(service_text, msg_text=""):
    s = str(service_text).upper().strip()
    m = str(msg_text).lower().strip()
    apps = bot_settings.get("premium_apps", {})
    
    detected_service = s
    if m:
        for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
            for kw in keywords:
                if kw in m:
                    detected_service = service_key.upper()
                    break
            if detected_service != s: break

    clean_s = re.sub(r'[^\w\s]', '', detected_service).strip()
    
    for app_name, data in apps.items():
        if app_name == detected_service or app_name == clean_s or app_name in detected_service or detected_service in app_name:
            full_name = data.get("name", app_name.title())
            char = data.get("char", "📱")
            eid = data.get("id")
            if eid: return full_name, f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
            return full_name, char
            
    if len(detected_service) > 20:
        return "Message", "💬"
        
    # 🌟 সার্ভিস লিস্টে না থাকলে (যেকোনো অচেনা নাম) সরাসরি Other-এ পাঠিয়ে দেবে
    if "OTHER" in apps:
        other_data = apps["OTHER"]
        eid = other_data.get("id")
        char = other_data.get("char", "📶")
        return other_data.get("name", "Other"), f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>' if eid else char
        
    return "Other", "📶"

def detect_language(text):
    if not text: return "#EN"
    text_str = str(text)

    # ১. Unicode Block দিয়ে নিখুঁত বর্ণমালা শনাক্তকরণ (100% Accurate for scripts)
    if any('\u0600' <= c <= '\u06ff' for c in text_str): return "#AR" # Arabic / Persian / Urdu
    if any('\u0980' <= c <= '\u09ff' for c in text_str): return "#BN" # Bengali
    if any('\u0900' <= c <= '\u097f' for c in text_str): return "#HI" # Hindi / Marathi / Nepali
    if any('\u0a00' <= c <= '\u0a7f' for c in text_str): return "#PA" # Punjabi (Gurmukhi)
    if any('\u0a80' <= c <= '\u0aff' for c in text_str): return "#GU" # Gujarati
    if any('\u0b00' <= c <= '\u0b7f' for c in text_str): return "#OR" # Odia
    if any('\u0b80' <= c <= '\u0bff' for c in text_str): return "#TA" # Tamil
    if any('\u0c00' <= c <= '\u0c7f' for c in text_str): return "#TE" # Telugu
    if any('\u0c80' <= c <= '\u0cff' for c in text_str): return "#KN" # Kannada
    if any('\u0d00' <= c <= '\u0d7f' for c in text_str): return "#ML" # Malayalam
    if any('\u0d80' <= c <= '\u0dff' for c in text_str): return "#SI" # Sinhala
    if any('\u0e00' <= c <= '\u0e7f' for c in text_str): return "#TH" # Thai
    if any('\u0e80' <= c <= '\u0eff' for c in text_str): return "#LO" # Lao
    if any('\u0f00' <= c <= '\u0fff' for c in text_str): return "#BO" # Tibetan
    if any('\u1000' <= c <= '\u109f' for c in text_str): return "#MY" # Burmese (Myanmar)
    if any('\u1200' <= c <= '\u137f' for c in text_str): return "#AM" # Amharic (Ethiopic)
    if any('\u1780' <= c <= '\u17ff' for c in text_str): return "#KM" # Khmer
    if any('\u10a0' <= c <= '\u10ff' for c in text_str): return "#KA" # Georgian
    if any('\u0530' <= c <= '\u058f' for c in text_str): return "#HY" # Armenian
    if any('\u0590' <= c <= '\u05ff' for c in text_str): return "#HE" # Hebrew
    if any('\u0370' <= c <= '\u03ff' for c in text_str): return "#EL" # Greek
    if any('\u0400' <= c <= '\u04ff' for c in text_str): return "#RU" # Russian / Ukrainian (Cyrillic)
    if any('\u4e00' <= c <= '\u9fff' for c in text_str): return "#ZH" # Chinese
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text_str): return "#JA" # Japanese
    if any('\uac00' <= c <= '\ud7af' for c in text_str): return "#KO" # Korean

    # ২. OTP Keyword দিয়ে ভাষা শনাক্তকরণ (Latin script languages)
    text_lower = text_str.lower()
    
    # Asian / Pacific
    if any(w in text_lower for w in ["kode verifikasi", "jangan bagikan", "rahasia"]): return "#ID" # Indonesian
    if any(w in text_lower for w in ["kod pengesahan", "jangan kongsi"]): return "#MS" # Malay
    if any(w in text_lower for w in ["mã của bạn", "không chia sẻ", "mã xác minh"]): return "#VN" # Vietnamese
    if any(w in text_lower for w in ["ang iyong code", "huwag ibahagi"]): return "#TL" # Tagalog / Filipino
    
    # European / Americas
    if any(w in text_lower for w in ["código", "tu código", "verificación", "no compartas"]): return "#ES" # Spanish
    if any(w in text_lower for w in ["seu código", "código de verificação", "não compartilhe"]): return "#PT" # Portuguese
    if any(w in text_lower for w in ["code secret", "ne partagez pas", "votre code"]): return "#FR" # French
    if any(w in text_lower for w in ["dein code", "bestätigungscode", "nicht teilen"]): return "#DE" # German
    if any(w in text_lower for w in ["il tuo codice", "codice di verifica", "non condividere"]): return "#IT" # Italian
    if any(w in text_lower for w in ["twój kod", "nie udostępniaj", "kod weryfikacyjny"]): return "#PL" # Polish
    if any(w in text_lower for w in ["doğrulama kodu", "paylaşmayın", "onay kodu"]): return "#TR" # Turkish
    if any(w in text_lower for w in ["jouw code", "verificatiecode", "niet delen"]): return "#NL" # Dutch
    if any(w in text_lower for w in ["din kod", "verifieringskod", "dela inte"]): return "#SV" # Swedish
    if any(w in text_lower for w in ["bekræftelseskode", "del ikke"]): return "#DA" # Danish
    if any(w in text_lower for w in ["bekreftelseskode", "ikke del"]): return "#NO" # Norwegian
    if any(w in text_lower for w in ["vahvistuskoodi", "älä jaa"]): return "#FI" # Finnish
    if any(w in text_lower for w in ["váš kód", "ověřovací kód", "nesdílejte"]): return "#CS" # Czech
    if any(w in text_lower for w in ["overovací kód", "nezdieľajte"]): return "#SK" # Slovak
    if any(w in text_lower for w in ["ellenőrző kód", "ne oszd meg"]): return "#HU" # Hungarian
    if any(w in text_lower for w in ["codul tău", "codul de verificare", "nu partaja"]): return "#RO" # Romanian
    if any(w in text_lower for w in ["kontrolni kod", "kod za potvrdu", "ne delite"]): return "#HR" # Croatian/Serbian
    if any(w in text_lower for w in ["код за потвърждение", "не споделяйте"]): return "#BG" # Bulgarian
    if any(w in text_lower for w in ["ваш код", "код підтвердження"]): return "#UK" # Ukrainian
    
    # African
    if any(w in text_lower for w in ["msimbo wako", "usishiriki"]): return "#SW" # Swahili
    if any(w in text_lower for w in ["verifikasiekode", "moenie deel nie"]): return "#AF" # Afrikaans
    
    # ৩. উপরের কোনোটি না মিললে ডিফল্ট
    return "#EN"

def parse_chat_id(text):
    text = text.strip()
    if text.startswith("-100") or (text.startswith("-") and text[1:].isdigit()):
        return text
    if "t.me/" in text:
        parts = text.split("/")
        username = parts[-1]
        if username: return "@" + username if not username.startswith("@") else username
    if text.startswith("@"):
        return text
    return "@" + text

def is_admin(user_id):
    return user_id in bot_settings["admins"] or user_id == OWNER_ID

def check_force_join(user_id):
    if not bot_settings["fj_on"] or not bot_settings["fj_channels"]: return True
    if is_admin(user_id): return True
    
    bot_id = int(TOKEN.split(":")[0])
    for ch in bot_settings["fj_channels"]:
        # 🌟 বট ওই চ্যানেলের অ্যাডমিন কিনা তা আগে চেক করবে
        bot_res = api_call("getChatMember", {"chat_id": ch, "user_id": bot_id})
        is_bot_admin = bot_res.get("ok") and bot_res.get("result", {}).get("status") in ["administrator", "creator"]
        
        # 🌟 যদি বট অ্যাডমিন না থাকে, তাহলে ওই চ্যানেলের জন্য ইউজারের জয়েন চেক স্কিপ করবে
        if not is_bot_admin:
            continue
            
        res = api_call("getChatMember", {"chat_id": ch, "user_id": user_id})
        if res.get("ok") and res["result"]["status"] not in ["left", "kicked"]: 
            continue
        else: 
            return False
    return True

def send_force_join_msg(chat_id):
    kb = []
    for ch in bot_settings["fj_channels"]:
        url = f"https://t.me/{ch.replace('@', '')}" if ch.startswith("@") else ch
        kb.append([{"text": f"𝗣𝗟𝗘𝗔𝗦𝗘 𝗝𝗢𝗜𝗡 𝗖𝗛𝗔𝗡𝗡𝗘𝗟", "icon_custom_emoji_id": "5988034234328030415", "url": url, "style": "danger"}])
    kb.append([{"text": "𝗜 𝗛𝗔𝗩𝗘 𝗝𝗢𝗜𝗡𝗘𝗗", "icon_custom_emoji_id": "5987975788413066720", "callback_data": "check_fj", "style": "primary"}])
    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Please join our channels to use the bot!</b>"), reply_markup={"inline_keyboard": kb})

def is_user_banned(user_id):
    if is_admin(user_id): return False
    if user_id in user_banned_cache and time.time() - user_banned_cache[user_id]['time'] < 60:
        return user_banned_cache[user_id]['banned']
    banned = False
    if db:
        try:
            doc = db.collection('users').document(str(user_id)).get()
            banned = doc.exists and doc.to_dict().get("banned", False)
        except: pass
    user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
    return banned

# ==========================================
# Captcha Auto Login & Parsing Core
# ==========================================
def extract_otp_code(text):
    clean_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', str(text))

    # 1. Multi-part OTPs (e.g. 123-456 or 809-761)
    multi_part = re.search(r'(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})', clean_text)
    if multi_part:
        # হাইফেন (-) থাকলে সেটা রেখে দিবে, কিন্তু স্পেস থাকলে মুছে একসাথে করে দিবে
        return multi_part.group(0).replace(" ", "")

    # 2. Keyword-based extraction
    otp_keywords = ['code', 'is', 'otp', 'pin', 'verification', 'auth', 'কোড', 'رمز', 'your code']
    keywords_pattern = '|'.join(otp_keywords)
    keyword_match = re.search(rf'(?:{keywords_pattern})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})', clean_text, re.I)
    if keyword_match and keyword_match.group(1).isdigit():
        return keyword_match.group(1)
        
    keyword_match_rev = re.search(rf'([a-z0-9]{{4,10}})\s*(?:is your|is the|কোড)', clean_text, re.I)
    if keyword_match_rev and keyword_match_rev.group(1).isdigit():
        return keyword_match_rev.group(1)

    # 3. Google OTP
    g_match = re.search(r'G-(\d{6})', clean_text, re.IGNORECASE)
    if g_match: return g_match.group(1)

    # 4. Digit sequences fallback
    digit_matches = re.findall(r'(?<!\d)\d{4,8}(?!\d)', clean_text)
    if digit_matches: return digit_matches[0]

    return None

def get_otp_copy_btn_data(otp, msg_text):
    raw_msg = str(msg_text or "").strip()
    clean_msg = re.sub(r'\s+', ' ', raw_msg)
    if not otp or otp in ("FULL_SMS", "CODE"):
        btn_label = clean_msg if clean_msg else "Copy Message"
        copy_val = raw_msg[:256] if raw_msg else btn_label[:256]
        return btn_label, copy_val
    return str(otp), str(otp)

def parse_panel_response(response_text, p_config=None):
    results = []
    p_type = p_config.get("type", "API Panel") if p_config else "API Panel"
    
    n_col_name = p_config.get("num_col_name", "number").lower() if p_config else "number"
    m_col_name = p_config.get("msg_col_name", "message").lower() if p_config else "message"
    n_idx = int(p_config.get("num_col_idx", 1)) - 1 if p_config and p_config.get("num_col_idx") else 1
    m_idx = int(p_config.get("msg_col_idx", 2)) - 1 if p_config and p_config.get("msg_col_idx") else 2

    if p_type == "Auto Captcha Panel":
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                if not rows: continue
                
                # 🌟 Option 1 + Smart HTML Detection: কলামের নাম ও ব্যবহারকারীর দেওয়া সিরিয়াল দিয়ে সঠিক পজিশন বের করা
                final_n_idx = n_idx
                final_m_idx = m_idx
                
                # প্রথম রো (Header) চেক করে কলামের আসল সিরিয়াল মিলিয়ে নেওয়া
                header_cells = rows[0].find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    c_text = cell.get_text(strip=True).lower()
                    if n_col_name in c_text: final_n_idx = i
                    if m_col_name in c_text: final_m_idx = i

                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    
                    # হেডার রো (যেখানে সব th থাকে) সেগুলো থেকে ডাটা নিবে না
                    if all(c.name == 'th' for c in cols): continue
                    
                    if len(cols) > max(final_n_idx, final_m_idx):
                        # HTML টেবিল থেকে টেক্সট বের করা
                        num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                        msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                        
                        clean_num = re.sub(r'\D', '', num_text)
                        
                        # নাম্বারটা আসলেই ৫-১৮ ডিজিটের কিনা তা নিশ্চিত করা (যাতে উল্টাপাল্টা টেক্সট না আসে)
                        if clean_num and 5 <= len(clean_num) <= 18 and len(msg_text) > 4:
                            otp = extract_otp_code(msg_text) or "FULL_SMS"
                            results.append({"number": clean_num, "message": msg_text, "otp": otp})
        except Exception as e:
            pass
    else:
        try:
            data = json.loads(response_text)
            temp_results = []
            
            def process_item(item):
                pot_nums_list = []
                pot_msg = None
                values = []
                
                if isinstance(item, dict):
                    # ১. প্রথমে পরিচিত JSON Key (যেমন: num, phone, sms) দিয়ে খোঁজার চেষ্টা
                    lower_keys = {str(k).lower(): v for k, v in item.items()}
                    for k in ["number", "num", "phone", "msisdn", "sender"]:
                        if k in lower_keys:
                            clean_val = re.sub(r'\D', '', str(lower_keys[k]))
                            if 5 <= len(clean_val) <= 18:
                                if clean_val not in pot_nums_list: pot_nums_list.append(clean_val)
                    for k in ["message", "msg", "sms", "content", "text"]:
                        if k in lower_keys:
                            val = str(lower_keys[k])
                            if len(val) > 4:
                                pot_msg = val
                                break
                    values = list(item.values())
                elif isinstance(item, list):
                    values = item

                # ২. যদি Key দিয়ে না পাওয়া যায়, তবে Smart Blind Scan (সব ভ্যালু চেক করবে)
                for v in values:
                    if isinstance(v, (dict, list)) or v is None: continue
                    v_str = str(v).strip()
                    
                    # Number Detection: 7 থেকে 18 ডিজিট
                    clean_v = re.sub(r'\D', '', v_str)
                    if 7 <= len(clean_v) <= 18 and not re.search(r'[a-zA-Z]', v_str):
                        # Date/Time/IP এড়ানোর লজিক
                        if not re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', v_str) and not re.search(r'\d{2}:\d{2}:\d{2}', v_str) and "." not in v_str:
                            if clean_v not in pot_nums_list:
                                pot_nums_list.append(clean_v)
                    
                    # Message Detection: 5 অক্ষরের বেশি এবং শুধু সংখ্যা নয়
                    if len(v_str) > 4 and not v_str.isdigit():
                        is_date = bool(re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', v_str) or re.search(r'\d{2}:\d{2}:\d{2}', v_str))
                        if not is_date and (extract_otp_code(v_str) or (" " in v_str and len(v_str) >= 10)):
                            if pot_msg is None or len(v_str) > len(pot_msg):
                                pot_msg = v_str
                                
                # 🌟 ৩. Multiple Numbers Logic (User Priority > Second Number > First Number)
                pot_num = None
                if pot_nums_list:
                    matched_user_num = None
                    for n in pot_nums_list:
                        # চেক করবে ইউজারের অ্যাসাইন করা নাম্বারের তালিকায় এই নাম্বারটি আছে কি না
                        if n in stex_assigned_numbers or any(n in str(key) for key in stex_assigned_numbers.keys()):
                            matched_user_num = n
                            break
                    
                    if matched_user_num:
                        pot_num = matched_user_num
                    elif len(pot_nums_list) >= 2:
                        pot_num = pot_nums_list[1] # ইউজারের কাছে না থাকলে সরাসরি দ্বিতীয় নাম্বারটি নেবে
                    else:
                        pot_num = pot_nums_list[0]
                            
                if pot_num and pot_msg:
                    otp = extract_otp_code(pot_msg) or "FULL_SMS"
                    temp_results.append({"number": pot_num, "message": pot_msg, "otp": otp})
                        
            def traverse_json(node):
                if isinstance(node, list):
                    if len(node) > 0 and not isinstance(node[0], (dict, list)):
                        # It's a flat list representing one record
                        process_item(node)
                    for child in node:
                        if isinstance(child, (dict, list)):
                            traverse_json(child)
                elif isinstance(node, dict):
                    process_item(node)
                    for val in node.values():
                        if isinstance(val, (dict, list)):
                            traverse_json(val)

            traverse_json(data)
            
            # Remove duplicates
            seen = set()
            for r in temp_results:
                uid = f"{r['number']}_{r['otp']}_{r['message'][:30]}"
                if uid not in seen:
                    seen.add(uid)
                    results.append(r)
        except: pass
        
    return results

# 🌟 Advanced Automated Background Captcha Solver & Session Keep-Alive 🌟
def attempt_auto_login(p, idx):
    raw_login_url = p.get("login_url", "").strip()
    if not raw_login_url:
        p["login_status"] = "❌ No login URL"
        return False

    if not raw_login_url.startswith("http"):
        raw_login_url = "http://" + raw_login_url

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })

    # Try original URL first without blindly mangling it
    candidate_urls = [raw_login_url]
    parsed_path = re.sub(r'^https?://[^/]+', '', raw_login_url).strip('/')
    if not parsed_path:
        base_clean = raw_login_url.rstrip('/')
        for sub in ['/login', '/login.php', '/signin', '/admin', '/index.php']:
            if (base_clean + sub) not in candidate_urls:
                candidate_urls.append(base_clean + sub)

    selected_url = None
    soup = None
    form = None
    all_text = ""

    for test_url in candidate_urls:
        try:
            res = session.get(test_url, timeout=15, verify=False)
            test_soup = BeautifulSoup(res.text, 'html.parser')
            # Look for form containing a password field or login field
            test_form = test_soup.find(lambda f: f.name == 'form' and (f.find('input', {'type': 'password'}) or f.find('input', {'name': re.compile(r'pass', re.I)})))
            if not test_form:
                test_form = test_soup.find('form')
            if test_form and (test_form.find('input', {'type': 'password'}) or test_form.find('input', {'name': re.compile(r'user|email|login', re.I)})):
                selected_url = test_url
                soup = test_soup
                form = test_form
                all_text = res.text
                break
        except Exception:
            continue

    if not form:
        p["login_status"] = "❌ No login form found"
        return False

    # 1. SOLVE CAPTCHA ACCURATELY (Exclude dates/years like 2024-2026)
    form_text = form.get_text(separator=" ", strip=True)
    captcha_text = None
    captcha_match = None

    equation_patterns = [
        r'(?:what\s+is|calculate[:\s]*)?\s*(\b\d{1,3}\s*[\+\-\*\/xX]\s*\d{1,3})\s*(?:[=\?:]|$)',
        r'(\b\d{1,3}\s*(?:plus|minus|times|divided|div|\+|\-|\*|\/|x|X)\s*\d{1,3})\s*(?:[=\?:]|\?)',
        r'(\b\d{1,3}\s*[\+\-\*\/]\s*\d{1,3})'
    ]

    for pat in equation_patterns:
        m = re.search(pat, form_text, re.IGNORECASE)
        if m:
            captcha_match = m
            break

    if not captcha_match:
        for el in form.find_all(["label", "div", "span", "p", "strong", "b"]):
            txt = el.get_text(separator=" ", strip=True)
            if any(op in txt for op in ["+", "-", "*", "/", "plus", "minus", "times", "divided"]):
                for pat in equation_patterns:
                    m = re.search(pat, txt, re.IGNORECASE)
                    if m:
                        captcha_match = m
                        break
                if captcha_match:
                    break

    if not captcha_match:
        for pat in equation_patterns:
            m = re.search(pat, all_text, re.IGNORECASE)
            if m:
                sub_nums = re.findall(r'\d+', m.group(1))
                if all(int(sn) < 1900 for sn in sub_nums):
                    captcha_match = m
                    break

    captcha_text = captcha_match.group(1) if captcha_match else "0 + 0"
    answer = "0"
    m2 = re.search(r'(\d+)\s*([\+\-\*\/xX]|plus|minus|times|divided|div)\s*(\d+)', captcha_text, re.IGNORECASE)
    if m2:
        a = int(m2.group(1))
        op = m2.group(2).lower().strip()
        b = int(m2.group(3))
        if op in ('+', 'plus'):
            answer = str(a + b)
        elif op in ('-', 'minus'):
            answer = str(a - b)
        elif op in ('*', 'x', 'times'):
            answer = str(a * b)
        elif op in ('/', 'div', 'divided'):
            answer = str(a // b if b != 0 else 0)

    # 2. RESOLVE ACTION URL
    action = form.get("action")
    post_url = urljoin(selected_url, action) if action else selected_url

    # 3. EXTRACT INPUTS & CSRF TOKENS
    form_data = {}
    for hidden in form.find_all("input", type="hidden"):
        h_name = hidden.get("name")
        if h_name:
            form_data[h_name] = hidden.get("value") or ""

    user_input = form.find("input", {"name": re.compile(r"user|email|login|account|uname|id", re.I)}) or \
                 form.find("input", {"type": "text", "placeholder": re.compile(r"user|email|login", re.I)}) or \
                 form.find("input", {"type": "text"})

    pass_input = form.find("input", {"name": re.compile(r"pass|pwd|secret", re.I)}) or \
                 form.find("input", {"type": "password"})

    captcha_input = form.find("input", {"placeholder": re.compile(r"answer|ans|code|verification|value|captcha|sum", re.I)}) or \
                    form.find("input", {"name": re.compile(r"ans|captcha|ver|code|sum|calc", re.I)})

    user_field = user_input.get("name") if user_input else "username"
    pass_field = pass_input.get("name") if pass_input else "password"
    captcha_field = captcha_input.get("name") if captcha_input else "answer"

    form_data[user_field] = p.get("username", "")
    form_data[pass_field] = p.get("password", "")
    if captcha_field:
        form_data[captcha_field] = answer

    session.headers.update({
        'Referer': selected_url,
        'Origin': '/'.join(selected_url.split('/')[:3]),
        'Content-Type': 'application/x-www-form-urlencoded'
    })

    # 4. SUBMIT FORM
    try:
        login_req = session.post(post_url, data=form_data, allow_redirects=True, timeout=15, verify=False)
        login_resp_text = login_req.text.lower()
    except Exception as e:
        p["login_status"] = f"❌ Request Error: {str(e)[:20]}"
        return False

    # 5. VERIFY LOGIN
    msg_link = p.get("msg_link", "").strip()
    if not msg_link.startswith("http") and msg_link != "":
        msg_link = "http://" + msg_link

    base_domain = '/'.join(selected_url.split('/')[:3])
    check_url = msg_link if msg_link else f"{base_domain}/client/SMSCDRStats"

    check_text = ""
    try:
        check_res = session.get(check_url, timeout=12, verify=False)
        check_text = check_res.text.lower()
    except Exception:
        pass

    success_markers = ['logout', 'sign out', 'dashboard', 'welcome', 'inbox', 'sms reports', 'cdrs', 'smscdrstats', 'balance', 'profile', 'sajaxsource']
    has_marker = any(m in login_resp_text for m in success_markers) or any(m in check_text for m in success_markers)
    has_cookies = len(session.cookies) > 0
    has_no_pass_input = 'type="password"' not in check_text and "type='password'" not in check_text

    is_logged_in = (has_marker or (has_cookies and has_no_pass_input)) and not any(err in login_resp_text for err in ['incorrect password', 'invalid credentials', 'user not found', 'wrong password'])

    if is_logged_in:
        panel_sessions[idx] = session
        p["login_status"] = "✅ Active & Fetching"
        p["last_login_time"] = time.time()
        return True
    else:
        p["login_status"] = f"❌ Login Failed (Math: {captcha_text} = {answer})"
        return False

def panel_monitor_thread():
    global processed_otps, recent_traffic, panel_sessions
    while True:
        try:
            for idx, p in enumerate(bot_settings.get("panels", [])):
                if p.get("status") == "ON":
                    
                    if p.get("type") == "Auto Captcha Panel":
                        sess = panel_sessions.get(idx)
                        now = time.time()
                        
                        # Re-login if not logged in or last login was more than 4 minutes ago (keep-alive)
                        if not sess or (now - p.get("last_login_time", 0) > 240):
                            if now - p.get("last_login_attempt", 0) < 20: 
                                continue 
                            p["last_login_attempt"] = now
                            
                            success = attempt_auto_login(p, idx)
                            save_db() # Save login status text to show in settings
                            if not success:
                                continue 
                            sess = panel_sessions.get(idx)
                            
                        try:
                            # 🌟 auto sessions with sAjaxSource and Fallback HTML Parser
                            parsed_data, res_text = fetch_cpt_panel_cdrs(p, sess, p["msg_link"])
                            p["login_status"] = "✅ Active & Fetching"
                        except Exception as e:
                            if "session expired" in str(e).lower():
                                p["login_status"] = "🔄 Re-logging in..."
                                panel_sessions.pop(idx, None)
                                p["last_login_attempt"] = now
                                re_ok = attempt_auto_login(p, idx)
                                if re_ok:
                                    sess = panel_sessions.get(idx)
                                    try:
                                        parsed_data, res_text = fetch_cpt_panel_cdrs(p, sess, p["msg_link"])
                                        p["login_status"] = "✅ Active & Fetching"
                                    except Exception:
                                        p["login_status"] = "✅ Active & Fetching"
                                save_db()
                            else:
                                p["login_status"] = f"⚠️ Fetch Notice: {str(e)[:25]}"
                            continue

                    elif p.get("api_url") or p.get("full_api_url"): 
                        full_url = p.get("full_api_url", "").strip()
                        url = p.get("api_url", "").strip()
                        token = p.get("token", "").strip()
                        if not full_url and not url: continue
                        
                        urls_to_try = []
                        if full_url:
                            urls_to_try.append(full_url)
                        else:
                            if "{token}" in url or "{key}" in url:
                                urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                            elif "token=" in url or "key=" in url:
                                urls_to_try.append(url)
                            else:
                                sep = '&' if '?' in url else '?'
                                urls_to_try.append(f"{url}{sep}token={token}")
                                urls_to_try.append(f"{url}{sep}key={token}&start=0")
                                urls_to_try.append(f"{url}{sep}key={token}")
                            
                        parsed_data = []
                        # 🌟 Browser Bypass (403 Forbidden Fix)
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                        for try_url in urls_to_try:
                            try:
                                res = requests.get(try_url, headers=headers, timeout=10)
                                parsed_data = parse_panel_response(res.text, p)
                                if parsed_data:
                                    if not full_url and try_url != url and token:
                                        p["api_url"] = try_url.replace(token, "{token}")
                                        save_db()
                                    break
                            except: continue
                        if not parsed_data: continue
                    else:
                        continue
                    
                    if p.get("type") != "Auto Captcha Panel":
                        limit = p.get("records", 0)
                        if limit > 0: parsed_data = parsed_data[:limit]
                        
                    for item in parsed_data:
                        num = item["number"]
                        otp = item["otp"]
                        msg_text = item["message"]
                        unique_id = f"{num}_{otp}_{msg_text.strip()}" if otp in ("FULL_SMS", "CODE") else f"{num}_{otp}"
                        
                        if unique_id not in processed_otps:
                            processed_otps.add(unique_id)
                            if len(processed_otps) > 5000: processed_otps.clear()
                                 
                            char, iso = get_flag_and_code(num)
                            app_full_name, prem_app_html = get_service_info_html(p.get("name", "Panel"), msg_text)
                            current_time = time.time()
                            
                            recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": num,
                                "time": current_time
                            })
                            # 🌟 শুধু লোকাল ফাইলে সেভ করবে, Firestore এ অহেতুক Write করবে না!
                            save_local_db()
                                 
                            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                            masked = mask_number(display_num)
                            lang = detect_language(msg_text)
                            
                            lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                            styled_masked = str(masked).replace("DXA", "•DXA•")
                            display_msg = render_body_text(f"━━━━━━━━━━━━━━━\n<blockquote>{prem_app_html} {str(app_full_name).upper()} ➜ 💬 {str(lang_name).upper()}</blockquote>\n<blockquote>『 {get_flag_info_html(display_num)} {iso} ➜ {styled_masked} 』</blockquote>\n━━━━━━━━━━━━━━━")
                            
                            btn_label, copy_val = get_otp_copy_btn_data(otp, msg_text)
                            
                            for fw in bot_settings.get("fw_groups", []):
                                emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
                                srv_emoji_id = emj_match.group(1) if emj_match else "5296369303661067030"
                                
                                styles = ["primary", "success", "danger"]
                                chan_link = bot_settings.get("otp_channel_link", "https://t.me/DXA_ZONE")
                                
                                kb = [
                                    [
                                        {"text": "𝗖𝗛𝗔𝗡𝗡𝗘𝗟", "icon_custom_emoji_id": "5987629038523392103", "url": chan_link, "style": "primary"},
                                        {"text": f"{btn_label}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": copy_val}, "style": "success"}
                                    ]
                                ]
                                
                                # 🌟 Auto GET NUMBER Button for OTP Group
                                clean_srv = re.sub(r'[^a-zA-Z0-9]', '', app_full_name)
                                dl_link = f"https://t.me/{BOT_USERNAME}?start=local_{str(num)[:5]}_{clean_srv}"
                                kb.append([{"text": "𝗚𝗘𝗧 𝗦𝗔𝗠𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", "icon_custom_emoji_id": "5291997181572570361", "url": dl_link, "style": "danger"}])
                                
                                temp_row = []
                                for i, btn in enumerate(fw.get("buttons", [])):
                                    b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[(i + 1) % 3]}
                                    if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                    temp_row.append(b_obj)
                                    if len(temp_row) == 2:
                                        kb.append(temp_row)
                                        temp_row = []
                                if temp_row: kb.append(temp_row)
                                send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                            
                            owners = []
                            clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                            
                            # 🌟 ALGORITHM FIX: সরাসরি Active Sessions থেকে মালিক খোঁজা 
                            # (কারণ Local Stock থেকে নাম্বার Assign হওয়ার সাথে সাথে ডিলিট হয়ে যায়)
                            for uid, session_data in user_active_sessions.items():
                                for act_num in session_data.get("nums", []):
                                    act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                        owners.append(uid)
                                        break
                                        
                            # ব্যাকআপ হিসেবে StexSMS-তে চেক করা 
                            if not owners:
                                for stex_n, n_owner in stex_assigned_numbers.items():
                                    clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                        owners.append(n_owner)
                                        
                            owners = list(set(owners)) 
                            for owner_id in owners:
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                
                                # রিওয়ার্ড যোগ করার লজিক (আপলোড করা ফাইলের রেট থাকলে সেটি, না থাকলে ডিফল্ট রেট)
                                reward = get_number_reward_rate(num, owner_id)
                                if reward > 0:
                                    update_balance(owner_id, reward)
                                    
                                emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
                                srv_emoji_id = emj_match.group(1) if emj_match else "5870972873450984431"
                                
                                inbox_msg_text = f" {get_flag_info_html(display_num)} <code>{display_num}</code>\n➕  {reward} 𝗧𝗞"
                                inbox_msg = render_body_text(inbox_msg_text)
                                
                                inbox_kb = [[{"text": f"{btn_label}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": copy_val}, "style": "success"}]]
                                
                                send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                increment_user_otp(owner_id)
        except Exception as e:
            pass
        time.sleep(5) 

# ==========================================
# Firebase User Management
# ==========================================
# 🌟 Local User Cache: বারবার Firestore থেকে Read করা বন্ধ করবে!
user_cache = {}

def get_user(user_id):
    uid = int(user_id)
    if uid in user_cache: return user_cache[uid]
    if not db: 
        new_user = {"user_id": uid, "balance": 0.0, "total_refers": 0, "total_otps": 0, "referral_otps": 0, "total_ws_added": 0, "banned": False, "verified": False}
        user_cache[uid] = new_user
        return new_user
    
    try:
        doc_ref = db.collection('users').document(str(uid))
        doc = doc_ref.get()
        if doc.exists: 
            data = doc.to_dict()
            if "total_otps" not in data: data["total_otps"] = 0
            if "referral_otps" not in data: data["referral_otps"] = 0
            if "total_ws_added" not in data: data["total_ws_added"] = 0
            if "banned" not in data: data["banned"] = False
            if "verified" not in data: data["verified"] = False
            user_cache[uid] = data
            return data
        else:
            new_user = {"user_id": uid, "balance": 0.0, "total_refers": 0, "total_otps": 0, "referral_otps": 0, "total_ws_added": 0, "banned": False, "verified": False}
            doc_ref.set(new_user)
            user_cache[uid] = new_user
            return new_user
    except Exception as e:
        # ফায়ারবেস কানেকশন ফেইল করলে লোকাল ডাটা দিয়ে ইউজারকে রেসপন্স পাঠাবে
        new_user = {"user_id": uid, "balance": 0.0, "total_refers": 0, "total_otps": 0, "referral_otps": 0, "total_ws_added": 0, "banned": False, "verified": False}
        user_cache[uid] = new_user
        return new_user

def update_balance(user_id, amount):
    uid = int(user_id)
    if uid not in user_cache:
        get_user(uid)
        
    user_cache[uid]["balance"] = round(user_cache[uid].get("balance", 0.0) + float(amount), 2)
    
    if not db: return
    try:
        doc_ref = db.collection('users').document(str(uid))
        doc_ref.set({"user_id": uid, "balance": firestore.Increment(float(amount))}, merge=True)
    except: pass

def increment_user_otp(user_id):
    uid = int(user_id)
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if uid not in user_cache: 
        get_user(uid)
        
    # ১. লোকাল ক্যাশে 'আজকের ওটিপি' আপডেট (Today's OTP)
    if user_cache[uid].get("last_otp_date") == today_str:
        user_cache[uid]["today_otps"] = user_cache[uid].get("today_otps", 0) + 1
    else:
        user_cache[uid]["today_otps"] = 1
        user_cache[uid]["last_otp_date"] = today_str
        
    # ২. লোকাল ক্যাশে ইউজারের নিজস্ব 'টোটাল ওটিপি' আপডেট (Total OTP)
    user_cache[uid]["total_otps"] = user_cache[uid].get("total_otps", 0) + 1
    
    # ৩. ফায়ারবেসে ইউজারের নিজস্ব 'টোটাল ওটিপি' আপডেট
    if db:
        try:
            db.collection('users').document(str(uid)).update({"total_otps": firestore.Increment(1)})
        except: pass

    # ৪. যদি এই ইউজার কারো রেফারে এসে থাকে, তাহলে রেফারকারীর 'referral_otps' আলাদাভাবে বাড়বে (total_otps বাড়বে না)
    inviter_id = user_cache[uid].get("referred_by")
    if inviter_id:
        try:
            inv_uid = int(inviter_id)
            if inv_uid != uid:
                if inv_uid not in user_cache:
                    get_user(inv_uid)
                user_cache[inv_uid]["referral_otps"] = user_cache[inv_uid].get("referral_otps", 0) + 1
                if db:
                    db.collection('users').document(str(inv_uid)).set({"referral_otps": firestore.Increment(1)}, merge=True)
        except: pass

def add_referral(inviter_id, new_user_id):
    if not db.collection('users').document(str(new_user_id)).get().exists:
        get_user(new_user_id) 
        reward = bot_settings.get("refer_reward", 0.2)
        update_balance(inviter_id, reward)
        db.collection('users').document(str(inviter_id)).update({"total_refers": firestore.Increment(1)})
        if inviter_id in user_cache:
            user_cache[inviter_id]["total_refers"] = user_cache[inviter_id].get("total_refers", 0) + 1
        
        # আপনার দেওয়া নতুন ডিজাইন
        ref_msg = (
            f"{PEM['gift']} <b>New Referral !</b>\n"
            f"------------------\n"
            f"🔥 <b>You Received {reward} TK</b>\n"
            f"------------------\n"
            f"{PEM['user']} <b>From User ID:</b> <code>{new_user_id}</code>"
        )
        send_message(inviter_id, render_body_text(ref_msg))

# ==========================================
# UI Keyboards & Menu Builders
# ==========================================
def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}

def main_menu(user_id):
    kb = [
        [
            {"text": "GET NUMBER", "icon_custom_emoji_id": "6005646495049587822", "style": "success"},
            {"text": "SET CHECKER", "icon_custom_emoji_id": "6005926741665653312", "style": "success"}
        ],
        [
            {"text": "MY INFO", "icon_custom_emoji_id": "5987716265014206147", "style": "primary"}, 
            {"text": "TRAFFIC", "icon_custom_emoji_id": "5987664755471425123", "style": "primary"}
        ],
        [
            {"text": "GET 2FA", "icon_custom_emoji_id": "5267421176841398765", "style": "danger"},
            {"text": "LEADERBOARD", "icon_custom_emoji_id": "5987610583048919551", "style": "danger"}
        ]
    ]
    if is_admin(user_id): 
        kb.append([{"text": "ADMIN PANEL", "icon_custom_emoji_id": "5420155432272438703", "style": "danger"}])
    return {"keyboard": kb, "resize_keyboard": True}

def get_admin_text():
    users_count = len(all_known_users) # 🌟 Zero Cost User Count!
    total_files = len(number_batches)
    available_nums = sum(len(b["numbers"]) for b in number_batches.values())

    txt = f"""
{PEM['admin']} <b>ADMIN CONTROL PANEL</b> {PEM['admin']}
━━━━━━━━━━━━━━━

{PEM['graph']} <b>DATABASE OVERVIEW</b>
— — — — — — — — — —
{PEM['user']} Users      » {users_count}
{PEM['file']} Files      » {total_files}
{PEM['num']} Numbers    » {total_uploaded_stats}
{PEM['ok']} Assigned   » {total_assigned_stats}
{PEM['rocket']} Available  » {available_nums}

{PEM['graph']} <b>STOCK LEVEL</b>
— — — — — — — — — —
[██████░░░░░░░░░] {available_nums} free
"""
    return render_body_text(txt)

def admin_panel_keyboard():
    return {"inline_keyboard": [
        [{"text": "MANAGE WS CHECKER", "icon_custom_emoji_id": "5985444815725142458", "callback_data": "manage_ws_tg_checker", "style": "primary"}],
        [{"text": "LEADER BOARD SYSTEM", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "lb_main", "style": "success"}],
        [{"text": "Upload Number", "icon_custom_emoji_id": "5445355530111437729", "callback_data": "upload_num", "style": "primary"},
         {"text": "Delete files", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "delete_files", "style": "danger"}],
        [{"text": "Broadcast", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "broadcast_msg", "style": "success"},
         {"text": "System", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "system_settings", "style": "primary"}],
        [{"text": "Used number", "icon_custom_emoji_id": "5987557149360792425", "callback_data": "show_used", "style": "danger"},
         {"text": "Unused number", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "show_unused", "style": "success"}],
        [{"text": "Upload FIREBASE", "icon_custom_emoji_id": "5352721946054268944", "callback_data": "upload_firebase", "style": "primary"}]
    ]}

def manage_checker_keyboard():
    return {"inline_keyboard": [
        [{"text": "WS CHECKER", "icon_custom_emoji_id": "5987961773934780806", "callback_data": "ws_checker_menu", "style": "success"}],
        [{"text": "MANAGE API KEY", "icon_custom_emoji_id": "5197288647275071607", "callback_data": "manage_api_key_menu", "style": "danger"}],
        [{"text": "BUY MASTER API KEY", "icon_custom_emoji_id": "5312361253610475399", "url": "https://t.me/WhatsappChecker_Tgbot", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def manage_api_key_keyboard():
    return {"inline_keyboard": [
        [{"text": "SET API KEY", "icon_custom_emoji_id": "5197288647275071607", "callback_data": "set_master_api_key", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_ws_tg_checker", "style": "danger"}]
    ]}

def checker_settings_keyboard(c_type):
    status_key = f"{c_type}_checker_on"
    is_on = bot_settings.get(status_key, False)
    
    srv_list = bot_settings.get(f"{c_type}_checker_services", [])
    if not isinstance(srv_list, list): srv_list = []
        
    file_list = bot_settings.get(f"{c_type}_checker_files", [])
    if not isinstance(file_list, list): file_list = []
    
    status_text = "STATUS ON" if is_on else "STATUS OFF"
    status_icon = "5987557149360792425" if is_on else "5420130255174145507"
    status_style = "success" if is_on else "danger"
    
    kb = [
        [{"text": status_text, "icon_custom_emoji_id": status_icon, "callback_data": f"toggle_{c_type}", "style": status_style}],
        [{"text": "SELECT SERVICE", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"sel_srv_{c_type}", "style": "primary"}],
        [{"text": "SELECT FILE", "icon_custom_emoji_id": "5352721946054268944", "callback_data": f"sel_file_{c_type}", "style": "primary"}],
    ]
    
    apps_db = bot_settings.get("premium_apps", {})
    # দেখাচ্ছে সার্ভিস লিস্ট
    for srv in srv_list:
        emoji_id = "5192739271886282680" 
        for app_key, app_data in apps_db.items():
            if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                if "id" in app_data: emoji_id = app_data["id"]; break
        kb.append([{"text": f"Delete {srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"c_del_s_{c_type}_{srv}", "style": "danger"}])
        
    # দেখাচ্ছে ফাইল লিস্ট
    for f_id in file_list:
        f_name = number_batches.get(f_id, {}).get("filename", f"Unknown ({f_id})")
        kb.append([{"text": f"Delete {f_name}", "icon_custom_emoji_id": "5352721946054268944", "callback_data": f"c_del_f_{c_type}_{f_id}", "style": "danger"}])
        
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_ws_tg_checker", "style": "danger"}])
    return {"inline_keyboard": kb}

def system_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "𝗦𝗧𝗘𝗫-𝗦𝗠𝗦", "icon_custom_emoji_id": "5877466056548691003", "callback_data": "stex_control", "style": "success"},
         {"text": "𝗩𝗢𝗟𝗧𝗫-𝗦𝗠𝗦", "icon_custom_emoji_id": "5987965205613648891", "callback_data": "voltx_control", "style": "success"}],
        [{"text": "𝗭𝗘𝗡𝗘𝗫-𝗦𝗠𝗦", "icon_custom_emoji_id": "6095712582016967568", "callback_data": "zenex_control", "style": "success"},
         {"text": "𝗠𝗜𝗡𝗢-𝗦𝗠𝗦", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "mino_control", "style": "success"}],
        [{"text": "𝗙𝗢𝗥𝗖𝗘 𝗝𝗢𝗜𝗡", "icon_custom_emoji_id": "5987840685921803178", "callback_data": "manage_fj", "style": "primary"},
         {"text": "𝗠𝗔𝗡𝗔𝗚𝗘 𝗔𝗗𝗠𝗜𝗡", "icon_custom_emoji_id": "5987764785259749210", "callback_data": "manage_admins", "style": "primary"}],
        [{"text": "𝗢𝗧𝗣 𝗚𝗥𝗢𝗨𝗣", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "primary"},
         {"text": "𝗠𝗔𝗡𝗔𝗚𝗘 𝗨𝗦𝗘𝗥", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}], 
        [{"text": "𝗣𝗔𝗡𝗘𝗟 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "manage_panels", "style": "success"},
         {"text": "𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗘𝗠𝗢𝗝𝗜", "icon_custom_emoji_id": "5996735464407571979", "callback_data": "manage_emojis", "style": "primary"}],
        [{"text": "𝗗𝗫𝗔 𝗖𝗢𝗡𝗧𝗥𝗢𝗟", "icon_custom_emoji_id": "5985444815725142458", "callback_data": "dxa_control", "style": "primary"},
         {"text": "𝗧𝗘𝗦𝗧", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}], 
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def get_user_management_text():
    # 🌟 Fast & Free User Management Stats!
    total = len(all_known_users)
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt = f"""➖➖➖➖➖➖➖➖
《 👋 USER VIEW 》
➖➖➖➖➖➖➖➖
📊 LIVE STATISTICS:
➖➖➖➖➖➖➖➖
🫂 TOTAL USERS: {total}
✅ VERIFIED USERS: (Hidden to save DB Cost)
🚫 BANNED USERS: (Hidden to save DB Cost)
➖➖➖➖➖➖➖➖
⌛ UPDATED: {now_str}"""
    return render_body_text(txt)

def user_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "Manage Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "um_manage_balance", "style": "primary"},
         {"text": "Ban/Unban User", "icon_custom_emoji_id": "5240241223632954241", "callback_data": "um_ban_unban", "style": "danger"}],
        [{"text": "User Profile", "icon_custom_emoji_id": "5987786010988125765", "callback_data": "um_user_profile", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_design_list_keyboard():
    return {"inline_keyboard": [
        [{"text": "Edit /start Menu", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "md_edit_start", "style": "primary"}],
        [{"text": "Edit 𝗚𝗘𝗧 𝗡𝗨𝗠𝗕𝗘𝗥", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "md_edit_get_number", "style": "success"}],
        [{"text": "Edit Select Country", "icon_custom_emoji_id": "5987629038523392103", "callback_data": "md_edit_select_country", "style": "primary"}],
        [{"text": "Edit 𝗧𝗥𝗔𝗙𝗙𝗜𝗖", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "md_edit_traffic", "style": "primary"},
         {"text": "Edit 𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "md_edit_refer", "style": "primary"}],
        [{"text": "Edit 𝗠𝗬 𝗜𝗡𝗙𝗢", "icon_custom_emoji_id": "5987716265014206147", "callback_data": "md_edit_withdrawal", "style": "danger"}],
        [{"text": "Reset Defaults", "icon_custom_emoji_id": "5192812028632274956", "callback_data": "md_reset_defaults", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def menu_edit_options_keyboard(menu_key):
    return {"inline_keyboard": [
        [{"text": "Edit Body (Text)", "icon_custom_emoji_id": "5395444784611480792", "callback_data": f"md_text_{menu_key}", "style": "primary"}],
        [{"text": "Edit Inline Buttons", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"md_btns_{menu_key}", "style": "success"}],
        [{"text": "Back to Menus", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "menu_design_list", "style": "danger"}]
    ]}

def menu_buttons_list_keyboard(menu_key):
    kb = []
    btns = bot_settings["custom_messages"].get(menu_key, {}).get("buttons", [])
    for idx, btn in enumerate(btns):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"md_delbtn_{menu_key}_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5987751449386296261", "callback_data": f"md_addbtn_{menu_key}", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{menu_key}", "style": "primary"}])
    return {"inline_keyboard": kb}

def emoji_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "UPLOAD FLAG", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_flags_txt", "style": "primary"},
         {"text": "Download Flags", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_flags_txt", "style": "success"}],
        [{"text": "UPLOAD SERVICE", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_apps_txt", "style": "primary"},
         {"text": "Download Services", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_apps_txt", "style": "success"}],
        [{"text": "Delete All Flags", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "del_all_flags", "style": "danger"},
         {"text": "ADD SINGLE EMOJI", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_single_emoji", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def generate_emoji_txt(mode):
    lines = []
    if mode == "flags":
        for code, data in bot_settings.get("premium_flags", {}).items():
            char = data.get("char", "")
            iso = data.get("iso", "")
            name = data.get("name", "")
            eid = data.get("id", "")
            lines.append(f'({code})({iso}){char} {name} {{"emoji": "{char}", "id": "{eid}"}}')
    else:
        for key, data in bot_settings.get("premium_apps", {}).items():
            char = data.get("char", "")
            name = data.get("name", key)
            eid = data.get("id", "")
            lines.append(f'{char} {name} {{"emoji": "{char}", "id": "{eid}"}}')
    return "\n".join(lines)

def fj_settings_keyboard():
    status_text = 'ON' if bot_settings['fj_on'] else 'OFF'
    status_icon = "5987557149360792425" if bot_settings['fj_on'] else "5318840353510408444"
    kb = [[{"text": f"STATUS: {status_text}", "icon_custom_emoji_id": status_icon, "callback_data": "toggle_fj", "style": "primary"}]]
    for idx, ch in enumerate(bot_settings["fj_channels"]):
        kb.append([{"text": f"Delete: {ch}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fj_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Channel", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_fj", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def admin_settings_keyboard():
    kb = []
    for idx, adm in enumerate(bot_settings["admins"]):
        text_btn = f"Owner: {adm}" if adm == OWNER_ID else f"Delete: {adm}"
        icon_id = "5353032893096567467" if adm == OWNER_ID else "5420130255174145507"
        cb_data = "ignore" if adm == OWNER_ID else f"del_adm_{idx}"
        kb.append([{"text": text_btn, "icon_custom_emoji_id": icon_id, "callback_data": cb_data, "style": "danger" if adm != OWNER_ID else "primary"}])
    kb.append([{"text": "Add Admin", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_adm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def otp_groups_list_keyboard():
    kb = [
        [{"text": "Edit OTP Button Link", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"}],
        [{"text": f"{bot_settings.get('otp_link', 'Not Set')[:25]}...", "icon_custom_emoji_id": "5420517437885943844", "url": bot_settings.get("otp_link", "https://t.me/"), "style": "primary"}],
        [{"text": "Edit Channel Link", "icon_custom_emoji_id": "5296278125800368800", "callback_data": "edit_channel_link", "style": "success"}],
        [{"text": f"{bot_settings.get('otp_channel_link', 'Not Set')[:25]}...", "icon_custom_emoji_id": "5296278125800368800", "url": bot_settings.get("otp_channel_link", "https://t.me/"), "style": "success"}]
    ]
    for idx, fg in enumerate(bot_settings["fw_groups"]):
        kb.append([{"text": f"Group: {fg['chat_id']}", "icon_custom_emoji_id": "5193063022226086560", "callback_data": f"manage_fw_{idx}", "style": "primary"}])
    kb.append([{"text": "Set Forward Group", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_fw", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}

def stex_control_keyboard():
    auto_status = "ON" if bot_settings.get("stex_auto", False) else "OFF"
    auto_emoji = "5987557149360792425" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add StexSMS Key", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_stex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_stex_keys", "style": "danger"}],
        [{"text": "Manage StexSMS Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_stex_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_stex_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5987629038523392103", "callback_data": "stex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def zenex_control_keyboard():
    auto_status = "ON" if bot_settings.get("zenex_auto", False) else "OFF"
    auto_emoji = "5987557149360792425" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Zenex Key", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_zenex_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_zenex_keys", "style": "danger"}],
        [{"text": "Manage Zenex Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_zenex_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_zenex_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5987629038523392103", "callback_data": "zenex_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def mino_control_keyboard():
    auto_status = "ON" if bot_settings.get("mino_auto", False) else "OFF"
    auto_emoji = "5987557149360792425" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Mino Key", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_mino_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_mino_keys", "style": "danger"}],
        [{"text": "Manage Mino Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_mino_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_mino_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5987629038523392103", "callback_data": "mino_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def voltx_control_keyboard():
    auto_status = "ON" if bot_settings.get("voltx_auto", False) else "OFF"
    auto_emoji = "5987557149360792425" if auto_status == "ON" else "5420130255174145507"
    return {"inline_keyboard": [
        [{"text": "Add Voltx Key", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_voltx_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_voltx_keys", "style": "danger"}],
        [{"text": "Manage Voltx Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_voltx_srv", "style": "success"}],
        [{"text": f"Auto Range: {auto_status}", "icon_custom_emoji_id": auto_emoji, "callback_data": "toggle_voltx_auto", "style": "primary"},
         {"text": "Search Country", "icon_custom_emoji_id": "5987629038523392103", "callback_data": "voltx_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def specific_fw_group_keyboard(idx):
    group = bot_settings["fw_groups"][idx]
    kb = []
    for b_idx, btn in enumerate(group.get("buttons", [])):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fwbtn_{idx}_{b_idx}", "style": "danger"}])
    
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5987751449386296261", "callback_data": f"add_fwbtn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Entire Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_fw_{idx}", "style": "danger"}])
    kb.append([{"text": "Back to Groups", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "primary"}])
    return {"inline_keyboard": kb}

def dxa_control_keyboard():
    w_status = "ON" if bot_settings["withdraw_on"] else "OFF"
    grp_status = "ON" if bot_settings.get("w_group") else "OFF"
    return {"inline_keyboard": [
        [{"text": f"WITHDRAW: {w_status}", "icon_custom_emoji_id": "5987641605597699007", "callback_data": "dxa_toggle_w", "style": "primary"}],
        [{"text": f"MIN WITHDRAW: {bot_settings['min_withdraw']}", "icon_custom_emoji_id": "5987664755471425123", "callback_data": "dxa_min_w", "style": "success"},
         {"text": f"OTP REWARD: {bot_settings['otp_reward']}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "dxa_otp_r", "style": "primary"}],
        [{"text": f"REFER REWARD: {bot_settings['refer_reward']}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "dxa_ref_r", "style": "success"},
         {"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "dxa_cool", "style": "primary"}],
        [{"text": f"NUM/REQ: {bot_settings['num_req']}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "dxa_num_req", "style": "success"},
         {"text": "W. METHODS", "icon_custom_emoji_id": "5988050370520161591", "callback_data": "manage_w_methods", "style": "primary"}],
        [{"text": f"W. GROUP: {grp_status}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "dxa_w_group", "style": "success"},
         {"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def dxa_otp_reward_keyboard():
    return {"inline_keyboard": [
        [{"text": f"DEFAULT RATE ({bot_settings['otp_reward']} TK)", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "dxa_default_rate", "style": "primary"}],
        [{"text": "FILE RATE", "icon_custom_emoji_id": "5352721946054268944", "callback_data": "dxa_file_rate_menu", "style": "success"}],
        [{"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "danger"}]
    ]}

def dxa_file_rate_list_keyboard():
    kb = []
    for b_id, b_data in number_batches.items():
        f_name = b_data.get("filename", b_id)
        srv = b_data.get("service", "")
        cur_rate = b_data.get("rate", bot_settings.get("otp_reward", 0.0))
        kb.append([{"text": f"{f_name} ({srv} - {cur_rate} TK)", "icon_custom_emoji_id": "5352721946054268944", "callback_data": f"dxa_set_fr_{b_id}", "style": "primary"}])
    kb.append([{"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_otp_r", "style": "danger"}])
    return {"inline_keyboard": kb}

def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        kb.append([{"text": f"Delete: {m}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "primary"}])
    return {"inline_keyboard": kb}

def typed_panels_list_keyboard(p_type):
    kb = []
    for idx, p in enumerate(bot_settings["panels"]):
        if p.get("type", "API Panel") != p_type: continue
        action_text = f"Turn OFF {p['name']}" if p['status'] == 'ON' else f"Turn ON {p['name']}"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        icon_id = "5420155432272438703" 
        kb.append([
            {"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"},
            {"text": f"{p['name']}", "icon_custom_emoji_id": icon_id, "callback_data": f"conf_pnl_{idx}", "style": "primary"}
        ])
    add_cb = "add_api_panel" if p_type == "API Panel" else "add_cpt_panel"
    kb.append([{"text": "Add New Provider", "icon_custom_emoji_id": "5987751449386296261", "callback_data": add_cb, "style": "success"}])
    kb.append([{"text": "Delete Provider", "icon_custom_emoji_id": "5336944168944047463", "callback_data": f"list_del_{'api' if p_type=='API Panel' else 'cpt'}", "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
    return {"inline_keyboard": kb}

def render_panel_config_text(p):
    if p.get("type") == "Auto Captcha Panel":
        return f"{PEM.get('gear', '⚙️')} <b>Configure {p['name']}</b>\n\n" \
               f"<b>Type:</b> {p['type']}\n" \
               f"<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n" \
               f"<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n\n" \
               f"{PEM.get('link', '🔗')} <b>Login Link:</b> <code>{p.get('login_url', 'None')}</code>\n" \
               f"{PEM.get('msg', '💬')} <b>Message Link:</b> <code>{p.get('msg_link', 'None')}</code>\n" \
               f"{PEM.get('user', '👤')} <b>Username:</b> <code>{p.get('username', 'None')}</code>\n" \
               f"{PEM.get('lock', '🔒')} <b>Password:</b> <code>{p.get('password', 'None')}</code>\n" \
               f"{PEM.get('phone', '📱')} <b>Num Col Name:</b> <code>{p.get('num_col_name', 'number')}</code> (Serial: <code>{p.get('num_col_idx', 1)}</code>)\n" \
               f"{PEM.get('msg', '💬')} <b>OTP Col Name:</b> <code>{p.get('msg_col_name', 'message')}</code> (Serial: <code>{p.get('msg_col_idx', 2)}</code>)"
    else:
        return f"{PEM.get('gear', '⚙️')} <b>Configure {p['name']}</b>\n\n" \
               f"<b>Type:</b> {p['type']}\n" \
               f"<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n" \
               f"{PEM.get('world', '🌐')} <b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n" \
               f"{PEM.get('lock', '🔑')} <b>Token:</b> <code>{p.get('token', 'None')}</code>\n" \
               f"{PEM.get('link', '🔗')} <b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"

def panel_config_keyboard(idx):
    p = bot_settings["panels"][idx]
    
    kb = []
    action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
    
    if p["type"] != "Auto Captcha Panel":
        rec_count_text = "All (Unlimited)" if p.get('records', 0) == 0 else str(p.get('records'))
        kb.append([{"text": "Set API URL", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_api_{idx}", "style": "primary"}])
        kb.append([{"text": "Set Token", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"set_p_tok_{idx}", "style": "primary"}])
        kb.append([{"text": "Full API (URL+Token)", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_fapi_{idx}", "style": "primary"}])
        kb.append([{"text": f"Set Records Count: {rec_count_text}", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"set_p_rec_{idx}", "style": "primary"}])
    else:
        kb.append([
            {"text": "EDIT LOGIN LINK", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"edit_cp_lurl_{idx}", "style": "primary"}
        ])
        kb.append([
            {"text": "EDIT USER", "icon_custom_emoji_id": "5987786010988125765", "callback_data": f"edit_cp_user_{idx}", "style": "primary"},
            {"text": "EDIT PASS", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"edit_cp_pass_{idx}", "style": "primary"}
        ])
        kb.append([
            {"text": "EDIT MESSAGE LINK", "icon_custom_emoji_id": "5337302974806922068", "callback_data": f"edit_cp_mlink_{idx}", "style": "primary"}
        ])
        kb.append([
            {"text": "NUM NAME", "icon_custom_emoji_id": "5337132498965010628", "callback_data": f"edit_cp_nname_{idx}", "style": "primary"},
            {"text": "NUM SERIAL", "icon_custom_emoji_id": "5303214794336125778", "callback_data": f"edit_cp_nidx_{idx}", "style": "primary"}
        ])
        kb.append([
            {"text": "OTP NAME", "icon_custom_emoji_id": "5337302974806922068", "callback_data": f"edit_cp_mname_{idx}", "style": "primary"},
            {"text": "OTP SERIAL", "icon_custom_emoji_id": "5303214794336125778", "callback_data": f"edit_cp_midx_{idx}", "style": "primary"}
        ])

    kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5987557149360792425", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
        
    back_data = "manage_api_panels" if p.get("type", "API Panel") == "API Panel" else "manage_cpt_panels"
    kb.append([{"text": "Back to Providers", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_data, "style": "danger"}])
    return {"inline_keyboard": kb}

def build_traffic_ui():
    global recent_traffic
    current_time = time.time()
    # ১৫ মিনিটের ট্রাফিক নেওয়ার জন্য 900 (১৫ মিনিট) করে দেওয়া হলো
    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 900]
    
    stats = {}
    total_otps_all = 0
    for t in recent_traffic:
        raw_srv = str(t.get("service", "Unknown"))
        app_full_name, prem_app_html = get_service_info_html(raw_srv)
        
        # 🌟 ছোট-বড় হাতের অক্ষরের কারণে ডাবল হওয়া আটকাতে .upper() ব্যবহার করা হলো
        srv_key = str(app_full_name).upper()
        
        if srv_key not in stats:
            stats[srv_key] = {"count": 0, "html": prem_app_html, "raw_name": raw_srv}
        stats[srv_key]["count"] += 1
        total_otps_all += 1
        
    txt = "<blockquote>📊 15 MINUTE LIVE TRAFFIC</blockquote>\n━━━━━━━━━━━━━━━\n"
    
    kb = []
    if not stats:
        txt += "<blockquote><i>No recent traffic found in the last 15 minutes...</i></blockquote>\n━━━━━━━━━━━━━━━\n"
    else:
        srv_totals = sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)
        
        lines = []
        for srv_key, data in srv_totals:
            lines.append(f"<blockquote>{data['html']} {srv_key} ➜ 🔥 {data['count']} OTP</blockquote>")
            
        txt += "\n— — — — — — — — — — — —\n".join(lines)
        txt += f"\n━━━━━━━━━━━━━━━\n<blockquote>📊 TOTAL ➜ 🔥 {total_otps_all} OTP</blockquote>\n━━━━━━━━━━━━━━━\n"

def build_traffic_ui():
    global recent_traffic
    current_time = time.time()
    # ১৫ মিনিটের ট্রাফিক নেওয়ার জন্য 900 (১৫ মিনিট) করে দেওয়া হলো
    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 900]
    
    stats = {}
    total_otps_all = 0
    for t in recent_traffic:
        raw_srv = str(t.get("service", "Unknown"))
        app_full_name, prem_app_html = get_service_info_html(raw_srv)
        
        # 🌟 ছোট-বড় হাতের অক্ষরের কারণে ডাবল হওয়া আটকাতে .upper() ব্যবহার করা হলো
        srv_key = str(app_full_name).upper()
        
        if srv_key not in stats:
            stats[srv_key] = {"count": 0, "html": prem_app_html, "raw_name": raw_srv}
        stats[srv_key]["count"] += 1
        total_otps_all += 1
        
    txt = "<blockquote>📊 15 MINUTE LIVE TRAFFIC</blockquote>\n━━━━━━━━━━━━━━━\n"
    
    kb = []
    if not stats:
        txt += "<blockquote><i>No recent traffic found in the last 15 minutes...</i></blockquote>\n━━━━━━━━━━━━━━━\n"
    else:
        srv_totals = sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)
        
        lines = []
        for srv_key, data in srv_totals:
            lines.append(f"<blockquote>{data['html']} {srv_key} ➜ 🔥 {data['count']} OTP</blockquote>")
            
        txt += "\n— — — — — — — — — — — —\n".join(lines)
        txt += f"\n━━━━━━━━━━━━━━━\n<blockquote>📊 TOTAL ➜ 🔥 {total_otps_all} OTP</blockquote>\n━━━━━━━━━━━━━━━\n"

        for srv_key, data in srv_totals: 
            safe_srv = data["raw_name"][:20] 
            # 🌟 বাটনের টেক্সট পরিবর্তন করে GET [APP] NUMBER করা হলো এবং ডাইনামিক ইমোজি বসানো হলো
            emj_match = re.search(r'emoji-id="(\d+)"', data['html'])
            srv_emoji_id = emj_match.group(1) if emj_match else "5190645917711114179"
            kb.append([{"text": f"GET {srv_key} NUMBER", "icon_custom_emoji_id": srv_emoji_id, "callback_data": f"exp_rng_{safe_srv}", "style": "success"}])
            
    txt = render_body_text(txt)
    kb.append([{"text": "𝗥𝗘𝗙𝗥𝗘𝗦𝗛", "icon_custom_emoji_id": "5988037279459844786", "callback_data": "refresh_traffic", "style": "primary"}])
    
    return txt, {"inline_keyboard": kb}

# ==========================================
# Message Handler
# ==========================================
def handle_message(msg):
    global total_uploaded_stats, total_assigned_stats, assigned_number_rates, used_numbers_list
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    
    if chat_type != "private":
        return
        
    text = msg.get("text", "")
    register_user_local(chat_id) # 🌟 Save User locally for Free Broadcasts!

    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text("🚫 <b>You are banned from using this bot!</b>\nIf you think this is a mistake, please contact support."))
        return
    
    # --- REFERRAL FIX: Save inviter BEFORE Force Join ---
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            inviter = int(parts[1])
            if inviter != chat_id:
                if db:
                    doc = db.collection('users').document(str(chat_id)).get()
                    if not doc.exists:
                        get_user(chat_id)
                        db.collection('users').document(str(chat_id)).update({"referred_by": inviter, "ref_paid": False})
                        
    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return
        
    MAIN_MENU_CMDS = [
        "GET NUMBER", "𝗚𝗘𝗧 𝗡𝗨𝗠𝗕𝗘𝗥",
        "SET CHECKER", "𝗦𝗘𝗧 𝗖𝗛𝗘𝗖𝗞𝗘𝗥",
        "TRAFFIC", "𝗧𝗥𝗔𝗙𝗙𝗜𝗖",
        "REFERRAL", "𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟",
        "MY INFO", "𝗠𝗬 𝗜𝗡𝗙𝗢",
        "ADMIN PANEL", "𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟",
        "GET 2FA", "𝗚𝗘𝗧 𝟮𝗙𝗔",
        "LEADERBOARD", "𝗟𝗘𝗔𝗗𝗘𝗥𝗕𝗢𝗔𝗥𝗗", "TODAY LEADERBOARD", "𝗧𝗢𝗗𝗔𝗬 𝗟𝗘𝗔𝗗𝗘𝗥𝗕𝗢𝗔𝗥𝗗"
    ]
    
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or text.startswith("/start"):
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        is_main_cmd = True
    
    if chat_id in user_states and not is_main_cmd:
        state = user_states[chat_id]
        
        # 🌟 Auto Captcha Panel Setup Flow 
        if state == "wait_for_cpanel_url" and text:
            temp_data[chat_id]["p_data"]["login_url"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_user"
            send_message(chat_id, render_body_text("2️⃣ <b>Username</b>\n➡️ Panel এর Username দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_user" and text:
            temp_data[chat_id]["p_data"]["username"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_pass"
            send_message(chat_id, render_body_text("3️⃣ <b>Password</b>\n➡️ Panel এর Password দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_pass" and text:
            temp_data[chat_id]["p_data"]["password"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_link"
            send_message(chat_id, render_body_text("4️⃣ <b>Message Link</b>\n➡️ যেখান থেকে SMS/OTP ডাটা (JSON) আসবে সেই Link দিন:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_link" and text:
            temp_data[chat_id]["p_data"]["msg_link"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_name"
            send_message(chat_id, render_body_text("5️⃣ <b>Number Column Name</b>\n➡️ Data তে Number column এর নাম কী? (যেমন: number, phone):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_name" and text:
            temp_data[chat_id]["p_data"]["num_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_idx"
            send_message(chat_id, render_body_text("6️⃣ <b>Number Column Serial</b>\n➡️ Number Column এর Serial Number কত? (যেমন: 3, 5):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["num_col_idx"] = int(text)
                user_states[chat_id] = "wait_for_cpanel_msg_col_name"
                send_message(chat_id, render_body_text("7️⃣ <b>Message Column Name</b>\n➡️ Message/OTP column এর নাম কী? (যেমন: message, sms):"), reply_markup=get_cancel_kb())
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_name" and text:
            temp_data[chat_id]["p_data"]["msg_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_col_idx"
            send_message(chat_id, render_body_text("8️⃣ <b>Message Column Serial</b>\n➡️ Message Column এর Serial Number কত? (যেমন: 5, 7):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["msg_col_idx"] = int(text)
                temp_data[chat_id]["p_data"]["login_status"] = "⏳ Pending Auto-Login..."
                
                # Save the panel configuration
                bot_settings["panels"].append(temp_data[chat_id]["p_data"])
                save_db()
                
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Auto Captcha Panel Added Successfully!</b>\nবট এখন থেকে নিজেই ব্যাকগ্রাউন্ডে ক্যাপচা সলভ করে লগিন করে নিবে।"), reply_markup=main_menu(chat_id))
                
                msg_id = temp_data[chat_id]["msg_id"]
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_cpt_panels", "id": "internal"})
                
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return

        # --- User Management Flows ---
        elif state == "wait_for_um_bal_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID! Please send a numeric User ID."), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc = db.collection('users').document(str(target_uid)).get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                current_bal = doc.to_dict().get('balance', 0.0)
                temp_data[chat_id]["target_uid"] = target_uid
                user_states[chat_id] = "wait_for_um_bal_amt"
                send_message(chat_id, render_body_text(f"✅ User found!\n💰 Current Balance: {current_bal} ৳\n\n📝 Send the amount to ADD (e.g. 50) or REMOVE (e.g. -50):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_bal_amt" and text:
            try:
                amt = float(text.strip())
                target_uid = temp_data[chat_id]["target_uid"]
                update_balance(target_uid, amt)
                send_message(chat_id, render_body_text(f"{PEM['ok']} Balance updated successfully for {target_uid}!"), reply_markup=main_menu(chat_id))
                send_message(target_uid, render_body_text(f"🔔 Your balance has been adjusted by <b>{amt} ৳</b> by an Admin."))
                del user_states[chat_id]
                del temp_data[chat_id]
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid amount! Please send a number."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_ban_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc_ref = db.collection('users').document(str(target_uid))
                doc = doc_ref.get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                current_status = doc.to_dict().get("banned", False)
                new_status = not current_status
                doc_ref.update({"banned": new_status})
                
                user_banned_cache[target_uid] = {'banned': new_status, 'time': time.time()}
                
                status_text = "BANNED 🚫" if new_status else "UNBANNED ✅"
                send_message(chat_id, render_body_text(f"✅ User {target_uid} has been {status_text}!"), reply_markup=main_menu(chat_id))
                del user_states[chat_id]
                del temp_data[chat_id]
            return

        elif state == "wait_for_um_prof_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            if db:
                doc = db.collection('users').document(str(target_uid)).get()
                if not doc.exists:
                    send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                    return
                data = doc.to_dict()
                is_verified = True if data.get('total_otps', 0) > 0 else data.get('verified', False)
                prof_text = f"""➖➖➖➖➖➖➖➖
👤 <b>USER PROFILE</b>
➖➖➖➖➖➖➖➖
🆔 ID: <code>{target_uid}</code>
💰 Balance: {data.get('balance', 0.0)} ৳
🤝 Total Refers: {data.get('total_refers', 0)}
🔐 Total OTPs: {data.get('total_otps', 0)}
✅ Verified: {is_verified}
🚫 Banned: {data.get('banned', False)}
➖➖➖➖➖➖➖➖"""
                kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "primary"}]]}
                send_message(chat_id, render_body_text(prof_text), reply_markup=kb)
                del user_states[chat_id]
                del temp_data[chat_id]
            return

        # --- Menu Design Flow ---
        elif state == "wait_for_menu_text" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                formatted_html_text = extract_premium_html(msg)
                
                bot_settings["custom_messages"][menu_key]["text"] = formatted_html_text
                save_db()
                
                delete_message(chat_id, msg["message_id"])
                
                preview_text = render_body_text(formatted_html_text)
                success_text = f"{PEM['ok']} <b>Message Body Updated successfully!</b>\n\n🎨 <b>Editing: {menu_key.upper()}</b>\n\nPreview of current Text:\n{preview_text}"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(success_text), reply_markup=menu_edit_options_keyboard(menu_key))
            except Exception as e:
                send_message(chat_id, f"❌ Error saving text: {e}")
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return
            
        elif state == "wait_for_menu_btn" and text:
            try:
                menu_key = temp_data[chat_id]["menu_key"]
                if "-" in text:
                    parts = text.split("-", 1)
                    btn_text = parts[0].strip()
                    btn_url = parts[1].strip()
                    
                    emoji_id = None
                    emoji_char = ""
                    for ent in msg.get("entities", []):
                        if ent.get("type") == "custom_emoji":
                            emoji_id = ent.get("custom_emoji_id")
                            offset = ent.get("offset", 0)
                            length = ent.get("length", 0)
                            b_text = text.encode('utf-16-le')
                            emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                            break
                            
                    if emoji_char:
                        btn_text = btn_text.replace(emoji_char, "").strip()
                        
                    btn_data = {"text": btn_text, "url": btn_url, "style": "primary"}
                    if emoji_id:
                        btn_data["icon_custom_emoji_id"] = emoji_id
                        
                    bot_settings["custom_messages"][menu_key]["buttons"].append(btn_data)
                    save_db()
                    delete_message(chat_id, msg["message_id"])
                    edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"{PEM['gear']} <b>Edit Inline Buttons: {menu_key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(menu_key))
                else:
                    send_message(chat_id, render_body_text(f"{PEM['no']} Invalid format. Use <code>Button Text - https://link.com</code>"))
            except Exception as e:
                 pass
            finally:
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        elif state == "wait_for_test_service" and text:
            temp_data[chat_id]["service"] = text.strip()
            user_states[chat_id] = "wait_for_test_number"
            send_message(chat_id, render_body_text("📝 Send the Number (e.g. +8801712345678):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_number" and text:
            temp_data[chat_id]["number"] = text.strip()
            user_states[chat_id] = "wait_for_test_otp"
            send_message(chat_id, render_body_text("📝 Send the OTP (e.g. 556677):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_otp" and text:
            temp_data[chat_id]["otp"] = text.strip()
            user_states[chat_id] = "wait_for_test_lang"
            send_message(chat_id, render_body_text("📝 Send the Language (e.g. EN, AR):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_lang" and text:
            lang = text.strip().upper()
            if not lang.startswith("#"):
                lang = "#" + lang
                
            srv = temp_data[chat_id]["service"]
            num = temp_data[chat_id]["number"]
            otp = temp_data[chat_id]["otp"]
            
            masked = mask_number(num)
            prem_flag_html = get_flag_info_html(num)
            char, iso = get_flag_and_code(num)
            app_full_name, prem_app_html = get_service_info_html(srv)
            
            lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
            styled_masked = str(masked).replace("DXA", "•DXA•")
            msg_text = render_body_text(f"━━━━━━━━━━━━━━━\n<blockquote>{prem_app_html} {str(app_full_name).upper()} ➜ 💬 {str(lang_name).upper()}</blockquote>\n<blockquote>『 {prem_flag_html} {iso} ➜ {styled_masked} 』</blockquote>\n━━━━━━━━━━━━━━━")
            
            for fw in bot_settings.get("fw_groups", []):
                emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
                srv_emoji_id = emj_match.group(1) if emj_match else "5296369303661067030"
                
                styles = ["primary", "success", "danger"]
                kb = [[{"text": f"{otp}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": otp}, "style": styles[0]}]]
                
                temp_row = []
                for i, btn in enumerate(fw.get("buttons", [])):
                    b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[(i + 1) % 3]}
                    if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                    temp_row.append(b_obj)
                    if len(temp_row) == 2:
                        kb.append(temp_row)
                        temp_row = []
                if temp_row: kb.append(temp_row)
                
                # --- GET SAME NUMBER (Random Panel) বাটন অ্যাড করার নতুন কোড ---
                active_panels = []
                if bot_settings.get("stex_keys"): active_panels.append("stex")
                if bot_settings.get("voltx_keys"): active_panels.append("voltx")
                if bot_settings.get("zenex_keys"): active_panels.append("zenex")
                
                selected_panel = random.choice(active_panels) if active_panels else "stex"
                clean_srv = re.sub(r'[^a-zA-Z0-9]', '', app_full_name)
                
                # + চিহ্ন এবং স্পেস রিমুভ করে ক্লিন নাম্বার তৈরি করা হলো
                clean_num_for_link = str(num).replace("+", "").replace(" ", "").strip()
                dl_link = f"https://t.me/{BOT_USERNAME}?start={selected_panel}_{clean_num_for_link[:5]}_{clean_srv}"
                
                kb.append([{"text": "𝗚𝗘𝗧 𝗦𝗔𝗠𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", "icon_custom_emoji_id": "5291997181572570361", "url": dl_link, "style": "danger"}])
                # -----------------------------------------------------------------

                send_message(fw["chat_id"], msg_text, reply_markup={"inline_keyboard": kb})
                
            # 🌟 Admin এর ইনবক্সে নতুন ডিজাইনের টেস্ট মেসেজ পাঠানো হচ্ছে
            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
            
            reward = float(bot_settings.get("otp_reward", 0.0))
            emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
            srv_emoji_id = emj_match.group(1) if emj_match else "5870972873450984431"
            
            inbox_msg_text = f" {get_flag_info_html(display_num)} <code>{display_num}</code>\n➕  {reward} 𝗧𝗞"
            inbox_msg = render_body_text(inbox_msg_text)
            
            inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": otp}, "style": "success"}]]
                
            send_message(chat_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                
            send_message(chat_id, render_body_text(f"{PEM['ok']} Test message formatted and sent to your Inbox & all Forward Groups!"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_emoji_extract":
            entities = msg.get("entities", [])
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0)
                    length = ent.get("length", 0)
                    b_text = msg.get("text", "").encode('utf-16-le')
                    emoji_text = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                    break
            
            if custom_emoji_id:
                temp_data[chat_id] = {"id": custom_emoji_id, "char": emoji_text}
                user_states[chat_id] = "wait_for_emoji_details"
                send_message(chat_id, render_body_text(f"{PEM['ok']} Emoji ID পাওয়া গেছে: <code>{custom_emoji_id}</code>\n\n📌 এখন এটি সেভ করার জন্য টাইপ এবং নাম লিখুন।\n\n<b>ফরমেট:</b>\n`FLAG | 880 | BD | Bangladesh`\nঅথবা\n`APP | WhatsApp`"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} কোনো Premium Emoji পাওয়া যায়নি! দয়া করে Custom Emoji সেন্ড করুন।"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_emoji_details" and text:
            parts = [p.strip() for p in text.split("|")]
            mode = parts[0].upper()
            eid = temp_data[chat_id]["id"]
            char = temp_data[chat_id]["char"]
            
            if mode == "FLAG" and len(parts) == 4:
                code, iso, name = parts[1], parts[2], parts[3]
                bot_settings["premium_flags"][code] = {"char": char, "iso": iso.upper(), "name": name, "id": eid}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} Flag Emoji সেভ হয়েছে!\nCode: {code} | Name: {name}"), reply_markup=emoji_settings_keyboard())
            elif mode == "APP" and len(parts) == 2:
                name = parts[1]
                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name.title()}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} App Emoji সেভ হয়েছে!\nName: {name}"), reply_markup=emoji_settings_keyboard())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']} ফরম্যাট ভুল!\n\nসঠিক ফরম্যাট:\n`FLAG | 880 | BD | Bangladesh`\n`APP | WhatsApp`"))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state in ["wait_for_flag_txt", "wait_for_app_txt"] and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            content = requests.get(f"{FILE_URL}{file_path}").text
            
            mode = "flags" if state == "wait_for_flag_txt" else "apps"
            count = 0
            
            if mode == "flags":
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            prefix_str = line[:json_match.start()].strip()
                            code_match = re.search(r'(?:^|\()(\d+)\)', prefix_str)
                            iso_match = re.search(r'\(([A-Za-z]+)\)', prefix_str)
                            
                            if code_match and iso_match and char and eid:
                                code = code_match.group(1)
                                iso = iso_match.group(1).upper()
                                name = prefix_str.replace(f"({code})", "").replace(f"{code})", "").replace(f"({iso_match.group(1)})", "").replace(char, "").strip()
                                bot_settings["premium_flags"][code] = {"char": char, "iso": iso, "name": name, "id": eid}
                                count += 1
                        except: pass
            else:
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            name_part = line[:json_match.start()].strip()
                            name = name_part.replace(char, '').strip() if char else name_part
                            
                            if char and eid and name:
                                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name}
                                count += 1
                        except: pass
            
            save_db()
            send_message(chat_id, render_body_text(f"{PEM['ok']} Successfully loaded {count} Emojis!"), reply_markup=emoji_settings_keyboard())
            del user_states[chat_id]
            return

        elif state == "wait_for_broadcast":
            msg_id = msg["message_id"]
            send_message(chat_id, render_body_text(f"{PEM['ok']} Broadcast started..."))
            threading.Thread(target=broadcast_copymessage, args=(chat_id, msg_id)).start()
            del user_states[chat_id]
            return

        elif state == "wait_for_firebase_json" and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".json"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a valid <b>.json</b> file only."))
                return
            
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            file_content = requests.get(f"{FILE_URL}{file_path}").text
            
            try:
                json.loads(file_content)
                with open("firebase_key.json", "w", encoding="utf-8") as f:
                    f.write(file_content)
                    
                is_connected = init_firebase()
                
                if is_connected:
                    # 🌟 ফায়ারবেস কানেক্ট হওয়ার সাথে সাথে পুরোনো সেটিংস রিস্টোর করা
                    try:
                        doc = db.collection('settings').document('bot_config').get()
                        if doc.exists:
                            fs_data = doc.to_dict()
                            for k in FS_KEYS:
                                if k in fs_data:
                                    bot_settings[k] = fs_data[k]
                            save_local_db() # লোকাল ফাইলে সেভ করে নেওয়া
                    except Exception as ex:
                        print("Sync Config Error:", ex)

                    # 🌟 ব্যাকগ্রাউন্ডে সমস্ত ইউজার সিঙ্ক করা (বট যেন স্লো না হয়)
                    def force_sync_users():
                        global all_known_users
                        try:
                            for u_doc in db.collection('users').select([]).stream():
                                all_known_users.add(u_doc.id)
                            with open("users_list.json", "w") as f:
                                json.dump(list(all_known_users), f)
                        except: pass
                    threading.Thread(target=force_sync_users, daemon=True).start()

                    send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Firebase Connected Successfully!</b>\nফায়ারবেস থেকে আপনার পুরোনো সমস্ত ইউজার এবং সিস্টেম সেটিং সফলভাবে রিস্টোর করা হয়েছে।"), reply_markup=main_menu(chat_id))
                else:
                    send_message(chat_id, render_body_text(f"{PEM['no']} <b>Failed to connect Firebase!</b>\nJSON ফাইলে কোনো সমস্যা থাকতে পারে।"), reply_markup=get_cancel_kb())
            except Exception as e:
                send_message(chat_id, render_body_text(f"{PEM['no']} Invalid JSON format! Error: {e}"))
                
            del user_states[chat_id]
            return

        elif state == "wait_for_txt" and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            file_content = requests.get(f"{FILE_URL}{file_path}").text
            
            temp_data[chat_id] = {"numbers": file_content.splitlines(), "filename": doc["file_name"]}
            user_states[chat_id] = "wait_for_service"
            send_message(chat_id, render_body_text(f"{PEM['ok']} File received.\n\n📌 Enter the service name (e.g., WHATSAPP):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_service" and text:
            temp_data[chat_id]["service"] = text.upper()
            user_states[chat_id] = "wait_for_country"
            send_message(chat_id, render_body_text(f"{PEM['ok']} Service set.\n\n🌍 Enter the country name (e.g., YEMEN):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_country" and text:
            country = text.upper()
            temp_data[chat_id]["country"] = country
            user_states[chat_id] = "wait_for_file_rate"
            send_message(chat_id, render_body_text(f"{PEM['ok']} Country set.\n\n💰 Enter the OTP reward rate for this file (e.g. 5.0):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_file_rate" and text:
            try:
                rate = float(text.strip())
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid rate! Please enter a number (e.g. 5.0):"), reply_markup=get_cancel_kb())
                return
                
            country = temp_data[chat_id]["country"]
            service = temp_data[chat_id]["service"]
            raw_numbers = temp_data[chat_id]["numbers"]
            
            clean_nums = []
            for num in raw_numbers:
                num = num.strip()
                if num:
                    if not num.startswith('+'): num = '+' + num
                    clean_nums.append(num)
                    clean_digits = re.sub(r'\D', '', num)
                    assigned_number_rates[num] = float(rate)
                    if clean_digits:
                        assigned_number_rates[clean_digits] = float(rate)
                        assigned_number_rates[f"+{clean_digits}"] = float(rate)
            
            batch_id = str(uuid.uuid4())[:8]
            number_batches[batch_id] = {
                "filename": temp_data[chat_id]["filename"], 
                "service": service, 
                "country": country, 
                "rate": rate,
                "numbers": [{"num": n, "shares": 0, "used_by": []} for n in clean_nums]
            }
            total_uploaded_stats += len(clean_nums)
            save_db()
            
            app_full_name, prem_app_html = get_service_info_html(service)
            prem_flag_html = get_flag_info_html(clean_nums[0]) if clean_nums else f"{PEM['world']} "
            
            broadcast_txt = f"➖➖➖➖➖➖➖➖\n《 NEW NUMBERS 》\n➖➖➖➖➖➖➖➖\n{prem_flag_html} {country} {prem_app_html} {service}\n➖➖➖➖➖➖➖➖\n📤 Total Added: <b>{len(clean_nums)}</b>\n💰 Reward: <b>{rate} TK</b>\n➖➖➖➖➖➖➖➖\nClick the button below to get your numbers!"
            broadcast_txt = render_body_text(broadcast_txt)
            
            # 🌟 ব্রডকাস্ট মেসেজের নিচে GET NUMBER বাটন যুক্ত করা হলো
            broadcast_kb = {
                "inline_keyboard": [
                    [{"text": "𝗚𝗘𝗧 𝗡𝗨𝗠𝗕𝗘𝗥", "icon_custom_emoji_id": "5352597830089347330", "callback_data": f"c_n_{service}_{country}", "style": "success"}]
                ]
            }
            
            send_message(chat_id, render_body_text(f"{PEM['ok']} Numbers added to local stock with {rate} TK rate! Starting broadcast..."))
            
            def simple_broadcast(txt, reply_markup):
                url = f"{BASE_URL}/sendMessage"
                b_session = requests.Session()
                
                def send_single(u_id):
                    try:
                        payload = {"chat_id": u_id, "text": txt, "parse_mode": "HTML", "disable_web_page_preview": True, "reply_markup": reply_markup}
                        b_session.post(url, json=payload, timeout=5)
                    except: pass
                
                # 🌟 15 গুণ দ্রুত ব্রডকাস্ট করার জন্য ThreadPoolExecutor ব্যবহার
                with ThreadPoolExecutor(max_workers=15) as executor:
                    executor.map(send_single, list(all_known_users))

            threading.Thread(target=simple_broadcast, args=(broadcast_txt, broadcast_kb)).start()
            
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_stex_key" and text:
            bot_settings["stex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ StexSMS API Key Added! Total Keys: {len(bot_settings.get('stex_keys', []))}"), reply_markup=stex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_voltx_key" and text:
            bot_settings["voltx_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Voltx API Key Added! Total Keys: {len(bot_settings.get('voltx_keys', []))}"), reply_markup=voltx_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_sc" and text:
            code = text.strip().replace("+", "")
            if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
            bot_settings["search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            kb = []
            for idx, c in enumerate(bot_settings.get("search_countries", [])):
                kb.append([{"text": f"❌ Delete {c}", "callback_data": f"del_sc_{idx}", "style": "danger"}])
            kb.append([{"text": "➕ Add Country Code", "callback_data": "add_search_country", "style": "success"}])
            kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_vsc" and text:
            code = text.strip().replace("+", "")
            if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
            bot_settings["voltx_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "voltx_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_nx_srv_name" and text:
            srv = text.strip().upper()
            if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
            if srv not in bot_settings["stex_services"]: bot_settings["stex_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_stex_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["stex_services"][srv]: bot_settings["stex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_nx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["stex_services"][srv][cnt]:
                bot_settings["stex_services"][srv][cnt].append(new_range)
                
                if "search_countries" not in bot_settings:
                    bot_settings["search_countries"] = []
                if new_range not in bot_settings["search_countries"]:
                    bot_settings["search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"nx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_srv_name" and text:
            srv = text.strip().upper()
            if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
            if srv not in bot_settings["voltx_services"]: bot_settings["voltx_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_voltx_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["voltx_services"][srv]: bot_settings["voltx_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["voltx_services"][srv][cnt]:
                bot_settings["voltx_services"][srv][cnt].append(new_range)
                
                if "voltx_search_countries" not in bot_settings:
                    bot_settings["voltx_search_countries"] = []
                if new_range not in bot_settings["voltx_search_countries"]:
                    bot_settings["voltx_search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_zenex_key" and text:
            bot_settings["zenex_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Zenex API Key Added! Total Keys: {len(bot_settings.get('zenex_keys', []))}"), reply_markup=zenex_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_zsc" and text:
            code = text.strip().replace("+", "")
            if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
            bot_settings["zenex_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "zenex_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_zx_srv_name" and text:
            srv = text.strip().upper()
            if "zenex_services" not in bot_settings: bot_settings["zenex_services"] = {}
            if srv not in bot_settings["zenex_services"]: bot_settings["zenex_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_zenex_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_zx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["zenex_services"][srv]: bot_settings["zenex_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"zx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_zx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            if new_range not in bot_settings["zenex_services"][srv][cnt]:
                bot_settings["zenex_services"][srv][cnt].append(new_range)
                if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
                if new_range not in bot_settings["zenex_search_countries"]: bot_settings["zenex_search_countries"].append(new_range)
                save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"zx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_mino_key" and text:
            if "mino_keys" not in bot_settings: bot_settings["mino_keys"] = []
            bot_settings["mino_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Mino API Key Added! Total Keys: {len(bot_settings.get('mino_keys', []))}"), reply_markup=mino_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_msc" and text:
            code = text.strip().replace("+", "")
            if "mino_search_countries" not in bot_settings: bot_settings["mino_search_countries"] = []
            bot_settings["mino_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "mino_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_mx_srv_name" and text:
            srv = text.strip().upper()
            if "mino_services" not in bot_settings: bot_settings["mino_services"] = {}
            if srv not in bot_settings["mino_services"]: bot_settings["mino_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_mino_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_mx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["mino_services"][srv]: bot_settings["mino_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"mx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_mx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            if new_range not in bot_settings["mino_services"][srv][cnt]:
                bot_settings["mino_services"][srv][cnt].append(new_range)
                if "mino_search_countries" not in bot_settings: bot_settings["mino_search_countries"] = []
                if new_range not in bot_settings["mino_search_countries"]: bot_settings["mino_search_countries"].append(new_range)
                save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"mx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_wm" and text:
            bot_settings["w_methods"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fj" and text:
            target_chat_id = parse_chat_id(text)
            bot_settings["fj_channels"].append(target_chat_id)
            save_db()
            
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🔗 <b>FORCE JOIN SYSTEM</b>\nManage channels below:\n<i>(Note: For private links, use numeric IDs like -100...)</i>"), reply_markup=fj_settings_keyboard())
            
            # DON'T 
            bot_id = int(TOKEN.split(":")[0])
            res = api_call("getChatMember", {"chat_id": target_chat_id, "user_id": bot_id})
            is_admin_check = res.get("ok") and res.get("result", {}).get("status") in ["administrator", "creator"]
            
            # DON'T 
            if not is_admin_check:
                error_msg = render_body_text("<blockquote>⚠️ 𝗜𝗠𝗣𝗢𝗥𝗧𝗔𝗡𝗧 𝗡𝗢𝗧𝗜𝗖𝗘 ⚠️</blockquote>")
                tut_kb = {"inline_keyboard": [[{"text": "𝗧𝗨𝗧𝗢𝗥𝗜𝗔𝗟", "icon_custom_emoji_id": "5988027598603559238", "url": "https://youtube.com/@dxa_universe", "style": "primary"}]]}
                send_photo(chat_id, "https://ibb.co.com/DPhp791p", caption=error_msg, reply_markup=tut_kb)
                
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_adm" and text:
            if text.isdigit():
                bot_settings["admins"].append(int(text))
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("👥 <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_master_api_key" and text:
            bot_settings["master_api_key"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_api_key_menu", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fw_id":
            if text == "Cancel":
                # 🌟 পপ-আপ সরিয়ে রেগুলার বাটন ফিরিয়ে আনার লজিক
                send_message(chat_id, render_body_text("❌ Action Cancelled."), reply_markup=main_menu(chat_id))
                send_message(chat_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return
            
            target_chat_id = None
            if "chat_shared" in msg:
                target_chat_id = str(msg["chat_shared"]["chat_id"])
            elif text:
                target_chat_id = parse_chat_id(text)
                
            if target_chat_id:
                bot_id = int(TOKEN.split(":")[0])
                res = api_call("getChatMember", {"chat_id": target_chat_id, "user_id": bot_id})
                is_admin_check = res.get("ok") and res.get("result", {}).get("status") in ["administrator", "creator"]
                
                invite_link = None
                if is_admin_check:
                    chat_info = api_call("getChat", {"chat_id": target_chat_id})
                    if chat_info.get("ok"):
                        invite_link = chat_info["result"].get("invite_link")
                        if not invite_link:
                            exp_res = api_call("exportChatInviteLink", {"chat_id": target_chat_id})
                            if exp_res.get("ok"):
                                invite_link = exp_res.get("result")
                                
                    if invite_link:
                        bot_settings["otp_link"] = invite_link

                # 🌟 গ্রুপ সব সময় সেভ হবে (অ্যাডমিন না হলেও)
                bot_settings["fw_groups"] = [{"chat_id": target_chat_id, "buttons": []}]
                save_db()
                
                # 🌟 প্রথমে OTP Group Updated মেসেজ এবং মেইন মেনু (যাতে রেগুলার বাটন ফিরে আসে)
                link_text = "\n🔗 <b>Link Auto Updated!</b>" if invite_link else ""
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>OTP Group Updated:</b> <code>{target_chat_id}</code>{link_text}"), reply_markup=main_menu(chat_id))
                send_message(chat_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
                
                # 🌟  DON'T TOUCH 
                if not is_admin_check:
                    error_msg = render_body_text("<blockquote>⚠️ 𝗜𝗠𝗣𝗢𝗥𝗧𝗔𝗡𝗧 𝗡𝗢𝗧𝗜𝗖𝗘 ⚠️</blockquote>")
                    # DON'T TOUCH 
                    tut_kb = {"inline_keyboard": [[{"text": "𝗧𝗨𝗧𝗢𝗥𝗜𝗔𝗟", "icon_custom_emoji_id": "5988027598603559238", "url": "https://youtube.com/@dxa_universe", "style": "primary"}]]}
                    send_photo(chat_id, "https://ibb.co.com/DPhp791p", caption=error_msg, reply_markup=tut_kb)
                
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return
            
        elif state == "wait_for_w_group_id":
            if text == "Cancel" or text == "𝗖𝗔𝗡𝗖𝗘𝗟":
                send_message(chat_id, render_body_text("❌ Action Cancelled."), reply_markup=main_menu(chat_id))
                send_message(chat_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return
            
            target_chat_id = None
            if "chat_shared" in msg:
                target_chat_id = str(msg["chat_shared"]["chat_id"])
            elif text:
                target_chat_id = parse_chat_id(text)
                
            if target_chat_id:
                bot_id = int(TOKEN.split(":")[0])
                res = api_call("getChatMember", {"chat_id": target_chat_id, "user_id": bot_id})
                is_admin_check = res.get("ok") and res.get("result", {}).get("status") in ["administrator", "creator"]
                
                bot_settings["w_group"] = target_chat_id
                save_db()
                
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Withdraw Group Updated:</b> <code>{target_chat_id}</code>"), reply_markup=main_menu(chat_id))
                send_message(chat_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
                
                # 🌟 যদি অ্যাডমিন না থাকে, তাহলে ছবির সাথে ওয়ার্নিং নোটিশ ও টিউটোরিয়াল বাটন যাবে
                if not is_admin_check:
                    error_msg = render_body_text("<blockquote>⚠️ 𝗜𝗠𝗣𝗢𝗥𝗧𝗔𝗡𝗧 𝗡𝗢𝗧𝗜𝗖𝗘 ⚠️</blockquote>")
                    tut_kb = {"inline_keyboard": [[{"text": "𝗧𝗨𝗧𝗢𝗥𝗜𝗔𝗟", "icon_custom_emoji_id": "5988027598603559238", "url": "https://youtube.com/@dxa_universe", "style": "primary"}]]}
                    send_photo(chat_id, "https://ibb.co.com/DPhp791p", caption=error_msg, reply_markup=tut_kb)
                
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        elif state == "wait_for_add_fw_btn" and text:
            fw_idx = temp_data[chat_id]["fw_idx"]
            if "-" in text:
                parts = text.split("-", 1)
                btn_text = parts[0].strip()
                btn_url = parts[1].strip()
                
                emoji_id = None
                emoji_char = ""
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji":
                        emoji_id = ent.get("custom_emoji_id")
                        offset = ent.get("offset", 0)
                        length = ent.get("length", 0)
                        b_text = text.encode('utf-16-le')
                        emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                        break
                
                if emoji_char:
                    btn_text = btn_text.replace(emoji_char, "").strip()
                    
                btn_data = {"text": btn_text, "url": btn_url}
                if emoji_id:
                    btn_data["icon_custom_emoji_id"] = emoji_id
                    
                bot_settings["fw_groups"][fw_idx]["buttons"].append(btn_data)
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][fw_idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(fw_idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_otp_link" and text:
            bot_settings["otp_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_channel_link" and text:
            bot_settings["otp_channel_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_panel_name" and text:
            p_name = text.strip()
            t_key = temp_data[chat_id].get("add_type", "api")
            msg_id = temp_data[chat_id]["msg_id"]
            delete_message(chat_id, msg["message_id"])
            
            if t_key == "logc":
                user_states[chat_id] = "wait_for_cpanel_url"
                temp_data[chat_id] = {"msg_id": msg_id, "p_data": {
                    "name": p_name, "type": "Auto Captcha Panel", "status": "ON", "records": 0, "login_status": "⏳ Pending First Login"
                }}
                edit_message(chat_id, msg_id, render_body_text("1️⃣ <b>Login URL</b>\n➡️ Panel এর Login Link দিন:"), reply_markup=get_cancel_kb())
                return
            else:
                bot_settings["panels"].append({
                    "name": p_name, "type": "API Panel", "status": "OFF", "api_url": "", "token": "", "records": 0
                })
                save_db()
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_api_panels", "id": "internal"})
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return

        elif state == "wait_for_p_api" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_tok" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["token"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_fapi" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["full_api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_rec" and text:
            if text.isdigit():
                idx = temp_data[chat_id]["p_idx"]
                bot_settings["panels"][idx]["records"] = int(text)
                save_db()
                delete_message(chat_id, msg["message_id"])
                p = bot_settings["panels"][idx]
                
                ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number! Try again."), reply_markup=get_cancel_kb())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_edit_cp_lurl" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["login_url"] = text.strip()
            bot_settings["panels"][idx]["login_status"] = "⏳ Pending Re-login"
            panel_sessions.pop(idx, None)
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(render_panel_config_text(p)), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_edit_cp_mlink" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["msg_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(render_panel_config_text(p)), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_edit_cp_user" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["username"] = text.strip()
            bot_settings["panels"][idx]["login_status"] = "⏳ Pending Re-login"
            panel_sessions.pop(idx, None)
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(render_panel_config_text(p)), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_edit_cp_pass" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["password"] = text.strip()
            bot_settings["panels"][idx]["login_status"] = "⏳ Pending Re-login"
            panel_sessions.pop(idx, None)
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(render_panel_config_text(p)), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_edit_cp_nname" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["num_col_name"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(render_panel_config_text(p)), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_edit_cp_nidx" and text:
            idx = temp_data[chat_id]["p_idx"]
            digits = re.sub(r'\D', '', text)
            if digits:
                bot_settings["panels"][idx]["num_col_idx"] = int(digits)
                save_db()
                delete_message(chat_id, msg["message_id"])
                p = bot_settings["panels"][idx]
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(render_panel_config_text(p)), reply_markup=panel_config_keyboard(idx))
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid serial number (e.g. 1, 3)!"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_edit_cp_mname" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["msg_col_name"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(render_panel_config_text(p)), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_edit_cp_midx" and text:
            idx = temp_data[chat_id]["p_idx"]
            digits = re.sub(r'\D', '', text)
            if digits:
                bot_settings["panels"][idx]["msg_col_idx"] = int(digits)
                save_db()
                delete_message(chat_id, msg["message_id"])
                p = bot_settings["panels"][idx]
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(render_panel_config_text(p)), reply_markup=panel_config_keyboard(idx))
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid serial number (e.g. 2, 4)!"), reply_markup=get_cancel_kb())
            return

        elif state == "set_dxa":
            msg_id = temp_data[chat_id]["msg_id"]
            key = temp_data[chat_id]["key"]
            try:
                if key in ["min_withdraw", "otp_reward", "refer_reward"]: bot_settings[key] = float(text)
                elif key in ["cooldown", "num_req", "num_share"]: bot_settings[key] = int(text)
                else: bot_settings[key] = text
                save_db()
                delete_message(chat_id, msg["message_id"])
                if key == "otp_reward":
                    edit_message(chat_id, msg_id, render_body_text(f"💰 <b>OTP REWARD SETTINGS</b>\n\n✅ Default Rate updated to <b>{bot_settings['otp_reward']} TK</b>!"), reply_markup=dxa_otp_reward_keyboard())
                else:
                    edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
            except:
                delete_message(chat_id, msg["message_id"])
                if key == "otp_reward":
                    edit_message(chat_id, msg_id, render_body_text("💰 <b>OTP REWARD SETTINGS</b>\n\n❌ Invalid value!"), reply_markup=dxa_otp_reward_keyboard())
                else:
                    edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>\n\n❌ Invalid value!"), reply_markup=dxa_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_dxa_file_rate" and text:
            msg_id = temp_data[chat_id]["msg_id"]
            b_id = temp_data[chat_id]["b_id"]
            try:
                new_rate = float(text.strip())
                if b_id in number_batches:
                    number_batches[b_id]["rate"] = new_rate
                    f_name = number_batches[b_id].get("filename", b_id)
                    for n_obj in number_batches[b_id].get("numbers", []):
                        n_str = str(n_obj.get("num", "")).strip()
                        clean_n = re.sub(r'\D', '', n_str)
                        if n_str:
                            assigned_number_rates[n_str] = new_rate
                        if clean_n:
                            assigned_number_rates[clean_n] = new_rate
                            assigned_number_rates[f"+{clean_n}"] = new_rate
                    for n_str in number_batches[b_id].get("all_nums", []):
                        clean_n = re.sub(r'\D', '', str(n_str))
                        if clean_n:
                            assigned_number_rates[clean_n] = new_rate
                            assigned_number_rates[f"+{clean_n}"] = new_rate
                    save_db()
                    delete_message(chat_id, msg["message_id"])
                    edit_message(chat_id, msg_id, render_body_text(f"📁 <b>FILE RATE MANAGEMENT</b>\n\n✅ Rate updated to <b>{new_rate} TK</b> for <code>{html.escape(str(f_name))}</code>!\n\nSelect a file below to change its OTP reward rate:"), reply_markup=dxa_file_rate_list_keyboard())
                else:
                    delete_message(chat_id, msg["message_id"])
                    edit_message(chat_id, msg_id, render_body_text("📁 <b>FILE RATE MANAGEMENT</b>\n\n❌ File not found!"), reply_markup=dxa_file_rate_list_keyboard())
            except:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("📁 <b>FILE RATE MANAGEMENT</b>\n\n❌ Invalid rate value! Please try again."), reply_markup=dxa_file_rate_list_keyboard())
            if chat_id in user_states: del user_states[chat_id]
            if chat_id in temp_data: del temp_data[chat_id]
            return

        elif state == "wait_for_search" and text:
            query = text.strip().replace("+", "")
            if not query.isdigit() or len(query) < 3 or len(query) > 9:
                send_message(chat_id, render_body_text("❌ Please enter a valid 3 to 9 digit number!"))
                return
                
            wait_msg = send_message(chat_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = wait_msg.get("result", {}).get("message_id")
            
            # 🌟 ১. প্রথমে Local থেকে নাম্বার খুঁজবে (যে কোনো দেশের জন্য)
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                # 🌟 ২. যদি Local এ না পায়, তখন চেক করবে Voltx বা StexSMS থেকে আনা যাবে কি না
                stex_allowed = bot_settings.get("search_countries", [])
                voltx_allowed = bot_settings.get("voltx_search_countries", [])
                
                # ফিক্স: অ্যাডমিন প্যানেলে দেশ এড না থাকলে অটোমেটিক Block করে দেবে
                is_stex_allowed = any(query.startswith(c) for c in stex_allowed) if stex_allowed else False
                is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
                
                if not is_stex_allowed and not is_voltx_allowed:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ This country code is not allowed!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                    
                if wait_msg_id: edit_message(chat_id, wait_msg_id, render_body_text("⌛ <i>Processing... Finding Number via API...</i>"))
                
                is_voltx_used = False
                req_count = bot_settings.get("num_req", 1)
                
                # 🌟 প্রথমে Voltx চেক করবে
                if is_voltx_allowed:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in voltx_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    voltx_assigned_numbers[num_str] = chat_id 
                                    is_voltx_used = True
                                    global total_assigned_stats
                                    total_assigned_stats += 1
                                    break # শুধু api_key লুপ ব্রেক করবে, যাতে পরের নাম্বার আনতে পারে
                            except: continue

                # 🌟 Voltx এ না পেলে বা আরও নাম্বার লাগলে StexSMS তে চেক করবে
                if len(fetched_nums) < req_count and is_stex_allowed:
                    stex_keys = bot_settings.get("stex_keys", [])
                    
                    for _ in range(req_count - len(fetched_nums)): 
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                data = res.json()
                                if data.get("meta", {}).get("code") == 200 and data.get("data"):
                                    num_str = str(data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    stex_assigned_numbers[num_str] = chat_id 
                                    total_assigned_stats += 1
                                    break 
                            except: continue
                        
                if not fetched_nums:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Number out of stock!"), reply_markup=main_menu(chat_id))
                    del user_states[chat_id]
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    
                    fetched_nums.append(num_str)
                    
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            kb = []
            
            # Message Text Variables
            app_full_name = "SEARCH"
            prem_app_html = "🔍"
            if 'service_from_cb' in locals() and service_from_cb:
                app_full_name, prem_app_html = get_service_info_html(service_from_cb)

            flags_db = bot_settings.get("premium_flags", {})
            country_emoji_html = ""
            country_full_name = "Unknown"
            iso_code = "XX"
            
            # 🌟 চেক করা হচ্ছে যে এই সার্চটি WS Checker এর আওতাভুক্ত কি না 🌟
            is_service_in_ws_checker = False
            if 'service_from_cb' in locals() and service_from_cb:
                ws_srvs = bot_settings.get("ws_checker_services", [])
                if any(service_from_cb.upper() == s.upper() for s in ws_srvs):
                    is_service_in_ws_checker = True

            checker_results = {}
            if is_service_in_ws_checker and bot_settings.get("ws_checker_on", False):
                if wait_msg_id: edit_message(chat_id, wait_msg_id, render_body_text("⌛ <i>Checking Numbers via WhatsApp Checker...</i>"))
                checker_results = check_whatsapp_numbers(fetched_nums, chat_id)

            for num in fetched_nums:
                char_flag, iso = get_flag_and_code(num)
                iso_code = iso
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                clean_num = str(num).replace("+", "").replace(" ", "")
                
                flag_emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: 
                            flag_emoji_id = flag_data["id"]
                            country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                        country_full_name = flag_data.get("name", iso)
                        break
                if not country_emoji_html: country_emoji_html = char_flag
                if country_full_name == "Unknown": country_full_name = iso_code
                
                # 🌟 চেকার রেজাল্ট অনুযায়ী বাটনের স্টাইল এবং ইমোজি সেট করা 🌟
                btn_style = "primary"
                btn_text_display = f"{display_num}"
                
                if clean_num in checker_results:
                    if checker_results[clean_num] == "Good":
                        btn_style = "success"
                        btn_text_display = f"{display_num} 🟢"
                    elif checker_results[clean_num] == "Bad":
                        btn_style = "danger"
                        btn_text_display = f"{display_num} 🚫"
                
                kb.append([{"text": btn_text_display, "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": btn_style}])
            
            vtx_ext = "_vtx" if 'is_voltx_used' in locals() and is_voltx_used else ""
            srv_ext = f"_{service_from_cb}" if 'service_from_cb' in locals() and service_from_cb else ""
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
                
            change_btns = []
            if 'service_from_cb' in locals() and service_from_cb:
                change_btns.append({"text": "COUNTRY", "icon_custom_emoji_id": "5987629038523392103", "callback_data": f"g_s_{service_from_cb}", "style": "danger"})
            change_btns.append({"text": "REFRESH", "icon_custom_emoji_id": "5987671562994590370", "callback_data": f"c_n_s_{query}{srv_ext}{vtx_ext}", "style": "success"})
            kb.append(change_btns)

            kb.append([{"text": "REMOVE CC", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "toggle_cc_off", "style": "danger"}])
                
            kb.append([{"text": "OTP GROUP", "icon_custom_emoji_id": "5246848468177143690", "url": bot_settings["otp_link"], "style": "primary"}])
            
            formatted_msg = build_live_number_text(prem_app_html, app_full_name, country_emoji_html, country_full_name, iso_code, False, False, fetched_nums)
            text_numbers = render_body_text(formatted_msg)
            
            if wait_msg_id:
                edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
                user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums, "text": text_numbers, "kb": kb}
            else:
                msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
                if msg_res and "result" in msg_res:
                    user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums, "text": text_numbers, "kb": kb}
            return
            
        elif state == "wait_for_withdraw_amount" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            try:
                amount = float(text.strip())
                bal = temp_data[chat_id]["balance"]
                min_w = bot_settings['min_withdraw']
                
                if amount < min_w:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ Minimum withdrawal is {min_w} ৳!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                if amount > bal:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ You don't have enough balance!\n💰 Balance: {bal} ৳\n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                    
                temp_data[chat_id]["amount"] = amount
                user_states[chat_id] = "wait_for_withdraw_number"
                if msg_id_to_edit:
                    back_kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "start_withdraw", "style": "danger"}]]}
                    edit_message(chat_id, msg_id_to_edit, render_body_text(f"✅ Amount: {amount} ৳\n\n📱 Now send your <b>{temp_data[chat_id]['method']}</b> account number:"), reply_markup=back_kb)
            except ValueError:
                if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Invalid amount!\n\n📝 Please send a valid number:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_2fa_key" and text:
            msg_id_to_edit = temp_data.get(chat_id, {}).get("msg_id")
            delete_message(chat_id, msg.get("message_id")) # ইউজারের মেসেজ ডিলিট

            if not msg_id_to_edit:
                send_message(chat_id, render_body_text("❌ Error: Message not found. Try again."))
                del user_states[chat_id]
                return

            try:
                secret = text.strip().replace(" ", "")
                totp = pyotp.TOTP(secret)
                code = totp.now()
                remaining_time = 30 - (int(time.time()) % 30)
                
                success_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"《 🔐 <b>2FA CODE</b> 》\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                    f"━━━━━━━━━━━━━━━"
                )
                kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                      [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                       {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                      [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
                
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            except Exception:
                error_txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━\n❌ <b>Invalid Secret Key! Try again.</b>\n━━━━━━━━━━━━━━━"
                cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
                edit_message(chat_id, msg_id_to_edit, render_body_text(error_txt), reply_markup=cancel_kb)
            return

        elif state == "wait_for_ws_link_number" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            num_str = text.strip().replace("+", "").replace(" ", "")
            
            if not num_str.isdigit() or len(num_str) < 10:
                if msg_id_to_edit: 
                    edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Invalid Number format!\n\n📝 Please send a valid WhatsApp number (e.g., +8801712345678):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_info", "style": "danger"}]]})
                return
                
            api_url = bot_settings.get("master_api_url", "https://bot.orabitsms.site/api")
            api_key = bot_settings.get("master_api_key", "")
            
            if not api_key:
                if msg_id_to_edit: 
                    edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Checker API Key is not set by Admin! Please contact Support."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_info", "style": "danger"}]]})
                del user_states[chat_id]
                del temp_data[chat_id]
                return
                
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text("⏳ <i>Checking WhatsApp status...</i>"))
                
            try:
                # আগে চেক করা হচ্ছে নাম্বারটি অলরেডি লগিন আছে কিনা
                status_res = requests.get(f"{api_url}/user-status", params={"apiKey": api_key}, timeout=10)
                status_data = status_res.json()
                active_sessions = status_data.get("ActiveSessions", [])
                
                is_already_connected = False
                for session in active_sessions:
                    if str(session.get("phone")) == num_str and session.get("status") == "connected":
                        is_already_connected = True
                        break
                        
                if is_already_connected:
                    err_txt = f"❌ <b>Already Connected!</b>\n\n📱 Number: <code>+{num_str}</code>\n⚠️ This WhatsApp is already active in the panel. Please logout the previous session before adding it again."
                    if msg_id_to_edit:
                        edit_message(chat_id, msg_id_to_edit, render_body_text(err_txt), reply_markup={"inline_keyboard": [[{"text": "Back to Info", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_info", "style": "danger"}]]})
                    del user_states[chat_id]
                    del temp_data[chat_id]
                    return
            except Exception as e:
                pass # যদি API চেক ফেইল করে, তাহলে সরাসরি কোড আনার জন্য প্রসিড করবে

            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text("⏳ <i>Requesting Link Code from API...</i>"))

            # API কল করে লিংক কোড (Pairing Code) আনার লজিক
            def fetch_ws_code_and_poll(c_id, m_id, number, url, key):
                try:
                    # ১. স্ক্রিনশট অনুযায়ী সঠিক Endpoint এবং Payload
                    endpoint = f"{url}/connect-whatsapp"
                    payload = {
                        "apiKey": key,
                        "phone": number
                    }
                    
                    res = requests.post(endpoint, json=payload, timeout=20)
                    
                    try:
                        data = res.json()
                    except ValueError:
                        edit_message(c_id, m_id, render_body_text(f"❌ <b>API Error!</b>\n\nInvalid JSON Response.\nStatus Code: {res.status_code}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_info", "style": "danger"}]]})
                        return
                    
                    # স্ক্রিনশট অনুযায়ী Response চেক করা
                    if data.get("success") == True and data.get("pairingCode"):
                        pairing_code = data.get("pairingCode")
                        session_id = number # স্ট্যাটাস চেক করার জন্য নাম্বারটাকেই সেশন আইডি হিসেবে ধরলাম
                        
                        code_msg = f"✅ <b>Link Code Generated!</b>\n\n📱 <b>Number:</b> <code>+{number}</code>\n🔗 <b>Code:</b> <code>{pairing_code}</code>\n\n<i>⚠️ Enter this code in your WhatsApp Linked Devices within 2 minutes.</i>\n\n⏳ <i>Polling for login status...</i>"
                        
                        kb = [[{"text": "Copy Code", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": pairing_code}, "style": "success"}],
                              [{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_info", "style": "danger"}]]
                        edit_message(c_id, m_id, render_body_text(code_msg), reply_markup={"inline_keyboard": kb})
                        
                        # ২. লগইন হয়েছে কি না তা চেক করার জন্য Polling (প্রতি ৫ সেকেন্ড পরপর চেক করবে)
                        for _ in range(24): # ২ মিনিট চেক করবে (24 * 5 = 120s)
                            time.sleep(5)
                            try:
                                # OrabitSMS API-এর user-status এন্ডপয়েন্ট কল করা হচ্ছে
                                status_res = requests.get(f"{url}/user-status", params={"apiKey": key}, timeout=10)
                                status_data = status_res.json()
                                
                                is_connected = False
                                
                                # ActiveSessions লিস্ট চেক করে দেখবে ইউজারের নাম্বারটি connected হিসেবে আছে কি না
                                active_sessions = status_data.get("ActiveSessions", [])
                                for session in active_sessions:
                                    if session.get("phone") == number and session.get("status") == "connected":
                                        is_connected = True
                                        break
                                
                                if is_connected:
                                    # লগইন সাকসেসফুল হলে ইউজারের WS Added কাউন্ট বাড়ানো
                                    if c_id not in user_cache: get_user(c_id)
                                    user_cache[c_id]["total_ws_added"] = user_cache[c_id].get("total_ws_added", 0) + 1
                                    if db:
                                        try: db.collection('users').document(str(c_id)).update({"total_ws_added": firestore.Increment(1)})
                                        except: pass
                                        
                                    # ইউজারের আইডি ম্যাপ করে রাখা হলো লগআউট চেকিংয়ের জন্য
                                    ws_linked_numbers[str(number)] = c_id
                                    save_local_db()
                                    
                                    # আগের মেসেজটা এডিট করে শুধু ফিনিশড লিখে দেওয়া হলো
                                    edit_message(c_id, m_id, render_body_text(f"✅ <b>Process Finished.</b>"), reply_markup={"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]})
                                    
                                    # প্রিমিয়াম ইমোজি সহ সাকসেস মেসেজ
                                    success_msg = f"<tg-emoji emoji-id=\"5987961773934780806\">💬</tg-emoji> <b>𝚆𝚑𝚊𝚝𝚜𝙰𝚙𝚙 𝙻𝚒𝚗𝚔𝚎𝚍 𝚂𝚞𝚌𝚌𝚎𝚜𝚜𝚏𝚞𝚕𝚕𝚢!</b>\n\n<tg-emoji emoji-id=\"5337132498965010628\">📱</tg-emoji> <b>𝙽𝚞𝚖𝚋𝚎𝚛 :</b> +{number}\n\n<tg-emoji emoji-id=\"5987629038523392103\">🌐</tg-emoji> <b>𝙶𝚊𝚝𝚎𝚠𝚊𝚢 :</b> 𝙰𝙿𝙸 𝙺𝚎𝚢"
                                    send_message(c_id, render_body_text(success_msg))
                                    return
                            except: pass
                            
                        # ২ মিনিট পার হয়ে গেলে Timeout
                        timeout_msg = f"❌ <b>Login Timeout!</b>\n\n📱 Number: <code>+{number}</code>\n⚠️ You didn't enter the code in time. Please try again."
                        edit_message(c_id, m_id, render_body_text(timeout_msg), reply_markup={"inline_keyboard": [[{"text": "Try Again", "icon_custom_emoji_id": "5438433185291611807", "callback_data": "set_checker", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_info", "style": "danger"}]]})
                        
                    else:
                        err_msg = data.get("message", "Unknown API error!")
                        edit_message(c_id, m_id, render_body_text(f"❌ <b>Failed to get code!</b>\n\nReason: {err_msg}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_info", "style": "danger"}]]})
                except Exception as e:
                    edit_message(c_id, m_id, render_body_text(f"❌ <b>API Connection Error!</b>\n\nDetails: {str(e)[:50]}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_info", "style": "danger"}]]})

            # Background thread এ API কল শুরু করা যাতে বট হ্যাং না হয়
            threading.Thread(target=fetch_ws_code_and_poll, args=(chat_id, msg_id_to_edit, num_str, api_url, api_key)).start()
                
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_withdraw_number":
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            
            method = temp_data[chat_id]["method"]
            amount = temp_data[chat_id]["amount"]
            number = text
            req_id = f"W_{str(uuid.uuid4())[:6].upper()}"
            
            first_name = msg.get("from", {}).get("first_name", "User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            
            update_balance(chat_id, -amount)
            pending_withdrawals[req_id] = {"user_id": chat_id, "amount": amount, "method": method, "number": number, "full_name": full_name}
            
            # Save to Firestore for History
            if db:
                try:
                    db.collection('withdrawals').document(req_id).set({
                        "user_id": str(chat_id),
                        "amount": amount,
                        "method": method,
                        "status": "pending",
                        "timestamp": firestore.SERVER_TIMESTAMP
                    })
                except: pass
                
            if bot_settings["w_group"]:
                admin_msg = f"🎙 <b>NEW WITHDRAWAL REQUEST</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={chat_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amount} TK\n🍏 <b>NUMBER:</b> <code>{number}</code>\n🏦 <b>METHOD:</b> {method}\n\n🧾 <b>REQ ID:</b> {req_id}\n👨‍⚖️ <b>PROCESSED BY ADMIN</b>"
                kb = {"inline_keyboard": [[{"text": "APPROVE", "icon_custom_emoji_id": "5987557149360792425", "callback_data": f"wapp_{req_id}", "style": "success"}, {"text": "REJECT", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"wrej_{req_id}", "style": "danger"}]]}
                send_message(bot_settings["w_group"], render_body_text(admin_msg), reply_markup=kb)
            
            kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            success_text = f"{PEM['ok']} Your withdrawal request has been submitted!\n\n🧾 <b>Req ID:</b> {req_id}\n💰 <b>Amount:</b> {amount} ৳\n🏦 <b>Method:</b> {method}\n📱 <b>Number:</b> <code>{number}</code>"
            
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_text), reply_markup=kb)
            else:
                send_message(chat_id, render_body_text(success_text), reply_markup=kb)
                
            del user_states[chat_id]
            del temp_data[chat_id]
            return

    # --- Regular Commands ---
    if text.startswith("/start"):
        get_user(chat_id)
        
        # --- PROCESS DEEP LINK (AUTO GET NUMBER) ---
        parts = text.split()
        if len(parts) > 1 and "_" in parts[1] and parts[1].startswith(("stex_", "voltx_", "zenex_", "mino_", "local_")):
            try:
                p_parts = parts[1].split("_", 2)
                provider = p_parts[0]
                query = p_parts[1]
                service_from_link = p_parts[2] if len(p_parts) > 2 else "Service"
                
                wait_msg = send_message(chat_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
                wait_msg_id = wait_msg.get("result", {}).get("message_id")
                
                fetched_nums = []
                req_count = bot_settings.get("num_req", 1)
                
                if provider == "local":
                    found_indices = []
                    for b_id, b_data in number_batches.items():
                        for idx, n_obj in enumerate(b_data["numbers"]):
                            if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                                found_indices.append((b_id, idx))
                    if found_indices:
                        random.shuffle(found_indices)
                        for b_id, idx in found_indices:
                            if len(fetched_nums) >= req_count: break
                            n_obj = number_batches[b_id]["numbers"][idx]
                            num_str = n_obj["num"]
                            fetched_nums.append(num_str)
                            assigned_number_rates[num_str] = float(number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))
                            n_obj["shares"] += 1
                            n_obj["used_by"].append(chat_id)
                            total_assigned_stats += 1
                            if n_obj["shares"] >= bot_settings.get("num_share", 1):
                                n_obj["to_remove"] = True
                                used_numbers_list.append(num_str)
                        for b_id in number_batches:
                            number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]

                elif provider == "mino":
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in bot_settings.get("mino_keys", []):
                            try:
                                headers = {"Content-Type": "application/json", "X-MINO-API-KEY": api_key}
                                payload = {"api_key": api_key, "rid": query, "national_format": 0, "remove_plus": 0}
                                res = requests.post(f"{MINO_BASE_URL}/getnumber", json=payload, headers=headers, timeout=10)
                                r_json = res.json()
                                num_str = ""
                                if r_json.get("status") == "success" and r_json.get("number"):
                                    num_str = str(r_json.get("number", "")).replace("+", "").strip()
                                elif r_json.get("data") and isinstance(r_json["data"], dict):
                                    num_str = str(r_json["data"].get("number", "") or r_json["data"].get("no_plus_number", "")).replace("+", "").strip()
                                if num_str:
                                    raw_mno_num = num_str
                                    sorted_ccs = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
                                    clean_q = query.replace("+", "").strip()
                                    for cc in sorted_ccs:
                                        if clean_q.startswith(cc):
                                            if not num_str.startswith(cc):
                                                num_str = cc + num_str
                                            break
                                    fetched_nums.append(num_str)
                                    mino_assigned_numbers[num_str] = chat_id
                                    mino_assigned_numbers[raw_mno_num] = chat_id
                                    break
                            except: continue

                elif provider == "zenex":
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in bot_settings.get("zenex_keys", []):
                            try:
                                res = requests.post(f"{ZENEX_BASE_URL}/v1/getnum", json={"range": query, "is_national": False, "remove_plus": False}, headers={"mapikey": api_key}, timeout=10)
                                if res.json().get("meta", {}).get("code") == 200 and res.json().get("data"):
                                    num_str = str(res.json()["data"].get("full_number", "")).replace("+", "")
                                    if not num_str: num_str = str(res.json()["data"].get("number", "")).replace("+", "")
                                    fetched_nums.append(num_str)
                                    zenex_assigned_numbers[num_str] = chat_id 
                                    break
                            except: continue
                elif provider == "voltx":
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in bot_settings.get("voltx_keys", []):
                            try:
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json={"rid": query}, headers={"mauthapi": api_key}, timeout=10)
                                if res.json().get("meta", {}).get("code") == 200 and res.json().get("data"):
                                    num_str = str(res.json()["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(res.json()["data"].get("national_number", "")).replace("+", "")
                                    fetched_nums.append(num_str)
                                    voltx_assigned_numbers[num_str] = chat_id 
                                    break
                            except: continue
                elif provider == "stex":
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in bot_settings.get("stex_keys", []):
                            try:
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers={"mauthapi": api_key}, timeout=10)
                                if res.json().get("meta", {}).get("code") == 200 and res.json().get("data"):
                                    num_str = str(res.json()["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(res.json()["data"].get("national_number", "")).replace("+", "")
                                    fetched_nums.append(num_str)
                                    stex_assigned_numbers[num_str] = chat_id 
                                    break
                            except: continue
                
                if not fetched_nums:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Number out of stock!"), reply_markup=main_menu(chat_id))
                    return
                
                total_assigned_stats += len(fetched_nums)
                save_db()
                
                app_full_name, prem_app_html = get_service_info_html(service_from_link)
                kb = []
                flags_db = bot_settings.get("premium_flags", {})
                country_emoji_html, country_full_name, iso_code = "", "Unknown", "XX"
                
                for num in fetched_nums:
                    char_flag, iso = get_flag_and_code(num)
                    iso_code = iso
                    display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                    flag_emoji_id = "5780471598922337683"
                    for _, flag_data in flags_db.items():
                        if iso == flag_data.get("iso"):
                            if "id" in flag_data: flag_emoji_id = flag_data["id"]
                            country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                            country_full_name = flag_data.get("name", iso)
                            break
                    if not country_emoji_html: country_emoji_html = char_flag
                    if country_full_name == "Unknown": country_full_name = iso_code
                    kb.append([{"text": f"{display_num}", "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": "primary"}])
                
                vtx_ext = "_vtx" if provider == "voltx" else "_znx" if provider == "zenex" else ""
                srv_ext = f"_{service_from_link}"
                for c_b in bot_settings["custom_messages"].get("search_number", {}).get("buttons", []): 
                    b_copy = c_b.copy()
                    if "style" not in b_copy: b_copy["style"] = "primary"
                    kb.append([b_copy])
                    
                kb.append([
                    {"text": "COUNTRY", "icon_custom_emoji_id": "5987629038523392103", "callback_data": f"g_s_{service_from_link}", "style": "danger"},
                    {"text": "REFRESH", "icon_custom_emoji_id": "5987671562994590370", "callback_data": f"c_n_s_{query}{srv_ext}{vtx_ext}", "style": "success"}
                ])
                kb.append([{"text": "REMOVE CC", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "toggle_cc_off", "style": "danger"}])
                kb.append([{"text": "OTP GROUP", "icon_custom_emoji_id": "5246848468177143690", "url": bot_settings["otp_link"], "style": "primary"}])
                
                formatted_msg = build_live_number_text(prem_app_html, app_full_name, country_emoji_html, country_full_name, iso_code, False, False, fetched_nums)
                text_numbers = render_body_text(formatted_msg)
                if wait_msg_id: edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
                else:
                    msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
                    if msg_res and "result" in msg_res: wait_msg_id = msg_res["result"]["message_id"]
                user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums, "text": text_numbers, "kb": kb}
                return
            except Exception as e:
                pass
        
        # --- PROCESS PENDING REFERRAL ---
        if db:
            doc = db.collection('users').document(str(chat_id)).get()
            if doc.exists:
                u_data = doc.to_dict()
                if u_data.get("referred_by") and not u_data.get("ref_paid"):
                    inviter = u_data["referred_by"]
                    db.collection('users').document(str(chat_id)).update({"ref_paid": True})
                    reward = bot_settings.get("refer_reward", 0.2)
                    update_balance(inviter, reward)
                    db.collection('users').document(str(inviter)).update({"total_refers": firestore.Increment(1)})
                    if inviter in user_cache:
                        user_cache[inviter]["total_refers"] = user_cache[inviter].get("total_refers", 0) + 1
                    ref_msg = (
                        f"{PEM['gift']} <b>New Referral !</b>\n"
                        f"------------------\n"
                        f"🔥 <b>You Received {reward} TK</b>\n"
                        f"------------------\n"
                        f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                    )
                    send_message(inviter, render_body_text(ref_msg))
                    
        c_msg = bot_settings["custom_messages"].get("start", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['hi']} Welcome!"))
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        
        if kb:
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['gear']} Navigation Menu:"), reply_markup=main_menu(chat_id))
        else:
            send_message(chat_id, txt, reply_markup=main_menu(chat_id))
            
    elif text in ["𝗧𝗥𝗔𝗙𝗙𝗜𝗖", "TRAFFIC"]:
        txt, markup = build_traffic_ui()
        send_message(chat_id, txt, reply_markup=markup)
        
    elif text in ["𝗟𝗘𝗔𝗗𝗘𝗥𝗕𝗢𝗔𝗥𝗗", "LEADERBOARD", "𝗧𝗢𝗗𝗔𝗬 𝗟𝗘𝗔𝗗𝗘𝗥𝗕𝗢𝗔𝗥𝗗", "TODAY LEADERBOARD"]:
        wait_msg = send_message(chat_id, render_body_text("⌛ <i>Fetching Leaderboard...</i>"))
        wait_msg_id = wait_msg.get("result", {}).get("message_id") if wait_msg else None
        
        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            # শুধুমাত্র লোকাল ক্যাশ থেকে আজকের ডেটা নেওয়া হচ্ছে
            valid_users = [u for u in user_cache.values() if u.get('last_otp_date') == today_str]
            sorted_users = sorted(valid_users, key=lambda x: x.get('today_otps', 0), reverse=True)
            top_users = sorted_users[:5]
                
            res_txt = ""
            count = 1
            num_map = {1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣"}
            
            for d in top_users:
                if d.get('today_otps', 0) > 0:
                    uid = d.get('user_id')
                    chat_info = api_call("getChat", {"chat_id": uid})
                    name = str(uid)
                    if chat_info.get("ok"):
                        name = chat_info["result"].get("first_name", "").strip() or str(uid)
                        
                    rank_emoji = num_map.get(count, f"{count}️⃣")
                    res_txt += f"<blockquote>{rank_emoji} <a href='tg://openmessage?user_id={uid}'>{name}</a> - {d.get('today_otps', 0)} OTP</blockquote>\n"
                    count += 1
                
            if not res_txt:
                res_txt = "<blockquote><i>No data found for today.</i></blockquote>\n"
                
            final_msg = f"📊 <b>𝗧𝗢𝗣 𝟱 𝗟𝗘𝗔𝗗𝗘𝗥𝗕𝗢𝗔𝗥𝗗 (TODAY)</b>\n━━━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━━━"
            
            if wait_msg_id:
                edit_message(chat_id, wait_msg_id, render_body_text(final_msg))
            else:
                send_message(chat_id, render_body_text(final_msg))
                
        except Exception as e:
            if wait_msg_id:
                edit_message(chat_id, wait_msg_id, render_body_text("❌ Error fetching leaderboard."))
        
    elif text in ["𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟", "REFERRAL"]:
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        
        raw_txt = (
            f"🎁 𝚁𝙴𝙵𝙴𝚁𝚁𝙰𝙻 𝙿𝚁𝙾𝙶𝚁𝙰𝙼\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔗 𝚈𝙾𝚄𝚁 𝙸𝙽𝚅𝙸𝚃𝙴 𝙻𝙸𝙽𝙺:\n\n"
            f"<code>{ref_link}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<blockquote>💬 𝚁𝙴𝙵𝙴𝚁𝚁𝙰𝙻 𝙾𝚃𝙿 : {u_data.get('referral_otps', 0)}</blockquote>\n"
            f"<blockquote><tg-emoji emoji-id=\"5420145051336485498\">👥</tg-emoji> 𝚃𝙾𝚃𝙰𝙻 𝙸𝙽𝚅𝙸𝚃𝙴𝚂 : {u_data.get('total_refers', 0)}</blockquote>\n"
            f"<blockquote>💸 𝚁𝙴𝚆𝙰𝚁𝙳 𝙿𝙴𝚁 𝙸𝙽𝚅𝙸𝚃𝙴 : {bot_settings['refer_reward']} 𝚃𝙺</blockquote>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💎 𝙸𝙽𝚅𝙸𝚃 𝙼𝙾𝚁𝙴 • 𝙴𝙰𝚁𝙽 𝙼𝙾𝚁𝙴"
        )
        txt = render_body_text(raw_txt)
        
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text in ["𝗠𝗬 𝗜𝗡𝗙𝗢", "MY INFO"]:
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        ws_count = sum(1 for uid in ws_linked_numbers.values() if str(uid) == str(chat_id))
        u_data["total_ws_added"] = ws_count
        
        c_msg = bot_settings.get("custom_messages", {}).get("withdrawal", {})
        raw_txt = (
            f"➖➖➖➖➖➖➖➖\n"
            f"《 😒 𝙼𝚈 𝙸𝙽𝙵𝙾 》\n"
            f"➖➖➖➖➖➖➖➖\n"
            f"<blockquote>🆔 𝚄𝚂𝙴𝚁 𝙸𝙳 : <code>{chat_id}</code></blockquote>\n"
            f"<blockquote>🔥 𝙾𝚃𝙿 𝚁𝙴𝙲𝙴𝙸𝚅𝙴𝙳 : {u_data.get('total_otps', 0)} 𝚃𝙾𝚃𝙰𝙻</blockquote>\n"
            f"<blockquote>🫂 𝚃𝙾𝚃𝙰𝙻 𝚁𝙴𝙵𝙴𝚁 : {u_data.get('total_refers', 0)}</blockquote>\n"
            f"<blockquote>📅 𝙱𝙰𝙻𝙰𝙽𝙲𝙴 : {bal:.2f}৳</blockquote>\n"
            f"<blockquote><tg-emoji emoji-id=\"5987961773934780806\">💬</tg-emoji> 𝚆𝚂 𝙰𝙳𝙳𝙴𝙳 : {ws_count} 𝚃𝙾𝚃𝙰𝙻</blockquote>\n"
            f"➖➖➖➖➖➖➖➖"
        )
        txt = render_body_text(raw_txt)
        
        kb = [
            [{"text": "WITHDRAW", "icon_custom_emoji_id": "5312441427764989435", "callback_data": "start_withdraw", "style": "success"}],
            [{"text": "REFERRAL", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "open_referral", "style": "primary"}]
        ]
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text in ["𝗦𝗘𝗧 𝗖𝗛𝗘𝗖𝗞𝗘𝗥", "SET CHECKER"]:
        if not is_checker_api_valid():
            close_kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            send_message(chat_id, render_body_text("❌ <b>Checker is currently OFF!</b>"), reply_markup=close_kb)
            return
        cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}
        txt = "💬 <b>LINK WHATSAPP ACCOUNT</b>\n\n📝 Please send your WhatsApp Number with country code.\n\n<i>Example: +8801712345678</i>"
        sent = send_message(chat_id, render_body_text(txt), reply_markup=cancel_kb)
        sent_msg_id = sent.get("result", {}).get("message_id") if sent else None
        user_states[chat_id] = "wait_for_ws_link_number"
        temp_data[chat_id] = {"msg_id": sent_msg_id}

    elif text in ["𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟", "ADMIN PANEL"] and is_admin(chat_id):
        send_message(chat_id, get_admin_text(), reply_markup=admin_panel_keyboard())

    elif text in ["𝗚𝗘𝗧 𝗡𝗨𝗠𝗕𝗘𝗥", "GET NUMBER"]:
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        stex_srvs = set(bot_settings.get("stex_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        zenex_srvs = set(bot_settings.get("zenex_services", {}).keys())
        mino_srvs = set(bot_settings.get("mino_services", {}).keys())
        all_services = local_srvs.union(stex_srvs).union(voltx_srvs).union(zenex_srvs).union(mino_srvs)
        
        if not all_services:
            send_message(chat_id, render_body_text(f"{PEM['no']} No numbers or services available!"))
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
            
            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            temp_row = []
            for s in all_services:
                emoji_id = "5987557149360792425" # Default icon
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data:
                            emoji_id = app_data["id"]
                            break
                temp_row.append({"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"})
                if len(temp_row) == 2:
                    kb.append(temp_row)
                    temp_row = []
            if temp_row:
                kb.append(temp_row)
            
            for b in c_msg.get("buttons", []): 
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text in ["𝗚𝗘𝗧 𝟮𝗙𝗔", "GET 2FA", "🔐 𝗚𝗘𝗧 𝟮𝗙𝗔"]:
        txt = "━━━━━━━━━━━━━━━\n🔐 <b>𝟮𝗙𝗔 𝗢𝗡𝗟𝗜𝗡𝗘</b>\n━━━━━━━━━━━━━━━\n\n🚀 Generate your 2FA security code instantly\nusing your secret key.\n\n━━━━━━━━━━━━━━━\n🛡️ <b>𝗦𝗘𝗖𝗨𝗥𝗘 • 𝗙𝗔𝗦𝗧 • 𝗥𝗘𝗟𝗜𝗔𝗕𝗟𝗘</b>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘 𝟮𝗙𝗔 𝗖𝗢𝗗𝗘", "icon_custom_emoji_id": "5445095448366823628", "callback_data": "gen_2fa", "style": "danger"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "primary"}]]
        send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

def expire_previous_number(chat_id):
    if chat_id in user_active_sessions:
        prev_data = user_active_sessions[chat_id]
        prev_msg_id = prev_data["msg_id"]
        nums = prev_data["nums"]
        
        # API সিস্টেম থেকে রিমুভ করা যাতে ইনবক্সে আর মেসেজ না যায়
        for num in nums:
            if num in stex_assigned_numbers: del stex_assigned_numbers[num]
            if num in voltx_assigned_numbers: del voltx_assigned_numbers[num]
            if num in zenex_assigned_numbers: del zenex_assigned_numbers[num]
            if num in mino_assigned_numbers: del mino_assigned_numbers[num]
        save_db()
        
        # আগের মেসেজ ইডিট করে Expired বাটন বসানো
        kb = [[{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}]]
        try:
            edit_message(chat_id, prev_msg_id, "NEW NUMBER\n", reply_markup={"inline_keyboard": kb})
        except:
            pass
        del user_active_sessions[chat_id]

# ==========================================
# Callback Query Handler
# ==========================================
def handle_callback(call):
    global total_assigned_stats
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")

    # 🌟 Button Loading Fix: বাটন চাপার সাথে সাথেই টেলিগ্রামকে Response দিয়ে দেওয়া, যাতে বাটন আটকে না থাকে!
    if not data.startswith("test_p_conn_") and not data.startswith("c_n_") and not data.startswith("g_c_") and not data.startswith("sel_wm_"):
        try: threading.Thread(target=answer_callback, args=(call["id"],)).start()
        except: pass

    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return

    msg_id = call["message"]["message_id"]

    if chat_type == "private":
        if is_user_banned(chat_id):
            answer_callback(call["id"], "🚫 You are banned from using this bot!", show_alert=True)
            return

        if not check_force_join(chat_id) and data != "check_fj":
            send_force_join_msg(chat_id)
            return

    if data == "check_fj":
        if check_force_join(chat_id):
            delete_message(chat_id, msg_id)
            send_message(chat_id, render_body_text(f"{PEM['ok']}𝗩𝗘𝗥𝗜𝗙𝗜𝗖𝗔𝗧𝗜𝗢𝗡 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟"), reply_markup=main_menu(chat_id))
            
            # --- PROCESS PENDING REFERRAL ---
            if db:
                doc = db.collection('users').document(str(chat_id)).get()
                if doc.exists:
                    u_data = doc.to_dict()
                    if u_data.get("referred_by") and not u_data.get("ref_paid"):
                        inviter = u_data["referred_by"]
                        db.collection('users').document(str(chat_id)).update({"ref_paid": True})
                        reward = bot_settings.get("refer_reward", 0.2)
                        update_balance(inviter, reward)
                        db.collection('users').document(str(inviter)).update({"total_refers": firestore.Increment(1)})
                        if inviter in user_cache:
                            user_cache[inviter]["total_refers"] = user_cache[inviter].get("total_refers", 0) + 1
                        ref_msg = (
                            f"{PEM['gift']} <b>New Referral !</b>\n"
                            f"------------------\n"
                            f"🔥 <b>You Received {reward} TK</b>\n"
                            f"------------------\n"
                            f"{PEM['user']} <b>From User ID:</b> <code>{chat_id}</code>"
                        )
                        send_message(inviter, render_body_text(ref_msg))
        else:
            answer_callback(call["id"], "❌ You haven't joined all channels yet!", show_alert=True)
        return

    if data == "close_msg":
        delete_message(chat_id, msg_id)
        
    elif data == "start_withdraw":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        
        if not bot_settings.get("withdraw_on", True):
            answer_callback(call["id"], "❌ Withdrawals are currently disabled.", show_alert=True)
            return
            
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        min_w = bot_settings.get('min_withdraw', 30.0)
        
        # নতুন টেক্সট সম্পূর্ণ কোট (blockquote) ফরম্যাটে
        raw_txt = (f"<blockquote>🆔 𝚄𝚂𝙴𝚁 𝙸𝙳 : <code>{chat_id}</code>\n\n"
                   f"💸 𝙼𝙸𝙽 𝚆𝙸𝚃𝙷𝙳𝚁𝙰𝚆 : {min_w}৳\n\n"
                   f"📅 𝙱𝙰𝙻𝙰𝙽𝙲𝙴 : {bal:.2f}৳\n\n"
                   f"💳 𝙿𝙻𝙴𝙰𝚂𝙴 𝚂𝙴𝙻𝙴𝙲𝚃 𝙰 𝙼𝙴𝚃𝙷𝙾𝙳</blockquote>")
        txt = render_body_text(raw_txt)
        
        kb = []
        styles = ["primary", "success", "danger"]
        temp_row = []
        for i, m in enumerate(bot_settings.get("w_methods", ["bKash", "Nagad"])):
            temp_row.append({"text": m.strip(), "icon_custom_emoji_id": "5988050370520161591", "callback_data": f"sel_wm_{m.strip()}", "style": styles[i % 3]})
            if len(temp_row) == 2:
                kb.append(temp_row)
                temp_row = []
        if temp_row:
            kb.append(temp_row)
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_info", "style": "danger"}])
        
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])
        
    elif data == "back_to_info":
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        ws_count = sum(1 for uid in ws_linked_numbers.values() if str(uid) == str(chat_id))
        u_data["total_ws_added"] = ws_count
        
        c_msg = bot_settings.get("custom_messages", {}).get("withdrawal", {})
        raw_txt = (
            f"➖➖➖➖➖➖➖➖\n"
            f"《 😒 𝙼𝚈 𝙸𝙽𝙵𝙾 》\n"
            f"➖➖➖➖➖➖➖➖\n"
            f"<blockquote>🆔 𝚄𝚂𝙴𝚁 𝙸𝙳 : <code>{chat_id}</code></blockquote>\n"
            f"<blockquote>🔥 𝙾𝚃𝙿 𝚁𝙴𝙲𝙴𝙸𝚅𝙴𝙳 : {u_data.get('total_otps', 0)} 𝚃𝙾𝚃𝙰𝙻</blockquote>\n"
            f"<blockquote>🫂 𝚃𝙾𝚃𝙰𝙻 𝚁𝙴𝙵𝙴𝚁 : {u_data.get('total_refers', 0)}</blockquote>\n"
            f"<blockquote>📅 𝙱𝙰𝙻𝙰𝙽𝙲𝙴 : {bal:.2f}৳</blockquote>\n"
            f"<blockquote><tg-emoji emoji-id=\"5987961773934780806\">💬</tg-emoji> 𝚆𝚂 𝙰𝙳𝙳𝙴𝙳 : {ws_count} 𝚃𝙾𝚃𝙰𝙻</blockquote>\n"
            f"➖➖➖➖➖➖➖➖"
        )
        txt = render_body_text(raw_txt)
        
        kb = [
            [{"text": "WITHDRAW", "icon_custom_emoji_id": "5312441427764989435", "callback_data": "start_withdraw", "style": "success"}],
            [{"text": "REFERRAL", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "open_referral", "style": "primary"}]
        ]
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "open_referral":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        
        raw_txt = (
            f"🎁 𝚁𝙴𝙵𝙴𝚁𝚁𝙰𝙻 𝙿𝚁𝙾𝙶𝚁𝙰𝙼\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🔗 𝚈𝙾𝚄𝚁 𝙸𝙽𝚅𝙸𝚃𝙴 𝙻𝙸𝙽𝙺:\n\n"
            f"<code>{ref_link}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<blockquote>💬 𝚁𝙴𝙵𝙴𝚁𝚁𝙰𝙻 𝙾𝚃𝙿 : {u_data.get('referral_otps', 0)}</blockquote>\n"
            f"<blockquote><tg-emoji emoji-id=\"5420145051336485498\">👥</tg-emoji> 𝚃𝙾𝚃𝙰𝙻 𝙸𝙽𝚅𝙸𝚃𝙴𝚂 : {u_data.get('total_refers', 0)}</blockquote>\n"
            f"<blockquote>💸 𝚁𝙴𝚆𝙰𝚁𝙳 𝙿𝙴𝚁 𝙸𝙽𝚅𝙸𝚃𝙴 : {bot_settings['refer_reward']} 𝚃𝙺</blockquote>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💎 𝙸𝙽𝚅𝙸𝚃 𝙼𝙾𝚁𝙴 • 𝙴𝙰𝚁𝙽 𝙼𝙾𝚁𝙴"
        )
        txt = render_body_text(raw_txt)
        
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_info", "style": "danger"}])
        
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "set_checker":
        if not is_checker_api_valid():
            answer_callback(call["id"], "❌ Checker is currently OFF!", show_alert=True)
            return
        user_states[chat_id] = "wait_for_ws_link_number"
        temp_data[chat_id] = {"msg_id": msg_id}
        
        cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_info", "style": "danger"}]]}
        text = "💬 <b>LINK WHATSAPP ACCOUNT</b>\n\n📝 Please send your WhatsApp Number with country code.\n\n<i>Example: +8801712345678</i>"
        
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=cancel_kb)
        answer_callback(call["id"])

    elif data == "connect_ws_from_num":
        if not is_checker_api_valid():
            answer_callback(call["id"], "❌ Checker is currently OFF!", show_alert=True)
            return
        cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}
        text = "💬 <b>LINK WHATSAPP ACCOUNT</b>\n\n📝 Please send your WhatsApp Number with country code.\n\n<i>Example: +8801712345678</i>"
        sent = send_message(chat_id, render_body_text(text), reply_markup=cancel_kb)
        sent_msg_id = sent.get("result", {}).get("message_id") if sent else msg_id
        user_states[chat_id] = "wait_for_ws_link_number"
        temp_data[chat_id] = {"msg_id": sent_msg_id}
        answer_callback(call["id"])

    elif data in ["toggle_cc_off", "toggle_cc_on"]:
        sess = user_active_sessions.get(chat_id)
        if not sess or "kb" not in sess or "nums" not in sess:
            answer_callback(call["id"], "❌ Session expired! Please get new numbers.", show_alert=True)
            return

        remove_cc = (data == "toggle_cc_off")
        kb = sess["kb"]
        nums = sess["nums"]

        for i, raw_num in enumerate(nums):
            if i < len(kb) and len(kb[i]) > 0:
                clean_num = re.sub(r'\D', '', str(raw_num))
                with_cc = f"+{clean_num}"
                without_cc = strip_country_code(clean_num)
                btn_obj = kb[i][0]
                old_text = btn_obj.get("text", "")
                parts = old_text.split(" ", 1)
                suffix = f" {parts[1]}" if len(parts) > 1 else ""
                new_num_display = without_cc if remove_cc else with_cc
                btn_obj["text"] = f"{new_num_display}{suffix}"
                btn_obj["copy_text"] = {"text": new_num_display}

        for row in kb:
            for btn_obj in row:
                if btn_obj.get("callback_data") in ["toggle_cc_off", "toggle_cc_on"]:
                    if remove_cc:
                        btn_obj["text"] = "ADD CC"
                        btn_obj["icon_custom_emoji_id"] = "5987751449386296261"
                        btn_obj["callback_data"] = "toggle_cc_on"
                        btn_obj["style"] = "primary"
                    else:
                        btn_obj["text"] = "REMOVE CC"
                        btn_obj["icon_custom_emoji_id"] = "5420130255174145507"
                        btn_obj["callback_data"] = "toggle_cc_off"
                        btn_obj["style"] = "danger"

        edit_message(chat_id, msg_id, sess.get("text", "LIVE NUMBER"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])
        
    elif data == "cancel_state":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        delete_message(chat_id, msg_id)

    elif data == "cancel_2fa":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        txt = "━━━━━━━━━━━━━━━\n🔐 <b>𝟮𝗙𝗔 𝗢𝗡𝗟𝗜𝗡𝗘</b>\n━━━━━━━━━━━━━━━\n\n🚀 Generate your 2FA security code instantly\nusing your secret key.\n\n━━━━━━━━━━━━━━━\n🛡️ <b>𝗦𝗘𝗖𝗨𝗥𝗘 • 𝗙𝗔𝗦𝗧 • 𝗥𝗘𝗟𝗜𝗔𝗕𝗟𝗘</b>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘 𝟮𝗙𝗔 𝗖𝗢𝗗𝗘", "icon_custom_emoji_id": "5445095448366823628", "callback_data": "gen_2fa", "style": "danger"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "gen_2fa":
        user_states[chat_id] = "wait_for_2fa_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━"
        kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
        answer_callback(call["id"])

    elif data.startswith("ref_2fa_"):
        secret = data.replace("ref_2fa_", "")
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            remaining_time = 30 - (int(time.time()) % 30)
            
            success_txt = (
                f"━━━━━━━━━━━━━━━\n"
                f"《 🔐 <b>2FA CODE</b> 》\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                f"━━━━━━━━━━━━━━━"
            )
            kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                  [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                   {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                  [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
            
            edit_message(chat_id, msg_id, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
        except:
            answer_callback(call["id"], "❌ Error refreshing code!", show_alert=True)

    elif data == "cancel_dxa_edit":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
        
    elif data == "dummy_alert":
        answer_callback(call["id"], "This feature will be added later!", show_alert=True)
        
    elif data == "refresh_traffic":
        txt, markup = build_traffic_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        answer_callback(call["id"], "✅ Traffic Refreshed!", show_alert=False)

    elif data.startswith("exp_rng_"):
        srv_query = data.replace("exp_rng_", "")
        
        country_stats = {}
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query):
                    iso = t.get("iso", "XX")
                    flag = t.get("flag", "🌍")
                    if iso not in country_stats:
                        country_stats[iso] = {"count": 0, "flag": flag}
                    country_stats[iso]["count"] += 1
        
        if not country_stats:
            answer_callback(call["id"], "❌ No recent traffic found for this service!", show_alert=True)
            return
            
        kb = []
        temp_row = []
        for iso, c_data in sorted(country_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            count = c_data["count"]
            emoji_id = "5780471598922337683"
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    if "id" in fdata: emoji_id = fdata["id"]
                    break
            
            # LAWRA 
            btn_text = f"{iso} ➠ {count} OTP"
            temp_row.append({"text": btn_text, "icon_custom_emoji_id": emoji_id, "callback_data": f"exp_c_{srv_query}_{iso}", "style": "primary"})
            if len(temp_row) == 2:
                kb.append(temp_row)
                temp_row = []
        if temp_row:
            kb.append(temp_row)
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "refresh_traffic", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Explore Service: {prem_app_html} {app_full_name}</b>\n\nSelect a country to view available ranges:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("exp_c_"):
        parts = data.split("_")
        srv_query = parts[2]
        iso_query = parts[3]
        
        nums = []
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query) and t.get("iso") == iso_query:
                    # 🌟 X রিমুভ করে ক্লিন রেঞ্জ নেওয়া হলো
                    num = t.get("real_range", t.get("number", "").replace("X", "").replace("x", "")).replace("+", "").strip()
                    if num: nums.append(num)
        
        if not nums:
            answer_callback(call["id"], "❌ No recent numbers found for this country!", show_alert=True)
            return
            
        # শুধুমাত্র StexSMS Services থেকে রেঞ্জ নিবো (Search Countries নিবো না, কারণ ওগুলোতে শুধু দেশের কোড থাকে)
        known_ranges = set()
        for s_name, c_dict in bot_settings.get("stex_services", {}).items():
            for c_name, r_list in c_dict.items():
                for r in r_list:
                    # 🌟 এখানেও সেভ করা রেঞ্জ থেকে X সরিয়ে নিচ্ছি
                    known_ranges.add(r.replace("X", "").replace("x", ""))
                    
        sorted_known = sorted(list(known_ranges), key=len, reverse=True)
        
        r_counts = Counter()
        for num in nums:
            matched = False
            for r in sorted_known:
                if num.startswith(r):
                    r_counts[r] += 1
                    matched = True
                    break
            if not matched:
                if len(num) >= 7:
                    r_counts[num[:7]] += 1
                else:
                    r_counts[num] += 1
                    
        r_list = r_counts.most_common(12)
        
        kb = []
        temp_row = []
        for r, count in r_list:
            # 🌟 বাটনে এবং কলব্যাকে যাতে কোনো X না থাকে তা নিশ্চিত করা হলো
            clean_r = str(r).replace("X", "").replace("x", "")
            temp_row.append({"text": f"{clean_r} ({count})", "icon_custom_emoji_id": "5303214794336125778", "callback_data": f"c_n_s_{clean_r}_{srv_query}", "style": "primary"})
            if len(temp_row) == 2:
                kb.append(temp_row)
                temp_row = []
        if temp_row:
            kb.append(temp_row)
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_rng_{srv_query}", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        prem_flag_html = get_flag_info_html(iso_query)
        
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Ranges for {prem_app_html} {app_full_name} - {prem_flag_html} {iso_query}</b>\n\nClick on any range to copy it."), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    # --- User Management Flows Integration ---
    elif data == "user_management":
        edit_message(chat_id, msg_id, get_user_management_text(), reply_markup=user_management_keyboard())

    elif data == "um_manage_balance":
        user_states[chat_id] = "wait_for_um_bal_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Manage Balance:"), reply_markup=get_cancel_kb())
        
    elif data == "um_ban_unban":
        user_states[chat_id] = "wait_for_um_ban_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Ban or Unban:"), reply_markup=get_cancel_kb())

    elif data == "um_user_profile":
        user_states[chat_id] = "wait_for_um_prof_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to View Profile:"), reply_markup=get_cancel_kb())

    # --- Menu Design Integration ---
    elif data == "menu_design_list":
        edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Menu Design Editor</b>\n\nSelect a menu block to edit its Body Text and Inline Buttons. You can use Premium Emojis too!"), reply_markup=menu_design_list_keyboard())

    elif data == "md_reset_defaults":
        bot_settings["custom_messages"] = DEFAULT_CUSTOM_MESSAGES.copy()
        save_db()
        answer_callback(call["id"], "✅ Resetted to Premium Defaults!", show_alert=True)

    elif data.startswith("md_edit_"):
        answer_callback(call["id"])
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_edit_", "")
        cm_text = render_body_text(bot_settings["custom_messages"].get(key, {}).get("text", "..."))
        try:
            edit_message(chat_id, msg_id, render_body_text(f"🎨 <b>Editing: {key.upper()}</b>\n\nPreview of current Text:\n{cm_text}"), reply_markup=menu_edit_options_keyboard(key))
        except: pass

    elif data.startswith("md_text_"):
        key = data.replace("md_text_", "")
        user_states[chat_id] = "wait_for_menu_text"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"📝 <b>Edit Body: {key.upper()}</b>\n\nSend the new text. You can use Premium Emojis directly here.\n(Use standard HTML like <b>bold</b>, <i>italic</i> for formatting)"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_edit_{key}", "style": "danger"}]]})

    elif data.startswith("md_btns_"):
        answer_callback(call["id"]) 
        if chat_id in user_states: del user_states[chat_id] 
        if chat_id in temp_data: del temp_data[chat_id]
        key = data.replace("md_btns_", "")
        try:
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))
        except: pass

    elif data.startswith("md_addbtn_"):
        key = data.replace("md_addbtn_", "")
        user_states[chat_id] = "wait_for_menu_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "menu_key": key}
        edit_message(chat_id, msg_id, render_body_text(f"➕ <b>Add Button: {key.upper()}</b>\n\nSend custom button in this format:\n<code>Button Text - https://link.com</code>\n\n<i>(Only normal Emojis supported here!)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"md_btns_{key}", "style": "danger"}]]})

    elif data.startswith("md_delbtn_"):
        parts = data.split("_")
        key = parts[2]
        b_idx = int(parts[3])
        if b_idx < len(bot_settings["custom_messages"][key]["buttons"]):
            del bot_settings["custom_messages"][key]["buttons"][b_idx]
            save_db()
            answer_callback(call["id"], "✅ Button Deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"⚙️ <b>Edit Inline Buttons: {key.upper()}</b>"), reply_markup=menu_buttons_list_keyboard(key))

    elif data.startswith("sel_wm_"):
        method = data.replace("sel_wm_", "")
        bal = get_user(chat_id).get('balance', 0.0)
        min_w = bot_settings['min_withdraw']
        
        if bal < min_w:
            answer_callback(call["id"], f"❌ Insufficient Balance! Minimum {min_w} ৳ required.", show_alert=True)
            return
            
        temp_data[chat_id] = {"method": method, "balance": bal, "msg_id": msg_id}
        user_states[chat_id] = "wait_for_withdraw_amount"
        
        # 🌟 Cancel এর বদলে Back বাটন দেওয়া হলো যা start_withdraw তে ফিরে যাবে
        back_kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "start_withdraw", "style": "danger"}]]}
        
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} Method: {method}\n💰 Available Balance: {bal} ৳\n\n📝 Enter the amount you want to withdraw (Min: {min_w} ৳):"), reply_markup=back_kb)
        answer_callback(call["id"])

    elif data == "test_message_flow":
        user_states[chat_id] = "wait_for_test_service"
        temp_data[chat_id] = {}
        edit_message(chat_id, msg_id, render_body_text("🧪 <b>Test Mode</b>\n\n📝 Send the Service Name (e.g., IG):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]]})

    elif data == "manage_emojis":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['star']} <b>Premium Emoji Management</b>\n\nUpload your TXT files or manually add them below:"), reply_markup=emoji_settings_keyboard())

    elif data == "up_flags_txt":
        user_states[chat_id] = "wait_for_flag_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Flag Emojis</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "up_apps_txt":
        user_states[chat_id] = "wait_for_app_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Service Apps</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "add_single_emoji":
        user_states[chat_id] = "wait_for_emoji_extract"
        edit_message(chat_id, msg_id, render_body_text("📝 যেকোনো একটি Premium Emoji সেন্ড করুন (যেমন: 🇧🇩 বা 🚫):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "dl_flags_txt":
        content = generate_emoji_txt("flags")
        if content:
            send_document(chat_id, "Flag_Emojis.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No Flag Emojis found!", show_alert=True)

    elif data == "dl_apps_txt":
        content = generate_emoji_txt("apps")
        if content:
            send_document(chat_id, "Service_Apps.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No App Emojis found!", show_alert=True)

    elif data == "del_all_flags":
        bot_settings["premium_flags"] = {}
        save_db()
        answer_callback(call["id"], "✅ All Premium Flags Deleted Successfully!", show_alert=True)

    elif data == "broadcast_msg":
        user_states[chat_id] = "wait_for_broadcast"
        edit_message(chat_id, msg_id, render_body_text("📢 <b>Broadcast Mode</b>\n\nSend the message you want to broadcast (Text, Photo, Video, File etc)."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "upload_num":
        user_states[chat_id] = "wait_for_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the numbers in a <b>.txt</b> file."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "upload_firebase":
        user_states[chat_id] = "wait_for_firebase_json"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload your Firebase <b>.json</b> key file."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "delete_files":
        kb = []
        for b_id, b_data in number_batches.items():
            kb.append([{"text": f"{b_data['filename']} ({len(b_data['numbers'])})", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_b_{b_id}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}])
        txt = "🗑 Select a file to delete:" if len(kb) > 1 else f"{PEM['no']} No files found."
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_b_"):
        b_id = data.split("del_b_")[1]
        if b_id in number_batches:
            del number_batches[b_id]
            save_db()
            answer_callback(call["id"], "✅ File deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "delete_files", "id": call["id"]})

    elif data == "show_used":
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_used", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Total Used Numbers:</b> {len(used_numbers_list)}"), reply_markup=kb)

    elif data == "show_unused":
        unused_count = sum(len(b["numbers"]) for b in number_batches.values())
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_unused", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['rocket']} <b>Total Unused Numbers:</b> {unused_count}"), reply_markup=kb)

    elif data == "dl_used":
        if not used_numbers_list:
            answer_callback(call["id"], "❌ No used numbers found!", show_alert=True)
            return
        content = "\n".join(used_numbers_list).encode('utf-8')
        send_document(chat_id, "used_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "dl_unused":
        unused_list = [n["num"] for b in number_batches.values() for n in b["numbers"]]
        if not unused_list:
            answer_callback(call["id"], "❌ No unused numbers found!", show_alert=True)
            return
        content = "\n".join(unused_list).encode('utf-8')
        send_document(chat_id, "unused_numbers.txt", content)
        answer_callback(call["id"])

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5987641605597699007", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get('amount',0)}৳</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5987641605597699007", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                users = db.collection('users').order_by(field, direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for u in users:
                    d = u.to_dict()
                    if d.get(field, 0) > 0:
                        p = "└" if count == limit else "├"
                        res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={u.id}'>{u.id}</a> ➔ <b>{d.get(field,0)}</b>\n"
                        count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                ws = db.collection('withdrawals').order_by('timestamp', direction="DESCENDING").limit(limit).stream()
                res_txt = ""
                count = 1
                for w in ws:
                    d = w.to_dict()
                    s = str(d.get('status','Pending')).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    uid = d.get('user_id','User')
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={uid}'>{uid}</a> ➔ <b>{d.get('amount',0)}৳</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "back_to_admin":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
        
    elif data == "manage_ws_tg_checker":
        api_url = bot_settings.get("master_api_url", "https://bot.orabitsms.site/api")
        api_key = bot_settings.get("master_api_key", "").strip()
        ws_added_local = len(ws_linked_numbers)

        if api_key and api_key != "Not Set":
            try:
                res = requests.get(f"{api_url}/user-status", params={"apiKey": api_key}, timeout=10)
                status_data = res.json() if res.status_code == 200 else {}
            except Exception:
                status_data = {}

            if isinstance(status_data, dict) and (status_data.get("apiKey") or status_data.get("status") == "connected" or "ActiveSessions" in status_data):
                disp_key = status_data.get("apiKey", api_key)
                ws_added = status_data.get("ActiveWhatsapp", status_data.get("totalSavedWhatsapp", ws_added_local))
                ws_limit_raw = status_data.get("Whatsapp_Checker_limit", "Unlimited")
                ws_limit = "Unlimited" if str(ws_limit_raw).lower() == "unlimited" else str(ws_limit_raw)
                tg_limit_avail = status_data.get("available_tg_limit", status_data.get("tg_limit", 0))

                exp_raw = (
                    status_data.get("api_expire")
                    or status_data.get("daysLeft")
                    or status_data.get("days_left")
                    or status_data.get("expire_days")
                    or status_data.get("expireDays")
                    or status_data.get("remainingDays")
                    or status_data.get("expire")
                    or status_data.get("expiryDate")
                )
                if exp_raw is not None:
                    exp_str = str(exp_raw).strip()
                    api_expire = f"{exp_str} Day Left" if exp_str.isdigit() else exp_str.title()
                else:
                    api_expire = "Unlimited"

                text = (
                    f"{PEM['gear']} <b>MANAGE CHECKER SYSTEM</b>\n\n"
                    f"🔑 <b>Api key :</b> <code>{disp_key}</code>\n\n"
                    f"<tg-emoji emoji-id=\"5987961773934780806\">💬</tg-emoji> <b>Whatsapp Added :</b> {ws_added}\n\n"
                    f"🟢 <b>Ws Checker Limit :</b> {ws_limit}\n\n"
                    f"⌛ <b>Api Key Expire :</b> {api_expire}"
                )
            else:
                text = (
                    f"{PEM['gear']} <b>MANAGE CHECKER SYSTEM</b>\n\n"
                    f"🔑 <b>Api key :</b> No Api Key Added\n\n"
                    f"<tg-emoji emoji-id=\"5987961773934780806\">💬</tg-emoji> <b>Whatsapp Added :</b> {ws_added_local}\n\n"
                    f"🟢 <b>Ws Checker Limit :</b> Add Api Key Frist\n\n"
                    f"⌛ <b>Api Key Expire :</b> Add Api Key Frist"
                )
        else:
            text = (
                f"{PEM['gear']} <b>MANAGE CHECKER SYSTEM</b>\n\n"
                f"🔑 <b>Api key :</b> No Api Key Added\n\n"
                f"<tg-emoji emoji-id=\"5987961773934780806\">💬</tg-emoji> <b>Whatsapp Added :</b> {ws_added_local}\n\n"
                f"🟢 <b>Ws Checker Limit :</b> Add Api Key Frist\n\n"
                f"⌛ <b>Api Key Expire :</b> Add Api Key Frist"
            )

        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=manage_checker_keyboard())

    elif data == "manage_api_key_menu":
        api_url = bot_settings.get("master_api_url", "https://bot.orabitsms.site/api")
        api_key = bot_settings.get("master_api_key", "Not Set")
        safe_key = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 10 else api_key
        text = f"<tg-emoji emoji-id='5197288647275071607'>🔑</tg-emoji> <b>API KEY MANAGEMENT</b>\n\n🌐 <b>URL:</b> <code>{api_url}</code>\n🔑 <b>KEY:</b> <code>{safe_key}</code>\n\nClick the button below to set or update your API Key:"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=manage_api_key_keyboard())
        answer_callback(call["id"])

    elif data == "set_master_api_key":
        user_states[chat_id] = "wait_for_master_api_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Send your Master API Key:</b>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_api_key_menu", "style": "danger"}]]})
        answer_callback(call["id"])

    elif data in ["ws_checker_menu", "tg_checker_menu"]:
        c_type = "ws" if data == "ws_checker_menu" else "tg"
        title = "WS CHECKER" if c_type == "ws" else "TG CHECKER"
        icon_id = "5987961773934780806" if c_type == "ws" else "5987728952347599001"
        text = f"<tg-emoji emoji-id='{icon_id}'>💬</tg-emoji> <b>{title} SETTINGS</b>\n\nManage your settings below:"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=checker_settings_keyboard(c_type))
        answer_callback(call["id"])

    elif data in ["toggle_ws", "toggle_tg"]:
        c_type = data.replace("toggle_", "")
        status_key = f"{c_type}_checker_on"
        bot_settings[status_key] = not bot_settings.get(status_key, False)
        save_db()
        title = "WS CHECKER" if c_type == "ws" else "TG CHECKER"
        icon_id = "5987961773934780806" if c_type == "ws" else "5987728952347599001"
        text = f"<tg-emoji emoji-id='{icon_id}'>💬</tg-emoji> <b>{title} SETTINGS</b>\n\nManage your settings below:"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=checker_settings_keyboard(c_type))
        answer_callback(call["id"])

    elif data.startswith("sel_srv_"):
        c_type = data.replace("sel_srv_", "")
        
        # বটের সমস্ত সার্ভিস লিস্ট একসাথে আনা হচ্ছে
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        stex_srvs = set(bot_settings.get("stex_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        zenex_srvs = set(bot_settings.get("zenex_services", {}).keys())
        all_services = local_srvs.union(stex_srvs).union(voltx_srvs).union(zenex_srvs)
        
        apps_db = bot_settings.get("premium_apps", {})
        kb = []
        temp_row = []
        for s in all_services:
            emoji_id = "5192739271886282680" # Default Service Icon
            for app_key, app_data in apps_db.items():
                if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
                        
            temp_row.append({"text": s, "icon_custom_emoji_id": emoji_id, "callback_data": f"c_set_s_{c_type}_{s}", "style": "primary"})
            if len(temp_row) == 2:
                kb.append(temp_row)
                temp_row = []
        if temp_row: kb.append(temp_row)
        
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"{c_type}_checker_menu", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("📝 <b>Select a Service for Checker:</b>"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("c_set_s_"):
        raw_data = data.replace("c_set_s_", "")
        c_type, srv = raw_data.split("_", 1)
        
        key = f"{c_type}_checker_services"
        if key not in bot_settings or not isinstance(bot_settings[key], list):
            bot_settings[key] = []
            
        if srv not in bot_settings[key]:
            bot_settings[key].append(srv)
            save_db()
            answer_callback(call["id"], f"✅ Service Added: {srv}", show_alert=False)
        else:
            answer_callback(call["id"], "⚠️ Service already added!", show_alert=True)
            
        handle_callback({"message": call["message"], "data": f"{c_type}_checker_menu", "id": call["id"]})

    elif data.startswith("c_del_s_"):
        raw_data = data.replace("c_del_s_", "")
        c_type, srv = raw_data.split("_", 1)
        key = f"{c_type}_checker_services"
        
        if key in bot_settings and isinstance(bot_settings[key], list):
            if srv in bot_settings[key]:
                bot_settings[key].remove(srv)
                save_db()
                answer_callback(call["id"], f"✅ Service Deleted: {srv}", show_alert=False)
                
        handle_callback({"message": call["message"], "data": f"{c_type}_checker_menu", "id": call["id"]})

    elif data.startswith("sel_file_"):
        c_type = data.replace("sel_file_", "")
        kb = []
        for b_id, b_data in number_batches.items():
            kb.append([{"text": f"{b_data['filename']} ({len(b_data['numbers'])})", "icon_custom_emoji_id": "5352721946054268944", "callback_data": f"c_set_f_{c_type}_{b_id}", "style": "primary"}])
        
        if not kb:
            answer_callback(call["id"], "❌ No local files uploaded yet!", show_alert=True)
            return
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"{c_type}_checker_menu", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("📁 <b>Select a Local File for Checker:</b>"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("c_set_f_"):
        raw_data = data.replace("c_set_f_", "")
        c_type, f_id = raw_data.split("_", 1)
        
        key = f"{c_type}_checker_files"
        if key not in bot_settings or not isinstance(bot_settings[key], list):
            bot_settings[key] = []
            
        if f_id not in bot_settings[key]:
            bot_settings[key].append(f_id)
            save_db()
            answer_callback(call["id"], "✅ File Added!", show_alert=False)
        else:
            answer_callback(call["id"], "⚠️ File already added!", show_alert=True)
            
        handle_callback({"message": call["message"], "data": f"{c_type}_checker_menu", "id": call["id"]})

    elif data.startswith("c_del_f_"):
        raw_data = data.replace("c_del_f_", "")
        c_type, f_id = raw_data.split("_", 1)
        key = f"{c_type}_checker_files"
        
        if key in bot_settings and isinstance(bot_settings[key], list):
            if f_id in bot_settings[key]:
                bot_settings[key].remove(f_id)
                save_db()
                answer_callback(call["id"], "✅ File Deleted!", show_alert=False)
                
        handle_callback({"message": call["message"], "data": f"{c_type}_checker_menu", "id": call["id"]})

    elif data == "system_settings":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>System Settings</b>\nManage advanced bot configurations below:"), reply_markup=system_settings_keyboard())

    elif data == "stex_control":
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your StexSMS API Keys below:"), reply_markup=stex_control_keyboard())

    elif data == "toggle_stex_auto":
        bot_settings["stex_auto"] = not bot_settings.get("stex_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"🌐 <b>StexSMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('stex_keys', []))}\nManage your StexSMS API Keys below:"), reply_markup=stex_control_keyboard())
        answer_callback(call["id"], f"✅ Stex Auto Range is now {'ON' if bot_settings['stex_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_stex_key":
        user_states[chat_id] = "wait_for_add_stex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new StexSMS API Key (e.g. nxa_...):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}]]})

    elif data == "view_stex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("stex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_nxa_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select StexSMS Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_nxa_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("stex_keys", [])):
            del bot_settings["stex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ StexSMS Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_stex_keys", "id": call["id"]})

    elif data == "stex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_sc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Allowed Search Countries:</b>\nOnly these country codes will be allowed in Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_search_country":
        user_states[chat_id] = "wait_for_add_sc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Country Code (e.g. 880 or 92):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_search_country", "style": "danger"}]]})

    elif data.startswith("del_sc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("search_countries", [])):
            del bot_settings["search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Country Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "stex_search_country", "id": call["id"]})

    elif data == "manage_stex_srv":
        kb = []
        srvs = bot_settings.get("stex_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "nx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "stex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("📦 <b>StexSMS Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "nx_add_srv":
        user_states[chat_id] = "wait_nx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_srv_"):
        srv = data.replace("nx_srv_", "")
        kb = []
        countries = bot_settings["stex_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"nx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5987751449386296261", "callback_data": f"nx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_stex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_add_cnt_"):
        srv = data.replace("nx_add_cnt_", "")
        user_states[chat_id] = "wait_nx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("nx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["stex_services"][srv].get(cnt, [])
        
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"nx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5987751449386296261", "callback_data": f"nx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"nx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_srv_{srv}", "style": "primary"}])
        
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("nx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_nx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 88017):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"nx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("nx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["stex_services"].get(srv, {}).get(cnt, []):
            bot_settings["stex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("nx_del_srv_"):
        srv = data.replace("nx_del_srv_", "")
        if srv in bot_settings["stex_services"]: del bot_settings["stex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_stex_srv", "id": call["id"]})

    elif data.startswith("nx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["stex_services"].get(srv, {}): del bot_settings["stex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"nx_srv_{srv}", "id": call["id"]})

    elif data == "voltx_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())

    elif data == "toggle_voltx_auto":
        bot_settings["voltx_auto"] = not bot_settings.get("voltx_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())
        answer_callback(call["id"], f"✅ Voltx Auto Range is now {'ON' if bot_settings['voltx_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_voltx_key":
        user_states[chat_id] = "wait_for_add_voltx_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Voltx API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}]]})

    elif data == "view_voltx_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("voltx_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vtx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Voltx Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_vtx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_keys", [])):
            del bot_settings["voltx_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_voltx_keys", "id": call["id"]})

    elif data == "voltx_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("voltx_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_voltx_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Voltx Allowed Ranges:</b>\nOnly these ranges/codes will be allowed in Voltx Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_voltx_search_country":
        user_states[chat_id] = "wait_for_add_vsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Voltx Range Code (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_search_country", "style": "danger"}]]})

    elif data.startswith("del_vsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_search_countries", [])):
            del bot_settings["voltx_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "voltx_search_country", "id": call["id"]})

    elif data == "manage_voltx_srv":
        kb = []
        srvs = bot_settings.get("voltx_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "vx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Voltx Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "vx_add_srv":
        user_states[chat_id] = "wait_vx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_srv_"):
        srv = data.replace("vx_srv_", "")
        kb = []
        countries = bot_settings["voltx_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5987751449386296261", "callback_data": f"vx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_voltx_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_add_cnt_"):
        srv = data.replace("vx_add_cnt_", "")
        user_states[chat_id] = "wait_vx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["voltx_services"][srv].get(cnt, [])
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"vx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5987751449386296261", "callback_data": f"vx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_vx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("vx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["voltx_services"].get(srv, {}).get(cnt, []):
            bot_settings["voltx_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("vx_del_srv_"):
        srv = data.replace("vx_del_srv_", "")
        if srv in bot_settings["voltx_services"]: del bot_settings["voltx_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_voltx_srv", "id": call["id"]})

    elif data.startswith("vx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["voltx_services"].get(srv, {}): del bot_settings["voltx_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_srv_{srv}", "id": call["id"]})

    # --- ZENEX CONTROL CALLBACKS ---
    elif data == "zenex_control":
        edit_message(chat_id, msg_id, render_body_text(f"💠 <b>Zenex Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('zenex_keys', []))}\nManage your Zenex API Keys below:"), reply_markup=zenex_control_keyboard())

    elif data == "toggle_zenex_auto":
        bot_settings["zenex_auto"] = not bot_settings.get("zenex_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"💠 <b>Zenex Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('zenex_keys', []))}\nManage your Zenex API Keys below:"), reply_markup=zenex_control_keyboard())
        answer_callback(call["id"], f"✅ Zenex Auto Range is now {'ON' if bot_settings['zenex_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_zenex_key":
        user_states[chat_id] = "wait_for_add_zenex_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Zenex API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "danger"}]]})

    elif data == "view_zenex_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("zenex_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_znx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Zenex Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_znx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("zenex_keys", [])):
            del bot_settings["zenex_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Zenex Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_zenex_keys", "id": call["id"]})

    elif data == "zenex_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("zenex_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_zsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_zenex_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Zenex Allowed Ranges:</b>\nOnly these codes will be allowed in Zenex Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_zenex_search_country":
        user_states[chat_id] = "wait_for_add_zsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Zenex Range Code (e.g. 447):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_search_country", "style": "danger"}]]})

    elif data.startswith("del_zsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("zenex_search_countries", [])):
            del bot_settings["zenex_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Zenex Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "zenex_search_country", "id": call["id"]})

    elif data == "manage_zenex_srv":
        kb = []
        srvs = bot_settings.get("zenex_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"zx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "zx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "zenex_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("💠 <b>Zenex Services Manager</b>\nManage your API-based manual services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "zx_add_srv":
        user_states[chat_id] = "wait_zx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_srv_"):
        srv = data.replace("zx_srv_", "")
        kb = []
        countries = bot_settings.get("zenex_services", {}).get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"zx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5987751449386296261", "callback_data": f"zx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"zx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_zenex_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("zx_add_cnt_"):
        srv = data.replace("zx_add_cnt_", "")
        user_states[chat_id] = "wait_zx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. UK, USA):"), reply_markup=get_cancel_kb())

    elif data.startswith("zx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["zenex_services"][srv].get(cnt, [])
        kb, row = [], []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"zx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5987751449386296261", "callback_data": f"zx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"zx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"zx_srv_{srv}", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("zx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_zx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 4473845XXX):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"zx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("zx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["zenex_services"].get(srv, {}).get(cnt, []):
            bot_settings["zenex_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"zx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("zx_del_srv_"):
        srv = data.replace("zx_del_srv_", "")
        if srv in bot_settings["zenex_services"]: del bot_settings["zenex_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_zenex_srv", "id": call["id"]})

    elif data.startswith("zx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["zenex_services"].get(srv, {}): del bot_settings["zenex_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"zx_srv_{srv}", "id": call["id"]})

    # --- MINO SMS CONTROL CALLBACKS ---
    elif data == "mino_control":
        edit_message(chat_id, msg_id, render_body_text(f"🚀 <b>Mino SMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('mino_keys', []))}\nManage your Mino SMS API Keys below:"), reply_markup=mino_control_keyboard())

    elif data == "toggle_mino_auto":
        bot_settings["mino_auto"] = not bot_settings.get("mino_auto", False)
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"🚀 <b>Mino SMS Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('mino_keys', []))}\nManage your Mino SMS API Keys below:"), reply_markup=mino_control_keyboard())
        answer_callback(call["id"], f"✅ Mino Auto Range is now {'ON' if bot_settings['mino_auto'] else 'OFF'}!", show_alert=False)

    elif data == "add_mino_key":
        user_states[chat_id] = "wait_for_add_mino_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Mino SMS API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "mino_control", "style": "danger"}]]})

    elif data == "view_mino_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("mino_keys", [])):
            safe_name = key[:10] + "..." if len(key) > 10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_mno_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "mino_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Mino Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_mno_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("mino_keys", [])):
            del bot_settings["mino_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Mino Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_mino_keys", "id": call["id"]})

    elif data == "mino_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("mino_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_msc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "add_mino_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "mino_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Mino Allowed Ranges:</b>\nOnly these codes will be allowed in Mino Search Number."), reply_markup={"inline_keyboard": kb})

    elif data == "add_mino_search_country":
        user_states[chat_id] = "wait_for_add_msc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Mino Range Code (e.g. 22507):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "mino_search_country", "style": "danger"}]]})

    elif data.startswith("del_msc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("mino_search_countries", [])):
            del bot_settings["mino_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Mino Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "mino_search_country", "id": call["id"]})

    elif data == "manage_mino_srv":
        kb = []
        srvs = bot_settings.get("mino_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"mx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5987751449386296261", "callback_data": "mx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "mino_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("🚀 <b>Mino Services Manager</b>\nManage your API-based manual services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "mx_add_srv":
        user_states[chat_id] = "wait_mx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("mx_srv_"):
        srv = data.replace("mx_srv_", "")
        kb = []
        countries = bot_settings.get("mino_services", {}).get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c.upper() == iso or c.upper() == name or c.upper() in name or name in c.upper():
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"mx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5987751449386296261", "callback_data": f"mx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"mx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_mino_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("mx_add_cnt_"):
        srv = data.replace("mx_add_cnt_", "")
        user_states[chat_id] = "wait_mx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. GUINEA, IVORY COAST):"), reply_markup=get_cancel_kb())

    elif data.startswith("mx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["mino_services"][srv].get(cnt, [])
        kb, row = [], []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"mx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2: kb.append(row); row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5987751449386296261", "callback_data": f"mx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"mx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"mx_srv_{srv}", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("mx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_mx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 2250789XXX):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"mx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("mx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["mino_services"].get(srv, {}).get(cnt, []):
            bot_settings["mino_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"mx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("mx_del_srv_"):
        srv = data.replace("mx_del_srv_", "")
        if srv in bot_settings["mino_services"]: del bot_settings["mino_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_mino_srv", "id": call["id"]})

    elif data.startswith("mx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["mino_services"].get(srv, {}): del bot_settings["mino_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"mx_srv_{srv}", "id": call["id"]})

    elif data == "manage_fj":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "toggle_fj":
        bot_settings["fj_on"] = not bot_settings["fj_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "add_fj":
        user_states[chat_id] = "wait_for_add_fj"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Channel Username or Invite Link:\n<i>(Note: For private channels, use the numeric ID like -100...)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})

    elif data.startswith("del_fj_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fj_channels"]):
            del bot_settings["fj_channels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Channel deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "manage_admins":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "add_adm":
        user_states[chat_id] = "wait_for_add_adm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID of the new Admin:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_admins", "style": "danger"}]]})

    elif data.startswith("del_adm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["admins"]):
            del bot_settings["admins"][idx]
            save_db()
            answer_callback(call["id"], "✅ Admin deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "manage_otp_groups":
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "add_fw":
        user_states[chat_id] = "wait_for_add_fw_id"
        temp_data[chat_id] = {"msg_id": msg_id}
        delete_message(chat_id, msg_id)
        select_kb = {
            "keyboard": [
                [{"text": "𝗦𝗘𝗟𝗘𝗖𝗧 𝗢𝗧𝗣 𝗚𝗥𝗢𝗨𝗣", "icon_custom_emoji_id": "5190447043545438788", "style": "primary", "request_chat": {"request_id": 1, "chat_is_channel": False}}], 
                [{"text": "𝗖𝗔𝗡𝗖𝗘𝗟", "icon_custom_emoji_id": "5267490665117275176", "style": "danger"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        send_message(chat_id, render_body_text("👇 <b>Select OTP Group from below:</b>"), reply_markup=select_kb)

    elif data.startswith("manage_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            grp_id = bot_settings["fw_groups"][idx]["chat_id"]
            edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {grp_id}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("add_fwbtn_"):
        idx = int(data.split("_")[2])
        user_states[chat_id] = "wait_for_add_fw_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "fw_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Custom Inline Button format:\n<code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_fw_{idx}", "style": "danger"}]]})

    elif data.startswith("del_fwbtn_"):
        parts = data.split("_")
        idx, b_idx = int(parts[2]), int(parts[3])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            if 0 <= b_idx < len(bot_settings["fw_groups"][idx]["buttons"]):
                del bot_settings["fw_groups"][idx]["buttons"][b_idx]
                save_db()
                answer_callback(call["id"], "✅ Button deleted!", show_alert=True)
                edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {bot_settings['fw_groups'][idx]['chat_id']}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("del_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            del bot_settings["fw_groups"][idx]
            save_db()
            answer_callback(call["id"], "✅ Group deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "edit_otp_link":
        user_states[chat_id] = "wait_for_otp_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new OTP Group Link:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "edit_channel_link":
        user_states[chat_id] = "wait_for_channel_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Channel Link (for OTP Group Button):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "manage_panels":
        api_count = len([p for p in bot_settings["panels"] if p.get("type") == "API Panel"])
        cpt_count = len([p for p in bot_settings["panels"] if p.get("type", "API Panel") == "Auto Captcha Panel"])
        text = f"{PEM['gear']} <b>Panel Management</b>\n\nSelect which type of panel system you want to manage:"
        kb = {"inline_keyboard": [
            [{"text": f"𝗔𝗗𝗗 𝗔𝗣𝗜 𝗣𝗔𝗡𝗘𝗟 ({api_count})", "icon_custom_emoji_id": "5987629038523392103", "callback_data": "manage_api_panels", "style": "primary"}],
            [{"text": f"𝗔𝗗𝗗 𝗔𝗨𝗧𝗢 𝗖𝗔𝗣𝗧𝗖𝗛𝗔 𝗣𝗔𝗡𝗘𝗟 ({cpt_count})", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "manage_cpt_panels", "style": "success"}],
            [{"text": "𝗣𝗔𝗡𝗘𝗟 𝗦𝗘𝗧𝗨𝗣 𝗧𝗨𝗧𝗢𝗥𝗜𝗔𝗟", "icon_custom_emoji_id": "5988027598603559238", "url": "https://youtu.be/1eGwD5gPZTA?si=NX1fWEZxP6aYeZ9E", "style": "primary"}],
            [{"text": "Back to System", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=kb)

    elif data in ["manage_api_panels", "manage_cpt_panels"]:
        p_type = "API Panel" if data == "manage_api_panels" else "Auto Captcha Panel"
        p_list = [p for p in bot_settings["panels"] if p.get("type", "API Panel") == p_type]
        icon = f"{PEM['world']} API" if p_type == 'API Panel' else f"{PEM['lock']} Auto Captcha"
        
        text = f"{icon} <b>{p_type}s Management</b>\n\n👀 <b>Active Monitors:</b> {len(p_list)}\n\n🟢 <b>Available Providers:</b>\n"
        for p in p_list:
            status = "Monitoring" if p['status'] == 'ON' else "Stopped"
            login_state = p.get('login_status', '')
            if p['type'] == 'Auto Captcha Panel':
                conf = f" {login_state}" if login_state else f"{PEM['ok']} Configured"
            else:
                conf = f"{PEM['ok']} Configured" if p.get('api_url') else f"{PEM['no']} Not Configured"
            text += f"• {p['name']}: {PEM['ok'] if p['status']=='ON' else PEM['no']} {status} | {conf}\n"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=typed_panels_list_keyboard(p_type))

    elif data in ["add_api_panel", "add_cpt_panel"]:
        user_states[chat_id] = "wait_for_panel_name"
        p_type = "api" if data == "add_api_panel" else "logc"
        temp_data[chat_id] = {"msg_id": msg_id, "add_type": p_type}
        edit_message(chat_id, msg_id, render_body_text("📝 Please send the name of the New Provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='api' else 'cpt'}_panels", "style": "danger"}]]})

    elif data.startswith("add_ptype_"):
        pass

    elif data in ["list_del_api", "list_del_cpt"]:
        p_type = "API Panel" if data == "list_del_api" else "Auto Captcha Panel"
        kb = []
        for idx, p in enumerate(bot_settings["panels"]):
            if p.get("type", "API Panel") == p_type:
                kb.append([{"text": f"Delete {p['name']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"do_del_pnl_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['trash']} <b>Select a Provider to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("do_del_pnl_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(bot_settings["panels"]):
            p_type = bot_settings["panels"][idx].get("type", "API Panel")
            del bot_settings["panels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Provider Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "id": "internal"})

    elif data.startswith("tog_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            p["status"] = "ON" if p["status"] == "OFF" else "OFF"
            save_db()
            edit_message(chat_id, msg_id, render_body_text(render_panel_config_text(p)), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("conf_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            edit_message(chat_id, msg_id, render_body_text(render_panel_config_text(p)), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("set_p_api_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_api"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the API URL for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_tok_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_tok"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Token for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_fapi_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_fapi"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the FULL API URL (Example: http://api.com/get?key=YOUR_TOKEN&start=0):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_rec_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_rec"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the number of records to fetch (e.g. 10).\nType <code>0</code> for Unlimited:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("edit_cp_lurl_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_edit_cp_lurl"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>EDIT LOGIN LINK</b>\n\n➡️ Panel এর নতুন Login Link দিন:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("edit_cp_mlink_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_edit_cp_mlink"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['msg']} <b>EDIT MESSAGE LINK</b>\n\n➡️ SMS/OTP ডাটার নতুন Link দিন:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("edit_cp_user_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_edit_cp_user"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>EDIT USERNAME</b>\n\n➡️ Panel এর নতুন Username দিন:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("edit_cp_pass_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_edit_cp_pass"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['lock']} <b>EDIT PASSWORD</b>\n\n➡️ Panel এর নতুন Password দিন:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("edit_cp_nname_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_edit_cp_nname"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['phone']} <b>EDIT NUMBER COLUMN NAME</b>\n\n➡️ Number Column এর নতুন নাম কী? (যেমন: number, phone):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("edit_cp_nidx_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_edit_cp_nidx"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['num']} <b>EDIT NUMBER COLUMN SERIAL</b>\n\n➡️ Number Column এর নতুন Serial Number কত? (যেমন: 1, 3, 5):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("edit_cp_mname_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_edit_cp_mname"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['msg']} <b>EDIT OTP/MESSAGE COLUMN NAME</b>\n\n➡️ OTP/Message Column এর নতুন নাম কী? (যেমন: message, sms, text):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("edit_cp_midx_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_edit_cp_midx"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['num']} <b>EDIT OTP/MESSAGE COLUMN SERIAL</b>\n\n➡️ OTP/Message Column এর নতুন Serial Number কত? (যেমন: 2, 4, 6):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("test_p_conn_"):
        idx = int(data.split("_")[3])
        p = bot_settings["panels"][idx]
        wait_msg = send_message(chat_id, render_body_text("⏳ Testing connection. Please wait..."))
        wait_msg_id = wait_msg.get("result", {}).get("message_id") if wait_msg else None
        answer_callback(call["id"])
        
        try:
            parsed = []
            raw_text = ""
            
            if p["type"] == "Auto Captcha Panel":
                sess = panel_sessions.get(idx)
                if not sess:
                    success = attempt_auto_login(p, idx)
                    if not success:
                        if wait_msg_id: delete_message(chat_id, wait_msg_id)
                        send_message(chat_id, render_body_text(f"❌ <b>Auto Login Failed!</b>\nReason: {html.escape(str(p.get('login_status', 'Unknown')))}"))
                        return
                    sess = panel_sessions.get(idx)
                    
                login_url = p.get("login_url", "").strip()
                if not login_url.startswith("http"): login_url = "http://" + login_url
                msg_link = p.get("msg_link", "").strip()
                if not msg_link.startswith("http") and msg_link != "": msg_link = "http://" + msg_link
                check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
                
                # 🌟 test connection supports sAjaxSource & HTML table parser
                parsed, raw_text = fetch_cpt_panel_cdrs(p, sess, check_url)
                
            else:
                full_url = p.get("full_api_url", "").strip()
                url = p.get("api_url", "").strip()
                token = p.get("token", "").strip()
                if not full_url and not url:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Please Set API URL or Full API URL first!"))
                    return
                
                urls_to_try = []
                if full_url:
                    urls_to_try.append(full_url)
                else:
                    if "{token}" in url or "{key}" in url:
                        urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                    elif "token=" in url or "key=" in url:
                        urls_to_try.append(url)
                    else:
                        sep = '&' if '?' in url else '?'
                        urls_to_try.append(f"{url}{sep}token={token}")
                        urls_to_try.append(f"{url}{sep}key={token}&start=0")
                        urls_to_try.append(f"{url}{sep}key={token}")
                    
                parsed = []
                raw_text = ""
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                for try_url in urls_to_try:
                    try:
                        res = requests.get(try_url, headers=headers, timeout=10)
                        raw_text = res.text
                        parsed = parse_panel_response(raw_text, p)
                        if parsed:
                            if not full_url and try_url != url and token:
                                p["api_url"] = try_url.replace(token, "{token}")
                                save_db()
                            break
                    except: pass
                 
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
                 
            if parsed:
                txt = f"✅ <b>Connection Successful!</b>\n\n🎯 <b>Parsed Data Sample (Max 3):</b>\n\n"
                
                for i, sample in enumerate(parsed[:3]):
                    num = sample['number']
                    msg = sample['message']
                    otp = sample['otp']
                    
                    detected_app = detect_service(msg)
                    app_name = detected_app if detected_app else p.get("name", "Unknown")
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg)
                    
                    txt += f"<b>{i+1}.</b> {prem_app_html} <b>{app_full_name}</b>\n"
                    txt += f"📱 Number: <code>{num}</code>\n"
                    txt += f"📝 Full Msg: <code>{html.escape(msg)}</code>\n"
                    txt += f"🔐 OTP: <code>{otp}</code>\n"
                    txt += "➖" * 12 + "\n"
                    
                send_message(chat_id, render_body_text(txt))
            else:
                p_name = p.get("name", "Provider")
                no_msg_txt = f"{PEM['ok']} <b>Connection Successful!</b>\n" \
                             f"━━━━━━━━━━━━━━━━━━━━━━\n" \
                             f"{PEM['rocket']} <b>Provider:</b> {html.escape(p_name)}\n" \
                             f"{PEM['lock']} <b>Session:</b> Active & Connected\n" \
                             f"{PEM['graph']} <b>Live Messages:</b> 0 টি\n" \
                             f"━━━━━━━━━━━━━━━━━━━━━━\n\n" \
                             f"ℹ️ <b>আপনার প্যানেলে আপাতত কোনো মেসেজ বা ওটিপি নেই।</b>\n" \
                             f"প্যানেল কানেকশন একদম ঠিক আছে, নতুন এসএমএস আসা মাত্রই বট স্বয়ংক্রিয়ভাবে তা রিসিভ করবে।"
                send_message(chat_id, render_body_text(no_msg_txt))
        except Exception as e:
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            send_message(chat_id, render_body_text(f"❌ <b>Connection Failed!</b>\nError: {html.escape(str(e))}"))

    elif data == "dxa_control":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())

    elif data == "dxa_toggle_w":
        bot_settings["withdraw_on"] = not bot_settings["withdraw_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DXA CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())

    elif data == "manage_w_methods":
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "add_wm":
        user_states[chat_id] = "wait_for_add_wm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the name of the new Withdrawal Method:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_w_methods", "style": "danger"}]]})

    elif data.startswith("del_wm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["w_methods"]):
            del bot_settings["w_methods"][idx]
            save_db()
            answer_callback(call["id"], "✅ Method deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "dxa_w_group":
        user_states[chat_id] = "wait_for_w_group_id"
        temp_data[chat_id] = {"msg_id": msg_id}
        delete_message(chat_id, msg_id)
        select_kb = {
            "keyboard": [
                [{"text": "𝗦𝗘𝗟𝗘𝗖𝗧 𝗪𝗜𝗧𝗛𝗗𝗥𝗔𝗪 𝗚𝗥𝗢𝗨𝗣", "icon_custom_emoji_id": "5190447043545438788", "style": "primary", "request_chat": {"request_id": 2, "chat_is_channel": False}}], 
                [{"text": "𝗖𝗔𝗡𝗖𝗘𝗟", "icon_custom_emoji_id": "5267490665117275176", "style": "danger"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": True
        }
        send_message(chat_id, render_body_text("👇 <b>Select Withdraw Group from below:</b>"), reply_markup=select_kb)

    elif data == "dxa_otp_r":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("💰 <b>OTP REWARD SETTINGS</b>\n\nSelect an option below to set Default Panel Rate or Uploaded File Rate:"), reply_markup=dxa_otp_reward_keyboard())
        answer_callback(call["id"])

    elif data == "dxa_default_rate":
        temp_data[chat_id] = {"msg_id": msg_id, "key": "otp_reward"}
        user_states[chat_id] = "set_dxa"
        cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_otp_r", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Please send the new <b>Default OTP Reward Rate</b> (Current: <code>{bot_settings['otp_reward']} TK</code>):"), reply_markup=cancel_kb)
        answer_callback(call["id"])

    elif data == "dxa_file_rate_menu":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        if not number_batches:
            answer_callback(call["id"], "❌ No uploaded files found!", show_alert=True)
            return
        edit_message(chat_id, msg_id, render_body_text("📁 <b>FILE RATE MANAGEMENT</b>\n\nSelect a file below to change its OTP reward rate:"), reply_markup=dxa_file_rate_list_keyboard())
        answer_callback(call["id"])

    elif data.startswith("dxa_set_fr_"):
        b_id = data.replace("dxa_set_fr_", "")
        if b_id not in number_batches:
            answer_callback(call["id"], "❌ File not found!", show_alert=True)
            return
        f_name = number_batches[b_id].get("filename", b_id)
        srv = number_batches[b_id].get("service", "")
        cur_rate = number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0))
        temp_data[chat_id] = {"msg_id": msg_id, "b_id": b_id}
        user_states[chat_id] = "wait_for_dxa_file_rate"
        cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_file_rate_menu", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new OTP reward rate for:\n📄 <b>{html.escape(str(f_name))}</b> ({html.escape(str(srv))})\n💰 Current Rate: <code>{cur_rate} TK</code>"), reply_markup=cancel_kb)
        answer_callback(call["id"])

    elif data.startswith("dxa_"):
        key = data.replace("dxa_", "")
        key_map = {"min_w": "min_withdraw", "otp_r": "otp_reward", "ref_r": "refer_reward", "cool": "cooldown", "num_req": "num_req", "num_share": "num_share"}
        if key in key_map:
            temp_data[chat_id] = {"msg_id": msg_id, "key": key_map[key]}
            user_states[chat_id] = "set_dxa"
            cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_dxa_edit", "style": "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(f"📝 Please send the new value for <code>{key_map[key]}</code>:"), reply_markup=cancel_kb)
            answer_callback(call["id"])

    elif data == "back_to_services":
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        stex_srvs = set(bot_settings.get("stex_services", {}).keys())
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        zenex_srvs = set(bot_settings.get("zenex_services", {}).keys())
        mino_srvs = set(bot_settings.get("mino_services", {}).keys())
        all_services = local_srvs.union(stex_srvs).union(voltx_srvs).union(zenex_srvs).union(mino_srvs)
        
        if not all_services:
            answer_callback(call["id"], "❌ No numbers or services available!", show_alert=True)
            return
            
        c_msg = bot_settings["custom_messages"].get("get_number", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
        
        apps_db = bot_settings.get("premium_apps", {})
        kb = []
        temp_row = []
        for s in all_services:
            emoji_id = "5987557149360792425" 
            for app_key, app_data in apps_db.items():
                if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                    if "id" in app_data:
                        emoji_id = app_data["id"]
                        break
            temp_row.append({"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"})
            if len(temp_row) == 2:
                kb.append(temp_row)
                temp_row = []
        if temp_row:
            kb.append(temp_row)
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_s_"):
        service = data.split("g_s_")[1]
        local_cnts = set([b["country"] for b in number_batches.values() if b["service"] == service and b["numbers"]])
        stex_cnts = set(bot_settings.get("stex_services", {}).get(service, {}).keys())
        voltx_cnts = set(bot_settings.get("voltx_services", {}).get(service, {}).keys())
        zenex_cnts = set(bot_settings.get("zenex_services", {}).get(service, {}).keys())
        mino_cnts = set(bot_settings.get("mino_services", {}).get(service, {}).keys())
        all_countries = local_cnts.union(stex_cnts).union(voltx_cnts).union(zenex_cnts).union(mino_cnts)
        
        c_msg = bot_settings["custom_messages"].get("select_country", {})
        raw_txt = c_msg.get("text", "📌 Select a country for {service}:").replace("{service}", service)
        txt = render_body_text(raw_txt)
        
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        for c in all_countries:
            emoji_id = "5780471598922337683" # Default flag
            c_up = c.strip().upper()
            matched_flag = False
            
            # ১. প্রথমে হুবহু নাম বা ISO কোড মিলাবে (যাতে Guinea এর জায়গায় Papua New Guinea না আসে)
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").strip().upper()
                name = flag_data.get("name", "").strip().upper()
                if c_up == iso or c_up == name:
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        matched_flag = True
                        break
            
            # ২. হুবহু নাম না মিললে ওই দেশের নাম্বার বা রেঞ্জের কোড (+224) থেকে সঠিক ফ্ল্যাগ বের করবে
            if not matched_flag:
                sample_num = None
                for b in number_batches.values():
                    if b.get("service") == service and b.get("country") == c and b.get("numbers"):
                        sample_num = b["numbers"][0]["num"]
                        break
                if not sample_num:
                    for srv_key in ["stex_services", "voltx_services", "zenex_services", "mino_services"]:
                        r_list = bot_settings.get(srv_key, {}).get(service, {}).get(c, [])
                        if r_list:
                            sample_num = r_list[0]
                            break
                if sample_num:
                    _, _, eid_from_num = get_flag_info_from_num(str(sample_num))
                    if eid_from_num:
                        emoji_id = eid_from_num
                        matched_flag = True
                        
            # ৩. তবুও না পেলে আংশিক নাম মিলাবে
            if not matched_flag:
                for flag_code, flag_data in flags_db.items():
                    name = flag_data.get("name", "").strip().upper()
                    if name and (c_up in name or name in c_up):
                        if "id" in flag_data:
                            emoji_id = flag_data["id"]
                            break
            
            otp_price = bot_settings.get("otp_reward", 0.0)
            # 🌟 ফাইলের নির্দিষ্ট কোনো রেট থাকলে সেটা নিয়ে আসবে
            for b in number_batches.values():
                if b.get("service") == service and b.get("country") == c and "rate" in b and b.get("numbers"):
                    otp_price = b.get("rate")
                    break
                    
            kb.append([{"text": f"{c} - {otp_price} TK/OTP", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_c_{service}_{c}", "style": "success"}])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_services", "style": "danger"}])
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("g_c_") or data.startswith("c_n_"):
        # ১. গ্লোবাল কুলডাউন চেক (সকল নাম্বার মেথডের জন্য)
        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Please wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s.", show_alert=True)
            return
        
        # কুলডাউন আপডেট
        user_cooldowns[chat_id] = now
        
        # আগের নাম্বার এক্সপায়ার করা
        expire_previous_number(chat_id)

        # যদি সার্চ নাম্বার থেকে আসে
        if data.startswith("c_n_s_"):
            is_voltx_req = data.endswith("_vtx")
            is_zenex_req = data.endswith("_znx")
            is_mino_req = data.endswith("_mno")
            
            if is_voltx_req or is_zenex_req or is_mino_req:
                clean_data = data[:-4]
            else:
                clean_data = data
                
            parts_s = clean_data.split("_", 4)
            
            query = parts_s[3] if len(parts_s) > 3 else ""
            service_from_cb = parts_s[4] if len(parts_s) > 4 else None
            
            allowed_countries = bot_settings.get("search_countries", [])
            voltx_allowed = bot_settings.get("voltx_search_countries", [])
            zenex_allowed = bot_settings.get("zenex_search_countries", [])
            mino_allowed = bot_settings.get("mino_search_countries", [])
            
            is_stex_allowed = any(query.startswith(c) for c in allowed_countries) if allowed_countries else False
            is_voltx_allowed = any(query.startswith(c) for c in voltx_allowed) if voltx_allowed else False
            is_zenex_allowed = any(query.startswith(c) for c in zenex_allowed) if zenex_allowed else False
            is_mino_allowed = any(query.startswith(c) for c in mino_allowed) if mino_allowed else False
            
            if not is_voltx_req and not is_zenex_req and not is_mino_req and not is_stex_allowed and not is_voltx_allowed and not is_zenex_allowed and not is_mino_allowed:
                answer_callback(call["id"], "❌ This country code is not allowed for search!", show_alert=True)
                return
                
            edit_message(chat_id, msg_id, render_body_text("⌛ <i>Processing... Finding Number...</i>"))
            wait_msg_id = msg_id
            
            found_indices = []
            for b_id, b_data in number_batches.items():
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if n_obj["num"].replace("+", "").startswith(query) and chat_id not in n_obj.get("used_by", []):
                        found_indices.append((b_id, idx))
            
            fetched_nums = []
            if not found_indices:
                api_found = False
                req_count = bot_settings.get("num_req", 1)

                # 🌟 প্রথমে Mino SMS চেক করবে
                if is_mino_allowed or is_mino_req:
                    mino_keys = bot_settings.get("mino_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in mino_keys:
                            try:
                                headers = {"Content-Type": "application/json", "X-MINO-API-KEY": api_key}
                                payload = {"api_key": api_key, "rid": query, "national_format": 0, "remove_plus": 0}
                                res = requests.post(f"{MINO_BASE_URL}/getnumber", json=payload, headers=headers, timeout=10)
                                resp_data = res.json()
                                num_str = ""
                                if resp_data.get("status") == "success" and resp_data.get("number"):
                                    num_str = str(resp_data.get("number", "")).replace("+", "").strip()
                                elif resp_data.get("data") and isinstance(resp_data["data"], dict):
                                    num_str = str(resp_data["data"].get("number", "") or resp_data["data"].get("no_plus_number", "")).replace("+", "").strip()
                                if num_str:
                                    raw_mno_num = num_str
                                    sorted_ccs = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
                                    clean_q = query.replace("+", "").strip()
                                    for cc in sorted_ccs:
                                        if clean_q.startswith(cc):
                                            if not num_str.startswith(cc):
                                                num_str = cc + num_str
                                            break
                                    fetched_nums.append(num_str)
                                    mino_assigned_numbers[num_str] = chat_id
                                    mino_assigned_numbers[raw_mno_num] = chat_id
                                    api_found = True
                                    total_assigned_stats += 1
                                    is_mino_req = True
                                    break
                            except: continue
                
                # তারপর Zenex চেক করবে
                if len(fetched_nums) < req_count and (is_zenex_allowed or is_zenex_req) and not is_mino_req:
                    zenex_keys = bot_settings.get("zenex_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in zenex_keys:
                            try:
                                headers = {"mapikey": api_key}
                                payload = {"range": query, "is_national": False, "remove_plus": False}
                                res = requests.post(f"{ZENEX_BASE_URL}/v1/getnum", json=payload, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("full_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("number", "")).replace("+", "")
                                    fetched_nums.append(num_str)
                                    zenex_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    is_zenex_req = True 
                                    break
                            except: continue

                # তারপর Voltx চেক করবে
                if len(fetched_nums) < req_count and (is_voltx_allowed or is_voltx_req) and not is_zenex_req and not is_mino_req:
                    voltx_keys = bot_settings.get("voltx_keys", [])
                    for _ in range(req_count):
                        if len(fetched_nums) >= req_count: break
                        for api_key in voltx_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                payload = {"rid": query}
                                res = requests.post(f"{VOLTX_BASE_URL}/getnum", json=payload, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    voltx_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    is_voltx_req = True
                                    break
                            except: continue

                # সবশেষে StexSMS তে চেক করবে
                if len(fetched_nums) < req_count and (is_stex_allowed and not is_voltx_req and not is_zenex_req and not is_mino_req):
                    stex_keys = bot_settings.get("stex_keys", [])
                    for _ in range(req_count - len(fetched_nums)):
                        for api_key in stex_keys:
                            try:
                                headers = {"mauthapi": api_key}
                                res = requests.post(f"{STEX_BASE_URL}/getnum", json={"rid": query}, headers=headers, timeout=10)
                                resp_data = res.json()
                                if resp_data.get("meta", {}).get("code") == 200 and resp_data.get("data"):
                                    num_str = str(resp_data["data"].get("no_plus_number", "")).replace("+", "")
                                    if not num_str: num_str = str(resp_data["data"].get("national_number", ""))
                                    fetched_nums.append(num_str)
                                    stex_assigned_numbers[num_str] = chat_id 
                                    api_found = True
                                    total_assigned_stats += 1
                                    break
                            except: continue
                        
                if not api_found:
                    answer_callback(call["id"], "❌ Number out of stock!", show_alert=True)
                    delete_message(chat_id, wait_msg_id)
                    return
                save_db()
            else:
                random.shuffle(found_indices)
                for b_id, idx in found_indices:
                    if len(fetched_nums) >= bot_settings.get("num_req", 1): break
                    n_obj = number_batches[b_id]["numbers"][idx]
                    num_str = n_obj["num"]
                    fetched_nums.append(num_str)
                    
                    # 🌟 Save File Specific Rate
                    assigned_number_rates[num_str] = float(number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))
                    
                    n_obj["shares"] += 1
                    n_obj["used_by"].append(chat_id)
                    total_assigned_stats += 1
                    if n_obj["shares"] >= bot_settings.get("num_share", 1):
                        n_obj["to_remove"] = True
                        used_numbers_list.append(num_str)
                for b_id in number_batches:
                    number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
                save_db()
                
            kb = []
            
            # Message Text Variables
            app_full_name = "SEARCH"
            prem_app_html = "🔍"
            if service_from_cb:
                app_full_name, prem_app_html = get_service_info_html(service_from_cb)

            flags_db = bot_settings.get("premium_flags", {})
            country_emoji_html = ""
            country_full_name = "Unknown"
            iso_code = "XX"

            # 🌟 সার্ভিস বা ফাইলটি WS Checker এর আওতাভুক্ত কি না তা চেক করা 🌟
            is_service_in_ws_checker = False
            ws_srvs = bot_settings.get("ws_checker_services", [])
            ws_files = bot_settings.get("ws_checker_files", [])

            if service_from_cb and any(str(service_from_cb).strip().upper() == str(s).strip().upper() for s in ws_srvs):
                is_service_in_ws_checker = True
            elif found_indices and any(b_id in ws_files for b_id, _ in found_indices):
                is_service_in_ws_checker = True

            run_ws = is_service_in_ws_checker and bot_settings.get("ws_checker_on", False)
            run_tg = False

            ws_checker_results = {}
            tg_checker_results = {}
            if run_ws:
                edit_message(chat_id, wait_msg_id, render_body_text("⌛ <i>Checking Numbers via WhatsApp Checker...</i>"))
                ws_checker_results = check_whatsapp_numbers(fetched_nums, chat_id)
            
            for num in fetched_nums:
                char_flag, iso = get_flag_and_code(num)
                iso_code = iso
                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                clean_num = re.sub(r'\D', '', str(num))
                flag_emoji_id = "5780471598922337683"
                for flag_code, flag_data in flags_db.items():
                    if iso == flag_data.get("iso"):
                        if "id" in flag_data: 
                            flag_emoji_id = flag_data["id"]
                            country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                        country_full_name = flag_data.get("name", iso)
                        break
                if not country_emoji_html: country_emoji_html = char_flag
                if country_full_name == "Unknown": country_full_name = iso_code
                
                btn_text_display, btn_style = format_checker_button(display_num, clean_num, ws_checker_results, tg_checker_results)
                kb.append([{"text": btn_text_display, "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": btn_style}])
            
            vtx_ext = "_vtx" if is_voltx_req else "_znx" if is_zenex_req else "_mno" if is_mino_req else ""
            srv_ext = f"_{service_from_cb}" if service_from_cb else ""
            
            c_btns = bot_settings["custom_messages"].get("search_number", {}).get("buttons", [])
            for c_b in c_btns: 
                b_copy = c_b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
                
            change_btns = []
            if service_from_cb:
                change_btns.append({"text": "COUNTRY", "icon_custom_emoji_id": "5987629038523392103", "callback_data": f"g_s_{service_from_cb}", "style": "danger"})
            change_btns.append({"text": "REFRESH", "icon_custom_emoji_id": "5987671562994590370", "callback_data": f"c_n_s_{query}{srv_ext}{vtx_ext}", "style": "success"})
            kb.append(change_btns)

            kb.append([{"text": "REMOVE CC", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "toggle_cc_off", "style": "danger"}])

            if run_ws:
                kb.append([{"text": "CONNECT WHATSAPP CHECKER", "icon_custom_emoji_id": "5987961773934780806", "callback_data": "connect_ws_from_num", "style": "primary"}])
                
            kb.append([{"text": "OTP GROUP", "icon_custom_emoji_id": "5246848468177143690", "url": bot_settings["otp_link"], "style": "primary"}])
            
            formatted_msg = build_live_number_text(prem_app_html, app_full_name, country_emoji_html, country_full_name, iso_code, run_ws, run_tg, fetched_nums)
            text_numbers = render_body_text(formatted_msg)
            edit_message(chat_id, wait_msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": wait_msg_id, "nums": fetched_nums, "text": text_numbers, "kb": kb}
            return

        # যদি আপলোড করা বা সার্ভিস থেকে আসে
        parts = data.split("_")
        service = parts[2]
        country = parts[3]

        available_indices = []
        # Check Local Stock First
        for b_id, b_data in number_batches.items():
            if b_data["service"] == service and b_data["country"] == country:
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if chat_id not in n_obj.get("used_by", []):
                        available_indices.append((b_id, idx))

        # IF NO LOCAL STOCK, Check StexSMS, Voltx, Zenex & Mino Services
        if not available_indices:
            stex_srv_data = bot_settings.get("stex_services", {}).get(service, {}).get(country)
            voltx_srv_data = bot_settings.get("voltx_services", {}).get(service, {}).get(country)
            zenex_srv_data = bot_settings.get("zenex_services", {}).get(service, {}).get(country)
            mino_srv_data = bot_settings.get("mino_services", {}).get(service, {}).get(country)
            
            target_range = None
            is_voltx = False
            is_zenex = False
            is_mino = False
            
            if stex_srv_data and len(stex_srv_data) > 0:
                target_range = random.choice(stex_srv_data)
            elif voltx_srv_data and len(voltx_srv_data) > 0:
                target_range = random.choice(voltx_srv_data)
                is_voltx = True
            elif zenex_srv_data and len(zenex_srv_data) > 0:
                target_range = random.choice(zenex_srv_data)
                is_zenex = True
            elif mino_srv_data and len(mino_srv_data) > 0:
                target_range = random.choice(mino_srv_data)
                is_mino = True
                
            if target_range:
                user_cooldowns[chat_id] = 0
                vtx_flag = "_vtx" if is_voltx else "_znx" if is_zenex else "_mno" if is_mino else ""
                handle_callback({"message": call["message"], "data": f"c_n_s_{target_range}_{service}{vtx_flag}", "id": call["id"]})
                return
            else:
                answer_callback(call["id"], "❌ Number out of stock or range missing!", show_alert=True)
                if data.startswith("c_n_"): delete_message(chat_id, msg_id)
                return

        random.shuffle(available_indices)
        
        fetched_nums = []
        picked_batch_ids = set()
        for b_id, idx in available_indices:
            if len(fetched_nums) >= bot_settings["num_req"]: break
            n_obj = number_batches[b_id]["numbers"][idx]
            
            fetched_nums.append(n_obj["num"])
            picked_batch_ids.add(b_id)
            
            # 🌟 Save File Specific Rate
            assigned_number_rates[n_obj["num"]] = float(number_batches[b_id].get("rate", bot_settings.get("otp_reward", 0.0)))
            
            n_obj["shares"] += 1
            n_obj["used_by"].append(chat_id)
            total_assigned_stats += 1
            
            if n_obj["shares"] >= bot_settings.get("num_share", 1):
                n_obj["to_remove"] = True
                used_numbers_list.append(n_obj["num"])

        for b_id in number_batches:
            number_batches[b_id]["numbers"] = [n for n in number_batches[b_id]["numbers"] if not n.get("to_remove")]
        save_db()

        if not fetched_nums:
            answer_callback(call["id"], "❌ You have already taken all numbers or stock is empty!", show_alert=True)
            if data.startswith("c_n_"): delete_message(chat_id, msg_id)
            return

        app_full_name, prem_app_html = get_service_info_html(service)
        kb = []
        
        flags_db = bot_settings.get("premium_flags", {})
        country_emoji_html = ""
        country_full_name = country
        iso_code = "XX"
        
        # 🌟 চেক করা হচ্ছে যে এই সার্ভিস বা ফাইলটি WS Checker এর আওতাভুক্ত কি না 🌟
        is_service_in_ws_checker = False
        ws_srvs = bot_settings.get("ws_checker_services", [])
        ws_files = bot_settings.get("ws_checker_files", [])
        
        if any(str(service).strip().upper() == str(s).strip().upper() for s in ws_srvs):
            is_service_in_ws_checker = True
        elif any(b_id in ws_files for b_id in picked_batch_ids):
            is_service_in_ws_checker = True

        run_ws = is_service_in_ws_checker and bot_settings.get("ws_checker_on", False)
        run_tg = False

        ws_checker_results = {}
        tg_checker_results = {}
        if run_ws:
            edit_message(chat_id, msg_id, render_body_text("⌛ <i>Checking Numbers via WhatsApp Checker...</i>"))
            ws_checker_results = check_whatsapp_numbers(fetched_nums, chat_id)
        
        for num in fetched_nums:
            char_flag, iso = get_flag_and_code(num)
            iso_code = iso
            display_num = f"+{num}" if not num.startswith("+") else num
            clean_num = re.sub(r'\D', '', str(num))
            
            flag_emoji_id = "5780471598922337683" # Default Flag
            for flag_code, flag_data in flags_db.items():
                if iso == flag_data.get("iso"):
                    if "id" in flag_data: 
                        flag_emoji_id = flag_data["id"]
                        country_emoji_html = f'<tg-emoji emoji-id="{flag_emoji_id}">{flag_data["char"]}</tg-emoji>'
                    country_full_name = flag_data.get("name", country)
                    break
            
            if not country_emoji_html: country_emoji_html = char_flag
            
            # 🌟 চেকার রেজাল্ট অনুযায়ী বাটনের স্টাইল এবং ইমোজি সেট করা 🌟
            btn_text_display, btn_style = format_checker_button(display_num, clean_num, ws_checker_results, tg_checker_results)
            kb.append([{"text": btn_text_display, "icon_custom_emoji_id": flag_emoji_id, "copy_text": {"text": display_num}, "style": btn_style}])
            
        c_btns = bot_settings["custom_messages"].get("get_number", {}).get("buttons", [])
        for c_b in c_btns: 
            b_copy = c_b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        kb.append([
            {"text": "COUNTRY", "icon_custom_emoji_id": "5987629038523392103", "callback_data": f"g_s_{service}", "style": "danger"},
            {"text": "REFRESH", "icon_custom_emoji_id": "5987671562994590370", "callback_data": f"c_n_{service}_{country}", "style": "success"}
        ])

        kb.append([{"text": "REMOVE CC", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "toggle_cc_off", "style": "danger"}])

        if run_ws:
            kb.append([{"text": "CONNECT WHATSAPP CHECKER", "icon_custom_emoji_id": "5987961773934780806", "callback_data": "connect_ws_from_num", "style": "primary"}])
        
        kb.append([{"text": "OTP GROUP", "icon_custom_emoji_id": "5246848468177143690", "url": bot_settings["otp_link"], "style": "primary"}])
        
        formatted_msg = build_live_number_text(prem_app_html, app_full_name, country_emoji_html, country_full_name, iso_code, run_ws, run_tg, fetched_nums)
        text_numbers = render_body_text(formatted_msg)
        # OAK 
        try:
            edit_message(chat_id, msg_id, text_numbers, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": fetched_nums, "text": text_numbers, "kb": kb}
        except:
            # যদি মেসেজ ইডিট করা সম্ভব না হয় (যেমন অনেক আগের মেসেজ), তবে নতুন মেসেজ দিবে
            msg_res = send_message(chat_id, text_numbers, reply_markup={"inline_keyboard": kb})
            if msg_res and "result" in msg_res:
                user_active_sessions[chat_id] = {"msg_id": msg_res["result"]["message_id"], "nums": fetched_nums, "text": text_numbers, "kb": kb}

    elif data.startswith("wapp_") or data.startswith("wrej_"):
        # অ্যাডমিন চেক (User ID চেক করতে হবে)
        user_id_clicked = call["from"]["id"]
        if not is_admin(user_id_clicked):
            answer_callback(call["id"], "🚫 Only Bot Admins can process withdrawals!", show_alert=True)
            return
            
        action = "APPROVE" if data.startswith("wapp_") else "REJECT"
        req_id = data.replace("wapp_", "").replace("wrej_", "")
        
        if req_id in pending_withdrawals:
            req_data = pending_withdrawals[req_id]
            u_id, amt = req_data["user_id"], req_data["amount"]
            num = req_data["number"]
            full_name = req_data.get("full_name", u_id)
            
            if action == "APPROVE" and len(num) >= 7:
                masked_num = f"{num[:4]}❖DXA❖{num[-3:]}"
            else:
                masked_num = num
            
            status_text = "APPROVED" if action == "APPROVE" else "REJECTED"
            emoji_icon_id = "5987557149360792425" if action == "APPROVE" else "5420130255174145507"
            new_text = f"🎙 <b>WITHDRAWAL {status_text}</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={u_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amt} TK\n🍏 <b>NUMBER:</b> <code>{masked_num}</code>\n🏦 <b>METHOD:</b> {req_data['method']}\n\n🧾 <b>REQ ID:</b> {req_id}\n👨‍⚖️ <b>PROCESSED BY ADMIN</b>"
            
            kb = {"inline_keyboard": [[{"text": status_text, "icon_custom_emoji_id": emoji_icon_id, "callback_data": "ignore", "style": "success" if action == "APPROVE" else "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(new_text), reply_markup=kb)
            
            if action == "REJECT":
                update_balance(u_id, amt) 
                send_message(u_id, render_body_text(f"❌ Your {amt} TK withdrawal request was rejected. Balance refunded."))
            else:
                send_message(u_id, render_body_text(f"{PEM['ok']} Your {amt} TK withdrawal request has been paid successfully!"))
            
            if db:
                try: db.collection('withdrawals').document(req_id).update({"status": "approved" if action == "APPROVE" else "rejected"})
                except: pass
                
            del pending_withdrawals[req_id]
        else:
            answer_callback(call["id"], "❌ Request already processed!", show_alert=True)

# ==========================================
# Polling Loop & Checkers
# ==========================================
def ws_logout_monitor_thread():
    while True:
        try:
            api_url = bot_settings.get("master_api_url", "https://bot.orabitsms.site/api")
            api_key = bot_settings.get("master_api_key", "")
            
            # যদি API Key থাকে এবং কোনো নাম্বার কানেক্টেড অবস্থায় আমাদের ডাটাবেসে থাকে
            if api_key and ws_linked_numbers:
                res = requests.get(f"{api_url}/user-status", params={"apiKey": api_key}, timeout=15)
                data = res.json()
                
                # API থেকে পাওয়া বর্তমান অ্যাকটিভ নাম্বারগুলোর লিস্ট তৈরি করা
                active_sessions = data.get("ActiveSessions", [])
                active_phones = [str(session.get("phone", "")) for session in active_sessions if session.get("status") == "connected"]
                
                # আমাদের সেভ করা নাম্বারগুলোর সাথে মেলানো
                # list() ব্যবহার করা হচ্ছে কারণ লুপ চলাকালীন আমরা ডিকশনারি থেকে ডেটা মুছবো
                for phone in list(ws_linked_numbers.keys()):
                    
                    # যদি আমাদের সেভ করা নাম্বারটি API-এর Active লিস্টে না থাকে, তার মানে লগআউট হয়েছে
                    if phone not in active_phones:
                        user_id = ws_linked_numbers[phone]
                        
                        # ১. ইউজারকে লগআউট মেসেজ পাঠানো (প্রিমিয়াম ইমোজি সহ এবং API শব্দ বাদে)
                        logout_msg = f"<tg-emoji emoji-id=\"5336944168944047463\">⚠️</tg-emoji> <b>𝚆𝚑𝚊𝚝𝚜𝙰𝚙𝚙 𝙻𝚘𝚐𝚐𝚎𝚍 𝙾𝚞𝚝!</b>\n\n<tg-emoji emoji-id=\"5337132498965010628\">📱</tg-emoji> <b>𝙽𝚞𝚖𝚋𝚎𝚛 :</b> +{phone}\n\n<tg-emoji emoji-id=\"5420130255174145507\">❌</tg-emoji> <b>Your connected WhatsApp account has been disconnected.</b>"
                        send_message(user_id, render_body_text(logout_msg))
                        
                        # ২. ইউজারের WS Added কাউন্ট কমানো (0 এর নিচে যেন না যায়)
                        if user_id in user_cache and user_cache[user_id].get("total_ws_added", 0) > 0:
                            user_cache[user_id]["total_ws_added"] -= 1
                        if db:
                            try: db.collection('users').document(str(user_id)).update({"total_ws_added": firestore.Increment(-1)})
                            except: pass
                            
                        # ৩. ডাটাবেস থেকে নাম্বারটি রিমুভ করা
                        del ws_linked_numbers[phone]
                        save_local_db()
        except Exception as e:
            pass
        time.sleep(60) # প্রতি ১ মিনিটে একবার চেক করবে

# ব্যাকগ্রাউন্ডে চেকার থ্রেডটি চালু করা হলো
threading.Thread(target=ws_logout_monitor_thread, daemon=True).start()

def poll_otp_with_status(number_id, num_str, owner_id, api_key):
    headers = {"X-API-Key": api_key}
    for _ in range(150): # 150 * 4 seconds = 10 Minutes Polling
        try:
            res = requests.get(f"{STEX_BASE_URL}/api/v1/numbers/{number_id}/sms", headers=headers, timeout=10)
            data = res.json()
            if data.get("success") and data.get("otp"):
                otp = str(data["otp"])
                msg_text = data.get("message", f"Your code is {otp}")
                
                # 🌟 সম্পূর্ণ মেসেজ থেকে ড্যাশসহ বা বড় OTP খোঁজার ফিক্স
                extracted_otp = extract_otp_code(msg_text)
                if extracted_otp and len(extracted_otp) > len(otp):
                    otp = extracted_otp
                    
                # 🌟 সম্পূর্ণ মেসেজ থেকে সার্ভিস/অ্যাপ চেনার ফিক্স
                app_name = data.get("service", "StexSMS Service")
                detected_app = detect_service(msg_text)
                if detected_app:
                    app_name = detected_app
                
                unique_id = f"POLL_{number_id}_{otp}"
                if unique_id not in processed_otps:
                    processed_otps.add(unique_id)
                    
                    char, iso = get_flag_and_code(num_str)
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                    
                    global recent_traffic
                    current_time = time.time()
                    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                    recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num_str, "time": current_time})
                    save_local_db()
                    
                    display_num = f"+{num_str}" if not str(num_str).startswith("+") else str(num_str)
                    masked = mask_number(display_num)
                    lang = detect_language(msg_text)
                    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                    styled_masked = str(masked).replace("DXA", "•DXA•")
                    display_msg = render_body_text(f"━━━━━━━━━━━━━━━\n<blockquote>{prem_app_html} {str(app_full_name).upper()} ➜ 💬 {str(lang_name).upper()}</blockquote>\n<blockquote>『 {get_flag_info_html(display_num)} {iso} ➜ {styled_masked} 』</blockquote>\n━━━━━━━━━━━━━━━")
                    
                    for fw in bot_settings.get("fw_groups", []):
                        emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
                        srv_emoji_id = emj_match.group(1) if emj_match else "5296369303661067030"
                        
                        styles = ["primary", "success", "danger"]
                        chan_link = bot_settings.get("otp_channel_link", "https://t.me/DXA_ZONE")
                        
                        kb = [
                            [
                                {"text": "𝗖𝗛𝗔𝗡𝗡𝗘𝗟", "icon_custom_emoji_id": "5987629038523392103", "url": chan_link, "style": "primary"},
                                {"text": f"{otp}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": otp}, "style": "success"}
                            ]
                        ]
                        
                        # 🌟 Auto GET NUMBER Button for OTP Group
                        clean_srv = re.sub(r'[^a-zA-Z0-9]', '', app_full_name)
                        dl_link = f"https://t.me/{BOT_USERNAME}?start=stex_{str(num_str)[:5]}_{clean_srv}"
                        kb.append([{"text": "𝗚𝗘𝗧 𝗦𝗔𝗠𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", "icon_custom_emoji_id": "5291997181572570361", "url": dl_link, "style": "danger"}])
                        
                        temp_row = []
                        for i, btn in enumerate(fw.get("buttons", [])):
                            b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[(i + 1) % 3]}
                            if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                            temp_row.append(b_obj)
                            if len(temp_row) == 2:
                                kb.append(temp_row)
                                temp_row = []
                        if temp_row: kb.append(temp_row)
                        
                        send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                    
                    reward = float(assigned_number_rates.get(num_str, bot_settings.get("otp_reward", 0.0)))
                    if reward > 0:
                        update_balance(owner_id, reward)
                        
                    emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
                    srv_emoji_id = emj_match.group(1) if emj_match else "5870972873450984431"
                    
                    inbox_msg_text = f" {get_flag_info_html(display_num)} <code>{display_num}</code>\n➕  {reward} 𝗧𝗞"
                    inbox_msg = render_body_text(inbox_msg_text)
                    
                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": otp}, "style": "success"}]]
                    
                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                    
                    increment_user_otp(owner_id)
                break
        except: pass
        time.sleep(4)

def stex_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()
    
    while True:
        try:
            # 🌟 Auto Mode OFF থাকলে সম্পূর্ণ বন্ধ থাকবে
            if not bot_settings.get("stex_auto", False):
                time.sleep(5)
                continue

            stex_keys = bot_settings.get("stex_keys", [])
            if stex_keys:
                api_key = stex_keys[0]
                headers = {"mauthapi": api_key}
                res = requests.get(f"{STEX_BASE_URL}/console", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("meta", {}).get("code") == 200 and data.get("data", {}).get("hits"):
                    current_time = time.time()
                    new_hits = False
                    
                    for hit in data["data"]["hits"]:
                        range_str = str(hit.get("range", "")).replace("X", "")
                        if len(range_str) > 9:
                            range_str = range_str[:9]
                        sid = str(hit.get("sid", "Unknown"))
                        msg = str(hit.get("message", ""))
                        hit_time = hit.get("time", current_time * 1000) / 1000.0
                        
                        unique_hit = f"STEX_{range_str}_{sid}_{hit.get('time', 0)}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000: seen_console_hits.clear()
                            
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)
                            
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": f"{range_str}XXX", 
                                "time": hit_time,
                                "real_range": range_str,
                                "source": "stex"
                            })
                            new_hits = True
                            
                    if new_hits:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    # 🌟 Auto ADD and DELETE logic for Stex
                    if bot_settings.get("stex_auto", False) and current_time - last_auto_update > 20:
                        last_auto_update = current_time
                        changed = False
                        
                        if "stex_services" not in bot_settings: bot_settings["stex_services"] = {}
                        if "search_countries" not in bot_settings: bot_settings["search_countries"] = []
                        
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if t.get("source") == "stex" and "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)]
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["stex_services"]:
                                bot_settings["stex_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("source") == "stex" and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)]
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["stex_services"][srv]:
                                    bot_settings["stex_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and t.get("source") == "stex" and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)]
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["stex_services"][srv][full_country_name]:
                                        bot_settings["stex_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["search_countries"]:
                                        bot_settings["search_countries"].append(country_code)
                                        changed = True

                        services_to_remove = []
                        for srv, countries in list(bot_settings["stex_services"].items()):
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("source") == "stex" and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and t.get("source") == "stex" and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and t.get("source") == "stex" and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["stex_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["stex_services"][s]
                            changed = True
                            
                        if changed and bot_settings.get("stex_auto", False):
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

def voltx_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()
    
    while True:
        try:
            # 🌟 FIX: voltx_on এর জায়গায় voltx_auto চেক করা হলো
            if not bot_settings.get("voltx_auto", False):
                time.sleep(5)
                continue

            voltx_keys = bot_settings.get("voltx_keys", [])
            if voltx_keys:
                api_key = voltx_keys[0]
                headers = {"mauthapi": api_key}
                res = requests.get(f"{VOLTX_BASE_URL}/console", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("meta", {}).get("code") == 200 and data.get("data", {}).get("hits"):
                    current_time = time.time()
                    new_hits = False
                    
                    for hit in data["data"]["hits"]:
                        range_str = str(hit.get("range", "")).replace("X", "")
                        if len(range_str) > 9:
                            range_str = range_str[:9]
                        sid = str(hit.get("sid", "Unknown"))
                        msg = str(hit.get("message", ""))
                        hit_time = hit.get("time", current_time * 1000) / 1000.0
                        
                        unique_hit = f"VOLTX_{range_str}_{sid}_{hit.get('time', 0)}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000: seen_console_hits.clear()
                            
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)
                            
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": f"{range_str}XXX", 
                                "time": hit_time,
                                "real_range": range_str,
                                "source": "voltx"
                            })
                            new_hits = True
                            
                    if new_hits:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    # 🌟 Auto ADD and DELETE logic for Voltx
                    if bot_settings.get("voltx_auto", False) and current_time - last_auto_update > 20:
                        last_auto_update = current_time
                        changed = False
                        
                        if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
                        if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
                        
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if t.get("source") == "voltx" and "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)]
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["voltx_services"]:
                                bot_settings["voltx_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("source") == "voltx" and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)]
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["voltx_services"][srv]:
                                    bot_settings["voltx_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and t.get("source") == "voltx" and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)]
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["voltx_services"][srv][full_country_name]:
                                        bot_settings["voltx_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["voltx_search_countries"]:
                                        bot_settings["voltx_search_countries"].append(country_code)
                                        changed = True

                        services_to_remove = []
                        for srv, countries in list(bot_settings["voltx_services"].items()):
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("source") == "voltx" and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and t.get("source") == "voltx" and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and t.get("source") == "voltx" and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["voltx_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["voltx_services"][s]
                            changed = True
                            
                        if changed and bot_settings.get("voltx_auto", False):
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

def voltx_sms_listener():
    global processed_otps, recent_traffic, voltx_assigned_numbers
    while True:
        try:
            voltx_keys = bot_settings.get("voltx_keys", [])
            for api_key in voltx_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{VOLTX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Voltx Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"VOLTX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                styled_masked = str(masked).replace("DXA", "•DXA•")
                                display_msg = render_body_text(f"━━━━━━━━━━━━━━━\n<blockquote>{prem_app_html} {str(app_full_name).upper()} ➜ 💬 {str(lang_name).upper()}</blockquote>\n<blockquote>『 {get_flag_info_html(display_num)} {iso} ➜ {styled_masked} 』</blockquote>\n━━━━━━━━━━━━━━━")
                                
                                for fw in bot_settings.get("fw_groups", []):
                                    emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
                                    srv_emoji_id = emj_match.group(1) if emj_match else "5296369303661067030"
                                    
                                    styles = ["primary", "success", "danger"]
                                    chan_link = bot_settings.get("otp_channel_link", "https://t.me/DXA_ZONE")
                                    
                                    kb = [
                                        [
                                            {"text": "𝗖𝗛𝗔𝗡𝗡𝗘𝗟", "icon_custom_emoji_id": "5987629038523392103", "url": chan_link, "style": "primary"},
                                            {"text": f"{otp}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": otp}, "style": "success"}
                                        ]
                                    ]
                                    
                                    # 🌟 Auto GET NUMBER Button for OTP Group
                                    clean_srv = re.sub(r'[^a-zA-Z0-9]', '', app_full_name)
                                    dl_link = f"https://t.me/{BOT_USERNAME}?start=voltx_{str(num)[:5]}_{clean_srv}"
                                    kb.append([{"text": "𝗚𝗘𝗧 𝗦𝗔𝗠𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", "icon_custom_emoji_id": "5291997181572570361", "url": dl_link, "style": "danger"}])
                                    
                                    temp_row = []
                                    for i, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[(i + 1) % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for vtx_n, n_owner in voltx_assigned_numbers.items():
                                        clean_vtx = str(vtx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_vtx == clean_api_num or (len(clean_vtx) >= 8 and clean_vtx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_vtx[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                    
                                    reward = float(assigned_number_rates.get(num, bot_settings.get("otp_reward", 0.0)))
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                        
                                    emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
                                    srv_emoji_id = emj_match.group(1) if emj_match else "5870972873450984431"
                                    
                                    inbox_msg_text = f" {get_flag_info_html(display_num)} <code>{display_num}</code>\n➕  {reward} 𝗧𝗞"
                                    inbox_msg = render_body_text(inbox_msg_text)
                                    
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": otp}, "style": "success"}]]
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    increment_user_otp(owner_id)
                except: pass
        except: pass
        time.sleep(5)

def zenex_sms_listener():
    global processed_otps, recent_traffic, zenex_assigned_numbers
    while True:
        try:
            zenex_keys = bot_settings.get("zenex_keys", [])
            for api_key in zenex_keys:
                try:
                    headers = {"mapikey": api_key}
                    res = requests.get(f"{ZENEX_BASE_URL}/v1/numsuccess/info", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("otp", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("nid", otp))
                            
                            app_name = "Zenex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"ZENEX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                styled_masked = str(masked).replace("DXA", "•DXA•")
                                display_msg = render_body_text(f"━━━━━━━━━━━━━━━\n<blockquote>{prem_app_html} {str(app_full_name).upper()} ➜ 💬 {str(lang_name).upper()}</blockquote>\n<blockquote>『 {get_flag_info_html(display_num)} {iso} ➜ {styled_masked} 』</blockquote>\n━━━━━━━━━━━━━━━")
                                
                                for fw in bot_settings.get("fw_groups", []):
                                    emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
                                    srv_emoji_id = emj_match.group(1) if emj_match else "5296369303661067030"
                                    
                                    styles = ["primary", "success", "danger"]
                                    chan_link = bot_settings.get("otp_channel_link", "https://t.me/DXA_ZONE")
                                    
                                    kb = [
                                        [
                                            {"text": "𝗖𝗛𝗔𝗡𝗡𝗘𝗟", "icon_custom_emoji_id": "5987629038523392103", "url": chan_link, "style": "primary"},
                                            {"text": f"{otp}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": otp}, "style": "success"}
                                        ]
                                    ]
                                    
                                    # 🌟 Auto GET NUMBER Button for OTP Group
                                    clean_srv = re.sub(r'[^a-zA-Z0-9]', '', app_full_name)
                                    dl_link = f"https://t.me/{BOT_USERNAME}?start=zenex_{str(num)[:5]}_{clean_srv}"
                                    kb.append([{"text": "𝗚𝗘𝗧 𝗦𝗔𝗠𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", "icon_custom_emoji_id": "5291997181572570361", "url": dl_link, "style": "danger"}])
                                    
                                    temp_row = []
                                    for i, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[(i + 1) % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for znx_n, n_owner in zenex_assigned_numbers.items():
                                        clean_znx = str(znx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_znx == clean_api_num or (len(clean_znx) >= 8 and clean_znx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_znx[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    reward = float(assigned_number_rates.get(num, bot_settings.get("otp_reward", 0.0)))
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                        
                                    emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
                                    srv_emoji_id = emj_match.group(1) if emj_match else "5870972873450984431"
                                    
                                    inbox_msg_text = f" {get_flag_info_html(display_num)} <code>{display_num}</code>\n➕  {reward} 𝗧𝗞"
                                    inbox_msg = render_body_text(inbox_msg_text)
                                    
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": otp}, "style": "success"}]]
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    increment_user_otp(owner_id)
                except: pass
        except: pass
        time.sleep(5)

def global_sms_listener():
    global processed_otps, recent_traffic, stex_assigned_numbers
    while True:
        try:
            stex_keys = bot_settings.get("stex_keys", [])
            for api_key in stex_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{STEX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Stex Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"STEX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                styled_masked = str(masked).replace("DXA", "•DXA•")
                                display_msg = render_body_text(f"━━━━━━━━━━━━━━━\n<blockquote>{prem_app_html} {str(app_full_name).upper()} ➜ 💬 {str(lang_name).upper()}</blockquote>\n<blockquote>『 {get_flag_info_html(display_num)} {iso} ➜ {styled_masked} 』</blockquote>\n━━━━━━━━━━━━━━━")
                                
                                for fw in bot_settings.get("fw_groups", []):
                                    emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
                                    srv_emoji_id = emj_match.group(1) if emj_match else "5296369303661067030"
                                    
                                    styles = ["primary", "success", "danger"]
                                    chan_link = bot_settings.get("otp_channel_link", "https://t.me/DXA_ZONE")
                                    
                                    kb = [
                                        [
                                            {"text": "𝗖𝗛𝗔𝗡𝗡𝗘𝗟", "icon_custom_emoji_id": "5987629038523392103", "url": chan_link, "style": "primary"},
                                            {"text": f"{otp}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": otp}, "style": "success"}
                                        ]
                                    ]
                                    
                                    # 🌟 Auto GET NUMBER Button for OTP Group
                                    clean_srv = re.sub(r'[^a-zA-Z0-9]', '', app_full_name)
                                    dl_link = f"https://t.me/{BOT_USERNAME}?start=stex_{str(num)[:5]}_{clean_srv}"
                                    kb.append([{"text": "𝗚𝗘𝗧 𝗦𝗔𝗠𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", "icon_custom_emoji_id": "5291997181572570361", "url": dl_link, "style": "danger"}])
                                    
                                    temp_row = []
                                    for i, btn in enumerate(fw.get("buttons", [])):
                                        b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[(i + 1) % 3]}
                                        if "icon_custom_emoji_id" in btn: b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
                                        temp_row.append(b_obj)
                                        if len(temp_row) == 2:
                                            kb.append(temp_row)
                                            temp_row = []
                                    if temp_row: kb.append(temp_row)
                                    
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for stex_n, n_owner in stex_assigned_numbers.items():
                                        clean_stex = str(stex_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_stex == clean_api_num or (len(clean_stex) >= 8 and clean_stex.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_stex[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
                                    
                                    reward = float(assigned_number_rates.get(num, bot_settings.get("otp_reward", 0.0)))
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                        
                                    emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
                                    srv_emoji_id = emj_match.group(1) if emj_match else "5870972873450984431"
                                    
                                    inbox_msg_text = f" {get_flag_info_html(display_num)} <code>{display_num}</code>\n➕  {reward} 𝗧𝗞"
                                    inbox_msg = render_body_text(inbox_msg_text)
                                    
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": otp}, "style": "success"}]]
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    increment_user_otp(owner_id)
                except: pass
        except: pass
        time.sleep(5)

def zenex_console_listener():
    global recent_traffic, bot_settings
    last_auto_update = time.time()
    zenex_last_hits = {} 
    
    while True:
        try:
            # 🌟 Auto Mode OFF থাকলে সম্পূর্ণ বন্ধ থাকবে
            if not bot_settings.get("zenex_auto", False):
                time.sleep(5)
                continue

            zenex_keys = bot_settings.get("zenex_keys", [])
            if zenex_keys:
                api_key = zenex_keys[0]
                headers = {"mapikey": api_key}
                res = requests.get(f"{ZENEX_BASE_URL}/v1/active-ranges", headers=headers, timeout=10)
                data = res.json()
                
                if data.get("success") and "data" in data and "active_ranges" in data["data"]:
                    current_time = time.time()
                    new_hits_added = False
                    
                    for hit in data["data"]["active_ranges"]:
                        range_str = str(hit.get("range", "")).replace("X", "").replace("x", "")
                        sid = str(hit.get("service", "Unknown")).upper()
                        hits_count = int(hit.get("hits", 1))
                        
                        if range_str:
                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, "")
                            
                            range_key = f"{range_str}_{app_full_name}"
                            prev_hits = zenex_last_hits.get(range_key, 0)
                            
                            if hits_count > prev_hits:
                                new_hits = hits_count - prev_hits
                            else:
                                new_hits = hits_count
                                
                            zenex_last_hits[range_key] = hits_count
                            if new_hits > 150: new_hits = 150
                            
                            for _ in range(new_hits):
                                recent_traffic.append({
                                    "service": app_full_name,
                                    "iso": iso,
                                    "flag": char,
                                    "number": f"{range_str}XXX", 
                                    "time": current_time,
                                    "real_range": range_str,
                                    "source": "zenex"
                                })
                                new_hits_added = True
                            
                    if new_hits_added:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()
                        
                    if bot_settings.get("zenex_auto", False) and current_time - last_auto_update > 20:
                        last_auto_update = current_time
                        changed = False
                        
                        if "zenex_services" not in bot_settings: bot_settings["zenex_services"] = {}
                        if "zenex_search_countries" not in bot_settings: bot_settings["zenex_search_countries"] = []
                        
                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if t.get("source") == "zenex" and "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)]
                        
                        for srv in top_srvs:
                            if srv not in bot_settings["zenex_services"]:
                                bot_settings["zenex_services"][srv] = {}
                                changed = True
                                
                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("source") == "zenex" and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)]
                            
                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["zenex_services"][srv]:
                                    bot_settings["zenex_services"][srv][full_country_name] = []
                                    changed = True
                                    
                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and t.get("source") == "zenex" and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)]
                                
                                for rng in top_rngs:
                                    if rng not in bot_settings["zenex_services"][srv][full_country_name]:
                                        bot_settings["zenex_services"][srv][full_country_name].append(rng)
                                        changed = True
                                        
                                    country_code = rng[:3]
                                    if country_code not in bot_settings["zenex_search_countries"]:
                                        bot_settings["zenex_search_countries"].append(country_code)
                                        changed = True

                        services_to_remove = []
                        for srv, countries in list(bot_settings["zenex_services"].items()):
                            srv_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("source") == "zenex" and "real_range" in t and current_time - t.get("time", 0) <= 120)
                            if srv_hit < 1:
                                services_to_remove.append(srv)
                                continue
                            
                            countries_to_remove = []
                            for country, ranges in list(countries.items()):
                                c_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and get_flag_info_html(t.get("iso"), return_full_name=True).title() == country and t.get("source") == "zenex" and "real_range" in t and current_time - t.get("time", 0) <= 120)
                                if c_hit < 1:
                                    countries_to_remove.append(country)
                                    continue
                                
                                ranges_to_remove = []
                                for rng in ranges:
                                    r_hit = sum(1 for t in recent_traffic if t.get("service", "").upper() == srv.upper() and t.get("real_range") == rng and t.get("source") == "zenex" and current_time - t.get("time", 0) <= 120)
                                    if r_hit < 1: 
                                        ranges_to_remove.append(rng)
                                
                                for r in ranges_to_remove:
                                    ranges.remove(r)
                                    changed = True
                                    
                            for c in countries_to_remove:
                                del bot_settings["zenex_services"][srv][c]
                                changed = True
                                
                        for s in services_to_remove:
                            del bot_settings["zenex_services"][s]
                            changed = True
                            
                        if changed:
                            save_db()
                            
        except Exception as e:
            pass
        time.sleep(10)

def process_mino_otp_item(num, msg_text, otp, unique_id):
    global processed_otps, recent_traffic, mino_assigned_numbers
    if unique_id in processed_otps or not num:
        return
    processed_otps.add(unique_id)
    if len(processed_otps) > 5000:
        processed_otps.clear()

    app_name = "Mino Service"
    detected_app = detect_service(msg_text)
    if detected_app:
        app_name = detected_app

    char, iso = get_flag_and_code(num)
    app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
    current_time = time.time()

    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
    recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
    save_local_db()

    display_num = f"+{num}" if not str(num).startswith("+") else str(num)
    masked = mask_number(display_num)
    lang = detect_language(msg_text)

    lang_name = LANG_MAP.get(lang, "English") if 'LANG_MAP' in globals() else lang.replace("#", "")
    styled_masked = str(masked).replace("DXA", "•DXA•")
    display_msg = render_body_text(f"━━━━━━━━━━━━━━━\n<blockquote>{prem_app_html} {str(app_full_name).upper()} ➜ 💬 {str(lang_name).upper()}</blockquote>\n<blockquote>『 {get_flag_info_html(display_num)} {iso} ➜ {styled_masked} 』</blockquote>\n━━━━━━━━━━━━━━━")

    for fw in bot_settings.get("fw_groups", []):
        emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
        srv_emoji_id = emj_match.group(1) if emj_match else "5296369303661067030"

        styles = ["primary", "success", "danger"]
        chan_link = bot_settings.get("otp_channel_link", "https://t.me/DXA_ZONE")

        kb = [
            [
                {"text": "𝗖𝗛𝗔𝗡𝗡𝗘𝗟", "icon_custom_emoji_id": "5987629038523392103", "url": chan_link, "style": "primary"},
                {"text": f"{otp}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": otp}, "style": "success"}
            ]
        ]

        clean_srv = re.sub(r'[^a-zA-Z0-9]', '', app_full_name)
        dl_link = f"https://t.me/{BOT_USERNAME}?start=mino_{str(num)[:5]}_{clean_srv}"
        kb.append([{"text": "𝗚𝗘𝗧 𝗦𝗔𝗠𝗘 𝗡𝗨𝗠𝗕𝗘𝗥", "icon_custom_emoji_id": "5291997181572570361", "url": dl_link, "style": "danger"}])

        temp_row = []
        for i, btn in enumerate(fw.get("buttons", [])):
            b_obj = {"text": btn["text"], "url": btn["url"], "style": styles[(i + 1) % 3]}
            if "icon_custom_emoji_id" in btn:
                b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
            temp_row.append(b_obj)
            if len(temp_row) == 2:
                kb.append(temp_row)
                temp_row = []
        if temp_row:
            kb.append(temp_row)

        send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})

    owner_id = None
    clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()

    for uid, session_data in user_active_sessions.items():
        for act_num in session_data.get("nums", []):
            act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
            if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                owner_id = uid
                break
        if owner_id:
            break

    if not owner_id:
        for mno_n, n_owner in mino_assigned_numbers.items():
            clean_mno = str(mno_n).replace("+", "").replace(" ", "").replace("-", "").strip()
            if clean_mno == clean_api_num or (len(clean_mno) >= 8 and clean_mno.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_mno[-8:])):
                owner_id = n_owner
                break

    if owner_id:
        reward = float(assigned_number_rates.get(num, bot_settings.get("otp_reward", 0.0)))
        if reward > 0:
            update_balance(owner_id, reward)

        emj_match = re.search(r'emoji-id="(\d+)"', prem_app_html)
        srv_emoji_id = emj_match.group(1) if emj_match else "5870972873450984431"

        inbox_msg_text = f" {get_flag_info_html(display_num)} <code>{display_num}</code>\n➕  {reward} 𝗧𝗞"
        inbox_msg = render_body_text(inbox_msg_text)

        inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": srv_emoji_id, "copy_text": {"text": otp}, "style": "success"}]]

        send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
        increment_user_otp(owner_id)

def mino_sms_listener():
    while True:
        try:
            mino_keys = bot_settings.get("mino_keys", [])
            for api_key in mino_keys:
                headers = {"X-MINO-API-KEY": api_key}

                # ১. অ্যাকটিভ ইউজারদের নাম্বারের জন্য GET /check পোলিং
                active_mno_nums = list(mino_assigned_numbers.keys())
                for alloc_num in active_mno_nums:
                    try:
                        chk_res = requests.get(f"{MINO_BASE_URL}/check", params={"api_key": api_key, "number": alloc_num}, headers=headers, timeout=10)
                        chk_data = chk_res.json()
                        if chk_data.get("status") == "success" and (chk_data.get("allocation_status") == "completed" or chk_data.get("otp_code")):
                            num = str(chk_data.get("number", alloc_num)).replace("+", "").strip()
                            msg_text = str(chk_data.get("full_sms") or chk_data.get("message") or "")
                            otp = str(chk_data.get("otp_code") or extract_otp_code(msg_text) or "").strip()
                            if otp:
                                unique_id = f"MINO_{num}_{otp}"
                                process_mino_otp_item(num, msg_text or f"Your code is {otp}", otp, unique_id)
                    except:
                        pass

                # ২. গ্লোবাল ওটিপি লিস্টের জন্য GET /success_otp পোলিং
                try:
                    res = requests.get(f"{MINO_BASE_URL}/success_otp", params={"api_key": api_key}, headers=headers, timeout=10)
                    resp_data = res.json()
                    items = []
                    if isinstance(resp_data, list):
                        items = resp_data
                    elif isinstance(resp_data, dict):
                        if isinstance(resp_data.get("data"), list):
                            items = resp_data["data"]
                        elif isinstance(resp_data.get("data"), dict) and isinstance(resp_data["data"].get("otps"), list):
                            items = resp_data["data"]["otps"]
                        elif isinstance(resp_data.get("otps"), list):
                            items = resp_data["otps"]
                        elif isinstance(resp_data.get("records"), list):
                            items = resp_data["records"]

                    for item in items:
                        if not isinstance(item, dict):
                            continue
                        num = str(item.get("number") or item.get("phone") or "").replace("+", "").strip()
                        msg_text = str(item.get("full_sms") or item.get("message") or item.get("sms") or item.get("otp") or "")
                        otp = str(item.get("otp_code") or extract_otp_code(msg_text) or "").strip()
                        otp_id = str(item.get("id") or item.get("otp_id") or otp)
                        if num and otp:
                            unique_id = f"MINO_{num}_{otp_id}"
                            process_mino_otp_item(num, msg_text, otp, unique_id)
                except:
                    pass
        except:
            pass
        time.sleep(4)

def mino_console_listener():
    global recent_traffic, bot_settings
    seen_console_hits = set()
    last_auto_update = time.time()

    while True:
        try:
            # 🌟 Auto Mode OFF থাকলে সম্পূর্ণ বন্ধ থাকবে
            if not bot_settings.get("mino_auto", False):
                time.sleep(5)
                continue

            mino_keys = bot_settings.get("mino_keys", [])
            if mino_keys:
                api_key = mino_keys[0]
                headers = {"X-MINO-API-KEY": api_key}
                res = requests.get(f"{MINO_BASE_URL}/console", params={"api_key": api_key}, headers=headers, timeout=10)
                data = res.json()

                hits_list = []
                if isinstance(data, list):
                    hits_list = data
                elif isinstance(data, dict):
                    if isinstance(data.get("hits"), list):
                        hits_list = data["hits"]
                    elif isinstance(data.get("data"), list):
                        hits_list = data["data"]
                    elif isinstance(data.get("data"), dict) and isinstance(data["data"].get("hits"), list):
                        hits_list = data["data"]["hits"]

                if hits_list:
                    current_time = time.time()
                    new_hits = False

                    for hit in hits_list:
                        if not isinstance(hit, dict):
                            continue
                        range_str = str(hit.get("range") or hit.get("rid") or hit.get("number") or "").replace("X", "").replace("x", "").replace("+", "").strip()
                        if len(range_str) > 9:
                            range_str = range_str[:9]
                        sid = str(hit.get("sid") or hit.get("service") or "Unknown")
                        msg = str(hit.get("full_sms") or hit.get("message") or "")
                        hit_time = current_time

                        unique_hit = f"MINO_{range_str}_{sid}_{hit.get('time', hit.get('created_at', ''))}"
                        if unique_hit not in seen_console_hits and range_str:
                            seen_console_hits.add(unique_hit)
                            if len(seen_console_hits) > 2000:
                                seen_console_hits.clear()

                            char, iso = get_flag_and_code(range_str)
                            app_full_name, _ = get_service_info_html(sid, msg)

                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": f"{range_str}XXX",
                                "time": hit_time,
                                "real_range": range_str,
                                "source": "mino"
                            })
                            new_hits = True

                    if new_hits:
                        recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                        save_local_db()

                    if bot_settings.get("mino_auto", False) and current_time - last_auto_update > 20:
                        last_auto_update = current_time
                        changed = False

                        if "mino_services" not in bot_settings:
                            bot_settings["mino_services"] = {}
                        if "mino_search_countries" not in bot_settings:
                            bot_settings["mino_search_countries"] = []

                        srv_counts = Counter(t["service"].upper() for t in recent_traffic if t.get("source") == "mino" and "real_range" in t)
                        top_srvs = [s for s, c in srv_counts.most_common(6)]

                        for srv in top_srvs:
                            if srv not in bot_settings["mino_services"]:
                                bot_settings["mino_services"][srv] = {}
                                changed = True

                            iso_counts = Counter(t["iso"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("source") == "mino" and "real_range" in t)
                            top_isos = [i for i, c in iso_counts.most_common(3)]

                            for iso in top_isos:
                                full_country_name = get_flag_info_html(iso, return_full_name=True).title()
                                if full_country_name not in bot_settings["mino_services"][srv]:
                                    bot_settings["mino_services"][srv][full_country_name] = []
                                    changed = True

                                rng_counts = Counter(t["real_range"] for t in recent_traffic if t.get("service", "").upper() == srv and t.get("iso") == iso and t.get("source") == "mino" and "real_range" in t)
                                top_rngs = [r for r, c in rng_counts.most_common(2)]

                                for rng in top_rngs:
                                    if rng not in bot_settings["mino_services"][srv][full_country_name]:
                                        bot_settings["mino_services"][srv][full_country_name].append(rng)
                                        changed = True

                                    country_code = rng[:3]
                                    if country_code not in bot_settings["mino_search_countries"]:
                                        bot_settings["mino_search_countries"].append(country_code)
                                        changed = True

                        if changed and bot_settings.get("mino_auto", False):
                            save_db()
        except Exception as e:
            pass
        time.sleep(10)

def main():
    global BOT_USERNAME
    res = api_call("getMe")
    if res.get("ok"): BOT_USERNAME = res["result"]["username"]
    print(f"🤖 Bot is starting... @{BOT_USERNAME}")
    
    threading.Thread(target=panel_monitor_thread, daemon=True).start()
    threading.Thread(target=global_sms_listener, daemon=True).start()
    threading.Thread(target=stex_console_listener, daemon=True).start()
    threading.Thread(target=voltx_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_console_listener, daemon=True).start()
    threading.Thread(target=zenex_sms_listener, daemon=True).start()
    threading.Thread(target=zenex_console_listener, daemon=True).start()
    threading.Thread(target=mino_sms_listener, daemon=True).start()
    threading.Thread(target=mino_console_listener, daemon=True).start()
    print("📡 Background APIs & Global SMS Listener Started!")
    
    # 🌟 PRO-LEVEL FAST SYSTEM: 500 Workers Pool
    executor = ThreadPoolExecutor(max_workers=500)
    
    offset = None
    while True:
        try:
            updates = api_call(f"getUpdates?timeout=50&offset={offset}")
            if updates and "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update: 
                        executor.submit(handle_message, update["message"])
                    elif "callback_query" in update: 
                        executor.submit(handle_callback, update["callback_query"])
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()    