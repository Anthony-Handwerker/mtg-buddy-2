import time
import re
import random
import string
import logging
import datetime
import urllib as ul

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
mtg_new = re.compile("!mtg[\s]*")
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

    if mtg_new.match(data['text']):
        try:
            temp_str = process_quoted(data['text'])
            #outputs.append([data['channel'], temp_str])

            tokens = temp_str.split(' ')
            tokens[2] = string.replace(tokens[2], '^', '+')
            card_name = tokens[2]
            response = ul.urlopen("http://magiccards.info/query?q="+card_name+"&v=card&s=cname")
            html = str(response.read())
            start = html.find("http://magiccards.info/scans/")
            end = html.find("\"", start)
            outputs.append([data['channel'], html[start:end]])


        except ValueError:
            outputs.append([data['channel'], "Failure"])
        except:
            outputs.append([data['channel'], "Failure"])



def process_mention(data):
    print("test")

#    outputs.append([data['channel'], "Once that's set, you're all ready to go!"])


