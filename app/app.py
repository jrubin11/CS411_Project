from flask import Flask, render_template, request, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError, TokenExpiredError, OAuth2Error
import os
from flask_sqlalchemy import SQLAlchemy
import eventful
api = eventful.API('test_key', cache='.cache')

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

app = Flask(__name__)

import requests

url = "https://api.yelp.com/v3/businesses/search"

# Key and Blueprint for Google OAuth
app.secret_key = "supersekrit"
blueprint = make_google_blueprint(
    client_id="979961139202-n4lsu6bqsgbremebfk1trlkddji2a9i9.apps.googleusercontent.com",
    client_secret="506Ch-L-9XfPUxvGSMTZEjX5",
    scope=["profile", "email"],
  #  offline=True,
    redirect_url="/app_login"

)

# Header for Yelp API
headers = {
    'Authorization': "Bearer PPUb3qtJOlbheSDF063leUrTjuS94ewmKDXGSI9Fr83x20SiBrLNP35nJtE61TcUpxEfLK9oJ5qsFwojDxGU-37B7a_LKPC0GsnXgryjk59PkC3NGrQ2SrjsjfqpXXYx",
    'User-Agent': "PostmanRuntime/7.18.0",
    'Accept': "/",
    'Cache-Control': "no-cache",
    'Postman-Token': "fe6219da-e389-4bb3-9643-93311717bcf2,55740bd4-51e1-40a6-bbeb-1a019c7e5427",
    'Host': "api.yelp.com",
    'Accept-Encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# Object to add to User Table
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False)

# Object to Add to event table
class Event(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = location = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)
    day = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)

# Register blueprint
app.register_blueprint(blueprint, url_prefix="/login")

# Login in page that registers new users
@app.route("/app_login")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))

    try:
        resp = google.get("/oauth2/v1/userinfo")
        email = resp.json()['email']
        #assert resp.ok, resp.text
    except (InvalidGrantError, TokenExpiredError) as e:  # or maybe any OAuth2Error
        return redirect(url_for("google.login"))
    user = User.query.filter_by(email=email).first()

    try:
        if user==None:
            new_user = User(email=email)
            db.session.add(new_user)
            db.session.commit()
    except:
        return f'There was an issue adding your user'
    return redirect(url_for('student'))

# Logout page
@app.route("/app_logout")
def logout():
    if google.authorized:
        session.clear()
    return redirect("/")


# Homepage
@app.route('/')
def student():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return render_template('homepage.html')
    

# Page that displays your food options
@app.route('/food')
def food():
    days={'sunday':0,'monday':1,'tuesday':2,'wednesday':3,'thursday':4,'friday':5,'saturday':6}
    days2=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    if not google.authorized:
        return redirect(url_for("google.login"))
    try:
        resp = google.get("/oauth2/v1/userinfo")
        email = resp.json()['email']
    #assert resp.ok, resp.text
    except (InvalidGrantError, TokenExpiredError) as e:  # or maybe any OAuth2Error
        return redirect(url_for("google.login"))
    lists=[[] for i in range(7)]
    
    # Get users events
    events = Event.query.filter_by(email=email).all()
    for i in events:
        lists[days[i.day]]+=[[i.start_time,i.name,i.location]]
    for i in range(7):
        lists[i].sort()
    foods={}
    locations=[[] for i in range(7)]
    for i in range(7):
        locations[i]=lists[i][1:]
        foods[days2[i]]=[]
    s= ''
    
    # Match food places with events throughout the day
    for i in range(len(lists)):
        if len(lists[i])>1:
            for j in range(1,len(lists[i])):
                querystring = {"location":lists[i][j][2].replace(' ','+'),"term":"food", "radius": 100,"limit":3}
                
                response = requests.request("GET", url, headers=headers, params=querystring)
                locations[i][j-1]+=[[k["name"] for k in response.json()['businesses']]]
                
    # format for html
    for i in range(len(locations)):
        for j in range(len(locations[i])):
            foods[days2[i]]+=[{'location':locations[i][j][2],'places':locations[i][j][3]}]
    return render_template('food.html',days=foods)


# Events page
@app.route('/result',methods = ['POST', 'GET'])
def result():
    if not google.authorized:
        return redirect(url_for("google.login"))
    searched_events=[]
    days={'sunday':1,'monday':2,'tuesday':3,'wednesday':4,'thursday':5,'friday':6,'saturday':7}
    try:
        resp = google.get("/oauth2/v1/userinfo")
        email = resp.json()['email']
    #assert resp.ok, resp.text
    except (InvalidGrantError, TokenExpiredError) as e:  # or maybe any OAuth2Error
        return redirect(url_for("google.login"))
    if request.method == 'POST':
        
        # Add event
        result = request.form
        if 'event_location' in result:
            events = api.call('/events/search',l=result['event_location'])
            for event in events['events']['event']:
                searched_events+=["%s at %s starting at %s on %s" % (event['title'], event['venue_name'],event['start_time'].split(' ')[1][:5],event['start_time'].split(' ')[0][:10])]
        else:
            event = Event(name=result['name'],location=result['location'],start_time=result['start_time'],end_time=result['end_time'],day=result['day'],email=email)
            db.session.add(event)
            db.session.commit()
            
    # Display schedule
    table=[[str(i)+' hr','','','','','','',''] for i in range(24)]
    events = Event.query.filter_by(email=email).all()
    for i in events:
        table[i.start_time][days[i.day]]=i.name
    
        
    return render_template("result.html",result = table, searched_events=searched_events)

if __name__ == '__main__':
    app.run(debug=False)

"""for i in range(7):
    for j in range(24):
        

<<<<<<< HEAD
querystring = {"location":str(, "radius": 100}
=======
querystring = querystring = {"location":"%20775%20commonwealth%20Ave,%20boston,%20MA%20%2002215","open_at":"1575821730","radius":"400"}
>>>>>>> f729621cb3c31e21b10601fb058396375d9e593b
querystring['term'] = result['search']
querystring['radius'] = 100
response = requests.request("GET", url, headers=headers, params=querystring)
s = (f'Name: {j["name"]}, Rating: {j["rating"]}, Phone: {j["phone"]}, Location: {j["location"]["address1"]}' for j in response.json()['businesses'])"""
