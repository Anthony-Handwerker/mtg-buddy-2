import time
import re
import random
import string
import logging
import datetime

crontable = []
outputs = []
attachments = []
current_raid = ""
raid_name = ""
raid_level = 0
raid_size = 0
players = {}
raids = {}
intro = 0
raid_date = datetime.date.today()

typing_sleep = 0

greetings = ['Hi friend!', 'Hello there.', 'Howdy!', 'Wazzzup!!!', 'Hi!', 'Hey.']
help_text = "{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n".format(
    "`!raid new [name] [lvl] [size] [mm/dd]` to schedule a new raid.",
    "`!raid player [username] [DPS Level] [Tank Level] [Healer Level]` to add a player to the raid roster.",
    "`!raid register [username] [start] [end]` to set a player's available times, in 24-hour format.",
    "`@secraidtary` to get a summary of the next raid.",
    "`!raid delete [player/raid] [name]` to remove a player or raid from the register.",
    "`!raid levelup [name] [d/t/h] {new-lvl}` to increase the level of a character on the roster.",
    "`!raid lookup [name]` to look up information on a raid or player.",
	"`!raid reset` to clear raid information.",
    "`!raid help` to see this again.")

# regular expression patterns for string matching
secraidtary_new = re.compile("!raid[\s]*new")
secraidtary_player = re.compile("!raid[\s]*player")
secraidtary_time = re.compile("!raid[\s]*time")
secraidtary_help = re.compile("!raid[\s]*help")
secraidtary_reset = re.compile("!raid[\s]*reset")

def get_times():
    s_times = [player['start'] for player in players]
    e_times = [player['end'] for player in players]
    s_time = max(s_times)
    e_time = min(e_times)
    return [s_time, e_time]

def get_roles2():
    DPS_only = [player['name'] for player in players if player['dps'] and not player['healer'] and not player['tank']]
    Heal_only = [player['name'] for player in players if not player['dps'] and player['healer'] and not player['tank']]
    Tank_only = [player['name'] for player in players if not player['dps'] and not player['healer'] and player['tank']]
    DPS_needed = raid_size/2 - len(DPS_only)
    Heal_needed = raid_size/4 - len(Heal_only)
    Tank_needed = raid_size/4 - len(Tank_only)
    return [DPS_needed, Heal_needed, Tank_needed]

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

def process_quoted(s):
    while 1:
        pos1 = string.find(s,'"')
        if pos1 == -1:
            break
        pos2 = string.find(s,'"',pos1 + 1)
        substr = s[pos1+1:pos2]
        substr = string.replace(substr, ' ', '^')
        s = s[:pos1] + substr + s[pos2+1:]
    return s

def process_message(data):
    logging.debug("process_message:data: {}".format(data))

    if secraidtary_new.match(data['text']):
        try:
            temp_str = process_quoted(data['text'])
            #outputs.append([data['channel'], temp_str])

            tokens = temp_str.split(' ')
            tokens[2] = string.replace(tokens[2], '^', ' ')
            raid_name = tokens[2]

            if raid_name in raids:
                outputs.append([data['channel'], "This raid is already on record, please enter a different name or use `!raid delete raid`"])
                return

            #shitposting code
            if raid_name == "CrystalBraves":
                outputs.append([data['channel'], "The Crystal Braves are a well-funded and effective organization."])
                return
            if raid_name == "TotoRak" or raid_name == "ThousandMaws":
                outputs.append([data['channel'], "Why are you running this dungeon? Why?"])
            if raid_name.lower() == "dutyroulette" or raid_name.lower() == "duty roulette":
                outputs.append([data['channel'], "http://i3.kym-cdn.com/photos/images/newsfeed/000/959/160/e65.jpg"])
            if raid_name == "Shitpost":
                outputs.append([data['channel'], "http://i0.kym-cdn.com/photos/images/newsfeed/000/875/364/dce.jpg"])
                return

            #filter out spaces

            #input checks
            raid_level = int(tokens[3])
            if raid_level > 60:
                outputs.append([data['channel'], "Current max level is 60, so I don't think that dungeon level is right."])
                return
            if raid_level < 1:
                outputs.append([data['channel'], "If you don't want to put a limit on the dungeon, just enter 1 as the level."])
                return
            raid_size = int(tokens[4])
            if not raid_size in [4,8,24]:
                outputs.append([data['channel'], "Current dungeon sizes are only 4, 8, and 24. Please try again."])
                return
            raid_date = time.strptime(tokens[5], "%m/%d")

            r_data = {'level':raid_level, 'date':raid_date, 'size':raid_size, 'party':[]}
            raids[raid_name]=r_data

            string_out = "Okay. I have scheduled a level {} raid for {} players on {}/{}.\nYou will be running {}.".format(raid_level,raid_size,raid_date.tm_mon,raid_date.tm_mday,raid_name)
            outputs.append([data['channel'], string_out])
        except ValueError:
            outputs.append([data['channel'], "I think you entered a number or date incorrectly. Check your command and try again."])
        except:
            outputs.append([data['channel'], "I don't quite know what you meant. Try again or check `!raid help`"])

    elif secraidtary_player.match(data['text']):
        try:
            temp_str = process_quoted(data['text'])
            tokens = temp_str.split(' ')
            tokens[2] = string.replace(tokens[2], '^', ' ')
            player_name = tokens[2]

            if player_name in players:
                outputs.append([data['channel'], "This player is already on record; please enter a different name, use `!raid levelup`, or use `!raid delete raid`"])
                return

            player_roles = tokens[3]
            player = {'dps': int(tokens[3]), 'healer': int(tokens[4]), 'tank': int(tokens[5])}

            output = "Okay, {} has been registered as a level {} DPS, a level {} healer, and a level {} tank.".format(player_name, player['dps'], player['healer'], player['tank'])
            players[player_name] = player
            outputs.append([data['channel'], output])
        except ValueError:
            outputs.append([data['channel'], "I think you entered a number incorrectly. Check your command and try again."])
        except:
            outputs.append([data['channel'], "I don't quite know what you meant. Try again or check `!raid help`"])

    elif secraidtary_time.match(data['text']):
        try:
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
                    players.append(player)
                    out = "Okay, {}. You have set yourself as available from {}:{} to {}:{}.".format(player_name, t_start.tm_hour, t_start.tm_min, t_stop.tm_hour, t_start.tm_min)
                    outputs.append([data['channel'], out])
                    return
            outputs.append([data['channel'], "It looks like you haven't registered your character. Please use `!raid player` first."])
        except:
            outputs.append([data['channel'], "I don't quite know what you meant. Try again or check `!raid help`"])

    elif secraidtary_help.match(data['text']):
        outputs.append([data['channel'], "{}".format(help_text)])

    elif secraidtary_reset.match(data['text']):
        global raid_name, raid_level, raid_date, raid_size, players
        raid_name = ""
        raid_level = 0
        raid_date = datetime.date.today()
        raid_size = 0
        players = []
        outputs.append([data['channel'], "Raid data cleared!"])

    elif data['text'].startswith("!raid"):
        outputs.append([data['channel'], "I'm sorry, I don't know how to: `{}`".format(data['text'])])

    elif data['channel'].startswith("D"):  # direct message channel to the bot
        outputs.append([data['channel'], "{}".format(help_text)])

def process_mention(data):
    global intro
    try:
        logging.debug("process_mention:data: {}".format(data))
        if "Introduce" in data['text'] and intro == 0:
            outputs.append([data['channel'], "Hello, everyone! I'm your new secRaidtary!\nI'll track when raids are planned and who's participating, so you know when everyone's okay to go!\nHere's a list of the commands you can use:"])
            outputs.append([data['channel'],help_text])
            intro = 1
            return
        if raid_name == '':
            outputs.append([data['channel'], 'Hello!'])
            outputs.append([data['channel'], 'Looks like you don\'t have any raids scheduled at the moment.'])
            return
        output = 'Alright, so here\'s how your {} raid on {}/{} looks so far:'.format(raid_name, raid_date.tm_mon,raid_date.tm_mday)
        outputs.append([data['channel'], output])
        output = 'The dungeon is level {}; {}/{} players have signed up.'.format(raid_level, len(players), raid_size)
        outputs.append([data['channel'], output])
        if len(players) == 0:
            return
        outputs.append([data['channel'], "Here's the player list:"])
        output = ""
        for player in players:
            output += "{}({})\n".format(player['name'], get_roles(player))
        outputs.append([data['channel'], output])
        times = get_times()
        if(times[0] > times[1]):
            outputs.append([data['channel'],"Unfortunately, there is no time where everyone is available."])
            return
        output = "Everyone is available between {}:{} and {}:{}".format(times[0].tm_hour, times[0].tm_min, times[1].tm_hour, times[0].tm_min)
        outputs.append([data['channel'], output])
        roles = get_roles2()
        output = "Players with more than one role, the party needs {} more DPS, {} more healer(s), and {} more tank(s).".format(roles[0], roles[1], roles[2])
        outputs.append([data['channel'], output])
    except:
        outputs.append([data['channel'], "Well, something went wrong reading your raid data. You might have to `!raid reset`"])
#    outputs.append([data['channel'], "Once that's set, you're all ready to go!"])


