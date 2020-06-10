import datetime
import json

import requests

from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from app import app

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

#    def __repr__(self):
#        return f'<User: {self.username}>'

class Project:

    def __init__(self, name, author):
        self.name = name
        self.author = author

        self.view_rates = []
        self.response_time_rates = []
        self.failures_rates = []

    def updateRates(self):

        get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
        response = requests.get(get_chain_address)
        
        if response.status_code == 200:
            chain = json.loads(response.content)
            for block in chain["chain"]:

                for tx in block["transactions"]:
                    
                    if( tx['project_name'] == self.name ):
                        self.view_rates.append( int(tx['view_rate']) )
                        self.response_time_rates.append( int(tx['response_time_rate']) )
                        self.failures_rates.append( int(tx['failures_rate']) )
                        print( tx['project_name'], self.view_rates )

    @property
    def view_rate_average(self):
        if( len( self.view_rates ) == 0 ):
            return 0
        return str( sum( self.view_rates ) / len( self.view_rates ) )

    @property
    def response_time_rate_average(self):
        if( len( self.response_time_rates ) == 0 ):
            return 0
        return str( sum( self.response_time_rates ) / len( self.response_time_rates ) )

    @property
    def failures_rate_average(self):
        if( len( self.failures_rates ) == 0 ):
            return 0
        return str( sum( self.failures_rates ) / len( self.failures_rates ) )

    @property
    def viability_grade(self):
        return ( float(self.response_time_rate_average) + float(self.failures_rate_average) + float(self.view_rate_average) ) / 3 * 10

    @property
    def its_viable(self):
        return self.viability_grade >= 90

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []
#projects = ["Uno", "Dos", "Tres"]

projects = [
    Project("Uno", "Erik"),
    Project("Dos", "Brenda"),
    Project("Tres", "Bryan")
]

users = []
users.append(User(id=1, username='Cris', password='password'))
users.append(User(id=2, username='Brenda', password='123'))
users.append(User(id=3, username='Aldeco', password='cripto'))

app.secret_key = 'secretkey' #llave necesaria para cualquir uso de sesiones en flask

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user
@app.route('/')
def index():

    if( g.user == None ):
        return redirect('/')

    for project in projects:
        project.updateRates()

    return render_template('index.html',
                           title='Califica los proyectos :D',
                           projects=projects,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        
        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('index'))

        return redirect(url_for('login'))

    return render_template('login.html')

#@app.route('/profile')
#def profile():
#    if not g.user:
#        return redirect(url_for('login'))
  #  return render_template('profile.html')

@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    failures_rate = request.form["failures"]
    response_time_rate = request.form["response_time"]
    view_rate = request.form["view"]
    project_name = request.form["project_name"]
    user = request.form["user"]



    post_object = {
        'failures_rate': failures_rate,
        'response_time_rate': response_time_rate,
        'view_rate': view_rate,
        'project_name': project_name,
        'user': user
    }


    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})


    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
