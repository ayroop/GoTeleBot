from apify_client import ApifyClient
import sys
import json
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
        cur.execute("SELECT target_group, api_token FROM settings LIMIT 1")
        settings = cur.fetchone()
        cur.close()
        conn.close()
        return settings
    except Exception as e:
        print(f"Error getting settings: {e}")
        sys.exit(1)

def add_members_to_telegram(json_file):
    target_group, api_token = get_settings()
    if not target_group or not api_token:
        print("Error: Missing target group or API token in settings.")
        sys.exit(1)

    try:
        # Initialize the ApifyClient with your Apify API token
        client = ApifyClient(api_token)

        # Read the JSON file with user data
        with open(json_file, 'r') as f:
            user_data = json.load(f)

        # Prepare the Actor input
        run_input = {
            "USER_Name": user_data,
            "Target_Group": target_group,
        }

        # Run the Actor and wait for it to finish
        run = client.actor("bhansalisoft/telegram-group-or-channel-adder-using-member-json-data").call(run_input=run_input)

        # Fetch and print Actor results from the run's dataset (if there are any)
        print("💾 Check your data here: https://console.apify.com/storage/datasets/" + run["defaultDatasetId"])
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            print(item)
    except Exception as e:
        print(f"Error adding members to Telegram: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python apify_adder.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    add_members_to_telegram(json_file)