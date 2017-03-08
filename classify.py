import spacy
import pandas as pd
import numpy as np
import math
# import random
from collections import Counter, defaultdict
import sys
import re
import os

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


        
    
    # print(conseptsPresent)

    for i in range(len(info['response'])):
        print("{0} : {1}".format(info['response'][i], info['category'][i]))

    updateLearingFile("Training_test/learning.csv" , info)
    return(classifications)



def read_training_file(filename):
    catagories = Counter()
    likelihood =defaultdict(Counter)
    
    
    csvFile = pd.read_csv(filename, low_memory=False, encoding='ISO-8859-1')
    
    for i in range(len(csvFile["response"])):
        doc =nlp(csvFile["response"][i])
        
        catagories[csvFile["category"][i]] += 1
        
        for word in doc:
            if notStopWord(word):
                likelihood[csvFile["category"][i]][word.lemma_] +=1
    
    
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

# def classify_baysian(line, priors, likelihood):
#     min_prob = 1E-9
#     doc = nlp(line)
    
#     max_class = (-1E6, '')
#     for catagory in priors:
        
#         p=priors[catagory]
#         n=float(sum(likelihood[catagory].values()))
#         for token in doc:
#             p = p * max(min_prob,likelihood[catagory][token.text] )/ n
#         if p > max_class[0]:
#             max_class=(p, catagory)
    
#     return max_class[1]

def read_testing_file(filename):
    csvFile = pd.read_csv(filename, low_memory=False, encoding='ISO-8859-1')
    textClassification=[]
    for i in range(len(csvFile["response"])):
        textClassification.append([csvFile["response"][i], csvFile["category"][i]])
    return textClassification 


def updateLearingFile(filename, addedClassification):
    # I don't understand why this works but it does
    # Create a Pandas dataframe from some data.
    
    
    if not is_non_zero_file(filename):
        # if file does not exsist or is empty
        print("The file does not exsist or has no headers create new learing file")
        csvFile = pd.DataFrame({'response' : [],
                'category' : []})
        
    else: 
        #load exsisting data
        csvFile = pd.read_csv(filename, low_memory=False, encoding='ISO-8859-1')
 

    if not 'response' in csvFile:
        print("there was no responce columb")
        csvFile['response']="NONE"
    if not 'category' in csvFile:
        print("there was no category columb")
        csvFile['category']="NONE"
    
    responses=csvFile["response"]
    category=csvFile["category"]

    
    if not responses.empty:
        #if list is not empty add after max else go to fist index
        startingIndex = max(responses.index) + 1
        
    else:
        #if list is empty
        startingIndex = 1
    
    
    for i in range(len(addedClassification['response'])):

        responses.set_value(startingIndex+i,  addedClassification['response'][i])
        category.set_value(startingIndex+i,  addedClassification['category'][i])
        
        
    textClassification={'response' : csvFile["response"],
          "category" : csvFile["category"]}



    # print(textClassification)
    df = pd.DataFrame(data=textClassification)

    # Convert the dataframe to an XlsxWriter Excel object.
    # df.to_excel(writer, sheet_name='Sheet1')
    df.to_csv(filename, sep=',', encoding='utf-8')


def is_non_zero_file(fpath):  
    return True if os.path.isfile(fpath) and os.path.getsize(fpath) > 0 else False


def train_modle():
    
    csvFile = pd.read_csv("Training_test/training.csv", low_memory=False, encoding='ISO-8859-1')
    
    
    training_file = "Training_test/training.csv"
    #learning file loaded each request
    # learning_file = "Training_test/learning.csv"

    # testing_file = "Training_test/testing.csv"
    global catagories
    global likelihood

    (catagories, likelihood) = read_training_file(training_file)
    load_responces("Training_test/responces.csv")

    

    # lines = read_testing_file(testing_file)
    
    # num_correct=0
    
    # for line in lines:
    #     category_assigned = classify_baysian(line[0], catagories, likelihood)
        
    #     print(line[0], "  real: ", line[1], "  assigned: ", category_assigned)
        
    #     if category_assigned==line[1]:
    #         num_correct += 1
            
    # print("Classified %d correct out of %d for an accuracy of %f"%(num_correct, len(lines),float(num_correct)/len(lines)))



def load_responces(filename):
    csvFile = pd.read_csv(filename, low_memory=False, encoding='ISO-8859-1')
    global nodes
    nodes = set()
    for i in range(len(csvFile["category"])):
        nodes.add(Node(csvFile,i))



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
    def __init__(self, csvFile, index):
        # csvFile["category"][i], csvFile["reply"][i],
        #                csvFile["input_context"][i],csvFile["output_context"][i]
        self.name = csvFile["category"][index].strip()
        self.responce = []
        self.numberOfCalls=0

        #[1,2,3,4]
        #load responces 1-4 into array 
        for i in range(1,5):
            responceX = csvFile["reply_{0}".format(i)][index]

            if type(responceX) == str:
                self.responce.append(responceX.strip())



        input_context = csvFile["input_context"][index]
        self.input_context=set()
        if(type(input_context)==float):
            input_context="none"
        for context in input_context.split(','):
            self.input_context.add(context.strip())
            
        output_context = csvFile["output_context"][index]    
        self.output_context=set()
        if(type(output_context)==float):
            output_context="none"
        for context in output_context.split(','):
            self.output_context.add(context.strip())  


        self.yes_force = csvFile["yes_force"][index]
        self.no_force = csvFile["no_force"][index]


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












