import tkinter as tk
import stations


class MyGUI:

    def __init__(self):
        self.root = tk.Tk()
        self.stations = stations.Stations()
        self.root.geometry("800x400")
        self.root.title("Netatmo app")

        # Options frame.
        self.options_frame = tk.Frame(self.root,
                                      width= 100,
                                      height=400,
                                      bg='#c3c3c3')
        self.options_frame.pack(side=tk.LEFT)
        self.options_frame.pack_propagate(False)

        # Main frame.
        self.main_frame = tk.Frame(self.root,
                              highlightbackground="black",
                              highlightthickness=2)
        self.main_frame.configure(width= 700, height= 400)
        self.main_frame.pack(side=tk.LEFT)
        self.main_frame.pack_propagate(False)


        # Option buttons.
        self.home_btn = tk.Button(self.options_frame,
                             text="Home",
                             fg="#158aff",
                             bd=0,
                             bg="#c3c3c3",
                             command=lambda: self.change_page(self.home_page))
        self.home_btn.place(x=10, y=50)
        self.home_indicate = tk.Label(self.options_frame, text='', bg='#c3c3c3')
        self.home_indicate.place(x=3, y=50, width=2, height=23)

        self.stat_btn = tk.Button(self.options_frame,
                             text="Stations",
                             fg="#158aff",
                             bd=0,
                             bg="#c3c3c3",
                             command=lambda: self.change_page(self.stations_page))
        self.stat_btn.place(x=10, y=100)
        self.stat_indicate = tk.Label(self.options_frame, text='', bg='#c3c3c3')
        self.stat_indicate.place(x=3, y=100, width=2, height=23)

        self.temp_btn = tk.Button(self.options_frame,
                             text="Temperatures",
                             fg="#158aff",
                             bd=0,
                             bg="#c3c3c3",
                             command=lambda: self.change_page(self.temperatures_page))
        self.temp_btn.place(x=10, y=150)
        self.temp_indicate = tk.Label(self.options_frame, text='', bg='#c3c3c3')
        self.temp_indicate.place(x=3, y=150, width=2, height=23)

        self.root.mainloop()

    def hide_indicators(self):
        self.home_indicate.config(bg='#c3c3c3')
        self.stat_indicate.config(bg='#c3c3c3')
        self.temp_indicate.config(bg='#c3c3c3')

    def indicate(self, lb):
        self.hide_indicators()
        lb.config(bg='#158aff')

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
        label = tk.Label(stations_frame, text="Stations page")
        label.pack()
        stations_frame.pack()

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

