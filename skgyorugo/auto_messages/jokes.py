from aptbot.bot import Message, Commands, Bot
import tools.smart_privmsg
import urllib3
import json

COOLDOWN = 20 * 60
END_TIME = 0

header = {
    "Accept": "application/json",
    "User-Agent": "For my twitch bot [MurphyAI] on https://twitch.tv/ihaspeks",
}


def main(bot: Bot, message: Message):
    http = urllib3.PoolManager()
    r = http.request("GET", "https://icanhazdadjoke.com", headers=header)
    if r.status != 200:
        tools.smart_privmsg.send(bot, message, f"Couldn't get a joke Sadge")
        return

    data = json.loads(r.data.decode("utf-8"))
    joke = data["joke"].replace("\r\n", " ")
    tools.smart_privmsg.send(
        bot, message, f"{joke} ||| Get more jokes by typing ?joke"
    )
