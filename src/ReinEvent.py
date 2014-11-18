'''
Created on Oct 28, 2014

@author: RenSol
@description: This class is used to store event data from the Smith College events calendar to be mapped later on.
'''
import feedparser
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
@summary Grab buildings and their associated codes to place in a dictionary to be looked up later.
@params client, the required URL to manipulate the sql
@return building_FM, the dictionary which will allow us to look up a building name and its code.
'''
def grab_FMDict(client):
    building_FM = {} #create an empty dict to later put building-FMCode pairs in

    #gain access to the buildings table from CartoDB account
    try:
        fields = client.sql('select * from buildings')
    except cartodb.CartoDBException as e:
        print ("some error occurred", e)
     
    num = len(fields['rows']) #figures number of rows in buildings table
    
    #go through each row within the buildings table
    for n in range(0,num): #n represents a row associated with a building
        building_name = fields['rows'][n]['bldg_name'] 
        FMCode = fields['rows'][n]['fmcode']
        building_FM[building_name] = FMCode #add as key-value pair to dict
    
    return building_FM

'''
@summary: Create a list which will hold the events.
@params: FM_Dict, dictionary to lookup buildings and 
@return: events, list of events
'''
def parse_events(FM_Dict):
    #set up to parse through content in RSS feed
    calendar = feedparser.parse("http://25livepub.collegenet.com/calendars/scevents.rss?filterview=Featured+Events&mixin=12162")
    events = [] #list that holds the events
    
    #parse through each event in the RSS feed which is listed as an entry
    for entry in calendar.entries:
        
        #fix any unicode errors or what can't translate well
        description = entry.description.split("<br />", 1) #split the description into a part
        entry.title.decode("utf-8", "strict").encode("utf-8", "ignore") #in case there's a title in a foreign language
        
        #check if the event is within the events list already
        without = True
        for event in events:
            #does it have the title (entry.title) and location (description[0]) as the same thing?
            if (event.name == entry.title) and (event.location == description[0]):
                without = False
                
        if without: #if event isn't already within the events list, add it to the events list
            
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
            Sometimes there's an exception where an event doesn't have a location, thus no FMCode, and has the date and time of the event in the
            description. 
            '''
            #format location
            location = description[0] 
            
            #format fmcode
            building_name = ""
            possibleBuildings = []
            keywords = location.split() # split the location name so we can isolate the building name
            
            print "this is the name of the event: " + name
            # loops through all building names to determine which one the event is located at        
            for building in FM_Dict.keys():
                if keywords[0] in building:
                    possibleBuildings.append(building)       
                    #print building     
                    print "this is the first word of the event location: " + keywords[0]
                    print "the first word of the location is in building name. will print all possible buildings it could be: "
                    print possibleBuildings
                    
            ''' EXCEPTIONS TO WORK ON
                
                NO LOCATION
                
                IF IT CAN'T FIND IT THEN JUST MOVE ON (KeyError)
                
                LOCATIONS THAT WORK AREN'T IN THE BUILDINGS TABLE (EX. THE QUAD)
                //IF BUILDINGS TABLE WAS ACCORDING TO WHERE YOU COULD BOOK EVENTS
                
                REMIND TO GET UPDATED LIST EVERY YEAR
                
                NEEDS TO ACCOMODATE FOR SAME EVENT ON DIFFERENT DATES
                
                WILL EVENTUALLY ACCOUNT FOR EXCEPTIONS INSTEAD OF HAVING SPECIFIC ELIFS
                
                THE RSS FEED ALLOWS FOR ABOUT 35 EVENTS
                
                DOES NOT FIND TV STUDIO
                CHAPIN HOUSE LAWN IS NOT ACCOUNTED FOR. NEED TO FIX HOW MANY KEYWORDS THE CODE CHECKS! MORE THAN 2!
                NEILSON BROWSING ROOM DEFAULTS TO NEILSON LIBRARY
            ''' 
                  
            try:
                if len(possibleBuildings) > 1:
                    for possibility in possibleBuildings:
                        if keywords[1] in possibility:
                            building_name = possibility    
                #some of the buildings are within another building so just assign them the same cartodb ID
                elif len(possibleBuildings) == 0:
                    # IF THE LIST IS BLANK OR THERE IS A DATE INSTEAD OF AN EVENT
                    butts = 5
                    print "we checked the first two keywords and they match with a building. we have to fix this but it works"
                elif len(possibleBuildings) == 1:
                    print possibleBuildings
                    building_name = possibleBuildings[0]
                    print "there is only one possible building name: " + building_name
                elif (keywords[0] == "Sweeney") or (keywords[0] == "Earle"):
                    building_name = "Sage Hall"
                elif (keywords[0] == "Lewis") or (keywords[0] == "Weinstein"):
                    building_name = "Wright Hall"
                elif (keywords[0] == "Hallie") or (keywords[0] == "Theatre") or (keywords[0] == "Formerly"):
                    building_name = "Mendenhall Center for Performing Arts"
                elif (keywords[0] == "BFAC") or (keywords[0] == "Hillyer") or (keywords[0] == "Graham"):
                    building_name = "Fine Arts Center"
                elif (keywords[0] == "Quad"):
                    building_name = "Wilson House"
                #only one code so get it
                else:
                    # IF THE LIST IS BLANK OR THERE IS A DATE INSTEAD OF AN EVENT
                    print "there are no possible events"

                fmcode = FM_Dict[building_name] #look up fmcode using the building name and FMCodedictionary
                                
                '''
                Possibly grab date and time from <pubdate> field rather than description[1]
                '''
                #format date
                date = description[1].split(",") #split string whenever it encounters a comma
                date_time = ",".join(date[:2]), ",".join(date[2:]) #only split until the second comma
                date = date_time[0]
                    
                '''
                date_time = entry.pubDate.split() #split pubDate's string into four parts
                date = date_time[0] + date_time[1] + date_time[2] #join the first three parts
                '''
                #format time
                time = date_time[1].split()
                times = time[1].split("&nbsp;&ndash;&nbsp;") #get rid of the character " - " and split the string there
                time = times[0] + " - " + times[1] #concatenate strings with the time    
    
                #create an Event object
                e = Event(name, location, fmcode, time, date)
                events.append(e)
                print e.name + " has been added to the list of events"
                print "its location is at " + building_name
                print
                #print e.name
            except KeyError:    
                # can't match the event, just keep going                   
                print "could not resolve event: " + name
                print
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
    FM_Dict = grab_FMDict(cl)
    parse_events(FM_Dict)

#calls the main function upon importing module
if __name__ == '__main__':
    main()
