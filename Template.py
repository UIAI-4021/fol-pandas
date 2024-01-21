import sys
import tkinter
import tkinter.messagebox
from tkintermapview import TkinterMapView
from pyswip import Prolog
import pandas as pd
from itertools import chain


uniqe_features_dict = {}

class App(tkinter.Tk):

    APP_NAME = "map_view_demo.py"
    WIDTH = 800
    HEIGHT = 750  # This is now the initial size, not fixed.

    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.title(self.APP_NAME)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Text area and submit button combined row
        self.grid_rowconfigure(1, weight=4)  # Map row

        # Upper part: Text Area and Submit Button
        self.text_area = tkinter.Text(self, height=5)  # Reduced height for text area
        self.text_area.grid(row=0, column=0, pady=(10, 0), padx=10, sticky="nsew")

        self.submit_button = tkinter.Button(self, text="Submit", command=self.process_text)
        self.submit_button.grid(row=0, column=0, pady=(0, 10), padx=10, sticky="se")  # Placed within the same cell as text area

        # Lower part: Map Widget
        self.map_widget = TkinterMapView(self)
        self.map_widget.grid(row=1, column=0, sticky="nsew")

        self.marker_list = []  # Keeping track of markers
        self.marker_path = None


    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        self.title(self.APP_NAME)
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")

        # Configure the grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Text area can expand/contract.
        self.grid_rowconfigure(1, weight=0)  # Submit button row; doesn't need to expand.
        self.grid_rowconfigure(2, weight=3)  # Map gets the most space.

        # Upper part: Text Area and Submit Button
        self.text_area = tkinter.Text(self)
        self.text_area.grid(row=0, column=0, pady=10, padx=10, sticky="nsew")
        
        self.submit_button = tkinter.Button(self, text="Submit", command=self.process_text)
        self.submit_button.grid(row=1, column=0, pady=10, sticky="ew")

        # Lower part: Map Widget
        self.map_widget = TkinterMapView(self)
        self.map_widget.grid(row=2, column=0, sticky="nsew")

        self.marker_list = []  # Keeping track of markers

    def check_connections(self, results):
        adjacency_df = pd.read_csv('Adjacency_matrix.csv')
        print('result2 ', results)
        locations = []

        for _,row in adjacency_df.iterrows():
            for i in range(len(row)):
                if row[i] == 1:
                    prolog.assertz(f"directly_connected('{str(row[0]).lower()}', \"{str(adjacency_df.columns[i]).lower()}\")")
        
        prolog.assertz("connected(X, Y) :- directly_connected(X, Y)")
        prolog.assertz("connected(X, Y) :- directly_connected(Y, X)")

        prolog.assertz("connected(X, Y) :- directly_connected(X, Z), connected(Z, Y)")

        def search(queary):
            connected_cities = set()
            connected = list(prolog.query(queary))
            for dest in connected:
                connected_city = dest['X']
                if isinstance(connected_city, bytes):
                    connected_city = connected_city.decode('utf-8')
                print(connected_city)
                connected_cities.add(connected_city)
            return connected_cities
        connected_dict = {}
        for result in results:
            city  = result["City"]
            locations.append(city)
            # TODO 5: create the knowledgebase of the city and its connected destinations using Adjacency_matrix.csv
            print(city)
            query = f"connected('{city}', X)"
            connected_dict[city] =  search(query)
    

        
        return locations

    def process_text(self):
        """Extract locations from the text area and mark them on the map."""
        text = self.text_area.get("1.0", "end-1c")  # Get text from text area
        features_dict = self.extract_locations(text)
        # locations = features_dict['']  # Extract locations (you may use a more complex method here)
        query_dict = {}
        
        temp_keys = ['A', 'B', 'C' , 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
        tmp_i = 0 

        for feature_set in features_dict:
            str = '('
            for feature in features_dict[feature_set]:
                if feature == '_':
                    str += temp_keys[tmp_i] + ' = '  + feature + ' ; '
                else:
                    str += temp_keys[tmp_i] + ' = ' + "'" + feature + "'" + ' ; '
            str = str[:-3]
            str += ')'
            query_dict[temp_keys[tmp_i]] = str
            tmp_i += 1
        query = f"destination(City,A, B, C, D, E, F, G, H, I, J, K, L), {query_dict['A']}, {query_dict['B']}, {query_dict['C']}, {query_dict['D']}, {query_dict['E']}, {query_dict['F']}, {query_dict['G']}, {query_dict['H']}, {query_dict['I']}, {query_dict['J']}, {query_dict['K']}, {query_dict['L']}"


        # TODO 4: create the query based on the extracted features of user desciption 
        ################################################################################################
        # query = "destination(City,_, _, _, low, _, _, _, _, _, _, _, _)"
        results = list(prolog.query(query))
        locations = []
        locations = self.check_connections(results)
        # TODO 6: if the number of destinations is less than 6 mark and connect them 
        ################################################################################################
        print(locations)
        locations = ['mexico_city','rome' ,'brasilia']
        self.mark_locations(locations)

    def mark_locations(self, locations):
        """Mark extracted locations on the map."""
        for address in locations:
            marker = self.map_widget.set_address(address, marker=True)
            if marker:
                self.marker_list.append(marker)
        self.connect_marker()
        self.map_widget.set_zoom(1)  # Adjust as necessary, 1 is usually the most zoomed out


    def connect_marker(self):
        print(self.marker_list)
        position_list = []

        for marker in self.marker_list:
            position_list.append(marker.position)

        if hasattr(self, 'marker_path') and self.marker_path is not None:
            self.map_widget.delete(self.marker_path)

        if len(position_list) > 0:
            self.marker_path = self.map_widget.set_path(position_list)

    def extract_locations(self, text):
        """Extract locations from text. A placeholder for more complex logic."""
        # Placeholder: Assuming each line in the text contains a single location name
        # TODO 3: extract key features from user's description of destinations
        ################################################################################################
        entered_features = {}
        words = {str(item).replace('-', ' ') for item in set(chain.from_iterable(line.strip().lower().split(' ') for line in text.split('\n') if line.strip()))}
        for feature_key in uniqe_features_dict:
            intersection = words.intersection(uniqe_features_dict[feature_key])
            if intersection:
                entered_features[feature_key] = intersection
            else:
                entered_features[feature_key] = '_'
        
        return entered_features

    def start(self):
        self.mainloop()

# TODO 1: read destinations' descriptions from Destinations.csv and add them to the prolog knowledge base
        
dest_df = pd.read_csv('./Destinations.csv')
prolog = Prolog()
prolog.retractall("destination(_, _, _, _, _, _, _, _, _, _, _, _, _)")

for _,row in dest_df.iterrows():
    prolog.assertz(f"destination('{str(row['Destinations']).lower()}', '{str(row['country']).lower()}', '{str(row['region']).lower()}', '{str(row['Climate']).lower()}', '{str(row['Budget']).lower()}', '{str(row['Activity']).lower()}', '{str(row['Demographics']).lower()}', '{str(row['Duration']).lower()}', '{str(row['Cuisine']).lower()}', '{str(row['History']).lower()}', '{str(row['Natural Wonder']).lower()}', '{str(row['Accommodation']).lower()}', '{str(row['Language']).lower()}')")





################################################################################################

# TODO 2: extract unique features from the Destinations.csv and save them in a dictionary
for column_name in dest_df.columns:
    if column_name == 'Destinations':
        continue
    feature_set = set()
    feature_set.update({feature.lower() for feature in dest_df[column_name]})
    uniqe_features_dict[str(column_name).lower()] = feature_set
################################################################################################

if __name__ == "__main__":
    app = App()
    app.start()
