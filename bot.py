# (c) @xditya

import logging

from decouple import config

from telethon import TelegramClient, events
from aioredis import Redis

# initializing logger
logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s"
)
log = logging.getLogger("XDITYA")

# fetching variales from env
try:
    BOT_TOKEN = config("BOT_TOKEN")
    OWNERS = config("OWNERS")
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


@bot.on(events.NewMessage(incoming=True, from_users=OWNERS, pattern="^/stats$"))
async def stats(event):
    await event.reply(f"Total chats: {len(eval(await db.get(var_name) or '[]'))}")


@bot.on(events.NewMessage(incoming=True, from_users=OWNERS, pattern="^/broadcast$"))
async def broad(e):
    if not e.reply_to_msg_id:
        return await e.reply(
            "Please use `/broadcast` as reply to the message you want to broadcast."
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


log.info("\nBot has started.\n(c) @xditya\n")
bot.run_until_disconnected()
