from aptbot.bot import Message, Commands, Bot
import os
import logging
import ttv_api.users
import sqlite3
import time

logger = logging.getLogger(__name__)

PERMISSION = 10
PREFIX = "\\"
DESCRIPTION = r"Makes yourself temporarily unavailable in the list."
USER_COOLDOWN = 0
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


def main(bot: Bot, message: Message):
    twitch_name = message.tags.get("reply-parent-user-login", None)
    if not twitch_name:
        twitch_name = message.value.split(" ")[1]
    twitch = ttv_api.users.get_users(user_logins=[twitch_name])
    if not twitch:
        bot.send_privmsg(
            message.channel,
            "There was an issue fetching their twitch data. They weren't made unavailable.",
            reply=message.tags["id"],
        )
        return
    twitch_id = twitch[0].user_id
    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    c.execute(
        """
        UPDATE lol_queue SET available = 0, priority_queue = null, last_available = ? WHERE twitch_id = ?;
        """,
        (
            int(time.time()),
            twitch_id,
        ),
    )
    if not c.rowcount:
        bot.send_privmsg(
            message.channel,
            "They aren't in the list or they were already unavailable.",
            reply=message.tags["id"],
        )
        conn.close()
        return
    conn.commit()
    bot.send_privmsg(
        message.channel,
        "Successfully made them unavailable",
        reply=message.tags["id"],
    )
    conn.close()
