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
raid_date = datetime.date.today()

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
secraidtary_player = re.compile("!raid[\s]*player")
secraidtary_time = re.compile("!raid[\s]*time")
secraidtary_help = re.compile("!raid[\s]*help")

def get_roles(player):
    roles = ''
    if player['dps']:
        roles += 'DPS'
    if player['healer']:
        if roles != '':
            roles += '/'
        roles += 'Healer'
    if player['tank']:
        if roles != '':
            roles += '/'
        roles += 'Tank'
    return roles

def process_message(data):
    global raid_name
    global raid_date
    global raid_level
    global raid_size
    logging.debug("process_message:data: {}".format(data))

    if secraidtary_new.match(data['text']):
        tokens = data['text'].split(' ')
        raid_name = tokens[2]
        raid_level = int(tokens[3])
        raid_size = int(tokens[4])
        raid_date = time.strptime(tokens[5], "%m-%d")
        string_out = "Okay. I have scheduled a level {} raid for {} players on {}/{}.\nYou will be running {}.".format(raid_level,raid_size,raid_date.tm_mon,raid_date.tm_mday,raid_name)
        outputs.append([data['channel'], string_out])

    elif secraidtary_player.match(data['text']):
        tokens = data['text'].split(' ')
        player_name = tokens[2]
        player_roles = tokens[3]
        player = {'name': player_name, 'dps': 'DPS' in tokens[3], 'healer': 'Heal' in tokens[3], 'tank': 'Tank' in tokens[3],
                  'start': time.ctime(0), 'end': time.ctime(0)}

        output = "Okay, {} has been registered as {}.".format(player_name, get_roles(player))
        players.append(player)
        outputs.append([data['channel'], output])

    elif secraidtary_time.match(data['text']):
        tokens = data['text'].split(' ')
        player_name = tokens[2]
        player_start = tokens[3]
        player_stop = tokens[4]
        t_start = time.strptime(player_start, "%H:%M")
        t_stop = time.strptime(player_stop, "%H:%M")
        for i in range(0, len(players)):
            player = players[i]
            if player['name'] == player_name:
                players.remove(player)
                player['start'] = t_start
                player['end'] = t_stop
                out = "Okay, {}. You have set yourself as available from {}:{} to {}:{}.".format(player_name, t_start.tm_hour, t_start.tm_min, t_stop.tm_hour, t_start.tm_min)
                outputs.append([data['channel'], out])
                return
        attachments.append([data['channel'], "It looks like you haven't registered your character. Please use `!raid player` first."])

    elif secraidtary_help.match(data['text']):
        outputs.append([data['channel'], "{}".format(help_text)])

    elif data['text'].startswith("pybot"):
        outputs.append([data['channel'], "I'm sorry, I don't know how to: `{}`".format(data['text'])])

    elif data['channel'].startswith("D"):  # direct message channel to the bot
        outputs.append([data['channel'], "Hello, I'm the BeepBoop python starter bot.\n{}".format(help_text)])

def process_mention(data):
    logging.debug("process_mention:data: {}".format(data))
    if raid_name == '':
        outputs.append([data['channel'], 'Hello!'])
        outputs.append([data['channel'], 'Looks like you don\'t have any raids scheduled at the moment.'])
        return
    output = 'Alright, so here\'s how your raid on {} looks so far:'.format(raid_name)
    outputs.append([data['channel'], output])
    output = 'The dungeon is level {}; {}/{} players have signed up.'.format(raid_level, len(players), raid_size)
    outputs.append([data['channel'], output])
    if len(players) == 0:
        return
    outputs.append([data['channel'], "Here's the player list:"])
    for player in players:
        output = "{}({})".format(player['name'], get_roles(player))
        outputs.append([data['channel'], output])

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
