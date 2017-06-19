# author : Ziji Shi
# email : shi.ziji.sm@gmail.com

import datetime
import json
import os
from urlparse import urlparse

import httplib2 as http

import time
from time import gmtime, strftime


def getCurrentTime():
    timeUTC = datetime.datetime.now()
    # time is to be displayed as file name, entry time is to be stored in database
    return {'date' : timeUTC.date(), 'time' : timeUTC.strftime("%H.%M.%S"), 'entryTime' : timeUTC.strftime("%H:%M:%S")}

def createFilePath(date, time):
    # Get output path ready, organized in folder named after their dates
    outPathRoot = '~\path\to\your\output\directory'

    # The folder path is like speedband\2017-06-06
    outPathDate = '\\' + str(date)

    # Check if this is a new day. If so, create a new folder
    outPathMain = outPathRoot + outPathDate
    dir = os.path.expanduser(outPathMain)
    if not os.path.exists(dir):
        os.mkdir(dir)
        print "Date : " + str(date)

    # The json file path is like speedband\2017-06-06\2017-06-06 16:00:00.json
    outFileName = '\\' + str(date) + ' ' + time
    outFullPath = os.path.expanduser(outPathMain + outFileName)
    return outFullPath

def byteify(input):
    # Output the json object in ASCII code
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('ascii')
    else:
        return input

def getJSONData(groupIndex):
    #Authent parameters
    headers = {"AccountKey" : "YOUR ACCOUNT KEY",
               "Accept" : "application/json"}

    #URL parameters
    urlbase = 'http://datamall2.mytransport.sg/'
    path = 'ltaodataservice/Taxi-Availability?'

    #Range of records
    inc = "$skip="+str(groupIndex*500)

    #Build string to query
    target = urlparse(urlbase+path+inc)
    method = 'GET'
    body = ''

    #Get handle to http
    h = http.Http()

    #Obtain result
    response, content = h.request(
        target.geturl(),
        method,
        body,
        headers
    )

    jsonObj = json.loads(content)
    return byteify(jsonObj)

def csvOutput(outputPath,result):
    #Output in .csv file
    outputPath+='.csv'
    with open(outputPath, 'w+') as outfile:
        outfile.write('Longitude, Latitude \n')
        for record in result:
            print >> outfile, str(record['Longitude']) + ', '+ str(record['Latitude']) 

# MAIN LOGIC HERE

# Time interval for retriving data in SECONDS
interval = 5*60.0

while True: 
    starttime = time.time()
    currTime = getCurrentTime()
    outputPath = createFilePath(currTime['date'], currTime['time'])

    result = []
    print "Now processing : " + str(currTime)
    for index in range(0,60,1):
        response = getJSONData(index)['value']
        result+=response
    print "  ->  Now Saving Data!"

    #Write to output file
    csvOutput(outputPath,result)
    endTime = getCurrentTime()

    print "   started : "+ currTime['time'] +"; ended : " + endTime['time']
    print "   Time elapsed in s: " + str(time.time()-starttime)+"\n"

    time.sleep(interval - (time.time()-starttime)% interval)