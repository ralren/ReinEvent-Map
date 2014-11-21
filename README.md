ReinEvent-Map
=============

### DESCRIPTION
This is a Revamp of the previous map events project for the Smith College Spatial Analysis Lab

### LINKS
- Events: http://www.smith.edu/calendar/#/?i=3
- Brief description of how the code works:
	- From ArcMap every event location (from the list of possible event locations to book for events) has been given a point by hand. 
	- From CartoDB the code gets the list of buildings
	- From the Events Calendar the code gets the XML code from the events page and parses through it.
	- The code can identify where the approximate location of each field (e.g. location, building name) and assigns the values to an event (a class we created).
	- You end up with a list of events to create the map.


### UPDATE INSTRUCTIONS
- Email the Events Management Office and get an updated list of events
- Briefly look over the code. See what you’re up against. Read the documentation.
	- NOTE: the code is presently in Python2
- Update the ArcGIS map by hand. Check to make sure every single event has a point using the new updated list.
	- NOTE: the code will parse over events it can’t identify, but it would be best to account for as many as possible so this is important for identifying new locations, buildings with changed names, etc.
	- NOTE: you will find a lot of event locations you never could have imagined. isn’t that cool?
- Go back to the code. Make sure you know how it works in case it crashes. Feel free to make more efficient.

### TO DO
- add building column called "row ref" to tables. This column will be used to attribute certain locations to a building. For example, if Bass Hall was in row 5, Young Science Library would have a 5 in its row ref column. Bass Hall would not have anything in its row ref column, because it is a major building/event location (in cartodb)
- change dictionary so it pulls category row ref instead of fm dictionary (in python)
- adjust function to put events as rows in building points table
