import os
import time
import random
import json
from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
# Handle backup codes - split by comma and strip whitespace
backup_codes_str = os.getenv("IG_BACKUP_CODES", "")
BACKUP_CODES = [code.strip() for code in backup_codes_str.split(",") if code.strip()]

# Debug: Check if environment variables are loaded
print(f"🔍 DEBUG: USERNAME = {USERNAME}")
print(f"🔍 DEBUG: PASSWORD = {'*' * len(PASSWORD) if PASSWORD else 'None'}")

# JSON storage file
DATA_FILE = "bot_data.json"

OWNER_USERNAME = "onlyrohanss"

# Load or init JSON data
if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r") as f:
            bot_data = json.load(f)
    except json.JSONDecodeError:
        print("⚠️ bot_data.json is corrupted. Creating new data structure.")
        bot_data = {"threads": {}}
else:
    bot_data = {"threads": {}}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(bot_data, f, indent=4)

# Safe sleep wrapper
def safe_sleep(min_sec=2, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))

# Login function with backup codes
def login():
    cl = Client()
    
    # Try to load existing session first
    try:
        if os.path.exists("session.json"):
            cl.load_settings("session.json")
            # Test if session is still valid
            cl.get_timeline_feed()
            print("✅ Successfully loaded existing session")
            return cl
    except Exception as e:
        print(f"⚠️ Session load failed: {e}")
        print("ℹ️ Proceeding with fresh login...")

    # Fresh login with 2FA handling
    try:
        print("🔐 Attempting login...")
        cl.login(USERNAME, PASSWORD)
        print("✅ Login successful without 2FA")
    except TwoFactorRequired as e:
        print("🔒 Two-factor authentication required (specific exception caught)")
        
        if not BACKUP_CODES or not BACKUP_CODES[0].strip():
            raise Exception("No backup codes available for 2FA")
        
        # Try each backup code until one works
        for i, backup_code in enumerate(BACKUP_CODES):
            code = backup_code.strip()
            if not code:
                continue
                
            try:
                print(f"🔄 Trying backup code {i+1}/{len(BACKUP_CODES)}: {code} (Remaining codes: {len(BACKUP_CODES)})")
                temp_code = input("Enter the 2FA code (or press Enter to use backup code): ").strip()
                cl.login(USERNAME, PASSWORD, verification_code=temp_code)
                print("✅ 2FA login successful!")
                
                # Remove used backup code and update environment
                updated_codes = [c for c in BACKUP_CODES if c.strip() != code]
                os.environ["IG_BACKUP_CODES"] = ",".join(updated_codes)
                
                # Optional: You might want to save this to .env file programmatically
                # or inform the user to update their .env file
                print(f"📝 Used backup code. Remaining codes: {len(updated_codes)}")
                
                break
            except Exception as twofa_error:
                print(f"❌ Backup code {i+1} failed: {twofa_error}")
                if i == len(BACKUP_CODES) - 1:
                    raise Exception("All backup codes failed. Please check your backup codes.")
    except Exception as e:
        # Re-raise other login errors
        print(f"❌ Login failed with error: {e}")
        raise

    # Save session for future use
    try:
        cl.dump_settings("session.json")
        print("💾 Session saved to session.json")
    except Exception as e:
        print(f"⚠️ Could not save session: {e}")

    return cl

cl = login()

# Ensure thread entry in data
def ensure_thread(thread_id):
    if thread_id not in bot_data["threads"]:
        admins = cl.direct_thread(thread_id).admin_user_ids
        bot_data["threads"][thread_id] = {
            "admins": admins,
            "members": [],
            "welcome_message": "Welcome @{}",
            "last_processed_message_id": None
        }
        save_data()

# Update admins list
def update_admins(thread):
    thread_id = thread.id
    ensure_thread(thread_id)
    if bot_data["threads"][thread_id]["admins"] != thread.admin_user_ids:
        return False
    bot_data["threads"][thread_id]["admins"] = thread.admin_user_ids
    save_data()

# Handle member changes (new members and members leaving)
def check_member_changes(thread):
    try:
        thread_id = thread.id
        ensure_thread(thread_id)
        print(f"ℹ️ Checking member changes for thread: {thread_id}")
    
        old_members = set(bot_data["threads"][thread_id]["members"])
        current_members = set(user.pk for user in thread.users)
        
        print(f"📊 Old members count: {len(old_members)}, Current members count: {len(current_members)}")

        # Find new members who joined
        new_members = current_members - old_members
        if new_members:
            print(f"👥 New members joined: {len(new_members)} users")
            for user in thread.users:
                if user.pk in new_members:
                    try:
                        welcome_template = bot_data["threads"][thread_id]["welcome_message"]
                        msg = welcome_template.format(user.username)
                        print(f"🤝 Welcoming new user: @{user.username}")
                        cl.direct_send(text=msg, thread_ids=[thread_id])
                        safe_sleep(3, 6)
                    except Exception as e:
                        print(f"❌ Error welcoming user @{user.username}: {e}")
                        cl.direct_send(text=f"⚠️ Error welcoming user. Contact @{OWNER_USERNAME}", thread_ids=[thread_id])

        # Find members who left (for tracking purposes, no action taken)
        left_members = old_members - current_members
        if left_members:
            print(f"📤 Members left: {len(left_members)} users")
            # Log usernames of members who left if possible
            try:
                for uid in left_members:
                    user = cl.user_info(uid)
                    print(f"   - @{user.username} left the group")
            except Exception as e:
                print(f"ℹ️ Could not fetch details for {len(left_members)} members who left")

        # Update the member list with current members
        bot_data["threads"][thread_id]["members"] = list(current_members)
        print(f"✅ Updated member list for thread {thread_id}")
        save_data()
        
    except Exception as e:
        print(f"❌ Error in check_member_changes: {e}")

# Command handler
def handle_command(thread, sender_id, text):
    thread_id = thread.id
    ensure_thread(thread_id)

    admins = bot_data["threads"][thread_id]["admins"]
    sender_is_admin = sender_id in admins

    if text.startswith("/mentionall") and sender_is_admin:
        members = bot_data["threads"][thread_id]["members"]
        mention_msgs = []
        msg = ""
        for idx, uid in enumerate(members, start=1):
            try:
                user = cl.user_info(uid)
                msg += f"@{user.username} "
                if idx % 5 == 0:  # send every 5 mentions to avoid spam block
                    mention_msgs.append(msg.strip())
                    msg = ""
            except Exception:
                cl.direct_send(text=f"⚠️ Error in mentionall. Contact @{OWNER_USERNAME}", thread_ids=[thread_id])

        if msg:
            mention_msgs.append(msg.strip())

        for m in mention_msgs:
            cl.direct_send(text=m, thread_ids=[thread_id])
            safe_sleep(8, 12)

    elif text.startswith("/setwelcome") and sender_is_admin:
        new_msg = text.replace("/setwelcome", "").strip()
        bot_data["threads"][thread_id]["welcome_message"] = new_msg
        save_data()
        cl.direct_send(text="✅ Welcome message updated!", thread_ids=[thread_id])

    elif text.startswith("/getwelcome") and sender_is_admin:
        wm = bot_data["threads"][thread_id]["welcome_message"]
        cl.direct_send(text=f"📢 Current welcome message:\n{wm}", thread_ids=[thread_id])

    elif text.startswith("/updateadmins") and sender_is_admin:
        is_updated = update_admins(thread)
        if is_updated:
            cl.direct_send(text="✅ Admin list updated!", thread_ids=[thread_id])

    elif text.startswith("/help") and sender_is_admin:
        help_text = (
            "📖 Commands:\n"
            "/mentionall – Mention everyone\n"
            "/setwelcome <msg> – Set welcome (use {} for username)\n"
            "/getwelcome – Show current welcome msg\n"
            "/updateadmins – Refresh admins\n"
            "/help – Show this menu"
        )
        cl.direct_send(text=help_text, thread_ids=[thread_id])

# Main loop
def run_bot():
    while True:
        try:
            inbox = cl.direct_threads()
            
            for thread in inbox:
                if not thread.is_group:
                    continue

                ensure_thread(thread.id)
                check_member_changes(thread)

                # Get messages and filter out already processed ones
                messages = cl.direct_messages(thread.id)
                new_messages = []
                last_processed_id = bot_data["threads"][thread.id]["last_processed_message_id"]
                
                for msg in messages:
                    # Skip if this is our own message
                    if msg.user_id == f"{cl.user_id}":
                        continue
                    
                    # Skip if we've already processed this message
                    if last_processed_id and msg.id == last_processed_id:
                        break
                    
                    new_messages.append(msg)
                
                # Process new messages in reverse order (oldest first)
                for msg in reversed(new_messages):
                    if msg.text and msg.text.startswith("/"):
                        handle_command(thread, int(msg.user_id), msg.text)
                
                # Update last processed message ID if we found new messages
                if new_messages:
                    bot_data["threads"][thread.id]["last_processed_message_id"] = new_messages[0].id
                    save_data()

            safe_sleep(10, 15)
        except Exception:
            safe_sleep(20, 30)

run_bot()