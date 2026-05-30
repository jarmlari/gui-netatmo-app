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


        # Nappi ja nappiin toiminto.
        home_btn = tk.Button(self.options_frame,
                             text="Home",
                             command=lambda: self.change_page(self.home_page))
        home_btn.pack()

        stat_btn = tk.Button(self.options_frame,
                           text="Stations",
                           command=lambda: self.change_page(self.stations_page))
        stat_btn.pack(pady=10, padx=10)

        temp_btn = tk.Button(self.options_frame,
                               text="Temperatures",
                               command=lambda: self.change_page(self.temperatures_page))
        temp_btn.pack(pady=10, padx=10)

        self.root.mainloop()

    def delete_pages(self):
        for frame in self.main_frame.winfo_children():
            frame.destroy()


    def change_page(self, page):
        self.delete_pages()
        page()

    def home_page(self):
        home_frame = tk.Frame(self.main_frame)
        label = tk.Label(home_frame, text="Home page")
        label.pack()
        home_frame.pack()

    def stations_page(self):
        stations_frame = tk.Frame(self.main_frame)
        label = tk.Label(stations_frame, text="Stations page")
        label.pack()
        stations_frame.pack()

    def temperatures_page(self):
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

