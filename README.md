ReinEvent-Map
=============

### Description
This is a Revamp of the previous map events project for the Smith College Spatial Analysis Lab created by the RenSol programming team.

Here (hyperlink)


### Links
- Events Calendar: http://www.smith.edu/calendar/#/?i=3
- Event Visualization: 

### How it Works:
	- From ArcMap every event location (from the list of possible event
      locations to book for events) has been given a point by hand. 
	- From CartoDB the code gets the list of buildings
	- From the Events Calendar the code gets the XML code from the events
      page and parses through it. There are five catagories of events
      that it pulls information from: Featured, Lectures & Symposia,
      
	- The code pushes all the event info into the CartoDB database
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
- put a cap on how big points can get. ideally they would be relative to each other
- think about having an info window explaining the project. hover or click.
- want points to be over map. maybe check that out.
- format infowindows
