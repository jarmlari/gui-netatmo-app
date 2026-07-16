import tkinter as tk
import customtkinter as ctk
import stations
import threading
import netatmo_auth_app
import os
import sys
import subprocess
from tkinter import filedialog as fd
from tkinter import ttk, messagebox
from datetime import datetime

import temperatures


class MyGUI:


    def __init__(self):
        ctk.set_appearance_mode('system')
        #ctk.set_default_color_theme()
        self.root = ctk.CTk()
        self.stations = stations.Stations()
        self.temperatures = temperatures.Temperatures()
        self.root.geometry("900x500")
        self.root.title("Netatmo app")
        self.temp_start_entry = None
        self.temp_end_entry = None
        self.temp_freq_var = None
        self.freq_menu = None
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.stat_output_folder = os.path.join(base_dir, "output/stations/")
        self.temp_output_folder = os.path.join(base_dir, "output/temperatures/")
        self.CHECKPOINT_TEXT = f'''
                A checkpoint for fetching stations from a shapefile in location: 
                {self.stations.get_shapefile_path()} is in memory. Continue that process by 
                pressing "start" or begin a new fetching process by pressing 
                "reset". The reset button will also reset/destroy the output csv
                file of the last run.
                '''
        self.temperatures.set_status_callback(self.temp_status_update)

        # Options frame.
        self.options_frame = ctk.CTkFrame(master=self.root, width= 150,
                                          border_width=1, border_color='black')
        self.options_frame.pack(side='left', fill='y', pady=5, padx=5)
        self.frame_colour = self.options_frame.cget('fg_color')

        # Main frame.
        self.main_frame = ctk.CTkFrame(master=self.root, fg_color=self.root.cget('fg_color'))
        self.main_frame.pack(side='left', fill='both', expand=True, pady=5, padx=5)

        # Home page button.
        self.home_btn = ctk.CTkButton(self.options_frame, text="Home & Instructions",
                                      text_color='black', font=('Bold', 14),
                                      width=70, hover=False, fg_color=self.frame_colour,
                                      command=lambda: self.change_page(self.home_page))
        self.home_btn.place(x=10, y=50)
        self.home_indicate = ctk.CTkLabel(self.options_frame, text='', width=5,
                                          height=33, fg_color=self.frame_colour)
        self.home_indicate.place(x=3, y=50)

        # Stations page button.
        self.stat_btn = ctk.CTkButton(self.options_frame, text="Stations",
                                      text_color='black', font=('Bold', 14),
                                      width=70, hover=False, fg_color=self.frame_colour,
                                      command=lambda: self.change_page(self.stations_page))
        self.stat_btn.place(x=10, y=100)
        self.stat_indicate = ctk.CTkLabel(self.options_frame, text='', width=5,
                                          height=33, fg_color=self.frame_colour)
        self.stat_indicate.place(x=3, y=100)

        # Temperatures page button.
        self.temp_btn = ctk.CTkButton(self.options_frame, text="Temperatures",
                                      text_color='black', font=('Bold', 14),
                                      width=70, hover=False, fg_color=self.frame_colour,
                                      command=lambda: self.change_page(self.temperatures_page))
        self.temp_btn.place(x=10, y=150)
        self.temp_indicate = ctk.CTkLabel(self.options_frame, text='', width=5,
                                          height=33, fg_color=self.frame_colour)
        self.temp_indicate.place(x=3, y=150)

        self.status_frame = None
        self.stat_status_label = None
        self.previous_info_frame = None
        self.temp_status_frame = None
        self.temp_status_label = None
        self.temp_button_frame = None

        self.server_thread = threading.Thread(target=netatmo_auth_app.app.run)
        self.server_thread.daemon = True
        self.server_thread.start()
        print("Authentication application started.")

        self.home_page()
        self.root.mainloop()

    def temp_status_update(self, msg):
        if self.temp_status_label is not None and self.temp_status_label.winfo_exists():
            self.root.after(0, lambda: self.temp_status_label.configure(text=msg))

    def select_shapefile(self):
        filetypes = (
            ('Shapefiles', '*.shp'),
            ('All files', '*.*')
        )
        filename = fd.askopenfilename(title='Select a shapefile',
                                      initialdir='/',
                                      filetypes=filetypes)
        return filename

    def select_stations_file(self):
        filetypes = (
            ('csv', '*.csv'),
            ('All files', '*.*')
        )
        filename = fd.askopenfilename(title='Select csv file',
                                      initialdir='/',
                                      filetypes=filetypes)
        return filename

    def hide_indicators(self):
        self.home_indicate.configure(fg_color=self.frame_colour)
        self.stat_indicate.configure(fg_color=self.frame_colour)
        self.temp_indicate.configure(fg_color=self.frame_colour)
        pass

    def indicate(self, lb):
        self.hide_indicators()
        lb.configure(fg_color='#158aff')
        pass

    def clear_frame(self, frame):
        print("Executing clear_frame().")
        if frame is None:
            return
        for widgets in frame.winfo_children():
            widgets.destroy()

    def delete_pages(self):
        for frame in self.main_frame.winfo_children():
            frame.destroy()
        self.temp_status_label = None

    def change_page(self, page):
        self.delete_pages()
        page()

    def home_page(self):
        self.indicate(self.home_indicate)
        home_frame = ctk.CTkFrame(self.main_frame)
        label = ctk.CTkLabel(home_frame, text="Home page")
        label.place(x=15, y=15)
        home_frame.pack()

    def stations_page(self):
        self.indicate(self.stat_indicate)
        # Frame for the whole page.
        stations_frame = ctk.CTkFrame(self.main_frame, fg_color=self.root.cget('fg_color'))
        stations_frame.pack(fill="both", expand=True)

        # Button to open the output folder.
        output_frame = ctk.CTkFrame(stations_frame,
                                    fg_color=self.root.cget('fg_color'))
        output_frame.pack(side="bottom", fill="x", padx=5, pady=10)
        output_folder_btn = ctk.CTkButton(output_frame,
                                          text="Open output folder",
                                          command=lambda: self.open_output_folder(self.stat_output_folder),
                                          fg_color="transparent",
                                          border_width=1,
                                          border_color="#1f6aa5",
                                          text_color=("#1f6aa5", "gray90"),
                                          hover_color=("gray85", "gray25"),
                                          width=160,
                                          height=28,
                                          font=("DM Sans", 12),
                                          corner_radius=6)
        output_folder_btn.pack(side="right", padx=5)

        # Page title.
        title_frame = ctk.CTkFrame(stations_frame, fg_color=self.root.cget('fg_color'))
        title_frame.pack(pady=10)
        label = ctk.CTkLabel(title_frame,
                          text="Download netatmo stations",
                          font=("DM Sans", 14, "bold"))
        label.pack()

        # Program status info frame and header for it.
        status_container = ctk.CTkFrame(stations_frame, fg_color=self.root.cget('fg_color'))
        status_container.pack(pady=10)
        status_frame_desc = ctk.CTkLabel(
            status_container,
            text="Program status:",
            font=ctk.CTkFont(size=11)
        )
        status_frame_desc.pack(anchor="w", padx=10, pady=(0, 0))
        self.status_frame = ctk.CTkFrame(status_container, border_width=1,
                                         border_color='gray', width=550, height=60)
        self.status_frame.pack(pady=(0, 0))
        self.status_frame.pack_propagate(False)

        # Set stations download status info.
        self.stat_status_label = ctk.CTkLabel(self.status_frame, text="")
        if self.stations.is_currently_executing():
            self.stat_status_label.configure(text="Downloading in progress...")
            self.stat_status_label.pack(expand=True)
        else:
            self.stat_status_label.configure(text='Not currently downloading.')
            self.stat_status_label.pack(expand=True)

        # Buttons.
        button_frame = ctk.CTkFrame(stations_frame, fg_color=self.root.cget('fg_color'))
        button_frame.pack(padx=5, pady=15)

        file_btn = ctk.CTkButton(button_frame,
                             text="Select a shapefile",
                             command=self.stations_file_button,
                                 fg_color=("gray75", "gray30"),
                                 text_color=("gray10", "gray90"),
                                 hover_color=("gray65", "gray40"))
        file_btn.pack(side='left', padx=3)

        start_fetching_btn = ctk.CTkButton(button_frame,
                                       text="Start fetching stations",
                                       command=self.stations_start_button)
        start_fetching_btn.pack(side='left', padx=3)

        stop_fetching_btn = ctk.CTkButton(button_frame,
                                       text="Stop fetching stations",
                                       command=self.stations_stop_button)
        stop_fetching_btn.pack(side='left', padx=3)



        # Functionality to info and reset about last execution/download.
        if self.stations.previous_execution_exists():
            self.previous_info_frame = ctk.CTkFrame(stations_frame,
                                                    fg_color=self.root.cget('fg_color'))
            self.previous_info_frame.pack()
            previous_label = ctk.CTkLabel(self.previous_info_frame,
                                      text=f'''
                A checkpoint for fetching stations from a shapefile in location: 
                {self.stations.get_shapefile_path()} is in memory. Continue that process by 
                pressing "start" or begin a new fetching process by pressing 
                "reset". The reset button will also reset/destroy the output csv
                file of the last run.
                ''')
            previous_label.pack(pady=10)
            reset_btn = ctk.CTkButton(self.previous_info_frame,
                                  text="Reset",
                                  command=lambda: self.stations_reset_button(self.previous_info_frame))
            reset_btn.pack()

    def open_output_folder(self, folder):
        if not os.path.exists(folder):
            print("Output folder not found")
            return
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def add_date_range(self):
        fmt = "%m-%d-%Y"
        try:
            start = datetime.strptime(self.temp_start_entry.get().strip(), fmt)
            end = datetime.strptime(self.temp_end_entry.get().strip(), fmt)
        except ValueError:
            messagebox.showerror(
                "Invalid format",
                "Use MM-DD-YYYY\nExample: 01-01-2015"
            )
            return
        if start >= end:
            messagebox.showerror("Invalid range", "Start date must be before end date.")
            return

        self.temperatures.add_date_range(start, end, self.temp_freq_var.get())

    def stations_reset_button(self, frame):
        self.stations.destroy_output_file()
        self.stations.reset_checkpoint()
        self.clear_frame(frame)
        self.previous_info_frame = None

    def stations_stop_button(self):
        if self.stations.is_currently_executing():
            self.stat_status_label.configure(text="Stopping, please wait.")
            stop_message = self.stations.stop_fetching()
            self.stat_status_label.configure(text=stop_message)
            self.change_page(self.stations_page)
        else:
            self.stat_status_label.configure(text="Downloading currently not in "
                                                  "progress, nothing to stop.")

    def stations_start_fetch(self):
        message = self.stations.start_fetching()
        self.stat_status_label.configure(text=message)

    def stations_start_button(self):
        if self.previous_info_frame is not None:
            print("Clearing previous execution info frame.")
            self.clear_frame(self.previous_info_frame)
            self.previous_info_frame = None
        self.stat_status_label.configure(text="")
        # Allow only one press of start. If already downloading don't do anything.
        if self.stations.is_currently_executing():
            print("Not accepting start if we are already downloading.")
            self.stat_status_label.configure(text="Downloading already in progress.")
        else:
            self.stat_status_label.configure(text="Downloading in progress...")
            thread = threading.Thread(target=lambda: self.stations_start_fetch(),
                                      daemon=True)
            thread.start()

    def stations_file_button(self):
        filename = self.select_shapefile()
        self.stations.set_shapefile_path(filename)
        self.stat_status_label.configure(text=f"Selected file path: {filename}")

    def temperatures_file_button(self):
        print("Selecting temperatures file.")
        filename = self.select_stations_file()
        self.temperatures.set_stationsfile_path(filename)
        self.temp_status_label.configure(text=f"Selected csv file path: {filename}")

    def stations_previous_execution(self):
        exists = self.stations.previous_execution_exists()
        if exists:
            return True
        else:
            False

    def temperatures_page(self):
        self.indicate(self.temp_indicate)

        # Frame for the whole page.
        temperatures_frame = ctk.CTkFrame(self.main_frame, fg_color=self.root.cget('fg_color'))
        temperatures_frame.pack(fill="both", expand=True)

        # Button to open the output folder.
        output_frame = ctk.CTkFrame(temperatures_frame,
                                    fg_color=self.root.cget('fg_color'))
        output_frame.pack(side="bottom", anchor="se", padx=5, pady=(0, 10)) # pady=(above, under)
        output_folder_btn = ctk.CTkButton(output_frame,
                                          text="Open output folder",
                                          command=lambda: self.open_output_folder(self.temp_output_folder),
                                          fg_color="transparent",
                                          border_width=1,
                                          border_color="#1f6aa5",
                                          text_color=("#1f6aa5", "gray90"),
                                          hover_color=("gray85", "gray25"),
                                          width=160,
                                          height=28,
                                          font=("DM Sans", 12),
                                          corner_radius=6)
        output_folder_btn.pack(side="right", padx=5)

        # Page title.
        title_frame = ctk.CTkFrame(temperatures_frame, fg_color=self.root.cget('fg_color'))
        title_frame.pack(pady=10)
        label = ctk.CTkLabel(title_frame,
                             text="Download temperatures from netatmo stations",
                             font=("DM Sans", 14, "bold"))
        label.pack()

        # Program status info frame and header for it.
        status_container = ctk.CTkFrame(temperatures_frame,
                                        fg_color=self.root.cget('fg_color'))
        status_container.pack(pady=5)
        status_frame_desc = ctk.CTkLabel(
            status_container,
            text="Program status:",
            font=ctk.CTkFont(size=11)
        )
        status_frame_desc.pack(anchor="w", padx=10, pady=(0, 0))
        self.temp_status_frame = ctk.CTkFrame(status_container, border_width=1,
                                         border_color='gray', width=550, height=60)
        self.temp_status_frame.pack(pady=(0, 0))
        self.temp_status_frame.pack_propagate(False)

        # Set temperature download status info.
        self.temp_status_label = ctk.CTkLabel(self.temp_status_frame, text="Download temperatures")
        self.temp_status_label.pack(expand=True)

        # Buttons.
        self.temp_button_frame = ctk.CTkFrame(temperatures_frame,
                                              fg_color=self.root.cget('fg_color'))
        self.temp_button_frame.pack(fill="both", expand=True, padx=(5, 15), pady=(0, 5))

        # Is currently executing?
        if self.temperatures.is_currently_executing():
            self.temp_status_label.configure(text="Downloading in progress...")
            # If there is a live download then we need to show the stop button view.
            self.temp_stop_view()
        elif self.temperatures.previous_execution_exists():
            # If there is not a live download going on, but a previous process exists we shot the continue/reset view.
            self.temp_status_label.configure(text="A previous download exists. Continue that download or reset it and start a new one?")
            self.temp_continue_reset_view()
        else:
            date_frame = ctk.CTkFrame(self.temp_button_frame, fg_color=self.root.cget('fg_color'))
            date_frame.columnconfigure(0, weight=1)
            date_frame.columnconfigure(1, weight=1)
            date_frame.pack(side='left', pady=10, padx=10)

            ctk.CTkLabel(date_frame,
                         text="Select date range",
                         font=ctk.CTkFont(size=13, weight="bold")).grid(row=0,
                                                                        column=0,
                                                                        columnspan=3,
                                                                        pady=(
                                                                        10, 10))
            ctk.CTkLabel(date_frame, text="Start date").grid(row=1, column=0,
                                                             sticky="w", padx=10)
            ctk.CTkLabel(date_frame, text="(MM-DD-YYYY)").grid(row=2, column=0,
                                                               sticky="w", padx=10)
            self.temp_start_entry = ctk.CTkEntry(date_frame, width=180,
                                            placeholder_text="01-01-2015")
            self.temp_start_entry.insert(0, "01-01-2015")
            self.temp_start_entry.grid(row=1, column=1, padx=10, rowspan=2, sticky="w")
            ctk.CTkLabel(date_frame, text="End date").grid(row=3, column=0,
                                                           sticky="w", padx=10,
                                                           pady=(10, 0))
            ctk.CTkLabel(date_frame, text="(MM-DD-YYYY)").grid(row=4, column=0,
                                                               sticky="w", padx=10)
            self.temp_end_entry = ctk.CTkEntry(date_frame, width=180,
                                          placeholder_text="12-31-2023")
            self.temp_end_entry.insert(0, "12-31-2023")
            self.temp_end_entry.grid(row=3, column=1, padx=10, rowspan=2, sticky="w",
                                pady=(10, 0))
            ctk.CTkLabel(date_frame, text="Frequency").grid(row=5, column=0,
                                                            sticky="w", padx=10,
                                                            pady=(10, 0))
            self.temp_freq_var = tk.StringVar(value="1h")
            freq_options = ["1h", "30min", "15min", "1D", "1W", "1ME"]
            self.freq_menu = ttk.Combobox(date_frame,
                                          textvariable=self.temp_freq_var,
                                          values=freq_options,
                                          width=10)
            self.freq_menu.grid(row=5, column=1, sticky="w", padx=10, pady=(10, 0))
            ctk.CTkButton(date_frame,
                          text="Add date range",
                          command=self.add_date_range,
                          fg_color=("gray75", "gray30"),
                          text_color=("gray10", "gray90"),
                          hover_color=("gray65", "gray40")
                          ).grid(row=6, column=0, columnspan=2, pady=20)

            # Select stations csv file button.
            other_btns_frame = ctk.CTkFrame(self.temp_button_frame, fg_color=self.root.cget('fg_color'))
            other_btns_frame.pack(expand=True, fill="both", pady=10, padx=(5, 20))
            file_btn = ctk.CTkButton(other_btns_frame,
                                     text="Select station file",
                                     command=self.temperatures_file_button,
                                     fg_color=("gray75", "gray30"),
                                     text_color=("gray10", "gray90"),
                                     hover_color=("gray65", "gray40"))
            file_btn.pack(side='top', padx=3, pady=(50, 10))
            start_fetching_btn = ctk.CTkButton(other_btns_frame,
                                               text="Start",
                                               command=self.temp_start_button)
            start_fetching_btn.pack(side='top', padx=3, pady=5)
            # start download button.

    def temp_stop_view(self):
        # Create stop button to the button frame.
        stop_fetching_btn = ctk.CTkButton(self.temp_button_frame,
                                          text="Stop",
                                          command=self.temp_stop_button)
        stop_fetching_btn.pack(side='top', pady=40)

    def temp_continue_reset_view(self):
        self.clear_frame(self.temp_button_frame)
        # Create continue and reset buttons.
        continue_btn = ctk.CTkButton(self.temp_button_frame,
                                     text="Continue",
                                     command=self.temp_start_button)
        reset_btn = ctk.CTkButton(self.temp_button_frame,
                                  text="Reset",
                                  command=self.temp_reset)
        continue_btn.pack(side='left', anchor='n', pady=(30, 100), padx=(200, 5))
        reset_btn.pack(side='left', anchor='n', pady=(30, 100), padx=5)


    def temp_start_button(self):
        print(f"Date range: {self.temperatures.get_date_range()}")
        # If the start is successful then update the page to show stop button.
        if self.temperatures.get_date_range() is None:
            self.temp_status_label.configure(text="Please set a date range")
        elif self.temperatures.get_stationsfile_path() == '':
            self.temp_status_label.configure(text="Please give a station file")
        else:
            thread = threading.Thread(target=lambda: self.temp_start_fetch(),
                                  daemon=True)
            thread.start()
            # Change the temperature page.
            self.temp_status_label.configure(text="Downloading in progress...")
            self.clear_frame(self.temp_button_frame)
            self.temp_stop_view()

    def temp_continue_button(self):
        print("Continue button pressed.")
        self.clear_frame(self.temp_button_frame)
        self.temp_stop_view()
        # Continue also needs to use threading.
        #self.temp_start_fetch()

    def temp_start_fetch(self):
        message = self.temperatures.start_fetch()
        self.temp_status_label.configure(text=message)

    def temp_stop_button(self):
        # Check if currently executing?
        self.temperatures.stop_fetch()
        # Continue and reset view.
        self.temp_continue_reset_view()

    def temp_reset(self):
        self.temperatures.reset_checkpoint()
        self.clear_frame(self.temp_button_frame)
        self.change_page(self.temperatures_page)

MyGUI()
