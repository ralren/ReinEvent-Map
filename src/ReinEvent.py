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
def grabFMCode(client):
    '''
    #initalize variables
    keyword = keywords[0]
    cbIDs = {} #potential CartoDB IDs
    cbID = 0 #the actual CartoDB ID
    FMCode = 0
    '''
    #go through the buildings table

    try:
        fields = client.sql('select * from buildings')
        print fields['rows']
    except cartodb.CartoDBException as e:
            print ("some error occurred", e)
    '''
    num = len(fields['rows'])
    
    
    #go through each row within the buildings table
    for n in range(0,num):
        name = fields['rows'][n]['bldg_name']
    
        if keyword in name:
            cbIDs[name] = fields['rows'][n]['cartodb_id']
      
  
    #narrow down what the cbID is
    if len(cbIDs) > 1:
        keyword = keywords[1]
        for bldg, cb in cbIDs.iteritems():
            if keyword in bldg:
                cbID = cb
    #some of the buildings are within another building so just assign them the same cartodb ID
    elif keywords[0] == "Sweeney" or (keywords[0] == "Earle"):
        cbID = 86
    elif (keywords[0] == "Lewis") or (keywords[0] == "Weinstein"):
        cbID = 97
    elif (keywords[0] == "Hallie") or (keywords[0] == "Theatre") or (keywords[0] == "Formerly"):
        cbID = 18
    elif (keywords[0] == "BFAC"):
        cbID = 5
    #only one code so get it
    else:
        for cb in cbIDs.itervalues():
            cbID = cb
    
    
    sqlcomm = 'SELECT {0}, ST_X(ST_Centroid(the_geom)), ST_Y(ST_Centroid(the_geom)) FROM buildings'.format(cbID)
    pt = client.sql(sqlcomm)
    point.append(pt['rows'][cbID]['st_x'] + random.uniform(0, .0003))
    point.append(pt['rows'][cbID]['st_y'] + random.uniform(0, .0003))
    return point
    '''

'''
@summary: Create a dictionary which will hold the events and their values
@params: 
'''
def parse_events():
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
            
                e.name = title
            else:
                e.name = entry.title
                
            #add other information
            location = description[0] 
            e.location = location
            
            #format date
            date = description[1].split(",") #split string whenever it encounters a comma
            date_time = ",".join(date[:2]), ",".join(date[2:]) #only split until the second comma
            e.date = date_time[0]
            
            #format time
            time = date_time[1].split    
            times = time[1].split("&nbsp;&ndash;&nbsp;") #get rid of the character " - " and split the string there
            e.time = times[0] + " - " + times[1] #concatenate strings with the time    
    
            #add FMCode :D
            #e.FMCode = grabFMCode(location.split, cl)
        
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
    grabFMCode(cl)


#calls the main function upon importing module
if __name__ == '__main__':
    main()
