import os
import sqlite3
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from PIL import Image
import pytesseract
import random
import requests


def send_message(bot_source:str, msg:str):
    url  = 'https://api.groupme.com/v3/bots/post'
    data = {'bot_id' : os.getenv(bot_source),
            'text'   : msg}
    request = Request(url, urlencode(data).encode())
    urlopen(request).read().decode()


def get_counts(database_name:str):
    counts_msg = ""
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        for row in cursor.execute("SELECT name,count FROM counts").fetchall():
            counts_msg += "{}: {}\n".format(row[0], row[1])
    return counts_msg


def increment_count(database_name:str, user:str):
    with sqlite3.connect(database_name) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE counts SET count=count+1 WHERE name=?", (user,))


def scan_images(attachments, name, sender_id):
    text = ''
    try:
        for attachment in attachments:
            if attachment['type'] == 'image':
                image = Image.open(requests.get(attachment['url'], stream=True).raw)
                text += pytesseract.image_to_string(image)
    except Exception as e:
        print("ERROR: caught exception in scan_images(): "+str(e))
    print("scan_images text: {}".format(text))
    check_for_political_words(text, name, sender_id)


def check_for_political_words(text:str, name:str, sender_id:str):
    for word in POLITICAL_WORDS:
        if word in text:
            response = RESPONSES[random.randrange(0, len(RESPONSES)-1)]
            msg = "@{}, your message is political. {}".format(name, response)
            send_message('POLITICAL_BOT_ID', msg)
            increment_count('politicalbot.db', ID_TO_NAME[sender_id])
            break


TEXT_LIMIT = 200
ID_TO_NAME = {'12064987': "Neff",
              '11989321': "Brian",
              '12064988': "Fuller",
              '12064985': "Danny",
              '12489342': "Grant",
              '38995562': "Kevin"}
RESPONSES = [
        "Did Mexico pay us for that border wall yet?",
        "How's Trumps healthcare plan coming along?",
        "Fuck you and fuck Susan Collins.",
        "If you're offended about an anti-racism speech, guess what. you're racist.",
        "Stop it.",
        "Looks like you may be buying the first round of beers.",
        "Please rethink your life's choices you Ted Cruz-loving motherfucker.",
        "Since you know it all, you should know when to shut the fuck up.",
        "Your ass must be jealous of all that shit you just typed."
        ]
POLITICAL_WORDS = [
    "antifa",
    "aoc",
    "ballot",
    "ballots",
    "bernie",
    "biden",
    "black lives matter",
    "blm",
    "capitol",
    "deficit",
    "democrat",
    "democrats",
    "desantis",
    "don ",
    "don jr",
    "drumpf",
    "election",
    "elections",
    "gop",
    "impeach",
    "ivanka",
    "lamestream",
    "lewinsky",
    "libs",
    "liberal",
    "libertarian",
    "libertarianism",
    "libertarians",
    "libtard",
    "maga",
    "nazi",
    "pizzagate",
    "pizza gate",
    "pizza-gate",
    "political",
    "politico",
    "politics",
    "proud boy",
    "proud boys",
    "qanon",
    "republican",
    "republicans",
    "senate",
    "trump",
]