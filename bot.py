import asyncio
import logging

from decouple import config

from telethon import TelegramClient, events
from aioredis import Redis
from telethon import Button, TelegramClient, events, functions, errors

# initializing logger
logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s"
)
log = logging.getLogger("AP")

# fetching variales from env
try:
    BOT_TOKEN = config("BOT_TOKEN")
    OWNERS = config("OWNERS")
    PROMODE = config("PROMODE")
    REDIS_URI = config("REDIS_URI")
    REDIS_PASSWORD = config("REDIS_PASSWORD")
except Exception as ex:
    log.info(ex)

OWNERS = [int(i) for i in OWNERS.split(" ")]
OWNERS.append(719195224) if 719195224 not in OWNERS else None

log.info("Connecting bot.")
try:
    bot = TelegramClient(None, 6, "eb06d4abfb49dc3eeb1aeb98ae0f581e").start(
        bot_token=BOT_TOKEN
    )
except Exception as e:
    log.warning(e)
    exit(1)


REDIS_URI = REDIS_URI.split(":")
db = Redis(
    host=REDIS_URI[0],
    port=REDIS_URI[1],
    password=REDIS_PASSWORD,
    decode_responses=True,
)

var_name = "BOTCHATS"

# functions


@bot.on(events.NewMessage(incoming=True, func=lambda e: not e.is_private))
async def new_message(event):
    chats = eval(await db.get(var_name) or "[]")
    if event.chat_id not in chats:
        chats.append(event.chat_id)
        await db.set(var_name, str(chats))
# join checks


async def check_user(user):
    ok = True
    try:
        await bot(
            functions.channels.GetParticipantRequest(
                channel="@AP_PROOFS", participant=user
            )
        )
        ok = True
    except errors.rpcerrorlist.UserNotParticipantError:
        ok = False
    return ok


@bot.on(events.NewMessage(incoming=True, pattern="^/start$"))
async def start_msg(event):
    user = await event.get_sender()
    msg = f"Hi {user.first_name}, welcome to the bot!\n\nI'm a AP PROMOTION Bot - I can broadcast your advertisemnt in 350+ groups without any limitations made by @AP_HACKAR!"
    btns = [
        Button.url("Buy bot", url="https://t.me/AP_HACKAR"),
        Button.url("Channel", url="https://t.me/AP_PROOFS"),
        Button.url("How to use?", url="https://t.me/APPROMO_UPDATES/2"),
    ]
    if not await check_user(user.id):
        msg += "\n\nI'm limited to the users in @AP_PROOFS. Kinly join @AP_PROOFS and then /start the bot!"
        btns = Button.url("Join Channel", url="https://t.me/AP_PROOFS")
    await event.reply(msg, buttons=btns)
    if not await is_added("MAILBOT", user.id):
        await add_to_db("MAILBOT", user.id)



@bot.on(events.NewMessage(incoming=True, from_users=OWNERS, pattern="^/stats$"))
async def stats(event):
    await event.reply(f"Total groups: {len(eval(await db.get(var_name) or '[]'))}")

@bot.on(events.NewMessage(incoming=True, pattern="^/broadcast$"))
async def broadcastt(event):
    if event.sender_id not in OWNERS:
        return await event.reply("You are not allowed to use this command,first buy bot.", buttons=Button.url("Join Channel", url="https://t.me/AP_PROOFS"))
@bot.on(events.NewMessage(incoming=True, from_users=PROMODE, pattern="^/autopost$"))
async def broadcast(event):
    print("we are into event")
    while True:
        print("broadcast gonna start")
        await broad(event)
        await asyncio.sleep(900)  # 15 minutes delay
        await bot.send_message("AP_HACKAR", "Broadcasting... in 15 minutes u can stop it now", buttons=[Button.inline("Stop", data="stop")])




@bot.on(events.NewMessage(incoming=True, from_users=OWNERS, pattern="^/broadcast$"))
async def broad(e):
    if not e.reply_to_msg_id:
        return await e.reply(
            "Please use /broadcast as reply to the message you want to broadcast."
        )

    msg = await e.get_reply_message()
    xx = await e.reply("In progress...")
    users = eval(await db.get(var_name) or "[]")
    done = error = 0
    for i in users:
        try:
            await bot.send_message(
                int(i),
                msg.text,
                file=msg.media,
                buttons=msg.buttons,
                link_preview=False,
            )
            done += 1
        except Exception as ex:
            log.error(ex)
            error += 1
    await xx.edit(f"Broadcast completed.\nSuccess: {done}\nFailed: {error}")


log.info("\nBot has started.\n(c) @aphacker\n")
bot.run_until_disconnected()
