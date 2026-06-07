
import os
import patatmo as patatmo
import pandas as pd
import fiona
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
from netatmo_auth_app import OAuth2Token
import subprocess
from time import sleep
from patatmo.api.errors import ApiResponseError

class Stations:

    CHECKPOINT_FILE = 'checkpoint.txt'
    OUTPUT_CSV_FILE = 'output/List_Netatmo_stations.csv'
    def __init__(self):
        self.shapefile_path = ''
        self.status_message = 'Not fetching currently.'
        self.previous_execution = False
        self.check_for_previous_execution()
        self.create_output_folder()
        self.stop_sign = True
        self.date_range = None

    def add_date_range(self, start, end, freq):
        print(f"Date range received: start:{start}, end:{end}, freq:{freq}")

    def create_output_folder(self):
        if not os.path.exists("output/"):
            print("output dont exist")
            os.makedirs("output/")
            print("Output folder created.")
        else:
            print("Output folder already exists. No need to create anything.")

    def set_shapefile_path(self, path):
        self.shapefile_path = path
        print(f"Shapefile path set: {self.shapefile_path}")

    def start_fetching(self):
        if self.shapefile_path == '':
            self.status_message = 'Please choose a shapefile.'
            return self.status_message
        else:
            self.stop_sign = False
            self.status_message = 'Fetching stations in progress.'
            val = self.fetch_stations()
            print(f'Return value from the retrieval loop: {val}')
            return self.status_message

    def stop_fetching(self):
        self.status_message = 'Stopped fetching. Not fetching currently.'
        self.stop_sign = True
        return self.status_message

    def previous_execution_exists(self):
        return self.previous_execution

    def reset_checkpoint(self):
        cp_exists = os.path.exists(self.CHECKPOINT_FILE)
        if cp_exists:
            open(self.CHECKPOINT_FILE, 'w').close()
        output_csv_exists = os.path.exists(self.OUTPUT_CSV_FILE)
        if output_csv_exists:
            # This file needs to be deleted so the headers will go nicely.
            print('Deleting the output csv file.')
            os.remove(self.OUTPUT_CSV_FILE)

    def check_for_previous_execution(self):
        exists = os.path.exists(self.CHECKPOINT_FILE)
        if exists:
            f = open(self.CHECKPOINT_FILE)
            line1 = f.readline()
            f.close()
            if len(line1) == 0:
                print("New execution.")
                self.previous_execution = False
            else:
                print("Previous execution exists.")
                self.previous_execution = True
                # Read the shapefile path value here from the checkpoint and set
                # it to the class variable.
                with open(self.CHECKPOINT_FILE) as f:
                    shp_file = f.readlines()[2]
                    self.shapefile_path = shp_file
        if not exists:
            f = open(self.CHECKPOINT_FILE, 'x')
            f.close()
            print("New execution, creating checkpoint file.")
            self.previous_execution = False

    def fetch_stations(self):

        token = OAuth2Token.from_file()
        if token.expired:
            token.refresh()
        client = patatmo.api.client.NetatmoClient()
        client.authentication.tokens = {'access_token': token.access_token,
                                        'refresh_token': token.refresh_token}

        shp = gpd.read_file(self.shapefile_path)
        enwl = shp.dissolve()
        enwl = enwl.set_crs('epsg:4326')
        ## Define boundaries of the box in which data will be gathered.
        llon, llat, ulon, ulat = enwl.geometry.bounds.values.squeeze()
        ## The Netatmo API automaticly lowers the amount of stations one can access on large scales
        ## According to colleagues in Germany, moving windows, or tiles, of 0.2°*0.2° permit the acquisition of all stations
        lon_tiles = np.append(np.around(np.arange(llon, ulon, 0.2), decimals=2),
                              np.array(ulon))
        lat_tiles = np.append(np.around(np.arange(llat, ulat, 0.2), decimals=2),
                              np.array(ulat))
        list_all_stations = pd.DataFrame(
            columns=['Lon', 'Lat', 'ID', 'moduleID', 'index'])

        f = open(self.CHECKPOINT_FILE)
        line1 = f.readline()
        line2 = f.readline()
        f.close()

        if len(line1) == 0:
            print('No previous execution info. Starting from the beginning.')
            startx = 0
            starty = 0
        else:
            print('Starting from where the last execution stopped.')
            startx = int(line1)
            starty = int(line2)

        station_file_exists = os.path.isfile(self.OUTPUT_CSV_FILE)
        for x in range(startx, len(lon_tiles) - 1):
            print("X iteration.")
            for y in range(starty, len(lat_tiles) - 1):
                if self.stop_sign:
                    print("Stop sign received. Stopping.")
                    # Write checkpoint and quit.
                    with open(self.CHECKPOINT_FILE, "w") as f:
                        f.write(f"{x}\n")
                        f.write(f"{y}\n")
                        f.write(f"{self.shapefile_path}")
                    return 'Received stop sign.'
                starty = 0
                ### Create a georeferenced polygon of the tile.
                poly = Polygon(
                    zip([lon_tiles[x + 1], lon_tiles[x + 1], lon_tiles[x],
                         lon_tiles[x]],
                        [lat_tiles[y + 1], lat_tiles[y], lat_tiles[y],
                         lat_tiles[y + 1]]))
                p = gpd.GeoDataFrame(data=['tile'], geometry=[poly],
                                     crs=enwl.crs)
                ### Check if the tile overlays the UK borders, if not continue loop
                ### Avoids increasing unnecessarily the number of requests to Netatmo server
                if gpd.overlay(enwl, p, how='intersection').empty:
                    print('Tile not over land!')
                    continue

                region = {
                    "lat_ne": lat_tiles[y + 1],
                    "lat_sw": lat_tiles[y],
                    "lon_ne": lon_tiles[x + 1],
                    "lon_sw": lon_tiles[x],
                }

                try:
                    # issue the API request
                    output = client.Getpublicdata(region=region, filter=True)
                except ApiResponseError as e:
                    if "Service temporarily unavailable" in str(e):
                        print("Service unavailable exception, sleeping for 10s.")
                        sleep(10)
                        continue
                    else:
                        print("Unknown ApiResponseError: ", e)
                        print("Exception type/name: ", type(e).__name__)
                        list_all_stations.to_csv(self.OUTPUT_CSV_FILE,
                                                 mode='a',
                                                 header=not station_file_exists)
                        with open(self.CHECKPOINT_FILE, "w") as f:
                            f.write(f"{x}\n")
                            f.write(f"{y}\n")
                            f.write(f"{self.shapefile_path}")
                        return 'Exception caught, returning.'

                except Exception as e:
                    print("Unexpected exception caught: ", e)
                    print("----")
                    print("Exception type/name: ", type(e).__name__)
                    print("----")
                    list_all_stations.to_csv(self.OUTPUT_CSV_FILE,
                                             mode='a',
                                             header=not station_file_exists)

                    with open(self.CHECKPOINT_FILE, "w") as f:
                        f.write(f"{x}\n")
                        f.write(f"{y}\n")
                        f.write(f"{self.shapefile_path}")
                    return 'Exception caught, returning.'

                ### Acquiring the names and places of all stations available in the domain
                stations = output.response["body"]
                ### If there are no stations in the tile jump to the next loop step
                if len(stations) == 0:
                    print('No stations in this tile...')
                    # sleep(1)
                    continue

                df = pd.DataFrame(
                    columns=['Lon', 'Lat', 'ID', 'moduleID', 'index'])
                for i in range(0, len(stations)):
                    ### Check if the station records temperature:
                    list_var = []
                    for key, value in stations[i]["measures"].items():
                        if value.get('type') is None:
                            continue
                        [list_var.append(v) for v in value.get('type')]
                    if 'temperature' in list_var:
                        lon = stations[i]["place"]["location"][0]
                        lat = stations[i]["place"]["location"][1]
                        device = stations[i]["_id"]
                        module_id = tuple(stations[i]["measures"].keys())[0]
                        new = pd.DataFrame(
                            np.array([[lon, lat, device, module_id]]),
                            columns=['Lon', 'Lat', 'ID', 'moduleID'])

                        df.loc[i, :] = np.array(
                            [[lon, lat, device, module_id, i]])
                        ### For an obscure reason the gathering of data includes stations outside of the box
                        df_filt = df[(df['Lon'].astype(float) > lon_tiles[x]) &
                                     (df['Lon'].astype(float) < lon_tiles[
                                         x + 1]) &
                                     (df['Lat'].astype(float) > lat_tiles[y]) &
                                     (df['Lat'].astype(float) < lat_tiles[
                                         y + 1])].copy()
                    else:
                        print(
                            'There were stations, but not with temperature :3')
                print(df_filt)
                list_all_stations = pd.concat([list_all_stations, df_filt],
                                              ignore_index=True)
                print(list_all_stations.head(), list_all_stations.tail())
                del df_filt, df, p, poly
                sleep(1)

        list_all_stations.to_csv(self.OUTPUT_CSV_FILE,
                                 mode='a',
                                 header=not station_file_exists)
        return 'Finished downloading stations.'