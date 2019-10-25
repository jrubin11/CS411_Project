from flask import Flask, render_template, request
app = Flask(__name__)

import requests

url = "https://api.yelp.com/v3/businesses/search"


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
@app.route('/')
def student():
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

if __name__ == '__main__':
    app.run(debug=True)
