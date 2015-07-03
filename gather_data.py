import json
import os
import time
import string
import datetime
import ijson
import re
from pprint import pprint

# mindshare!

RESULTS_FILE = "results.txt"
STORIES_FILE = "top.txt"
SAFE = False

def get_data():

    if SAFE and os.path.exists(RESULTS_FILE):
        print("%s already exists" % RESULTS_FILE)
        return

    # load static language list
    with open("languages.json") as fi:
        languages = json.loads(fi.read())

    # init results file and vars
    writeData('[', RESULTS_FILE, append=False)
    writeData('[', STORIES_FILE, append=False)
    store = initStore('init', languages)
    topStory = {}
    currentDate = ()
    primary_key = ''

    # initialize some counters
    top_score = 0
    stories = 0
    days = 0

    # we will store each day as a line in the file
    # format is {[day, month, year]: {language: score, lanuage: score, etc...}
    filepath = "D:\\Inbox\\HackerNewsStoriesAndCommentsDump\\HNStoriesAll.json"
    print("Loading file: %s" % filepath)
    with open(filepath) as fi:
        start = time.time()
        # each "hits" list is 1000 items
        for hits in ijson.items(fi, 'item.hits'):
            for story in hits:
                stories += 1
                # check what day the story is from, init new primary key if necessary
                newDate = parseTimestamp(story.get('created_at'))
                if newDate != currentDate:
                    primary_key = str(newDate)
                    if currentDate != ():
                        writeLine(store, RESULTS_FILE)
                        writeLine(topStory, STORIES_FILE)
                    store = initStore(primary_key, languages)
                    topStory = {primary_key: ""}
                    currentDate = newDate
                    top_score = 0
                    days += 1
                if stories % 1000 == 0:
                    # print some occasional status
                    print("Processed: %s stories, %s days" % (stories, days))
                for item in languages:
                    # core loop iterates over the stores in the hit list
                    # check if any of our language targets are present
                    score = find(story, item['words'])
                    if score:
                        # if we found a match, store the associated score
                        #print("+%s: %s" % (score, key))
                        language_key = item['name']
                        store[primary_key][language_key] += score
                        if score >= top_score:
                            topStory[primary_key] = story

        # wrap it up
        writeData(']', RESULTS_FILE, append=True)
        writeData(']', STORIES_FILE, append=True)
        end = time.time()
        print("total time: %s min" % ((end - start) / 60) )
        print("time per query: %s sec" % ((end - start) / stories) )

def parseTimestamp(dateString):
    # return a tuple of (day, month, year) from a given timestampe
    d = datetime.datetime.strptime(dateString, "%Y-%m-%dT%H:%M:%SZ")
    return (d.day, d.month, d.year)

def writeLine(data, filename):
    # take some json data and write it out
    writeData(json.dumps(data) + ',\n', filename)

def writeData(data, filename, append=True):
    # direct write for strings
    mode = 'a' if append else 'w'
    with open(filename, mode) as fi:
        fi.write(data)

def initStore(primary_key, languages):
    # populate initial date structure, a dict of {primary_key: {language: score, language: score, ...}}
    store = {primary_key: {}}
    for item in languages:
        store[primary_key][item['name']] = 0
    return store

def find(data, targets):
    # take some string data and look for matches from the given list of targets
    score = 0
    #print(data)
    title = data.get('title', '')
    text = data.get('text', '')
    norm_title = normalizeString(title)
    norm_text = normalizeString(text)
    score = data.get('score', 0)
    for target in targets:
        target = " %s " % target
        #print("searching for '%s' in '%s'" % (target, title))
        if title and (target in norm_title):
            if verifySingle(target, title):
                #print("Found @ title %s: %s -> %s" % (target, title, norm_title))
                score += int(data.get('points', 0))
        if text and (target in norm_text):
            if verifySingle(target, text):
                #print("Found @ text %s: %s -> %s" % (target, text, norm_text))
                score += int(data.get('points', 0))
    return score

def verifySingle(target, text):
    # a special function to handle single letter targets
    target = target.strip()
    if len(target) != 1:
        return True
    target = target.upper()
    if not re.search("\\b(%s)\\b" % target, text):
        #print("Denied regex %s: %s" % (target, text))
        return False
    if target + '.' in text:
        if target + '.  ' not in text:
            #print("Denied initials %s: %s" % (target, text))
            return False
    #print("Allowed %s: %s" % (target, text))
    return True

def normalizeString(sentence):
    """
    iterate over the string char by char and convert any troublesome characters
    such as period, comma, etc into spaces. once the string has been normalized,
    we can search for matches on word boundaries only by surrounding our targets
    with spaces.  this allows us to find matches for "i like python." while
    avoiding matches such as 'c' with 'computer'
    """
    fixed = ""
    special_chars = '+#-'  # these are necessary for c++, objective-c, c#, etc
    for char in sentence:
        if (char in string.ascii_letters) or (char in special_chars) or char.isnumeric():
            fixed += char
        elif (char not in string.printable):
            fixed += "~"
        else:
            fixed += " "
    return " " + fixed.lower() + " "

if __name__ == "__main__":
    get_data()