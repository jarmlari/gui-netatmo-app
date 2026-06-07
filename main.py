import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk, messagebox
import stations
import threading
import netatmo_auth_app
from datetime import datetime


class MyGUI:


    def __init__(self):
        self.root = tk.Tk()
        self.stations = stations.Stations()
        self.root.geometry("800x500")
        self.root.title("Netatmo app")
        self.temp_start = None
        self.temp_end = None
        self.temp_freq_var = None
        self.freq_menu = None
        self.CHECKPOINT_TEXT = f'''
                A checkpoint for fetching stations from a shapefile in location: 
                {self.stations.shapefile_path} is in memory. Continue that process by 
                pressing "start" or begin a new fetching process by pressing 
                "reset". The reset button will also reset/destroy the output csv
                file of the last run.
                '''

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

        self.status_frame = None
        self.previous_info_frame = None

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
        self.status_frame = tk.Frame(stations_frame,
                                width=550,
                                height=60,
                                highlightbackground="black",
                                highlightthickness=1)
        self.status_frame.pack()
        self.status_frame.pack_propagate(False)
        if self.stations.is_currently_executing():
            ttk.Label(self.status_frame, text="Downloading in progress...").pack()
        else:
            ttk.Label(self.status_frame, text='Not currently downloading.').pack()

        button_frame = tk.Frame(stations_frame,
                                pady=20)
        button_frame.pack()
        label = ttk.Label(title_frame,
                          text="Download netatmo stations",
                          font=("DM Sans", 10, "bold"))
        label.pack()

        # Buttons.
        file_btn = ttk.Button(button_frame,
                             text="Select a shapefile",
                             command=self.stations_file_button)
        file_btn.pack(side=tk.LEFT, padx=3)

        start_fetching_btn = ttk.Button(button_frame,
                                       text="Start fetching stations",
                                       command=self.stations_start_button)
        start_fetching_btn.pack(side=tk.LEFT, padx=3)

        stop_fetching_btn = ttk.Button(button_frame,
                                       text="Stop fetching stations",
                                       command=self.stations_stop_button)
        stop_fetching_btn.pack(side=tk.LEFT, padx=3)

        if self.stations.previous_execution_exists():
            self.previous_info_frame = tk.Frame(stations_frame)
            self.previous_info_frame.pack()
            previous_label = tk.Label(self.previous_info_frame,
                                      text=self.CHECKPOINT_TEXT)
            previous_label.pack(pady=10)
            reset_btn = ttk.Button(self.previous_info_frame,
                                  text="Reset",
                                  command=lambda: self.stations_reset_button(self.previous_info_frame))
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

    def stations_stop_button(self):
        self.clear_frame(self.status_frame)
        stop_message = self.stations.stop_fetching()
        label = tk.Label(self.status_frame, text=stop_message)
        label.pack()

    def stations_start_fetch(self):
        message = self.stations.start_fetching()
        self.clear_frame(self.status_frame)
        label = tk.Label(self.status_frame, text=message)
        label.pack()

    def stations_start_button(self):
        if self.previous_info_frame is not None:
            self.clear_frame(self.previous_info_frame)
        self.clear_frame(self.status_frame)
        # Allow only one press of start. If already downloading dont do anything.
        if self.stations.is_currently_executing():
            print("Not accepting start if we are already downloading.")
            ttk.Label(self.status_frame, text="Downloading already in progress.").pack()
        else:
            ttk.Label(self.status_frame, text="Downloading in progress...").pack()
            thread = threading.Thread(target=lambda: self.stations_start_fetch(),
                                      daemon=True)
            thread.start()

    def stations_file_button(self):
        self.clear_frame(self.status_frame)
        filename = self.select_file()
        self.stations.set_shapefile_path(filename)
        label = tk.Label(self.status_frame, text=f"Selected file path: {filename}")
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

