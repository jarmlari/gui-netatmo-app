
import json
import os
import pandas as pd
import patatmo as patatmo
import datetime
import threading
from netatmo_auth_app import OAuth2Token
from time import sleep

class Temperatures:

    CHECKPOINT_FILE = 'temperatures_checkpoint.txt'
    OUTPUT_FILE_START = 'netatmo_output_'
    def __init__(self):
        self.output_folder = None
        self.output_filename = None
        self.date_input = None
        self.date_range = None
        self.stationsfile_path = ''
        self.previous_execution = False
        self.check_for_previous_execution()
        self.create_output_folder()
        self.status_callback = None
        self.stop_event = threading.Event()
        # set() when not downloading. clear() when we want to download.
        # set() == True, clear() == False
        self.stop_event.set()

    def set_status_callback(self, callback):
        self.status_callback = callback

    def update_status(self, message):
        if self.status_callback:
            self.status_callback(message)

    def check_for_previous_execution(self):
        exists = os.path.exists(self.CHECKPOINT_FILE)
        if exists:
            print("Checkpoint already exists.")
            # Set the class variables here from the checkpoint file.
            f = open(self.CHECKPOINT_FILE)
            line1 = f.readline()
            f.close()
            if len(line1) == 0:
                # This is the execution where a previous info doesn't exist?
                print("New execution. Wtf and why are we here?")
                self.previous_execution = False
                # Should we call the reset function?
            else:
                # Execution where info about last execution exists.
                self.previous_execution = True
                with open(self.CHECKPOINT_FILE) as f:
                    lines = f.readlines()
                    self.stationsfile_path = lines[4].strip()
                    start, end, freq = lines[5].split("_")
                    self.date_input = f"{start}_{end}_{freq}".strip()
                    self.date_range = pd.date_range(start=start, end=end, freq=freq)
                    # Read and save the output folder name.
                    self.output_folder = lines[6].strip()
        else:
            # This is the very very first execution where the file is created?
            print("The checkpoint DOESNT yet exist.")
            f = open(self.CHECKPOINT_FILE, 'x')
            f.close()

    def previous_execution_exists(self):
        return self.previous_execution

    def is_currently_executing(self):
        return not self.stop_event.is_set()

    def reset_checkpoint(self):
        print("Temperature reset_checkpoint function goings.")
        cp_exists = os.path.exists(self.CHECKPOINT_FILE)
        if cp_exists:
            open(self.CHECKPOINT_FILE, 'w').close()
            self.stationsfile_path = ''
            self.date_range = None
            self.output_filename = None
            self.output_folder = None
            self.previous_execution = False

    def add_date_range(self, start, end, freq):
        print(f"start: {start}")
        print(f"end: {end}")
        print(f"freq: {freq}")
        self.date_input = f"{start}_{end}_{freq}"
        self.date_range = pd.date_range(start=start, end=end, freq=freq)
        print(f"Date range saved: {self.date_range}")

    def create_output_folder(self):
        if not os.path.exists("output/temperatures/"):
            print("Temperatures output folder dont exist")
            os.makedirs("output/temperatures/")
            print("Output folder created.")
        else:
            print("Temperature output folder already exists. No need to create anything.")

    def set_stationsfile_path(self, path):
        self.stationsfile_path = path
        print(f"Stations file path set: {self.stationsfile_path}")

    def get_stationsfile_path(self):
        return self.stationsfile_path

    def get_date_range(self):
        return self.date_range

    def start_fetch(self):
        print("Temperatures start fetch.")
        if self.stationsfile_path == '':
            return 'Please choose a csv file for the Netatmo stations.'
        elif self.date_range is None:
            return 'Please set a date range.'
        else:
            # Create an output folder with the current date and time in the name if this is a new execution?
            if not self.previous_execution_exists():
                time = datetime.datetime.now()
                time = time.strftime("%Y-%m-%d %H:%M:%S")
                time = time.replace(' ', '_')
                date = time.replace(':', '-')
                print(f"Date in start fetch temp: {date}")
                os.makedirs(f"output/temperatures/temperatures_output_{date}/")
                # OUTPUT_FOLDER = 'output/temperatures/'
                self.output_folder = f'output/temperatures/temperatures_output_{date}/'
            self.stop_event.clear()
            val = self.fetch_temp()
            return val

    def stop_fetch(self):
        self.previous_execution = True
        self.stop_event.set()

    def wait_with_countdown(self, seconds):
        for remaining in range(seconds, 0, -1):
            if self.stop_event.wait(timeout=1):
                return False
            self.update_status(f"Request limit reached. Sleeping for a while and then trying again...")
        return True

    def write_progress(self, yr, mon, df, y, x):
        filename = self.OUTPUT_FILE_START + str(yr) + '-{0:02d}'.format(mon) + '.csv'
        self.output_filename = filename
        # Check if file for this month in this year exists in the current output folder.
        month_file_exists = os.path.isfile(self.output_folder + filename)
        # Write the progress to this month's output file.
        df.to_csv(self.output_folder + filename,
                             mode="a",
                             header=not month_file_exists)
        # Write everything necessary to the checkpoint file.
        with open(self.CHECKPOINT_FILE, 'w') as f:
            f.write(f"{yr}\n")
            f.write(f"{mon}\n")
            f.write(f"{y}\n")
            f.write(f"{x}\n")
            f.write(f"{self.stationsfile_path}\n")
            f.write(f"{self.date_input}\n")
            f.write(f"{self.output_folder}")
        return df

    def fetch_temp(self):
        list_stations = pd.read_csv(self.stationsfile_path)
        token = OAuth2Token.from_file()
        client = patatmo.api.client.NetatmoClient()
        client.authentication.tokens = {'access_token': token.access_token,
                                        'refresh_token': token.refresh_token}
        epoch = datetime.datetime.fromtimestamp(0).replace(
            tzinfo=datetime.timezone.utc)

        def unix_time_millis(dt):
            return (dt - epoch).total_seconds()

        counter = 0
        years = list(dict.fromkeys(self.date_range.year))
        months = list(dict.fromkeys(self.date_range.month))

        # Read from the checkpoint file where the last execution stopped (year, month, y and x).
        f = open(self.CHECKPOINT_FILE)
        yearcp = f.readline()
        yearcp = yearcp[0:4]
        monthcp = f.readline()
        monthcp = monthcp.rstrip('\n')
        ycp = f.readline()
        xcp = f.readline()
        f.close()

        # Set loop variables based on the checkpoint file so we can continue from where the last execution left off.
        if len(yearcp) == 0:
            # No previous execution, starting from the beginning.
            startyear = years[0]
            startmonth = months[0]
            starty = 0
            startx = 0
        else:
            # Start where the previous execution left off.
            yearidx = years.index(int(yearcp))
            years = years[yearidx:]
            monthidx = months.index(int(monthcp))
            months = months[monthidx:]
            starty = int(ycp)
            startx = int(xcp)

        monthsfirstrun = True
        firstrun = True

        print(f"The length of stations: {len(list_stations)}")
        for yr in years:
            # Return months list to the full version if not first iteration.
            if not monthsfirstrun:
                months = list(dict.fromkeys(self.date_range.month))
            print(f"Months: {months}")
            for mon in months:
                monthsfirstrun = False
                if mon == 12:
                    follow_mon = 1
                    follow_yr = yr + 1
                else:
                    follow_mon = mon + 1
                    follow_yr = yr
                startDate_dt = datetime.datetime(yr, mon, 1, 0, 0, 0, 0,
                                                 tzinfo=datetime.timezone.utc)
                endDate_dt = datetime.datetime(follow_yr, follow_mon, 1, 0, 0,
                                               0, 0,
                                               tzinfo=datetime.timezone.utc)
                startDate = str(int(unix_time_millis(startDate_dt)))
                endDate = str(int(unix_time_millis(endDate_dt)))

                step = 200
                for y in range(starty, len(list_stations), step):
                    starty = 0
                    dfNetatmo = pd.DataFrame()
                    if not firstrun:
                        startx = y
                    # Goes through 0-200, 200-399, 400-599...
                    for x in range(startx, y + step):
                        firstrun = False
                        errorcount = 0
                        if x == len(list_stations):
                            break
                        # Handle user input stop.
                        if self.stop_event.is_set():
                            self.write_progress(yr, mon, dfNetatmo, y, x)
                            return 'Downloading stopped.'
                        while True:
                            try:
                                print("Start while loop.")
                                sleep(1)
                                lat = list_stations.iloc[x]["Lat"]
                                lon = list_stations.iloc[x]["Lon"]
                                device_id = list_stations.iloc[x]["ID"]
                                module_id = list_stations.iloc[x]["moduleID"]
                                index = x

                                response = client.Getmeasure(device_id=device_id,
                                                             module_id=module_id,
                                                             type=['Temperature'],
                                                             scale='1hour',
                                                             date_begin=startDate,
                                                             date_end=endDate)
                                while response is None:
                                    print('waiting for payload')  # sometimes the request to Netatmo servers fails on first attempt
                                    sleep(1)
                                print(f"calls made: {counter}")
                                print(f"x: {x}, year: {yr}, month: {mon}")
                                counter = counter + 1
                                payload = response.dataframe()
                                payload['ID'] = device_id
                                payload['index'] = index
                                payload['Lat'] = lat
                                payload['Lon'] = lon
                                dfNetatmo = pd.concat((dfNetatmo, payload))

                                break

                            # Bad json for some reason.
                            except json.JSONDecodeError as e:
                                print(f"Empty/bad response: {e}")

                            # API limit reached.
                            except patatmo.api.errors.ApiResponseError as e:
                                print(repr(e))
                                if "API limit exceeded" in str(e):
                                    print("Going to sleep.")
                                    completed = self.wait_with_countdown(1000)
                                    if not completed:
                                        self.update_status("Download stopped.")
                                        # Save progress if stop is called while sleeping.
                                        self.write_progress(yr, mon, dfNetatmo, y, x)
                                        return 'Downloading stopped'

                                    # Could we just do the continue here either way?
                                    continue
                                elif "Access token expired" in str(e):
                                    print("Expired token, trying to refresh.")
                                    # Refresh and set a new token to the client object.
                                    if token.expired:
                                        token.refresh()
                                        newtoken = OAuth2Token.from_file()
                                        client.authentication.tokens = {
                                            'access_token': newtoken.access_token,
                                            'refresh_token': newtoken.refresh_token
                                        }
                                        sleep(5)
                                    continue
                                elif "Invalid access token" in str(e):
                                    print("Invalid access token error caught.")
                                    continue
                                else:
                                    break

                            # Unknown error.
                            except BaseException as e:
                                print("Base exception.")
                                print(type(e).__name__)
                                print('The temporary dataframe contains ' + str(
                                    len(dfNetatmo)) + ' measurements')
                                self.write_progress(yr, mon, dfNetatmo, y, x)
                                return "Unknown exception."

                    # Write the downloaded data to the monthly output file on every y-iteration.
                    print('The temporary dataframe contains ' + str(len(dfNetatmo)) + ' measurements')
                    filename = self.OUTPUT_FILE_START + str(yr) + '-{0:02d}'.format(mon) + '.csv'
                    self.output_filename = filename
                    month_file_exists = os.path.isfile(self.output_folder + filename)
                    dfNetatmo.to_csv(self.output_folder + filename, mode="a", header=not month_file_exists)
