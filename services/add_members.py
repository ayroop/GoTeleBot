import json
import time
import pandas as pd
import asyncio
import random
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, PhoneNumberInvalidError
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.channels import InviteToChannelRequest

# 🔹 Settings
API_FILE = "apis.json"
EXCEL_FILE = "phone_numbers.xlsx"
PHONE_COLUMN = "Phone"
GROUP_USERNAME = "your_group_username_here"
DELAY_BETWEEN_REQUESTS = random.randint(10, 20)
DELAY_BETWEEN_INVITES = random.randint(20, 40)
DAILY_LIMIT = 50
BATCH_SIZE = 5  

# 🔹 Load API credentials from apis.json
def load_apis():
    with open(API_FILE, "r") as f:
        return json.load(f)

# 🔹 Load phone numbers from phone_numbers.xlsx
def load_phone_numbers():
    df = pd.read_excel(EXCEL_FILE)
    df[PHONE_COLUMN] = df[PHONE_COLUMN].astype(str).apply(
        lambda x: "+98" + x[1:] if x.startswith("0") else ("+98" + x if not x.startswith("+") else x)
    )
    return df[PHONE_COLUMN].dropna().tolist()

# 🔹 Check Internet connection
def check_internet():
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        return False

# 🔹 Verify if a phone number exists on Telegram
async def check_phone_on_telegram(client, phone_number):
    try:
        entity = await client.get_entity(phone_number)
        print(f"✅ Number {phone_number} exists on Telegram (User ID: {entity.id}).")
        return entity.id
    except PhoneNumberInvalidError:
        print(f"❌ Number {phone_number} is invalid or not registered on Telegram.")
        return None
    except Exception as e:
        print(f"⚠️ Error checking {phone_number}: {e}")
        return None

# 🔹 Add users to the group without relying on ImportContactsRequest
async def add_members(client, phone_numbers, group_username):
    success = []
    failed = []
    added_count = 0

    async with client:
        try:
            group = await client.get_entity(group_username)
        except Exception as e:
            print(f"❌ Error fetching group details: {e}")
            return [], []

        for phone in phone_numbers:
            if added_count >= DAILY_LIMIT:
                print(f"⚠️ Daily limit reached for this account!")
                break

            user_id = await check_phone_on_telegram(client, phone)
            if user_id:
                try:
                    await asyncio.sleep(random.randint(DELAY_BETWEEN_REQUESTS, DELAY_BETWEEN_INVITES))
                    await client(InviteToChannelRequest(group, [user_id]))
                    success.append(phone)
                    print(f"✅ {phone} added to the group.")
                    added_count += 1
                except FloodWaitError as e:
                    print(f"🚨 Telegram requested to wait {e.seconds} seconds... Sleeping.")
                    await asyncio.sleep(e.seconds)
                    continue
                except Exception as e:
                    failed.append(phone)
                    print(f"❌ {phone} could not be added: {e}")

    return success, failed

# 🔹 Execute process for all accounts
async def main():
    if not check_internet():
        print("🚨 No internet connection! Please check your server.")
        return

    apis = load_apis()
    phone_numbers = load_phone_numbers()

    for api in apis:
        print(f"\n🔹 Logging in with account {api['PHONE']}")

        try:
            client = TelegramClient(StringSession(api["SESSION_STRING"]), api["API_ID"], api["API_HASH"])

            await client.connect()
            if not await client.is_user_authorized():
                print(f"⚠️ Session for {api['PHONE']} is invalid. Please generate a new SESSION_STRING.")
                await client.disconnect()
                continue

            # 🔹 1. Add users directly to the group
            success, failed = await add_members(client, phone_numbers, GROUP_USERNAME)

            await client.disconnect()
        except Exception as e:
            print(f"❌ Unexpected error for {api['PHONE']}: {e}")

if __name__ == "__main__":
    asyncio.run(main())