ReinEvent-Map
=============
## Introduction
Hello friend!

This is a revamp of the previous map events project for the Smith College Spatial Analysis Lab created by the RenSol programming team. It is essentially a visualization of all the events happening at Smith College.

There are five categories of events that can be viewed: Featured, Student Interest, Lectures and Symposia, Multicultural Events, and Athletic Events.

The visualization can be viewed [here](http://www.science.smith.edu/departments/sal/devel/MappingEvents.html).

Feel free to click around and see what is happening on Smith's campus (updated daily). And check out the info below to see how it works!

~ Ren and Sol

## How it Works
	- From ArcMap every event location (from the list of possible event
      locations to book for events) has been given a point by hand 
      
	- From CartoDB the code gets the list of buildings at Smith College
    
	- From the [Events Calendar](http://www.smith.edu/calendar/#/?i=3) the code gets the XML code from the events
      page and parses through it. There are five categories of events
      that it pulls information from: Featured, Student Interest,
      Lectures and Symposia, Multicultural Events, and Athletic Events
      
	- The code pushes all the event info into the CartoDB database
    
    - The code then maps all the events to their respective locations
      (a building on campus).
      
	- The visualization can then be viewed [here](http://www.science.smith.edu/departments/sal/devel/MappingEvents.html) with an updated
      list of events.
    	- NOTE: The points are sized relative to the number of events at
        		that location.
        - NOTE: Each point can be selected to see what events are happening
        		at a specific building, and other information pertinant to
                that event (e.g. date, time, location)
                
    - The map is scheduled to update daily at 6:15 AM


## UPDATE AND MAINTENANCE INSTRUCTIONS
- Email the Events Management Office and get an updated list of events
- Briefly look over the code. See what you’re up against. Read the documentation.
	- NOTE: the code is presently in Python2
- Update the ArcGIS map by hand. Check to make sure every single event has a point using the new updated list.
	- NOTE: the code will parse over events it can’t identify, but it would be best to account for as many as possible so this is important for identifying new locations, buildings with changed names, etc.
	- NOTE: you will find a lot of event locations you never could have imagined. You can technically book a vending machine.
- Go back to the code. Make sure you know how it works in case it crashes
  (though this is highly unlikely). Feel free to make more efficient.
  
## TO FIX
- FIX SCROLL THING ON INFO WINDOWS
- FIX FONT SIZE IN INFO WINDOWS
- CREATE BACK BUTTON
- FIX LOCATION STUFF (when they’re all clumped together)
- EMAIL THOSE PEOPLE ABOUT THE DOTS BEING BEHIND THE MAP SOMETIMES. WHAT'S UP WITH THAT?

