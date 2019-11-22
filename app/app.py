from flask import Flask, render_template, request, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError, TokenExpiredError, OAuth2Error
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

app = Flask(__name__)

import requests

url = "https://api.yelp.com/v3/businesses/search"

app.secret_key = "supersekrit"
blueprint = make_google_blueprint(
    client_id="979961139202-n4lsu6bqsgbremebfk1trlkddji2a9i9.apps.googleusercontent.com",
    client_secret="506Ch-L-9XfPUxvGSMTZEjX5",
    scope=["profile", "email"],
  #  offline=True,
    redirect_url="/app_login"

)

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


'''
for i in response.json():
    for j in (response.json()[i]):
        print(j["name"] + ': ' + j["price"] + ', ' + str(j["rating"]) + ', ' + j["phone"] + ', ' + j["location"]["address1"])        
    break
'''

app.register_blueprint(blueprint, url_prefix="/login")

@app.route("/app_login")
def index():
    if not google.authorized:
        return redirect(url_for("google.login"))



    try:
        resp = google.get("/plus/v1/people/me")
        #assert resp.ok, resp.text
    except (InvalidGrantError, TokenExpiredError) as e:  # or maybe any OAuth2Error
        return redirect(url_for("google.login"))
    return redirect(url_for('student'))


@app.route("/app_logout")
def logout():
    if google.authorized:
        session.clear()
    return redirect("/")


@app.route('/')
def student():
    if not google.authorized:
        return redirect(url_for("google.login"))
    return render_template('search.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form
        querystring = {"location":"boston"}
        querystring['term'] = result['search']
        response = requests.request("GET", url, headers=headers, params=querystring)
        s = (f'Name: {j["name"]}, Rating: {j["rating"]}, Phone: {j["phone"]}, Location: {j["location"]["address1"]}' for j in response.json()['businesses'])
        return render_template("result.html",result = s)

