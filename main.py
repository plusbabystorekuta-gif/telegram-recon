from telethon import TelegramClient
import gspread
import os
import json
import base64

from google.oauth2.service_account import Credentials

# ====================================
# TELEGRAM CONFIG
# ====================================

api_id = int(os.environ["TELEGRAM_API_ID"])
api_hash = os.environ["TELEGRAM_API_HASH"]

# ====================================
# RESTORE SESSION FILE
# ====================================

session_base64 = os.environ["TELEGRAM_SESSION"]

with open("session.session", "wb") as f:
    f.write(base64.b64decode(session_base64))

# ====================================
# TELETHON CLIENT
# ====================================

client = TelegramClient(
    "session",
    api_id,
    api_hash
)

# ====================================
# GOOGLE SHEETS AUTH
# ====================================

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_info = json.loads(
    os.environ["GOOGLE_CREDENTIALS"]
)

creds = Credentials.from_service_account_info(
    creds_info,
    scopes=scope
)

gc = gspread.authorize(creds)

sheet = gc.open_by_key(
    "1sP377OIK4AT_9BavW6RBoiOyzNme2heD__amSOaMamM"
).worksheet("raw")
# ====================================
# MAIN FUNCTION
# ====================================

async def main():

    print("LOGIN TELEGRAM...")

    await client.start()

    print("AMBIL MESSAGE TELEGRAM...")

    messages = await client.get_messages(
        "Kutamimba_bot",
        limit=1000
    )

    print("AMBIL EXISTING IDS...")

    existing_ids = set(
        sheet.col_values(2)[1:]
    )

    rows = []

    print("FILTER DEDUP...")

    for msg in messages:

        if not msg.message:
            continue

        msg_id = str(msg.id)

        if msg_id in existing_ids:
            continue

        rows.append([
            str(msg.date),
            msg_id,
            msg.message
        ])

    print(f"MESSAGE BARU: {len(rows)}")

    if rows:

        rows.reverse()

        print("APPEND KE SHEET...")

        sheet.append_rows(rows)

    print("DONE!")

# ====================================
# RUN
# ====================================

with client:
    client.loop.run_until_complete(main())