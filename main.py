import os
import telebot
from telebot import types

TOKEN = "7575017843:AAEhjPO0AdvOQ2PJs2C-Ej4W-YWchquCOFE"  # PASTE YOUR TG Token here
ADMIN_ID = 1679122331  # Paste your telegram account ID, you can check it
ADMIN_IDS = {ADMIN_ID}  # Admins
MSG_DIR = "msg/user"
status = "open"

# Status file
STATUS_FILE = 'suggestions_status.txt'

# Banned users
banned_users = set()

# Reading status file
def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            status = f.read().strip()
            return status == 'open'  # If 'open' in file, return True
    return True  # If the file doesn't exist, by default the suggestion box is open

# Write status file
def save_status(status):
    with open(STATUS_FILE, 'w') as f:
        f.write('open' if status else 'closed')

# Adds to ban list
def add_banned_user(user_id):
    with open("banned_users.txt", "a") as f:
        f.write(f"{user_id}\n")

# Loading status
suggestions_open = load_status()

bot = telebot.TeleBot(TOKEN)

# Send msg storage
user_message_cache = {}

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

@bot.message_handler(commands=['start'])
def start(message):
    # Path to the file
    photo_path = "welcome.gif"
    
    # Sending photo
    with open(photo_path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo, caption="Hello, this is an open-source suggestion bot!")

@bot.message_handler(commands=['send'])
def send_suggestion(message):
    text = message.text[6:].strip()
    if text:
        user_id = message.from_user.id
        username = message.from_user.username or "No username"
        bot.send_message(ADMIN_ID, f"New message from @{username}.\nMSG:\n\n{text}")
        
        user_dir = os.path.join(MSG_DIR, str(user_id))
        ensure_directory_exists(user_dir)
        with open(os.path.join(user_dir, "suggestions.txt"), "a", encoding="utf-8") as file:
            file.write(f"{text}\n")
        
        bot.reply_to(message, "Message sent!")
    else:
        status_text = "open" if suggestions_open else "closed"
        bot.reply_to(message, "So, after this message, you can skip anything, it will go to the admins of the humor houses.\nATTENTION:\n- This must be either a message or a file, if you send a file with a signature, it will only be a file direction\n- Only ONE file, for example, if you create several video commands, only ONE video will be sent.\n\nIMPORTANT: Suggestion now: " + status_text + ".")

@bot.message_handler(commands=['checkid'])
def check_id(message):
    bot.send_message(message.chat.id, f"Your ID: {message.from_user.id}")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("✅ Get your ID", callback_data="checkid"))
    
    if message.from_user.id in ADMIN_IDS:
        keyboard.add(types.InlineKeyboardButton("📂 Forward all messages", callback_data="forward_msgs"))
        keyboard.add(types.InlineKeyboardButton("➕ Add another ADMIN_ID", callback_data="add_admin"))
        keyboard.add(types.InlineKeyboardButton("🔄 Close/Open suggestion box", callback_data="toggle_suggestions"))
    
    bot.send_message(message.chat.id, "Admin Panel:", reply_markup=keyboard)

suggestions_open = True

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global suggestions_open
    
    if call.data == "checkid":
        # Reply to ID request already sent
        bot.answer_callback_query(call.id, "ID has been sent in another message.")
    elif call.data == "forward_msgs" and call.from_user.id in ADMIN_IDS:
        ensure_directory_exists(MSG_DIR)
        bot.send_message(call.message.chat.id, "Messages saved in folder msg/user/")
    elif call.data == "add_admin" and call.from_user.id in ADMIN_IDS:
        bot.send_message(call.message.chat.id, "Send the ID of the new admin.")
        bot.register_next_step_handler(call.message, add_admin)
    elif call.data == "toggle_suggestions" and call.from_user.id in ADMIN_IDS:
        suggestions_open = not suggestions_open
        save_status(suggestions_open)  # Save new status to file
        status = "open" if suggestions_open else "closed"
        bot.send_message(call.message.chat.id, f"Suggestion box is now {status}.")
    elif call.data.startswith("block_user_"):
        user_id = int(call.data.split("_")[-1])
        banned_users.add(user_id)
        add_banned_user(user_id)  # Write to file
        bot.send_message(call.message.chat.id, f"User with ID {user_id} has been blocked.")
        bot.answer_callback_query(call.id, "User has been blocked.")
    elif call.data.startswith("reply_to_user_"):
        user_id = int(call.data.split("_")[-1])
        bot.send_message(call.message.chat.id, f"Send the message you want to send to the user with ID {user_id}.")
        bot.register_next_step_handler(call.message, reply_to_user, user_id)
        bot.answer_callback_query(call.id, "You can send a reply.")
    else:
        bot.answer_callback_query(call.id, "This is allowed only for admins.")

def add_admin(message):
    try:
        new_admin_id = int(message.text.strip())
        ADMIN_IDS.add(new_admin_id)
        bot.send_message(message.chat.id, f"Admin {new_admin_id} has been added.")
    except ValueError:
        bot.send_message(message.chat.id, "Invalid ID. Please try again.")

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'document', 'animation', 'video', 'audio'])
def handle_message(message):
    if suggestions_open:
        # Check if user is banned
        if message.from_user.id in banned_users:
            bot.reply_to(message, "YOU ARE BLOCKED FOR VIOLATING THE RULES. You will no longer be able to send suggestions, but you can still use other features.")
            return
        
        # Create "Yes" and "No" buttons
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add(types.KeyboardButton("Yes"), types.KeyboardButton("No"))
        bot.send_message(message.chat.id, "Are you sure you want to send this message to the admins of the humor houses?", reply_markup=markup)
        
        # Cache the user's sent message
        user_message_cache[message.from_user.id] = {
            'type': message.content_type,
            'message': message
        }
        bot.register_next_step_handler(message, process_suggestion)

def process_suggestion(message):
    user_id = message.from_user.id
    
    if user_id in user_message_cache:
        cached_message = user_message_cache[user_id]
        original_message = cached_message['message']
        message_type = cached_message['type']
        
        if message.text == "Yes":
            text = ""
            file_to_send = None  # Here we store the file if it exists

            if message_type == "text":
                text = original_message.text
            elif message_type == "photo":
                text = "Contains photo."
                file_id = original_message.photo[-1].file_id
                file = bot.get_file(file_id)
                file_path = file.file_path
                file_name = file_path.split('/')[-1]
                downloaded_file = bot.download_file(file_path)
                file_to_send = (file_name, downloaded_file)  # Add file
            elif message_type == "animation":
                text = "Sent GIF."
                file_id = original_message.animation.file_id
                file = bot.get_file(file_id)
                file_path = file.file_path
                file_name = file_path.split('/')[-1]
                downloaded_file = bot.download_file(file_path)
                file_to_send = (file_name, downloaded_file)  # Add file
            elif message_type == "document":
                text = "Sent document."
                file_id = original_message.document.file_id
                file = bot.get_file(file_id)
                file_path = file.file_path
                file_name = file_path.split('/')[-1]
                downloaded_file = bot.download_file(file_path)
                file_to_send = (file_name, downloaded_file)  # Add file
            elif message_type == "video":
                text = "Sent video."
                file_id = original_message.video.file_id
                file = bot.get_file(file_id)
                file_path = file.file_path
                file_name = file_path.split('/')[-1]
                downloaded_file = bot.download_file(file_path)
                file_to_send = (file_name, downloaded_file)  # Add file
            elif message_type == "audio":
                text = "Sent audio file."
                file_id = original_message.audio.file_id
                file = bot.get_file(file_id)
                file_path = file.file_path
                file_name = file_path.split('/')[-1]
                downloaded_file = bot.download_file(file_path)
                file_to_send = (file_name, downloaded_file)  # Add file

            if text:
                username = message.from_user.username or "No username"
                # Before sending the file, ensure the directory exists
                user_dir = os.path.join(MSG_DIR, str(user_id))
                ensure_directory_exists(user_dir)

                # Create InlineKeyboardMarkup with buttons "Blacklist" and "Reply"
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton("Blacklist", callback_data=f"block_user_{user_id}"))
                keyboard.add(types.InlineKeyboardButton("Reply", callback_data=f"reply_to_user_{user_id}"))

                # Send file to suggestion box
                if file_to_send:
                    file_name, file_data = file_to_send
                    with open(os.path.join(user_dir, file_name), 'wb') as f:
                        f.write(file_data)

                    # Send file to admin with buttons
                    with open(os.path.join(user_dir, file_name), 'rb') as f:
                        bot.send_document(ADMIN_ID, f, caption=f"New message with file from @{username}:\n\n{text}", reply_markup=keyboard)
                else:
                    # If no file, send just the text with buttons
                    bot.send_message(ADMIN_ID, f"New message from @{username}:\n\n{text}", reply_markup=keyboard)

                # Notify user that their message has been sent to the admins
                bot.send_message(message.chat.id, "Sorry to disappoint... your message has been successfully delivered to the Admins of Humor Houses!")
            else:
                bot.send_message(message.chat.id, "Error processing the file. Please try again.")
        else:
            bot.send_message(message.chat.id, "Well, indeed, why bother.")
    else:
        bot.send_message(message.chat.id, "Something went wrong, please try again.")

def reply_to_user(message, user_id):
    bot.send_message(user_id, f"Admin from Humor Houses replied to one of your messages with the following text:\n{message.text}")
    bot.send_message(message.chat.id, "Message sent to the user.")

bot.polling(none_stop=True)

