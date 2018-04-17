Data Sources Used

For my final project, there are three main data sources that were used, and two of them requires an API key. The link to each source/API application page are listed as follows:
  1. Event Information: https://www.fairsandfestivals.net/
  2. Restaurant Information: Yelp Fusion API (API key required: https://www.yelp.com/fusion)
  3. Event and Parking Information: Google Map API (API key required: https://developers.google.com/places/web-service/)
  4. Map Visualization: Mapbox Tokens API (Access token required: https://www.mapbox.com/account/access-tokens)

To successfully incorporate these data sources into the program, a secrets.py file is needed. In the file, please specify the keys with the following variable names:
  Yelp Fusion API - yelp_fusion_key;
  Google Map API - google_places_key;
  Mapbox Tokens API - mapbox_access_token

As the program also uses plotly for the data visualization, here is the link to the 'Getting Started' page on plotly, in order to launch plotly in Python on your computer: https://plot.ly/python/getting-started/



Program Structure

My program is consisted of several different modules, the brief introduction for each module and important function are listed as follows:
  1. event_class.py: specify all the classes needed in the program
  2. event_db.py: initialize the sqlite database and handle all the database-related issues
     init_event_db(db_name): initiate the database by dropping existed tables and regenerate new tables
  3. event_plot.py: set down all the parameters for plotly to plot the map and bar char
  4. run_event_search.py: initiate all the functions related to search requests and the interactive prompt of the final program
     search_events_by_state(state_abbr): crawl the event information on the website and insert it into the database

There are three main classes used in this program:
  1. Event(): the class for each single event, containing all the important information of the event including name, date, address and others
  2. Restaurant(): the class for restaurants that nearby one target event, containing restaurant name, rate, address and location Information
  3. ParkingStructure(): the class for parking structures that nearby one target event, containing structure name and address



User Guide

1. To run the program successfully, the user will need to start the search by using the command of 'list + state_abbreviation' to first check the overview of the top 100 upcoming events in the state. User can choose to view the events by city or by event type by adding a params after the command as 'groupby=city/type'.   
Data presentation options: If events are grouped by city, commanding 'plot' will generate a state map of the event distributions. If grouped by event type, 'plot' will generate a bar chart indication how many events are there in each type of events.

2. The next step will be checking the detailed information that belongs to one specific category (one city or one type) by using the command of 'more + category index number'. The program will list all the detailed information of the each event that belongs to the target category.
Data presentation options: By using 'plot' in this stage, the program will generate a map showing all the events in geographically.

3. If user finds an interesting event after browsing the list, they can check the restaurants and parking lots nearby the event location in order to plan their visit. This can be achieved by using the command of 'nearby + event index number'.
Data presentation options: By using 'plot' in this stage, the program will generate a map showing the event, the restaurants and the parking lots with different colors in the same map.

4. If user finishes all the search, the 'exit' command will help them exit the program successfully. If user have questions or confusions at any time, they can use 'help' to call out the command guide in the program.
