'''
Created on Oct 28, 2014

@author: Ren Delos Reyes and Sol Kim
@description: This class is used to store event data from the Smith College events calendar to be mapped later on.

CODE UPKEEP: Hi! This program was written by the RenSol programming team for the SAL lab at Smith.
             If you are reading this you are probably:
                 1) a person who is just browsing the code
                 2) casually updating the code
                 3) SOMEONE WHO HAS GOT ERRORS UP THE WAZOO!
                 or
                 4) THE PROGRAM IS BROKEN! WHAT SHOULD I DO?!?!?!
             If you are 1, feel free to skip over this part. If you are 3, 4, or even 2, read on.
             
             We've left a lot of information about how to maintain this code, and we've created several tests
             in case something happens.
                          
             For a description of what exactly the code is for, what it is doing, and why it is doing it: https://github.com/sessionista/ReinEvent-Map/blob/master/README.md
             
             Specific tips and instructions on the code's upkeep:
             
             The original code: https://github.com/sessionista/ReinEvent-Map/blob/master/src/ReinEvent.py

             Below you will find commends blocks that say "something" TEST. These tests include descriptions and
             debugging tips. Uncomment these blocks and read the print statements. These should give some insight
             on whether this specific block is what is causing the problems. We created tests for the most
             variable elements of our code that we have the least control over (ex. building names, RSS feed, etc.)
             There will be # comments to tell you where to uncomment the test.  
             
             The first test you chould check is "Parsed events" near the main function below.
'''

import Private      # file with sensitive information
import feedparser
import cartodb
'''
@summary: Event is a class that each singular event WILL be stored in. Each event object will then have several parameters containing information about the event.
'''
class Event:
    '''
    @summary: Constructor for the Event class
    @params: self,
             name, event's name
             location, where the event will take place
             row_ref, building code associated with the location (e.g. Neilson Browsing Room will have a row_ref pointing to Neilson Library)
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
@params: events, list of event objects created
         client, allows access to edit cartoDB table
'''
def insert_events(events, client, rssFeed):
    #try:
        #print "Inserting events..."
        for e in events:
            try:
                #print e.name
                ''' TABLE NAMES REMOVED FOR PRIVACY'''
                if rssFeed == "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Student+Interest&filter3=_Confirmed_&filterfield3=2591&mixin=12185":
                    command = "INSERT INTO student_events (event_name, event_loca, event_date, event_time, row_ref) VALUES('{0}', '{1}', '{2}', '{3}', '{4}')".format(e.name, e.location, e.date, e.time, e.row_ref)
                elif rssFeed == "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Lectures+%2f+Symposia&mixin=12178":
                    command = "INSERT INTO lecture_events (event_name, event_loca, event_date, event_time, row_ref) VALUES('{0}', '{1}', '{2}', '{3}', '{4}')".format(e.name, e.location, e.date, e.time, e.row_ref)
                elif rssFeed == "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Athletic+Events&filter3=_Confirmed_&filterfield3=2591&mixin=12172":
                    command = "INSERT INTO athletic_events (event_name, event_loca, event_date, event_time, row_ref) VALUES('{0}', '{1}', '{2}', '{3}', '{4}')".format(e.name, e.location, e.date, e.time, e.row_ref)
                elif rssFeed == "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Multicultural+Events&mixin=12180":
                    command = "INSERT INTO multicultural_events (event_name, event_loca, event_date, event_time, row_ref) VALUES('{0}', '{1}', '{2}', '{3}', '{4}')".format(e.name, e.location, e.date, e.time, e.row_ref)
                elif rssFeed == "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Featured+Events&mixin=12162":
                    command = "INSERT INTO featured_events (event_name, event_loca, event_date, event_time, row_ref) VALUES('{0}', '{1}', '{2}', '{3}', '{4}')".format(e.name, e.location, e.date, e.time, e.row_ref)
                else:
                    print
                
                client.sql(command)
            except Exception:
                print "Could not insert: " + e.name
       
        
                      
        print "Done inserting events."   
        print
        print
        
  

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
        
        ''' TABLE NAMES REMOVED FOR PRIVACY'''
        fields = client.sql('select * from buildingpoints_smithevents')
        
    except cartodb.CartoDBException as e:
        print ("some error occurred", e)
     
    num = len(fields['rows']) #figures number of rows in buildings table
    
    #go through each row within the buildings table
    for n in range(0,num): #n represents a row associated with a building
        row_ref = fields['rows'][n]['row_ref']
        
        building_name = fields['rows'][n]['bldg_name'] 
        event_loca = fields['rows'][n]['event_loca']
        
        if ((building_name == None) and (event_loca != None)) or ((building_name != None) and (event_loca != None)):
            cap_location = event_loca
        elif (building_name != None) and (event_loca == None):
            cap_location = building_name 
        else:        
            cap_location = "LOCATION NOT FOUND"
            
        cap_location = cap_location.upper() # making uppercase so we eliminate any errors from case sensitivity
            
        building_RowRef[cap_location] = row_ref
        
        
        
        ''' RowRef TEST START
        
        DESCRIPTION: IF THE CODE BREAKS FOR SOME REASON THIS TEST IS TO MAKE SURE THE ROW REFERENCES
                     ARE WORKING (FROM CARTODB)
        POSSIBLE BREAK REASONS: The buildings need to be updated periodically because names change
                                (e.g. a center gets named after someone), locations change, and new buildings
                                are added almost annually. This means that certain locations will need to have their
                                bldg_name (if it's a main building) or event_loca (if it's a location within a main building)
                                updated in the buildingpoints_smithevents table
        DEBUGGING: Uncomment this test to check the row references. You will need the cartodb table
                   the code is referencing (buildingpoints_smithevents). RowRef is
                   a column in the table used to attribute certain locations to a building.
                   For example, if Bass Hall was in row 5, Young Science Library would have a 5 in its row ref
                   column. Bass Hall would not have anything in its row ref column, because it is a major
                   building/event location (in cartodb). Make sure the row references are correct. This will
                   require some Googling and/or good knowledge of the campus locations
        '''
        
        #START UNCOMMENTING HERE 
        '''
        print location
        print fields['rows'][n]['cartodb_id'] 
        print row_ref
        print
        '''
        # STOP UNCOMMENTING HERE
        
        '''RowRef TEST END '''
        
    return building_RowRef

'''
@summary: Create a list which will hold the events.
@params: Row_Dict, dictionary to lookup buildings 
         cl, allows us to edit the table 
@return: events, list of events
'''
def parse_events(Row_Dict, client, rssFeed):
    
    # variables to count events
    events_dropped = 0
    events_added = 0
    total_events = 0 # should be events_dropped + events_added. to account for any errors
    
    #set up to parse through content in RSS feed
    calendar = feedparser.parse(rssFeed)
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
        
        keywords = location.upper().split() # split the location name so we can isolate the building name
                                            # making uppercase so we eliminate any errors from case sensitivity
        ''' Find event location TEST START
        
        DESCRIPTION: THIS IS A SPECIAL TEST!!! IT HAS 5 PARTS! UNCOMMENT ALL 5 PARTS FOR THE BEST RESULTS!
                     EACH PART HAS A DESCRIPTION OF WHAT THAT PART DOES.
                     AT THE END OF THE 5TH PART IT WILL SAY "Find event location TEST END"
        POSSIBLE BREAK REASONS: The series of these tests will give you insight into what events are being added and what events aren't. The most likely reason
                                for an event not being added is the event location/building undergoing a name change (e.g. Center for Work and Life -> Wurtele Center).
                                Other reasons could be minor spelling or errors (upper and lower case distinctions have be accounted for), the addition of a new event,
                                or some other result of people changing stuff around. It will help to go to the smith college calendar site, check the event locations,
                                and compare them to the buildings in the cartoDB table.
        ''' 
        
        
        ''' Find event location TEST (pt 1)
            TEST 1 DESCRIPTION: This test will tell you what event from the event calendar is being 
        '''
        # START UNCOMMENTING HERE
        '''
        print
        print "EVENT NAME: " + name
        '''
        # STOP UNCOMMENTING HERE
                
        total_events += 1
        # loops through all building names to determine which one the event is located at        
        for building in Row_Dict.keys():
            
            if keywords[0] in building:
                possibleBuildings.append(building)       
                ''' Find event location TEST START (pt 2)
                    TEST 2 DESCRIPTION: This test will tell you the possible buildings the event could be located in/at based on the first word of the event location from the website
                '''
               
               # START UNCOMMENTING HERE
                '''
                print "FIRST WORD OF EVENT LOCATION: " + keywords[0]
                print "FIRST WORD OF EVENT LOCATION MATCHES FIRST WORD OF: "
                print possibleBuildings
                '''
                # STOP UNCOMMENTING HERE
              
        try:
            if len(possibleBuildings) > 1:
                for possibility in possibleBuildings:
                    if keywords[1] in possibility:
                        building_name = possibility    
                        
                        ''' Find event location TEST START (pt 3)
                            TEST 3 DESCRIPTION: This test will tell you whether a building has been matched to the event location.

                        '''
                        
                        # START UNCOMMENTING HERE
                        '''
                        print "CHECKED TWO FIRST WORDS AND GOT A MATCH. WE WILL USE THE MATCH."
                        '''
                        # STOP UNCOMMENTING HERE
            elif len(possibleBuildings) == 1:
                building_name = possibleBuildings[0]
               
                ''' Find event location TEST START (pt 3)
                    TEST 4 DESCRIPTION: There is only one possible building that can be matched so we choose it
                '''
                        
                # START UNCOMMENTING HERE
                '''
                print "ONLY ONE POSSIBLE BUILDING: " + building_name
                '''
                # STOP UNCOMMENTING HERE

            else:       
                ''' Find event location TEST START (pt 3)
                     TEST 5 DESCRIPTION: There are no possible buildings that can be matched. This is the test that probably indicates that a name has been changed
                                         or there is a minor spelling or punctuation error
                '''
                        
                # START UNCOMMENTING HERE
                '''
                print "NO POSSIBLE EVENT LOCATIONS"  # this is usually if there is a date instead of an event location
                '''
                # STOP UNCOMMENTING HERE
                '''Find event location TEST END'''

            row_ref = Row_Dict[building_name] #look up row_ref using the building name and row_refdictionary


            ''' TABLE NAMES REMOVED FOR PRIVACY'''
            if rssFeed == "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Student+Interest&filter3=_Confirmed_&filterfield3=2591&mixin=12185":
                command = "UPDATE buildingpoints_smithevents SET student_events = student_events+1 WHERE cartodb_id = {0}".format(row_ref) # student events
            elif rssFeed == "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Lectures+%2f+Symposia&mixin=12178":
                command = "UPDATE buildingpoints_smithevents SET lecture_events = lecture_events+1 WHERE cartodb_id = {0}".format(row_ref) # lectures events
            elif rssFeed == "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Athletic+Events&filter3=_Confirmed_&filterfield3=2591&mixin=12172":
                command = "UPDATE buildingpoints_smithevents SET athletic_events = athletic_events+1 WHERE cartodb_id = {0}".format(row_ref) # athletic events
            elif rssFeed == "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Multicultural+Events&mixin=12180":
                command = "UPDATE buildingpoints_smithevents SET multicultural_events = multicultural_events+1 WHERE cartodb_id = {0}".format(row_ref) # multicultural events
            elif rssFeed == "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Featured+Events&mixin=12162":
                command = "UPDATE buildingpoints_smithevents SET featured_events = featured_events+1 WHERE cartodb_id = {0}".format(row_ref) # featured events
            else:
                print("butts")

            client.sql(command) 
            
            #format date
            date = description[1].split(",") #split string whenever it encounters a comma
            date_time = ",".join(date[:2]), ",".join(date[2:]) #only split until the second comma
            date = date_time[0]
                
            #format time
            time = date_time[1].split()
            times = time[1].split("&nbsp;&ndash;&nbsp;") #get rid of the character " - " and split the string there
            try:
                time = times[0] + " - " + times[1] #concatenate strings with the time    
            except IndexError:
                time = "TBA" #concatenate strings with the time 
                
            #create an Event object
            e = Event(name, location, row_ref, time, date)
            events.append(e)
            events_added+=1
            
            '''
            Events added TEST START
            DESCRIPTION: This test is in case an event on the website has weird information. This test is so you can see the information individually and pinpoint
                         where the odd information is coming from.
            POSSIBLE BREAK REASONS: Smith Calendar has formatted the information differently than when we started. It is not likely.
            DEBUGGING: Double check insert_events function, and check the XML from the calendar's RSS feed. Contact the administrator in charge of the calendar
                       if needed.
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
            '''
            print keywords[0]            
            print "could not resolve event: " + name
            '''
            
            events_dropped+=1
            
    '''        
    Parsed events TEST START
    DESCRIPTION: This test is to see how many events have been added and how many events have been dropped. This is a good place to start to see if there
                 are any issues with adding events. It also may give insight into why the visualization may or may not be showing very many events.
    DEBUGGING: 
    '''

    # START UNCOMMENTING HERE
    '''
    print
    print "Finished parsing... " + rssFeed         
    print "Number of events added: "
    print events_added
    print "Number of events dropped: "
    print events_dropped
    print "Total number of events parsed: "
    print total_events
    print   
    '''
    # STOP UNCOMMENTING HERE
            
    return events    
            
'''
@summary: Initializes user data and create the CartoDB client to manipulate tables within.
'''
def main():

    ''' USER INFO REMOVED FOR PRIVACY'''
    
    user = Private.USER
    api_key = Private.API_KEY
    cartodb_domain = Private.CARTODB_DOMAIN
    
    ''' RSS FEEDS REMOVED FOR PRIVACY'''
    student_events = "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Student+Interest&filter3=_Confirmed_&filterfield3=2591&mixin=12185"
    lecture_events = "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Lectures+%2f+Symposia&mixin=12178"
    athletic_events = "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Athletic+Events&filter3=_Confirmed_&filterfield3=2591&mixin=12172"
    multicultural_events = "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Multicultural+Events&mixin=12180"
    featured_events = "http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Featured+Events&mixin=12162"

    #initialize CartoDB client to deal with SQL commands
    cl = cartodb.CartoDBAPIKey(api_key, cartodb_domain)
    
    ''' TABLES REMOVED FOR PRIVACY '''
    cl.sql("DELETE FROM student_events")
    cl.sql("DELETE FROM lecture_events") 
    cl.sql("DELETE FROM athletic_events") 
    cl.sql("DELETE FROM multicultural_events") 
    cl.sql("DELETE FROM featured_events") 

    cl.sql("UPDATE buildingpoints_smithevents SET student_events = 0")
    cl.sql("UPDATE buildingpoints_smithevents SET lecture_events = 0") 
    cl.sql("UPDATE buildingpoints_smithevents SET athletic_events = 0") 
    cl.sql("UPDATE buildingpoints_smithevents SET multicultural_events = 0") 
    cl.sql("UPDATE buildingpoints_smithevents SET featured_events = 0") 
    
    Row_Dict = grab_RowDict(cl)
    insert_events(parse_events(Row_Dict, cl, student_events), cl, student_events)
    insert_events(parse_events(Row_Dict, cl, lecture_events), cl, lecture_events)
    insert_events(parse_events(Row_Dict, cl, athletic_events), cl, athletic_events)
    insert_events(parse_events(Row_Dict, cl, multicultural_events), cl, multicultural_events)
    insert_events(parse_events(Row_Dict, cl, featured_events), cl, featured_events)

#calls the main function upon importing module
if __name__ == '__main__':
    main()

