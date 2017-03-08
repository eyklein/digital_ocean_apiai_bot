import json
from pprint import pprint
import os


# data = loadData('data.json')
# data.append(entry.getJSON())
# saveData('data.json', data)

def is_non_zero_file(fpath):  
    return True if os.path.isfile(fpath) and os.path.getsize(fpath) > 0 else False

def loadData(fpath):
    if(is_non_zero_file(fpath)):
        with open(fpath, 'r') as f:
            dataLoaded = json.load(f)
        return dataLoaded
    else:
        return []

def saveData(fpath, data):
    with open(fpath, 'w') as outfile:
        json.dump(data, outfile)


class LearingEntry(object):
    def __init__(self, classification, phrase,key_words):
        self.classification = classification
        self.phrase = phrase
        self.key_words = key_words
#         self.classification_rankings = classification_rankings
        
    def getJSON(self):
        return {
            "phrase": self.phrase,
#             "classification_ranking": self.classification_rankings,
            "key_words": self.key_words,
            "classification": self.classification
        }

        
# entry = LearingEntry("rain", "it went up as rain",["went", "rain"])