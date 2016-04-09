import time
import re
import random
import logging
import datetime
crontable = []
outputs = []
attachments = []
raid_name = ""
raid_level = 0
raid_size = 0
players = []
raid_date = date.today()

typing_sleep = 0

greetings = ['Hi friend!', 'Hello there.', 'Howdy!', 'Wazzzup!!!', 'Hi!', 'Hey.']
help_text = "{}\n{}\n{}\n{}\n{}\n{}\n{}".format(
    "Hello! I'm your secRaidtary! ",
    "`!raid new [name] [lvl] [size] [mm-dd]` to schedule a new raid.",
    "`!raid player [username] [DPS/Heal/Tank]` to add a player to the raid roster.",
    "`!raid time [username] [start] [end]` to set a player's available times, in 24-hour format.",
    "`@secraidtary` to get a summary of the current raid.",
	"`!raid reset` to clear raid information.",
    "`!raid help` to see this again.")

# regular expression patterns for string matching
secraidtary_new = re.compile("!raid[\s]*new")
p_bot_joke = re.compile("!raid[\s]*player")
p_bot_attach = re.compile("!raid[\s]*time")
p_bot_help = re.compile("!raid[\s]*help")

def process_message(data):
    logging.debug("process_message:data: {}".format(data))

    if secraidtary_new.match(data['text']):
		tokens = data['text'].split(' ')
		raid_name = tokens[2]
		raid_level = int(tokens[3])
		raid_size = int(tokens[4])
		raid_date = strptime(tokens[5], "%b-%d")
		string_out = "Okay. I have scheduled a level {} raid for {} players on {}.\nYou will be running {}.".format(raid_level,raid_size,raid_date,raid_name)
        outputs.append([data['channel'], string_out])

    elif p_bot_joke.match(data['text']):
        outputs.append([data['channel'], "Why did the python cross the road?"])
        outputs.append([data['channel'], "__typing__", 5])
        outputs.append([data['channel'], "To eat the chicken on the other side! :laughing:"])

    elif p_bot_attach.match(data['text']):
        txt = "Beep Beep Boop is a ridiculously simple hosting platform for your Slackbots."
        attachments.append([data['channel'], txt, build_demo_attachment(txt)])

    elif p_bot_help.match(data['text']):
        outputs.append([data['channel'], "{}".format(help_text)])

    elif data['text'].startswith("pybot"):
        outputs.append([data['channel'], "I'm sorry, I don't know how to: `{}`".format(data['text'])])

    elif data['channel'].startswith("D"):  # direct message channel to the bot
        outputs.append([data['channel'], "Hello, I'm the BeepBoop python starter bot.\n{}".format(help_text)])

def process_mention(data):
    logging.debug("process_mention:data: {}".format(data))
    outputs.append([data['channel'], "You really do care about me. :heart:"])

def build_demo_attachment(txt):
    return {
        "pretext" : "We bring bots to life. :sunglasses: :thumbsup:",
		"title" : "Host, deploy and share your bot in seconds.",
		"title_link" : "https://beepboophq.com/",
		"text" : txt,
		"fallback" : txt,
		"image_url" : "https://storage.googleapis.com/beepboophq/_assets/bot-1.22f6fb.png",
		"color" : "#7CD197",
    }
