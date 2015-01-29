'''
Created on Oct 28, 2014

@author: RenSol
@description: This class is used to store event data from the Smith College events calendar to be mapped later on.

CODE UPKEEP: Hi! This program was written by the RenSol programming team for the SAL lab at Smith.
             If you are reading this you are probably:
                 1) a person who is just browsing the code
                 2) casually updating the code
                 3) WE GOT ERRORS UP THE WAZOO!
                 or
                 4) THE PROGRAM IS BROKEN! EVERYTHING IS TERRIBLE! WHAT SHOULD I DO?!?!?!
             If you are 1, feel free to skip over this part. If you are 3,4, or even 2, read on.
             
             We've left a lot of information about how to maintain this code, and we've created several tests
             in case something happens.
                          
             For a description of what exactly the code is for, what it is doing, and why it is doing it: https://github.com/sessionista/ReinEvent-Map/blob/master/README.md
             
             Specific tips and instructions on the code's upkeep:
             
             The original code: https://github.com/sessionista/ReinEvent-Map/blob/master/src/ReinEvent.py

             Below you will find commends blocks that say "something" TEST. These tests include descriptions and
             debugging tips. Uncomment these blocks and read the print statements. These should give some insight
             on whether this specific block is what is causing the problems. We created tests for the most
             variable elements of our code that we have the least control over (ex. building names, RSS feed, etc.)
             
'''

import feedparser
import cartodb



'''
@summary: Event is a class that each singular event would be stored in. Each event object will then have several parameters containing info about the event.
'''
class Event:
    '''
    @summary: Constructor for the Event class
    @params: self,
             name, event's name
             location, where the event will take place
             row_ref, building code associated with the location
             time, hour(s) the event will take place
             date, when the event will happen
    '''
    def __init__(self, name, location, row_ref, time, date):
        self.name = name
        self.location = location
        self.row_ref = row_ref
        self.time = time
        self.date = date
   


'''
@summary: Insert the data into the CartoDB account
@params: 
'''
def insert_events(events, client):
    print "Inserting events..."
    for e in events:
        command = "INSERT INTO buildingpoints_copy (event_name, event_loca, event_date, event_time, row_ref) VALUES('{0}', '{1}', '{2}', '{3}', '{4}')".format(e.name, e.location, e.date, e.time, e.row_ref)
        client.sql(command)
    print "Done inserting events."   


'''
@summary Grab buildings and their associated row references to place in a dictionary to be looked up later.
         Row references are numbers for smaller locations  (ex. Seelye 102, Weinstein Auditorium) to
         references the larger locations they are within (ex. Seelye Hall, Wright Hall). This is so we
         end up creating one point per building/major event location, rather than a large jumble of random points
@params client, the required URL to manipulate the sql
@return building_FM, the dictionary which will allow us to look up a building name and its code.
'''
def grab_RowDict(client):
    building_RowRef = {} #create an empty dict to later put building-row_ref pairs in

    #gain access to the buildings table from CartoDB account
    try:
        fields = client.sql('select * from buildingpoints_copy')
    except cartodb.CartoDBException as e:
        print ("some error occurred", e)
     
    num = len(fields['rows']) #figures number of rows in buildings table
    
    #go through each row within the buildings table
    for n in range(0,num): #n represents a row associated with a building
        row_ref = fields['rows'][n]['row_ref']
        
        building_name = fields['rows'][n]['bldg_name'] 
        event_loca = fields['rows'][n]['event_loca']
        
        if ((building_name == None) and (event_loca != None)) or ((building_name != None) and (event_loca != None)):
            location = event_loca
        elif (building_name != None) and (event_loca == None):
            location = building_name 
        else:        
            location = "LOCATION NOT FOUND"
            
        building_RowRef[location] = row_ref
        
        ''' RowRef TEST START
        
        DESCRIPTION: IF THE CODE BREAKS FOR SOME REASON THIS TEST IS TO MAKE SURE THE ROW REFERENCES
                     ARE WORKING (FROM CARTODB)
        POSSIBLE BREAK REASONS: The buildings need to be updated periodically because names change
                                (ex. a center gets named after someone), locations change, and new buildings
                                are added almost annually. This means that certain 
        DEBUGGING: Uncomment this test to check the row references. You will need the cartodb table
                   the code is referencing (see main method to get api key for table). RowRef is
                   a column in the table used to attribute certain locations to a building.
                   For example, if Bass Hall was in row 5, Young Science Library would have a 5 in its row ref
                   column. Bass Hall would not have anything in its row ref column, because it is a major
                   building/event location (in cartodb). Make sure the row references are correct. This will
                   require some Googling and/or good knowledge of the campus locations
        
        '''
        
        '''     
        print location
        print fields['rows'][n]['cartodb_id'] 
        print row_ref
        print
        '''
        
        '''RowRef TEST END '''
        
    return building_RowRef

'''
@summary: Create a list which will hold the events.
@params: FM_Dict, dictionary to lookup buildings 
@return: events, list of events
'''
def parse_events(FM_Dict):
    
    # variables to count events
    events_dropped = 0
    events_added = 0
    total_events = 0 # should be events_dropped + events_added. to account for any errors
    
    #set up to parse through content in RSS feed
    calendar = feedparser.parse("http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Featured+Events&mixin=12162")
    #calendar = feedparser.parse("http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Featured+Events")
    events = [] #list that holds the events
    
    #parse through each event in the RSS feed which is listed as an entry
    for entry in calendar.entries:
        
        #fix any unicode errors or what can't translate well
        description = entry.description.split("<br />", 2) #split the description into two parts
        entry.title.decode("utf-8", "strict").encode("utf-8", "ignore") #in case there's a title in a foreign language
                    
        #remove quotation marks in title because it creates conflict when putting the name in CartoDB table
        if ("\'" in entry.title) or ("\"" in entry.title):
            title = "" 
            for letter in entry.title: #go through letter by letter in the title to check if it's a quotation mark
                if (letter != "'") and (letter != "\""): #if not a quotation mark, add it to the title
                    title += letter
            name = title     
        else: #if quotation marks doesn't exist in the title, go ahead and grab it
            name = entry.title
            
        '''
        Sometimes there's an exception where an event doesn't have a location, thus no building name, but still has the date and time of the event in the
        description. 
        '''
        #format location
        location = description[0] 
        
        #format row_ref
        building_name = ""
        possibleBuildings = []
        keywords = location.split() # split the location name so we can isolate the building name
        
        ''' Find event location TEST START (pt 1)
        
        DESCRIPTION: THIS IS A SPECIAL TEST!!! IT HAS 5 PARTS! IN ORDER TO USE THIS TEST, MAKE SURE YOU UNCOMMENT
                     ALL 5 PARTS! AT THE END OF THE 5TH PART IT WILL SAY "Find event location TEST END"
        POSSIBLE BREAK REASONS:
        DEBUGGING: 
        '''
        
        '''
        print
        print "EVENT NAME: " + name
        '''
                
        total_events += 1
        # loops through all building names to determine which one the event is located at        
        for building in FM_Dict.keys():
            if keywords[0] in building:
                possibleBuildings.append(building)       
                #print building  
                
                ''' Find event location TEST START (pt 2)'''
               
                ''' 
                print "FIRST WORD OF EVENT LOCATION: " + keywords[0]
                print "FIRST WORD OF EVENT LOCATION MATCHES FIRST WORD OF: "
                print possibleBuildings
                '''
                
              
        try:
            if len(possibleBuildings) > 1:
                for possibility in possibleBuildings:
                    if keywords[1] in possibility:
                        building_name = possibility    
                        
                        ''' Find event location TEST START (pt 3)'''
                        '''
                        print "CHECKED TWO FIRST WORDS AND GOT A MATCH. FOR NOW WE WILL USE THE MATCH BUT WILL HAVE TO ACCOUNT FOR MORE LATER"
                        '''
            elif len(possibleBuildings) == 1:
                building_name = possibleBuildings[0]
               
                ''' Find event location TEST START (pt 4)'''
                '''
                print "ONLY ONE POSSIBLE BUILDING: " + building_name
                '''
            else:       
                ''' Find event location TEST START (pt 5)'''
                '''
                print "NO POSSIBLE EVENT LOCATIONS"  # this is usually if there is a date instead of an event location
                '''
                '''Find event location TEST END'''

            row_ref = FM_Dict[building_name] #look up row_ref using the building name and row_refdictionary
                            
            #format date
            date = description[1].split(",") #split string whenever it encounters a comma
            date_time = ",".join(date[:2]), ",".join(date[2:]) #only split until the second comma
            date = date_time[0]
                
            '''
            Possibly grab date and time from <pubdate> field rather than description[1]            
            
            date_time = entry.pubDate.split() #split pubDate's string into four parts
            date = date_time[0] + date_time[1] + date_time[2] #join the first three parts
            http://www.quora.com/How-can-I-convert-a-GMT-time-zone-into-local-time-in-Python
            http://stackoverflow.com/questions/6288892/convert-datetime-format
            '''
            #format time
            time = date_time[1].split()
            times = time[1].split("&nbsp;&ndash;&nbsp;") #get rid of the character " - " and split the string there
            time = times[0] + " - " + times[1] #concatenate strings with the time    

            #create an Event object
            e = Event(name, location, row_ref, time, date)
            events.append(e)
            events_added+=1
            
            '''
            Events added TEST START
            DESCRIPTION:
            POSSIBLE BREAK REASONS:
            DEBUGGING: 
            '''
            
            '''
            print e.name + " has been added to the list of events"
            print e.name + "'s" + " loca: " + building_name
            print e.name + "'s" + " time: " + e.time
            print e.name + "'s" + " date: " + e.date
            print
            '''
            
            '''Events added TEST END'''
            
        except KeyError:    
            # can't match the event, just keep going                   
            print "could not resolve event: " + name
            print
            events_dropped+=1
            
    ''' 
    Parsed events TEST START
    DESCRIPTION:
    POSSIBLE BREAK REASONS:
    DEBUGGING: 
    '''
       
    '''
    print
    print "Finished parsing..."            
    print "Number of events added: "
    print events_added
    print "Number of events dropped: "
    print events_dropped
    print "Total number of events parsed: "
    print total_events   
    '''
            
    return events    
            
'''
@summary: Initializes user data and create the CartoDB client to manipulate tables within.
'''
def main():

    #user information
    user = "" # empty string for privacy
    api_key = "" # empty string for privacy
    cartodb_domain = "" # empty string for privacy
        
    #initialize CartoDB client to deal with SQL commands
    cl = cartodb.CartoDBAPIKey(api_key, cartodb_domain)
    cl.sql("DELETE FROM buildingpoints_copy WHERE cartodb_id > 223") #CHANGE!!! 224 is the last row for the buildingpoints_copy up until we add events to the table
    FM_Dict = grab_RowDict(cl)
    insert_events(parse_events(FM_Dict), cl)

#calls the main function upon importing module
if __name__ == '__main__':
    main()
