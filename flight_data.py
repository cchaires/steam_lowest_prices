from tkinter import Tk


class Gui:
    # This class is responsible for Graphical User Interface.
    def __init__(self):
        self.window = Tk()
        self.window.title("Steam Games Lowest Price")
        self.window.config(padx=25, pady=25)
        self.window.mainloop()


gui = Gui()
