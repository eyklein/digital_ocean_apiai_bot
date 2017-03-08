#!/usr/bin/env python

# from __future__ import print_function
# from future import standard_library
# standard_library.install_aliases()
import urllib.request, urllib.parse, urllib.error
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():

    req = request.get_json(silent=True, force=True)

    # print("Request:")
    # print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)




    # convert speach onbject (json fromat) to api.ai format
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    query = getQuery(req)
    # if req.get("result").get("action") != "yahooWeatherForecast":
    #     return {}
    # baseurl = "https://query.yahooapis.com/v1/public/yql?"
    # yql_query = makeYqlQuery(req)
    # if yql_query is None:
    #     return {}
    # yql_url = baseurl + urllib.parse.urlencode({'q': yql_query}) + "&format=json"
    # result = urllib.request.urlopen(yql_url).read()
    # data = json.loads(result)
    res = makeWebhookResult('<speak>Step 1, take a deep breath. <break time="2s" />Step 2, exhale.</speak>')
    return res


def getQuery(req):
    result = req.get("result")
    query = result.get("resolvedQuery")

    return query


def makeWebhookResult(data):

    speech = data

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    from OpenSSL import SSL
    context = SSL.Context(SSL.SSLv23_METHOD)
    # context.use_privatekey_file('my-key.pem')
    # context.use_certificate_file('my-cert.pem')

    # app.run(debug=False, port=port, host='0.0.0.0' , ssl_context=context)
    context = ('my-cert.pem', 'my-key.pem')
    app.run(host='0.0.0.0', port=5000, ssl_context=context, threaded=True, debug=True)
