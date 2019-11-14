# Fencing Competition App
This app will assist in the planning and management of fencing competition. Its purpose is not to recreate information that is already available in the USFA website and fencingtimelive, but instead to aggregate that data differently so that it can be used to more effectively select suitable tournaments based on field quality, points availability, distance.
## Functionality
It will: 
1. maintain a database upcoming tournaments including: 
    * how far away thay are
    * events being contested
    * number of fencers competing
    * day/time or event
    * fencers competing including seeding
    * average standard of competition
    * generate spreadsheet for event day to compare pools

1. Maintain a database of past tournaments:
    * list of competitors
    * final result
    * results of each pool/pool bout
    * results of each DE 

1. Display Summary performance data for an individual fencer
    * Name, club ,rating , YoB
    * Last five event results  (include international? ) including pool results, seeding and DE results
    * Last ten bout  results including 
    * Regional and National Points standings with link to full listing and number of points required 
      to qualify

### Upcoming Tournaments
#### Summary
1. List regional and national tournaments, their dates, locations, events and field size/event rating
1. The app will scrape national and regional tournaments from the USFA website and create google calendar entries for each of the tournaments.  

#### Status
 currently the data entry is manually done by putting results into a spreadsheet and the spreadsheet data is loaded into python which then writes to the Fencing Competition calendar, adding color coding, address and USFA hyperlinks and registration deadlines to the entry.
 The application should add all tournaments to the fencing competition calendar and then, when a registration has been completed, add an entry for each registered event at the correct time
#### Next Steps
1. Build a structured scraper to pull data Tournaments->Events->Entrants, from the USFA website.
1. Build a database to store those events 
1. Build code to insert initial records into database and allow updates to the data, particularly as fencers as added and removed from the roster

### Registered tournaments
1. First version should create excel sheet with event field
1. Detect when a tournament has been registered and add the events for those tournaments in Google calendar
1. download pool assignments and assess pool strength.
1. Allow inspection of competitors' rating and competition history
1. allow recording of bout results
1. download DE rounds and

### Past Tournaments
1. results of tournaments - can be done with a link to fencingtimelive



### Fencer Tracking

1. Number of regional and national points for each age group
1. Progress towards JO and National Qualification
1. Current standings and change in standings
1. points earned history
1. rating history
1. Favorite fencers list 

## Implementation
The app needs to be accessible from mobile devices so it will be web based, likely running on AWS ultimately