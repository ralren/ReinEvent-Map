'''
Created on Oct 28, 2014

@author: RenSol
@description: This class is used to store event data from the Smith College events calendar to be mapped later on.
'''
import feedparser
import random
import cartodb

''' START THIS CLASS!
@summary: Event is a class that each singular event would be stored in. Each event object will then have several parameters containing info about the event.
'''
class Event:
    '''
    @summary: Constructor for the Event class
    @params: self,
             name, event's name
             location, where the event will take place
             FMCode, building code associated with the location
             time, hour(s) the event will take place
             date, when the event will happen
    '''
    def __init__(self, name, location, FMCode, time, date):
        self.name = name
        self.location = location
        self.FMCode = FMCode
        self.time = time
        self.date = date
''' CLASS OVER '''   

'''
@summary: Insert the data into the CartoDB account
@params: 
'''
def insert_events():
    print "Inserting events..."
    print "Done inserting events."   



'''
@summary Parse through the buildings table to get the FMCode of the event
@params keywords, the location of the event
        client, the required URL to manipulate the sql
@return FMCode, the FMCode of a particular event
'''
def grabFMDictionary(client):
    '''
    #initalize variables
    keyword = keywords[0]
    '''
    buildFM = {}

    #go through the buildings table

    try:
        fields = client.sql('select * from buildings')
    except cartodb.CartoDBException as e:
        print ("some error occurred", e)
    
    num = len(fields['rows'])
    
    #go through each row within the buildings table
    for n in range(0,num):
        buildName = fields['rows'][n]['bldg_name']
        FMCode = fields['rows'][n]['fmcode']
        buildFM[buildName] = FMCode
    
    return buildFM

'''
@summary: Create a dictionary which will hold the events and their values
@params: 
'''
def parse_events(FMDictionary):
    #set up to parse through content in RSS feed
    calendar = feedparser.parse("http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Featured+Events&mixin=12162")
    events = {} #holds the events PROBABLY CHANGE INTO A LIST
    count = 0 #keeps track of how many events there are
    
    #parse through each event in the RSS feed
    for entry in calendar.entries:
        
        #fix any unicode errors or what can't translate well
        description = entry.description.split("<br />", 3) #split the description into three parts
        entry.title.decode("utf-8", "strict").encode("utf-8", "ignore") #in case there's a title in a foreign language

        
        #check if the event is within the events dictionary already
        without = True
        for event in events.itervalues():
            #does it have the title (entry.title), location (description[0]), and time/date as the same thing?
            if (event[0] == entry.title) and (event[1] == description[0]) and (event[2] == description[1].split("&",2)[0]):
                without = False
                
        if without: #if event isn't already within the dictionary, put it in the dictionary
            
            #create an Event object
            e = Event()
            
            #remove quotation marks in title because it creates conflict
            if ("\'" in entry.title) or ("\"" in entry.title):
                title = ""
                for letter in entry.title:
                    if (letter != "'") and (letter != "\""):
                        title += letter
            
                name = title
            else:
                name = title
                
            #format location
            location = description[0] 
            
            #format fmcode
            buildingName = ""
            possibleBuildings = []
            keywords = location.split() # split the location name so we can isolate the building name
                    
            for building in FMDictionary.keys():
                if keywords[0] in building:
                    possibleBuildings.append(building)
            
            if possibleBuildings.length() < 1:
                for possibility in possibleBuildings:
                    if keywords[1] in possibility:
                        buildingName = possibility
                        
            #some of the buildings are within another building so just assign them the same cartodb ID
            elif keywords[0] == "Sweeney" or (keywords[0] == "Earle"):
                buildingName = "Sage Hall"
            elif (keywords[0] == "Lewis") or (keywords[0] == "Weinstein"):
                buildingName = "Wright Hall"
            elif (keywords[0] == "Hallie") or (keywords[0] == "Theatre") or (keywords[0] == "Formerly"):
                buildingName = "Mendenhall Center for Performing Arts"
            elif (keywords[0] == "BFAC"):
                buildingName = "Fine Arts Center"
            #only one code so get it
            else:
                buildingName = possibleBuildings[0]
                
            fmcode = FMDictionary[buildingName] #look up fmcode using the building name and FMCodedictionary
                        
            #format date
            date = description[1].split(",") #split string whenever it encounters a comma
            date_time = ",".join(date[:2]), ",".join(date[2:]) #only split until the second comma
            date = date_time[0]
            
            #format time
            time = date_time[1].split    
            times = time[1].split("&nbsp;&ndash;&nbsp;") #get rid of the character " - " and split the string there
            time = times[0] + " - " + times[1] #concatenate strings with the time    

    return events    
            
'''
@summary: Initializes user data and create the CartoDB client to manipulate tables within.
'''
def main():

    #user information
    user = "smithgis@smith.edu"
    api_key = "59651a7eb7bfa39b60a7160859432749e92b8fda"
    cartodb_domain = "smithgis"
        
    #initialize CartoDB client to deal with SQL commands
    cl = cartodb.CartoDBAPIKey(api_key, cartodb_domain)
    FMDictionary = grabFMDictionary(cl)
    parse_events(FMDictionary)

#calls the main function upon importing module
if __name__ == '__main__':
    main()
