from aptbot.bot import Message, Commands, Bot
import os
import logging
import ttv_api.users
import sqlite3
import time

logger = logging.getLogger(__name__)

PERMISSION = 99
PREFIX = "?"
DESCRIPTION = r"Makes yourself available in the list."
USER_COOLDOWN = 600
GLOBAL_COOLDOWN = 0

PATH = os.path.dirname(os.path.realpath(__file__))
PATH = os.path.join(PATH, "..")


def main(bot: Bot, message: Message):
    twitch = ttv_api.users.get_users(user_logins=[message.nick])
    if not twitch:
        bot.send_privmsg(
            message.channel,
            "There was an issue fetching your twitch data. You weren't made unavailable.",
            reply=message.tags["id"],
        )
        return
    twitch_id = twitch[0].user_id
    conn = sqlite3.connect(os.path.join(PATH, "lol_data.db"))
    c = conn.cursor()

    c.execute(
        """
        UPDATE
            lol_queue
        SET
            position = (
                CASE
                    WHEN (
                        SELECT
                            position
                        FROM
                            lol_queue
                        WHERE
                            twitch_id = ?
                    ) < (
                        SELECT
                            max(position)
                        FROM (
                            SELECT
                                position
                            FROM
                                lol_queue
                            WHERE
                                available = 1
                            ORDER BY
                                position
                            LIMIT (
                                SELECT
                                    data
                                FROM
                                    lol_queue_data
                                WHERE
                                    name = 'queuesize'
                            )
                        )
                    )
                    THEN position + 1
                    ELSE position
                END
            )
        WHERE
            position > (
                SELECT
                    max(position)
                FROM
                    lol_queue
                WHERE
                    priority_queue = 1
                    OR position <= (
                        SELECT
                            max(position)
                        FROM (
                            SELECT
                                position
                            FROM
                                lol_queue
                            WHERE
                                available = 1
                            ORDER BY 
                                position
                            LIMIT (
                                SELECT
                                    data
                                FROM
                                    lol_queue_data
                                WHERE
                                    name = 'queuesize'
                            )
                        )
                            
                    )
            );
        """,
        (twitch_id,),
    )

    c.execute(
        """
        UPDATE
            lol_queue
        SET 
            available = 1,
            priority_queue = (
                CASE
                    WHEN (
                        SELECT
                            position
                        FROM
                            lol_queue
                        WHERE
                            twitch_id = ?
                    ) < (
                        SELECT
                            max(position)
                        FROM (
                            SELECT
                                position
                            FROM
                                lol_queue
                            WHERE
                                available = 1
                            ORDER BY 
                                position
                            LIMIT (
                                SELECT
                                    data
                                FROM
                                    lol_queue_data
                                WHERE
                                    name = 'queuesize'
                            )
                        )
                    )
                    THEN 1
                    ELSE null
                END
            ),
            position = (
                CASE
                    WHEN (
                        SELECT
                            position
                        FROM
                            lol_queue
                        WHERE
                            twitch_id = ?
                    ) < (
                        SELECT
                            max(position)
                        FROM (
                            SELECT
                                position
                            FROM
                                lol_queue
                            WHERE
                                available = 1
                            ORDER BY 
                                position
                            LIMIT (
                                SELECT
                                    data
                                FROM
                                    lol_queue_data
                                WHERE
                                    name = 'queuesize'
                            )
                        )
                    )
                    THEN 1 + (
                        SELECT
                            max(position)
                        FROM
                            lol_queue
                        WHERE
                            priority_queue = 1
                            OR position <= (
                                SELECT
                                    max(position)
                                FROM (
                                    SELECT
                                        position
                                    FROM
                                        lol_queue
                                    WHERE
                                        available = 1
                                    ORDER BY 
                                        position
                                    LIMIT (
                                        SELECT
                                            data
                                        FROM
                                            lol_queue_data
                                        WHERE
                                            name = 'queuesize'
                                    )
                                )
                            )
                    )
                    ELSE position
                END
            ),
            time_remaining = time_remaining - (? - last_available)
        WHERE 
            twitch_id = ?
            AND available = 0;
        """,
        (
            twitch_id,
            twitch_id,
            int(time.time()),
            twitch_id,
        ),
    )
    if c.rowcount < 1:
        bot.send_privmsg(
            message.channel,
            "You aren't in the list or you were already available.",
            reply=message.tags["id"],
        )
        conn.close()
        return
    conn.commit()
    c.execute("DELETE FROM lol_queue WHERE time_remaining < 0;")
    if c.rowcount > 0:
        bot.send_privmsg(
            message.channel,
            "You were unavailable for too long, you have been removed from the list.",
            reply=message.tags["id"],
        )
        conn.commit()
        conn.close()
        return
    conn.commit()
    bot.send_privmsg(
        message.channel,
        "Successfully made you available",
        reply=message.tags["id"],
    )
    conn.close()
