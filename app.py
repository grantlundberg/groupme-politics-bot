import os
import json
import sqlite3
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request

app = Flask(__name__)
@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    # We don't want to reply to ourselves!
    if data['name'] != 'PoliticalBot':
        
        text_lower = data['text'].lower()

        # If someone messaged the politialbot, send the counts
        if text_lower.startswith('@politicalbot'):
            send_message(get_counts())
    
    return "ok", 200


def send_message(msg):
    url  = 'https://api.groupme.com/v3/bots/post'

    data = {
            'bot_id' : os.getenv('GROUPME_BOT_ID'),
            'text'   : msg,
            }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()


def get_counts():
    counts_msg = ""
    with sqlite3.connect('politicalbot.db') as conn:
        cursor = conn.cursor()
        for row in cursor.execute("SELECT name,count FROM counts").fetchall():
            counts_msg += "{}: {}\n".format(row[0], row[1])
    return counts_msg

def increment_count(user:str):
    with sqlite3.connect('politicalbot.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE counts SET count=count+1 WHERE name=?", (user,))


ID_TO_NAME = {12064987: "Neff",
              11989321: "Brian",
              12064988: "Fuller",
              12064985: "Danny",
              12489342: "Grant"}
RESPONSES = [
        "Did Mexico pay us for that border wall yet?",
        "How's Trumps healthcare plan coming along?",
        "Fuck you and fuck Susan Collins",
        "If you're offended about an anti-racism speech, guess what. you're racist",
        "Stop it.",
        "Looks like you may be buying the first round of beers.",
        "Please rethink your life's choices you Ted Cruz-loving motherfucker"
        ]
POLITICAL_WORDS = None
with open('political_words.txt', 'r') as f:
    POLITICAL_WORDS = f.read().split('\n')


