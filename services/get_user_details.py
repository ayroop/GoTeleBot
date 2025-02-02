from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact
import json
import sys
import psycopg2

def get_settings():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="admin_user",
            password="@345gtJHyf652SD",
            dbname="admin_panel"
        )
        cur = conn.cursor()
        cur.execute("SELECT api_id, api_hash, authorized_phone_number FROM settings LIMIT 1")
        settings = cur.fetchone()
        cur.close()
        conn.close()
        return settings
    except Exception as e:
        print(f"Error getting settings: {e}")
        sys.exit(1)

def get_user_details(phone_numbers_file, output_json_file):
    api_id, api_hash, authorized_phone_number = get_settings()
    client = TelegramClient('session_name', api_id, api_hash)
    client.connect()

    if not client.is_user_authorized():
        print(f"Phone number {authorized_phone_number} is not authorized. Please authorize it.")
        client.send_code_request(authorized_phone_number)
        code = input(f"Enter the code for {authorized_phone_number}: ")
        client.sign_in(authorized_phone_number, code)

    try:
        with open(phone_numbers_file, 'r') as f:
            phone_numbers = f.read().splitlines()

        users = []
        for phone in phone_numbers:
            if phone == "":
                continue
            contact = InputPhoneContact(client_id=0, phone=phone, first_name='First', last_name='Last')
            result = client(ImportContactsRequest([contact]))
            user = result.users[0]
            users.append({
                "user_id": user.id,
                "user_name": user.username,
                "access_hash": user.access_hash,
                "first_name": user.first_name,
                "last_name": user.last_name,
            })
            client(DeleteContactsRequest([contact]))

        with open(output_json_file, 'w') as f:
            json.dump(users, f, indent=2)

        print(f"User details saved to {output_json_file}")
    except Exception as e:
        print(f"Error getting user details: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python get_user_details.py <phone_numbers_file> <output_json_file>")
        sys.exit(1)

    phone_numbers_file = sys.argv[1]
    output_json_file = sys.argv[2]
    get_user_details(phone_numbers_file, output_json_file)