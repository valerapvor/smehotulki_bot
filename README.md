# Smehotulki (Humor House) Suggestion Bot
> A simple proposal bot for Telegram in Python (PyTelegramBotAPI)
> that will send messages, video gifs, files, etc. bot administrator.

**Smehotulki Suggestion Bot** - *A free open source bot that runs on Python and the PyTelegramBotAPI library.
It has simple and functional functionality.*

---

# Functions
- Check user ID with `/checkid`.
- Send suggestions to admins via `/send`.
- Display a welcome message with `/start`.
- Admins can manage the suggestion box (open/closed) with `/admin`.
- Forward all received messages to admins.
- Add new admins by providing their ID.
- Handle text, photos, videos, documents, and animations.
- Block users who violate rules.
- Store suggestions and forward them to admins.
- Reply to users' suggestions.
- Inform users if the suggestion box is open or closed.
- Allow admins to reply directly to users.
- Save suggestion box status to a file.
- Ensure necessary directories exist for storing messages.
- Handle media files (photos, videos, documents).

---

# Demo

**Sending message**

![image](https://github.com/user-attachments/assets/071733fe-2a86-41d6-8490-c2131221a60b)

**Sended message**

![image](https://github.com/user-attachments/assets/364e2912-512f-409a-aca4-7ad45378974b)


**Message Management**

![image](https://github.com/user-attachments/assets/88637a88-69f8-4f52-a5c7-53e8a1839bdb)

- `Blacklist` - add the sender to the blacklist (he will not be able to send messages, but will be able to use other functions)

- `Reply` - reply to the user (the bot will send the user a message with the admin’s response)

### *...and a bunch of other features*


---

# Installation (by Git on Linux)

1) Select the folder in which you want to install the bot
2) Clone the repository:
```
git clone https://github.com/valerapvor/smehotulki_bot.git
```
3) Install dependencies:
```
pip install PyTelegramBotAPI
```
4) Edit main.py:
Change in `TOKEN` - `-` to you real telegram bot api, created using @BotFather in telegram.
5) Start bot:
```
./start.sh
```
6) Go to bot and send `/checkid` command, bot send a id you copy he.
7) Go to `main.py` and paste copy id into `ADMIN_ID`.
8) Restart bot.

*Guide version 1.0 *(I will update frequently)*
