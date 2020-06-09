import datetime
import json

import requests
from flask import render_template, redirect, request

from app import app


# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []
#projects = ["Uno", "Dos", "Tres"]

class Project:

    def __init__(self, name, author):
        self.name = name
        self.author = author

    def getRates(self):
        pass
        #get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
        #response = requests.get(get_chain_address)
        #if response.status_code == 200:
        #    content = []
        #    chain = json.loads(response.content)
        #    for block in chain["chain"]:
        #        for tx in block["transactions"]:
        #            tx["index"] = block["index"]
        #            tx["hash"] = block["previous_hash"]
        #            content.append(tx)

        #    global posts
        #    posts = sorted(content, key=lambda k: k['timestamp'],
        #                reverse=True)

projects = [
    Project("Uno", "Erik"),
    Project("Dos", "Brenda"),
    Project("Tres", "Bryan")
]

def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/')
def index():
    fetch_posts()

    for project in projects:
        project.getRates()

    return render_template('index.html',
                           title='Califica los proyectos :D',
                           posts=posts,
                           projects=projects,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    failures_rate = request.form["failures"]
    response_time_rate = request.form["response_time"]
    view_rate = request.form["view"]



    post_object = {
        'failures_rate': failures_rate,
        'response_time_rate': response_time_rate,
        'view_rate': view_rate,
    }


    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
