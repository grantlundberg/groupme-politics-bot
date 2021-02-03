import random
from flask import Flask, request
import threading
import utils

app = Flask(__name__)
@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    # We don't want to reply to ourselves!
    if data['name'] != 'PoliticalBot' and data['name'] != 'Neffbot':
        
        text_lower = data['text'].lower().replace('-', '').replace('_', '')
        text_length = len(text_lower)

        # Log some details
        print("{sender_id},{name},{text},{attachments}".format(**data))

        # If the data has image attachments, grab them and run tesseract on them
        if len(data['attachments']) > 0:
            print("Found {} attachments. Spawning a thread to handle it".format(len(data['attachments'])))
            th = threading.Thread(target=utils.scan_images, args=(data['attachments'], data['name'], data['sender_id']))
            th.start()
        # If someone sends more than TEXT_LIMIT characters, call the Neffbot
        if text_lower.startswith('http://') == False and text_length > utils.TEXT_LIMIT:
            msg = "@{}, your message exceeded {} characters. ({}). {}".format(
                data['name'],
                utils.TEXT_LIMIT,
                text_length,
                utils.RESPONSES[random.randrange(0, len(utils.RESPONSES)-1)])
            utils.send_neff_message(msg)
            utils.increment_count('neffbot', utils.ID_TO_NAME[data['sender_id']])

        # If someone messaged the politicalbot, send the counts
        if text_lower.startswith('@politicalbot'):
            utils.send_political_message(utils.get_counts('politicalbot'))
        elif text_lower.startswith('@neffbot'):
            utils.send_neff_message(utils.get_counts('neffbot'))
        # If someone uses a political word, send them a message
        else:
            utils.check_for_political_words(text_lower, data['name'], data['sender_id'])

    return "ok", 200
