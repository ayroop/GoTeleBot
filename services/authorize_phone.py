import sys
import time
import phonenumbers
import psycopg2
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneNumberInvalidError
from contextlib import contextmanager

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "user": "admin_user",
    "password": "@345gtJHyf652SD",
    "dbname": "admin_panel"
}

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def update_authorization_state(phone_number, state):
    """Update the authorization state for a phone number"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE settings SET authorization_state=%s WHERE authorized_phone_number=%s",
                    (state, phone_number)
                )
                conn.commit()
        return True
    except Exception as e:
        print(f"Error updating authorization state: {e}")
        return False

def get_last_code_sent_time(phone_number):
    """Get the timestamp of the last sent verification code"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT last_code_sent_time FROM settings WHERE authorized_phone_number=%s",
                    (phone_number,)
                )
                result = cur.fetchone()
                return result[0] if result else None
    except Exception as e:
        print(f"Error getting last code sent time: {e}")
        return None

def update_last_code_sent_time(phone_number):
    """Update the timestamp of the last sent verification code"""
    current_time = int(time.time())
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE settings SET last_code_sent_time=%s WHERE authorized_phone_number=%s",
                    (current_time, phone_number)
                )
                conn.commit()
        return True
    except Exception as e:
        print(f"Error updating last code sent time: {e}")
        return False

def validate_phone_number(phone_number):
    """Validate phone number format and structure"""
    try:
        phone_number = phone_number.strip()
        if not phone_number.startswith('+'):
            return False

        parsed_number = phonenumbers.parse(phone_number)
        if not phonenumbers.is_valid_number(parsed_number):
            return False

        # Simple length check
        digits = ''.join(filter(str.isdigit, phone_number))
        if len(digits) < 8 or len(digits) > 15:
            return False
            
        return True
    except phonenumbers.phonenumberutil.NumberParseException:
        return False

async def handle_send_code(client, phone_number):
    """Handle the send code step of authorization"""
    try:
        if await client.is_user_authorized():
            return True

        last_sent_time = get_last_code_sent_time(phone_number)
        current_time = int(time.time())
        
        if last_sent_time is not None and (current_time - last_sent_time) < 60:
            print("Rate limit: Please wait before requesting another code.")
            return False

        await client.send_code_request(phone_number)
        success = all([
            update_authorization_state(phone_number, "code_sent"),
            update_last_code_sent_time(phone_number)
        ])
        return success
    except Exception as e:
        print(f"Failed to send code: {e}")
        return False

async def handle_verify_code(client, phone_number, code):
    """Handle the verify code step of authorization"""
    if not code:
        return False

    try:
        await client.sign_in(phone_number, code)
        return update_authorization_state(phone_number, "authorized")
    except SessionPasswordNeededError:
        print("Two-step verification is enabled.")
        return False
    except Exception as e:
        print(f"Failed to authorize phone number: {e}")
        return False

async def main(api_id, api_hash, phone_number, step, code=None):
    """Main function to handle Telegram authorization process"""
    if not validate_phone_number(phone_number):
        print("Invalid phone number format.")
        return False

    client = None
    try:
        client = TelegramClient('session_name', api_id, api_hash)
        await client.connect()

        if step == "send_code":
            return await handle_send_code(client, phone_number)
        elif step == "verify_code":
            return await handle_verify_code(client, phone_number, code)
        return False

    except Exception as e:
        print(f"Error during authorization process: {e}")
        return False
    finally:
        if client:
            await client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python authorize_phone.py <api_id> <api_hash> <phone_number> <step> [code]")
        sys.exit(1)

    try:
        api_id = int(sys.argv[1])
        api_hash = sys.argv[2]
        phone_number = sys.argv[3]
        step = sys.argv[4]
        code = sys.argv[5] if len(sys.argv) > 5 else None

        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            main(api_id, api_hash, phone_number, step, code)
        )
        if not result:
            sys.exit(1)
    except Exception as e:
        print(f"Script execution error: {e}")
        sys.exit(1)