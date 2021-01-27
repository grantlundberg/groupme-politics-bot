import os
import json
import random
import sqlite3
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request

app = Flask(__name__)
@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    # We don't want to reply to ourselves!
    if data['name'] != 'PoliticalBot' and data['name'] != 'Neffbot':
        
        text_lower = data['text'].lower().replace('-', '').replace('_', '')
        text_length = len(text_lower)

        # If someone sends more than TEXT_LIMIT characters, call the Neffbot
        if text_lower.startswith('http://') == False and text_length > TEXT_LIMIT:
            msg = "@{}, your message exceeded {} characters. ({}). {}".format(
                data['name'],
                TEXT_LIMIT,
                text_length,
                RESPONSES[random.randrange(0, len(RESPONSES)-1)])
            send_message('NEFF_BOT_ID', msg)
            increment_count('neffbot.db', ID_TO_NAME[data['sender_id']])

        # If someone messaged the politicalbot, send the counts
        if text_lower.startswith('@politicalbot'):
            send_message('POLITICAL_BOT_ID', get_counts('politicalbot.db'))
        elif text_lower.startswith('@neffbot'):
            send_message('NEFF_BOT_ID', get_counts('neffbot.db'))
        # If someone uses a political word, send them a message
        else:
            for word in POLITICAL_WORDS:
                if word in text_lower:
                    response = RESPONSES[random.randrange(0, len(RESPONSES)-1)]
                    msg = "@{}, your message is political. {}".format(data['name'], response)
                    send_message('POLITICAL_BOT_ID', msg)
                    increment_count('politicalbot.db', ID_TO_NAME[data['sender_id']])
                    break
    return "ok", 200


def send_message(bot_source:str, msg:str):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
            'bot_id' : os.getenv(bot_source),
            'text'   : msg,
            }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()


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
POLITICAL_WORDS = None
with open('political_words.txt', 'r') as f:
    POLITICAL_WORDS = f.read().split('\n')[0:-1]
