from aptbot.bot import Message, Commands, Bot

COOLDOWN = 30 * 60
END_TIME = 2 * 60 * 60


def main(bot: Bot, message: Message):
    msg = "I'm a cute lil' wolf UwU and you're all cute lil' chatters OwO"
    bot.send_privmsg(message.channel, msg)
