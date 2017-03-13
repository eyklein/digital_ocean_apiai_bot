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
from flask_cors import CORS, cross_origin
# cors allows cross origin requests


# Flask app should start in global layout
app = Flask(__name__)
CORS(app)
# cors allows cross origin requests


import classify

classify.train_modle()



@app.route("/getIdeas" , methods=['POST'])
@cross_origin(supports_credentials=True)
def getIdeas():
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))
    res = processRequest(req)
    print("1")
    res = json.dumps(res, indent=4)
    print("2")
    # convert speach onbject (json fromat) to api.ai format
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    print("3")
    return r

@app.route('/webhook', methods=['POST'])
def webhook():

    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))



    res = processRequest(req)

    res = json.dumps(res, indent=4)
   
    # convert speach onbject (json fromat) to api.ai format
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    [action, decition, query, sessionId] = getQuery(req)

    session = classify.getSession(sessionId)
    if(action==""):
        intents = classify.getIntents(query)
        responce = session.nextNode(intents)
    else:

        responce = session.forceNode(action, decition)

    

    # print("intents")
    # print(str(intents))

    # text = ''
    
    # for intent in intents:
    #     text = "{0}, {1}".format(text, str(intent))



    res = makeWebhookResult(responce)
    print(res)
    return res


def getQuery(req):
    
    sessionId = req.get("sessionId")
    result = req.get("result")
    action = result.get("action")
    desition =[]
    for key in result.get("parameters"):
        desition.append(result.get("parameters").get(key))
    query = result.get("resolvedQuery")
    

    return [action, desition, query, sessionId]


def makeWebhookResult(data):

    speech = data

    print("Response:")
    print(speech)

    return {
        "speech": speech,# how do i add noResponse Items
        "displayText": speech,

        # "messages":[
        #     {
        #       "type": 0,
        #       "speech": "say what?"
        #     }
        #   ],

        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    # port = int(os.getenv('PORT', 5000))

    # print("Starting app on port %d" % port)

    from OpenSSL import SSL
    context = SSL.Context(SSL.SSLv23_METHOD)
    context = ('my-cert.pem', 'my-key.pem')
    app.run(host='0.0.0.0', port=5000, ssl_context=context, threaded=True, debug=True)
