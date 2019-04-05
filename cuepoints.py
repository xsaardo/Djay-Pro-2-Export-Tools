# takes 2 params: location of djay pro db file, destination of output json

import biplist
import sqlite3
import json
import sys

def recurse(objectArray, currDict, resultsDict):
	for obj,val in currDict.items():
		if (obj != '$class' and obj != '$classname' and obj != 'userChangedCloudKeys'):
			if isinstance(val, biplist.Uid):
				resultsDict[obj] = getProps(objectArray, val)
				#print("uid " + str(resultsDict[obj]))
			elif isinstance(val, list):
				resultsDict[obj] = [getProps(objectArray,x) for x in val if isinstance(x,biplist.Uid)]
				#print("list " + str(resultsDict[obj]))
			else:
				resultsDict[obj] = val
				#print("scalar " + str(val))
	return resultsDict

def getProps(objectArray, uid):
	if isinstance(objectArray[uid.integer], dict):
		resultsDict = {}
		return recurse(objectArray, objectArray[uid.integer], resultsDict)
	else:
		return objectArray[uid.integer]

#conn = sqlite3.connect('/Users/cuong/Music/djay Pro 2/djay Media Library.djayMediaLibrary/MediaLibrary.db')
conn = sqlite3.connect(sys.argv[1])
conn.text_factory = str
c = conn.cursor()
c.execute("select d.key, d.data from database2 d where d.collection='mediaItemTitleIDs'")
response = c.fetchall()
print(len(response))

result = {}

for x in response:
	key = x[0]
	data = x[1]
	titleData = biplist.readPlistFromString(str(data))
	objects = titleData['$objects']
	objectIndices = objects[1]
	resultsDict = {}
	recurse(objects, objectIndices, resultsDict)
	result[key] = {}
	result[key].update(resultsDict)

c.execute("select d.key, d.data from database2 d where d.collection='mediaItemUserData'")
userDataResponse = c.fetchall()
#print(len(userDataResponse))

for x in userDataResponse:
	key = x[0]
	data = x[1]
	userData = biplist.readPlistFromString(str(data))
	objects = userData['$objects']
	objectIndices = objects[1]
	resultsDict = {}
	recurse(objects, objectIndices, resultsDict)
	result[key].update(resultsDict)
	'''
	for param, ind in {y1: y2 for (y1,y2) in objectIndices.items() if y1 != '$class' and y1 != 'userChangedCloudKeys'}.items():
		if isinstance(ind, biplist.Uid):
			if (objects[ind.integer] != '$null'):
				if objects[ind.integer].isDict:

				else:
					result[key][param] = objects[ind.integer]
		else:
			result[key][param] = ind
	'''


conn.close()
#print(result)
#print(json.dumps(result, indent=2))
with open(sys.argv[2], 'w') as outfile:
	json.dump(result, outfile, indent=2)









