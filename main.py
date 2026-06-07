import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk, messagebox
import stations
import threading
import netatmo_auth_app
from datetime import datetime


class MyGUI:

    CHECKPOINT_TEXT = '''
        A checkpoint for fetching stations from a shapefile in location: 
        D:/some/path is in memory. Continue that process by pressing "start"
         or begin a new fetching process by pressing "reset". The reset button 
         will also reset/destroy the output csv file of the last run.
        '''
    def __init__(self):
        self.root = tk.Tk()
        self.stations = stations.Stations()
        self.root.geometry("800x500")
        self.root.title("Netatmo app")
        self.start_entry = None
        self.end_entry = None
        self.freq_var = None
        self.freq_menu = None

        # Options frame.
        self.options_frame = tk.Frame(self.root,
                                      width= 100,
                                      height=500,
                                      bg='#c3c3c3')
        self.options_frame.pack(side=tk.LEFT)
        self.options_frame.pack_propagate(False)

        # Main frame.
        self.main_frame = tk.Frame(self.root,
                              highlightbackground="black",
                              highlightthickness=2)
        self.main_frame.configure(width= 700, height= 500)
        self.main_frame.pack(side=tk.LEFT)
        self.main_frame.pack_propagate(False)


        # Home page button.
        self.home_btn = tk.Button(self.options_frame,
                             text="Home",
                             fg="#158aff",
                             bd=0,
                             bg="#c3c3c3",
                             command=lambda: self.change_page(self.home_page))
        self.home_btn.place(x=10, y=50)
        self.home_indicate = tk.Label(self.options_frame, text='', bg='#c3c3c3')
        self.home_indicate.place(x=3, y=50, width=2, height=23)

        # Stations page button.
        self.stat_btn = tk.Button(self.options_frame,
                             text="Stations",
                             fg="#158aff",
                             bd=0,
                             bg="#c3c3c3",
                             command=lambda: self.change_page(self.stations_page))
        self.stat_btn.place(x=10, y=100)
        self.stat_indicate = tk.Label(self.options_frame, text='', bg='#c3c3c3')
        self.stat_indicate.place(x=3, y=100, width=2, height=23)

        # Temperatures page button.
        self.temp_btn = tk.Button(self.options_frame,
                             text="Temperatures",
                             fg="#158aff",
                             bd=0,
                             bg="#c3c3c3",
                             command=lambda: self.change_page(self.temperatures_page))
        self.temp_btn.place(x=10, y=150)
        self.temp_indicate = tk.Label(self.options_frame, text='', bg='#c3c3c3')
        self.temp_indicate.place(x=3, y=150, width=2, height=23)

        self.server_thread = threading.Thread(target=netatmo_auth_app.app.run)
        self.server_thread.daemon = True
        self.server_thread.start()
        print("Authentication application started.")

        self.root.mainloop()

    def select_file(self):
        filetypes = (
            ('Shapefiles', '*.shp'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename(title='Wtf is this title',
                                      initialdir='/',
                                      filetypes=filetypes)
        return filename

    def hide_indicators(self):
        self.home_indicate.config(bg='#c3c3c3')
        self.stat_indicate.config(bg='#c3c3c3')
        self.temp_indicate.config(bg='#c3c3c3')

    def indicate(self, lb):
        self.hide_indicators()
        lb.config(bg='#158aff')

    def clear_frame(self, frame):
        for widgets in frame.winfo_children():
            widgets.destroy()

    def delete_pages(self):
        for frame in self.main_frame.winfo_children():
            frame.destroy()

    def change_page(self, page):
        self.delete_pages()
        page()

    def home_page(self):
        self.indicate(self.home_indicate)
        home_frame = tk.Frame(self.main_frame)
        label = tk.Label(home_frame, text="Home page")
        label.pack()
        home_frame.pack()

    def stations_page(self):
        self.indicate(self.stat_indicate)
        stations_frame = tk.Frame(self.main_frame)
        stations_frame.pack()
        title_frame = tk.Frame(stations_frame)
        title_frame.pack(pady=20)
        status_frame = tk.Frame(stations_frame,
                                width=550,
                                height=60,
                                highlightbackground="black",
                                highlightthickness=1)
        status_frame.pack()
        status_frame.pack_propagate(False)
        button_frame = tk.Frame(stations_frame,
                                pady=20)
        button_frame.pack()
        label = tk.Label(title_frame, text="Stations page")
        label.pack()



        #Date selector to the top of the button frame.
        date_frame = ttk.Frame(button_frame)
        date_frame.pack()
        ttk.Label(date_frame,
                  text="Select date range",
                  font=("Helvetica", 10, "bold")).grid(row=0,
                                                       column=0,
                                                       columnspan=3,
                                                       pady=(0, 10))
        ttk.Label(date_frame, text="Start date").grid(row=1,
                                                      column=0,
                                                      sticky="w")
        ttk.Label(date_frame, text="(MM-DD-YYYY)").grid(row=2,
                                                        column=0,
                                                        sticky="w")
        self.start_entry = ttk.Entry(date_frame, width=28)
        self.start_entry.insert(0, "01-01-2015")
        self.start_entry.grid(row=1, column=1, padx=10)

        ttk.Label(date_frame, text="End date").grid(row=3,
                                                    column= 0,
                                                    sticky="w")
        ttk.Label(date_frame, text="(MM-DD-YYYY)").grid(row=4,
                                                        column=0,
                                                        sticky="w")
        self.end_entry = ttk.Entry(date_frame, width=28)
        self.end_entry.insert(0, "12-31-2023")
        self.end_entry.grid(row=3, column=1, padx=10, pady=(10, 0))

        #Frequency to the date selector.
        ttk.Label(date_frame, text="Frequency").grid(row=5,
                                                     column=0,
                                                     sticky="w",
                                                     pady=(10, 0))
        self.freq_var = tk.StringVar(value="1h")
        freq_options = ["1h", "30min", "15min", "1D", "1W", "1ME"]
        self.freq_menu = ttk.Combobox(date_frame,
                                 textvariable=self.freq_var,
                                 values=freq_options,
                                 width=10)
        self.freq_menu.grid(row=5, column=1, sticky="w", padx=10, pady=(10, 0))
        ttk.Button(date_frame, text="Add date range",
                   command=self.add_date_range).grid(row=6,
                                                     column=0,
                                                     columnspan=2,
                                                     pady=20)


        # Buttons.
        file_btn = tk.Button(button_frame,
                             text="Select a shapefile",
                             height=2,
                             padx=8,
                             command=lambda: self.stations_file_button(status_frame))
        file_btn.pack(side=tk.LEFT, padx=3)

        start_fetching_btn = tk.Button(button_frame,
                                       text="Start fetching stations",
                                       height=2,
                                       padx=8,
                                       command=lambda: self.stations_start_button(status_frame))
        start_fetching_btn.pack(side=tk.LEFT, padx=3)

        stop_fetching_btn = tk.Button(button_frame,
                                       text="Stop fetching stations",
                                      height=2,
                                      padx=8,
                                       command=lambda: self.stations_stop_button(status_frame))
        stop_fetching_btn.pack(side=tk.LEFT, padx=3)

        if self.stations.previous_execution_exists():
            previous_info_frame = tk.Frame(stations_frame)
            previous_info_frame.pack()
            previous_label = tk.Label(previous_info_frame,
                                      text=self.CHECKPOINT_TEXT)
            previous_label.pack(pady=10)
            reset_btn = tk.Button(previous_info_frame,
                                  text="Reset",
                                  command=lambda: self.stations_reset_button(previous_info_frame))
            reset_btn.pack()

    def add_date_range(self):
        fmt = "%m-%d-%Y"
        try:
            start = datetime.strptime(self.start_entry.get().strip(), fmt)
            end = datetime.strptime(self.end_entry.get().strip(), fmt)
        except ValueError:
            messagebox.showerror(
                "Invalid format",
                "Use MM-DD-YYYY\nExample: 01-01-2015"
            )
            return
        if start >= end:
            messagebox.showerror("Invalid range", "Start date must be before end date.")
            return

        self.stations.add_date_range(start, end, self.freq_var.get())

    def stations_reset_button(self, frame):
        self.stations.reset_checkpoint()
        self.clear_frame(frame)

    def stations_stop_button(self, status_frame):
        self.clear_frame(status_frame)
        stop_message = self.stations.stop_fetching()
        label = tk.Label(status_frame, text=stop_message)
        label.pack()

    def stations_start_fetch(self, status_frame):
        message = self.stations.start_fetching()
        label = tk.Label(status_frame, text=message)
        label.pack()

    def stations_start_button(self, status_frame):
        self.clear_frame(status_frame)
        thread = threading.Thread(target=lambda: self.stations_start_fetch(status_frame),
                                  daemon=True)
        thread.start()

    def stations_file_button(self, status_frame):
        self.clear_frame(status_frame)
        filename = self.select_file()
        self.stations.set_shapefile_path(filename)
        label = tk.Label(status_frame, text=f"Selected file path: {filename}")
        label.pack()

    def stations_previous_execution(self):
        exists = self.stations.previous_execution_exists()
        if exists:
            return True
        else:
            False

    def temperatures_page(self):
        self.indicate(self.temp_indicate)
        temperatures_frame = tk.Frame(self.main_frame)
        label = tk.Label(temperatures_frame, text="Temperatures page")
        label.pack()
        temperatures_frame.pack()

    def start_button(self):
        result = self.stations.start_fetching()
        self.statuslabel.config(text=result)

    def stop_button(self):
        result = self.stations.stop_fetching()
        self.statuslabel.config(text=result)

MyGUI()

