import spacy
import pandas as pd
import numpy as np
import math
# import random
from collections import Counter, defaultdict
import sys
import re
import os

import dataManagment as dm

nlp = spacy.load('en')
import spacy.parts_of_speech as pos_t

VERB = 'VERB'
nsubj = 'nsubj'
dobj = 'dobj'
NN = 'NOUN'
NNS = 'NNS'
ADJ = 'ADJ'

sessions = set()

# this should be replaced with a entity recognition
directions = ["up", "down", "side", "left", "right", "in", "out", "forward", "backward", "north", "south", "east", "west"]   
def isDirection(text):
    if text in directions:
        return True
    else:
        return False


class Ideas(object):
    def __init__(self, doc_):
        self.ideas = []
        

        # start with verbs
        for word in doc_:
            if word.pos_ == VERB:
                self.ideas.append(Idea(word))
                
        for idea in self.ideas:
            idea.removeBlockWords()
            idea.sortTokensToArray()

    def __str__(self):
        my_string = ""
        for idea in self.ideas:
            my_string = "{0} *** {1}".format(my_string, str(idea))
            # idea should contain noun chunks i think
        
        return my_string

class Idea(object):
    def __init__(self, verb):
        self.words = set()
        self.wordsArray=[]
        self.verb = verb
        self.words.add(verb)
        self.addToken(verb)
        

    def addToken(self, token):
        for child in token.children:
            if child.pos != pos_t.VERB:
                self.addToken(child)
                self.words.add(child)
    def sortTokensToArray(self):
        self.wordsArray = sorted(self.words, key=lambda Token: Token.i)
    
#     run before sort
#     removed stop words that are not directions
    def removeBlockWords(self):
        nonBlockedWords=set()
        for token in self.words:
            if notStopWord(token):
                nonBlockedWords.add(token)
        self.words = nonBlockedWords
      

    def __str__(self):
        return str(self.wordsArray)

# doc = nlp(u"the rain goes up into the clouds and then comes back down")
# ideas = Ideas(doc)
# print(ideas)

def getIntents(text):
    doc=nlp(text)
    print("doc")
    print(doc)
    conseptsPresent=Ideas(doc)

    classifications = []



    
    info = {}
    info['response']=[]
    info["category"]=[]
    
    for idea in conseptsPresent.ideas:
        # print(idea)
        classifications.append(classify_baysian(idea.wordsArray, catagories, likelihood))
        

        info['response'].append(str(idea))
        info['category'].append(classify_baysian(idea.wordsArray, catagories, likelihood))


        
    
    # save learning data as JSON
    for i in range(len(info['response'])):
        entry = dm.LearingEntry(info['category'], info['response'][i], info['response'][i])
        updateLearingFile("Training_test/learning.json" , entry)





   
    
    return(classifications)



def read_training_file(fpath):
    catagories = Counter()
    likelihood =defaultdict(Counter)
    
    training_data = dm.loadData(fpath)
    
    for entry in training_data:

        doc =nlp(entry["phrase"])

        catagories[entry["classification"]] += 1
        
        for word in doc:
            if notStopWord(word):
                likelihood[entry["classification"]][word.lemma_] +=1
    
    
    return (catagories, likelihood)

def printDict(dict):
    print(len(dict))
    for key, value in dict.items():
        print(key, value)

def notStopWord(token):
    return not token.is_stop or isDirection(token.lemma_)


#     return the class that maxamizes postereor with min probobility
def classify_baysian(doc, priors, likelihood):
    # print("************************************************")
    # printDict(priors)
    
    if len(doc) < 1:
        return "garbage"
    
    min_prob = 1E-9  
    max_class = (-1E6, '')

    for catagory in priors:
        p=priors[catagory]
        n=float(sum(likelihood[catagory].values()))
        
        for token in doc:
            p = p * max(min_prob,likelihood[catagory][token.lemma_] )/ n
        if p > max_class[0]:
            max_class=(p, catagory)
    
    return max_class[1]


def updateLearingFile(fpath, entry):

    currentData = dm.loadData(fpath)
    currentData.append(entry.getJSON())
    dm.saveData(fpath, currentData)



def is_non_zero_file(fpath):  
    return True if os.path.isfile(fpath) and os.path.getsize(fpath) > 0 else False


def train_modle():
    training_file = "Training_test/training.json"

    global catagories
    global likelihood

    (catagories, likelihood) = read_training_file(training_file)
    load_responces("Training_test/nodes.json")




def load_responces(fpath):
    # csvFile = pd.read_csv(filename, low_memory=False, encoding='ISO-8859-1')
    global nodes
    nodes = set()
    loadedNodes = dm.loadData(fpath)
    
    for node in loadedNodes:
        nodes.add(node)



    for node in nodes:
        print(node.name)



class Session(object):
    def __init__(self, sessionId,baseNode):
        self.id=sessionId
        self.nodesActivated=[]
        self.sortedNodes= sorted(nodes, key=lambda Node: Node.numberOfCalls)
        
    
#     def nodeAvailible(self, inputContext):
#         return self.nodesActivated[-1].
    
    def forceNode(self, actionIntent, decition):
        if  "yesno" in actionIntent:
            print("decition ", decition)
            if "yes" in decition:
                print("got here yes!!!!!!!!!!!!!!!!!!!!!!!")
                if self.activateNode(getNode(self.nodesActivated[-1].yes_force)):
                    return self.getCurrentBOTResponce()    
                else:
                    print("error: could not add forced yes")
            if "no" in decition:
                if self.activateNode(getNode(self.nodesActivated[-1].no_force)):
                    return self.getCurrentBOTResponce()    
                else:
                    print("error: could not add forced no")

        else:
            if "restart" in decition:
                self.nodesActivated=[]

            if self.activateNode(getNode(actionIntent)):
                return self.getCurrentBOTResponce()    
            else:
                print("error: could not add foced node")



    def nextNode(self, intents):
        # self.nodesActivated
        # self.wordsArray = sorted(self.words, key=lambda Token: Token.i)

        for node in self.sortedNodes:                           #search ordered list of lest used responces
            if node.name in intents:                            #if the node is in the list of intents
                if self.activateNode(node):                     #try and add the node to current sesstion
                    return self.getCurrentBOTResponce()         # if added return responce
        


        # for intent in intents:
        #     if self.activateNode(getNode(str(intent))):
        #         return self.getCurrentBOTResponce()





        # not found
        return "defalt text responce"



    def activateNode(self, node):
        if self.isContextAvailable(node.input_context):

            self.nodesActivated.append(node)
            # self.sortedNodes = sorted(self.nodesActivated, key=lambda Token: Token.i
            self.sortedNodes = sorted(nodes, key=lambda Node: Node.numberOfCalls)

            for node in self.sortedNodes:
                print(node.name," ",node.numberOfCalls)
            return True
        else:
            return False
        
        
    def printHistory(self):
        histString=''
        for node in self.nodesActivated:
            histString = "{0} > {1}".format(histString, node.name)
        print(histString)

    def getCurrentBOTResponce(self):
        callResponceIndex = self.nodesActivated[-1].getCallNumberInctement()
        print(callResponceIndex)

        return self.nodesActivated[-1].responce[callResponceIndex]
    
    def isContextAvailable(self, input_contexts):
        if len(self.nodesActivated) == 0: #first welcome node
            return True


        # if "pass_through" in input_contexts:
        #     if len(self.nodesActivated)<2:
        #         print("not sure how we got here with less then 2 activate nodes")
        #     return self.nodesActivated[-2].isContextAvailableNode(input_contexts)
        # else:
        return self.nodesActivated[-1].isContextAvailableNode(input_contexts)

        
    def currentContext(self):
        return self.nodesActivated[-1].output_context

class Node(object):
    # def __init__(self, name, responce,input_context,output_context):
    def __init__(self, nodeLoadedInfo):
        # csvFile["category"][i], csvFile["reply"][i],
        #                csvFile["input_context"][i],csvFile["output_context"][i]
        self.name = nodeLoadedInfo["classification"]   
        
        self.numberOfCalls=0



        input_context = nodeLoadedInfo["input_context"]
        output_context = nodeLoadedInfo["input_context"]


        self.responses = []

        for responce in nodeLoadedInfo["response"]:
            self.responses.append(Responce(responce))

        



        # self.yes_force = nodeLoadedInfo["yes_force"]
        # self.no_force = nodeLoadedInfo["no_force"]


    # this should indicate if we have gone through them all which it does not right now ********      
    def getCallNumberInctement(self):
        currentCallIndex = self.numberOfCalls
        print(self.responce)
        self.numberOfCalls = (self.numberOfCalls + 1)%len(self.responce)
        return currentCallIndex
    
    # check  
    def isContextAvailableNode(self, input_contexts):
        for input_context in input_contexts:
            if input_context in self.output_context:
                return True
        return False
            
#         self.availibleNodes=2 

class Responce(object):
    def __init__(self, responceLoaded):
        self.text = responceLoaded["text"]
        self.input_context = responceLoaded["input_context"]
        self.output_context = responceLoaded["output_context"]

        self.decisions = set()

        for decision in responceLoaded["decision"]:
            self.decisions.add(Decision(decision))
            

class Decision(object):
    def __init__(self, loadedDecision):
        self.name = loadedDecision["name"]
        self.destination = loadedDecision["node"]


def getNode(category):
    for node in nodes:

        if node.name == category:
            return node

    print(category, " is unclasified")

    for node in nodes:
        if node.name == "unknown":
            return node

    # should never get here
    return False


def startSession(ID, node):
    session = Session(ID, node)
    sessions.add(session)
    return session

def getSession(ID):
    for session in sessions:
        if ID == session.id:
            return session
    # if not found
    return startSession(ID, getNode("base"))












