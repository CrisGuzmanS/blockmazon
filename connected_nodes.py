from hashlib import sha256
from random import randint 
import json
import time

from flask import Flask, request
import requests


class Node:

    def __init__(self, address):
        self.address = address

app = Flask(__name__)

nodes = []
nodes.append( Node('http://127.0.0.1:8001') )
nodes.append( Node('http://127.0.0.1:8002') )

@app.route('/add_new_node', methods=['POST'])
def add_node():
    node_address = request.get_json()["node_address"]
    nodes.append( Node( node_address ) )
    return request.address


@app.route('/random_node', methods=['GET'])
def random_node():
    
    number_of_nodes = len( nodes )

    node = nodes[ randint(0, number_of_nodes - 1 ) ]

    return json.dumps({ 
        "address": node.address
        })

