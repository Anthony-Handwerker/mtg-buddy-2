import time
import re
import random
import string
import logging
import datetime
import urllib as ul

crontable = []
outputs = []


typing_sleep = 0

# regular expression patterns for string matching, kept for reference
#mtg_new = re.compile("!mtg[\s]*")


def process_message(data):
    logging.debug("process_message:data: {}".format(data))

    try:
        s1 = data['text']
        thread = data.get('thread_ts', data['ts'])
        print(thread)

        #outputs.append([data['channel'], temp_str])
        if s1.find("[[") == 0:
            s1 = "A"+s1

        tokens = s1.split('[[')

        counter = 0

        for i in range(1, len(tokens)):
            if tokens[i].find("]]") > -1:
                card_names = tokens[i].split(']]')
                card_name = card_names[0]
                url = {'q' : card_name}
                temp = ul.urlencode(url)
                response = ul.urlopen("http://mtg.wtf/card?"+temp)

                html = str(response.read())

                start = html.find("/cards")
                end = html.find("\'", start)
                if end <= start or html[start:end] == "":
                    outputs.append([data['channel'], "Could not find " + card_name, thread])
                else:
                    outputs.append([data['channel'], "http://mtg.wtf" + html[start:end], thread])


    except ValueError:
        outputs.append([data['channel'], "Failure"])
    except:
        outputs.append([data['channel'], "Failure"])



def process_mention(data):
    print("test") #currently unused

#    outputs.append([data['channel'], "Once that's set, you're all ready to go!"])


