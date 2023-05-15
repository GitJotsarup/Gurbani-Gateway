import json
from tkinter import *
import tkinter as tk
from tkinter import ttk
import os
# from indicnlp import common, loader, transliterate
from PIL import ImageTk, Image
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1) # this line is some crazy trick man, made all the text and pixels clear and support the computer resolution and dpi
# note that the above does not work on mac and is done automatically on mac

REPLACE_DICT = { # keyboard layout for punjabi, using win isn't an option for macOS
    "q": "ੳ",
    "w": "ਾ",
    "e": "ੲ",
    "r": "ਰ",
    "t": "ਟ",
    "y": "ਯ",
    "u": "ੁ",
    "i": "ਿ",
    "o": "ੋ",
    "p": "ਪ",
    "[": "ਔ",
    "]": "ਐ",
    "a": "ੳ",
    "s": "ਸ",
    "d": "ਦ",
    "f": "ਡ",
    "g": "ਗ",
    "h": "ਹ",
    "j": "ਜ",
    "k": "ਕ",
    "l": "ਲ",
    ";": "ਞ",
    "'": "ਵ",
    "z": "ਜ਼",
    "x": "ਣ",
    "c": "ਚ",
    "v": "ਞ",
    "b": "ਬ",
    "n": "ਨ",
    "m": "ਮ",
    ",": "ਾ",
    ".": "ੀ",
    "/": "ੂ",
}



def keyboard_pressed(event):
        char_pressed = event.char
        if char_pressed.lower() in REPLACE_DICT:
            char = REPLACE_DICT[char_pressed.lower()]
            if char_pressed.upper() == char_pressed:
                # If uppercase:
                char = char.upper()
            # Insert the character
            event.widget.insert("insert", char)
            # Return "break" to stop the event
            return "break"


# Saving the python script as '.pyw' file instead of '.py' will remove command window.

class GurbaniGateway(ttk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Gurbani Gateway")
        dpi_scale = self.master.winfo_fpixels(1)
        #self.master.configure(background="black")
        self.master.geometry("1920x1080")
        width_multiplier = (1920/self.master.winfo_screenwidth())
        height_multiplier = (1080/self.master.winfo_screenheight())

        self.presenter_window = None
        # Initialize labels
        self.english_label = None
        self.punjabi_label = None
        self.transliteration_label = None

        # Initialize display options
        self.display_options = {"punjabi": True}

        self.english_label = ttk.Label(self.english_label, text="english")
        self.punjabi_label = ttk.Label(self.punjabi_label, text="english")
        self.transliteration_label = ttk.Label(self.transliteration_label, text="english")

        # create a style for the ttk widgets
        self.style = ttk.Style()
        self.style.configure('TButton', background="white", foreground="black")
        self.style.configure('TCheckbutton', background="grey", foreground="white")
        self.style.configure('TLabel', background="black", foreground="white")

        # create a label for the search bar
        self.search_label = ttk.Label(self.master, text="Search for a Dharna:")
        self.search_label.place(x=20*dpi_scale/width_multiplier, y=35*dpi_scale/height_multiplier)

        # create a search bar and a search button
        self.search_bar = ttk.Entry(self.master, font=("Arial Bold", 13))
        self.search_bar.place(x=(200*dpi_scale/width_multiplier)+5, y=30*dpi_scale/height_multiplier)
        self.search_bar.bind("<Key>", keyboard_pressed)
        self.search_button = ttk.Button(self.master, text="Search", command=self.search_dharna)
        self.search_button.place(x=(500*dpi_scale/width_multiplier)+10, y=30*dpi_scale/height_multiplier)

        # create a listbox for displaying search results
        self.results_listbox = ttk.Treeview(self.master, columns=("title"), selectmode="browse")
        self.results_listbox.column("#0", width=0, stretch="no")
        self.results_listbox.column("title", width=int(920*dpi_scale/width_multiplier))
        # self.results_listbox.heading("title", text="Title")
        self.results_listbox.place(x=20*dpi_scale/width_multiplier, y=90*dpi_scale/height_multiplier)
        self.results_listbox.configure(height=int(7*dpi_scale/height_multiplier))

        # create the lines_listbox Treeview
        self.lines_listbox = ttk.Treeview(self, columns=("Punjabi Line",), selectmode="browse")
        self.lines_listbox.column("#0", width=int(20*dpi_scale/width_multiplier), anchor="w")
        self.lines_listbox.column("Punjabi Line", width=int(902.5*dpi_scale/width_multiplier), anchor="w")
        self.lines_listbox.heading("Punjabi Line", text="Dharna Lines") # anchor="w"
        self.lines_listbox.place(x=20*dpi_scale/width_multiplier, y=535*dpi_scale/height_multiplier)
        self.lines_listbox.configure(height=int(7*dpi_scale/height_multiplier))
        self.results_listbox.bind("<<TreeviewSelect>>", self.display_punjabi_lines)
        
        # 1275 is the width
        # Panedwindow
        self.paned = ttk.PanedWindow(self)
        self.paned.place(x=995*dpi_scale/width_multiplier, y=70*dpi_scale/height_multiplier, height=int(500*dpi_scale/height_multiplier), width=int(910*dpi_scale/width_multiplier))
        # Notebook, pane #1
        self.pane_1 = ttk.Frame(self.paned, padding=5)
        self.paned.add(self.pane_1, weight=3)
        # Notebook, pane #1
        self.notebook = ttk.Notebook(self.pane_1)
        self.notebook.pack(fill="both", expand=True)
        # dharna display box
        self.dharna_disbox = ttk.Frame(self.notebook)
        self.notebook.add(self.dharna_disbox, text="Dharna")
        # add text widget to the frame
        self.dharna_text = tk.Text(self.dharna_disbox, wrap="word", bg='black', state='disabled')
        self.dharna_text.grid(row=0, column=0, sticky="nsew")

        self.presenter_notebook = None
        self.presenter_dharna_disbox = None

        # add scrollbars to the text widget
        self.dharna_vscrollbar = ttk.Scrollbar(self.dharna_disbox, orient="vertical", command=self.dharna_text.yview)
        self.dharna_vscrollbar.grid(row=0, column=1, sticky="ns")
        self.dharna_hscrollbar = ttk.Scrollbar(self.dharna_disbox, orient="horizontal", command=self.dharna_text.xview)
        self.dharna_hscrollbar.grid(row=1, column=0, sticky="ew")
        self.dharna_text.configure(yscrollcommand=self.dharna_vscrollbar.set, xscrollcommand=self.dharna_hscrollbar.set)

        # create the button
        self.presenter_button_clicked = False
        self.presenter_button = ttk.Button(self.master, text="Presenter View", command=self.presenter_button_click)
        self.presenter_button.place(x=1750*dpi_scale/width_multiplier, y=40*dpi_scale/height_multiplier)

        # create checkboxes for display options
        self.display_options = {"punjabi": tk.BooleanVar(value=True),
                                "transliteration": tk.BooleanVar(value=True),
                                "english": tk.BooleanVar(value=True),
                                "theme": tk.BooleanVar(value=True)}
        
        # create settings button for display options
        self.settings_button = ttk.Button(self.master, text="Settings", command=self.open_settings)
        self.settings_button.place(x=1760*dpi_scale/width_multiplier, y=920*dpi_scale/height_multiplier)

        self.show_splash_screen()

        # load dharnas from the JSON file
        with open("dharnas.json", "r", encoding="utf-8") as file:
            self.dharnas = json.load(file)

        # defining the dharna frame widget
        self.dharna_frame = ttk.Frame(self.master)

        # load all the necissary data for the auto transliteration
        #loader.load() 

        self.presenter_window_created = False # to check if a window is already created or not

    def show_splash_screen(self):
        image = Image.open(".\\SplashScreen\\SplashScreenImage.png")
        image = image.resize((self.master.winfo_screenwidth(), self.master.winfo_screenheight()), Image.Resampling.BICUBIC)
        self.splash_photo = ImageTk.PhotoImage(image)
        self.splash_label = tk.Label(self.master, image=self.splash_photo)
        self.splash_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.splash_label.lift()  # Move the splash screen label to the top
        self.master.after(3000, self.hide_splash_screen)

    def hide_splash_screen(self):
        self.splash_label.destroy()
        # Continue with the rest of your app setup and show the main content
    
    def on_line_select(self, event):
        selection = event.widget.selection()
        if selection:
            line_item = event.widget.selection()[0]
            line_number = int(event.widget.item(line_item, "text"))
            dharna_item = self.results_listbox.selection()[0]
            dharna_title = self.results_listbox.item(dharna_item, "values")[0]
            for dharna in self.dharnas:
                if dharna["title"] == dharna_title:
                    self.display_dharna(dharna, line_number)
                    if self.presenter_button_clicked:
                        self.open_presenter_view(dharna, line_number)
                    break

    def presenter_button_click(self):
        self.presenter_button_clicked = True

    def display_punjabi_lines(self, event):
        # clear previous selections
        self.lines_listbox.delete(*self.lines_listbox.get_children())

        # get selected dharna from results_listbox
        selection = self.results_listbox.selection()
        if selection:
            item = self.results_listbox.selection()[0]
            dharna_title = self.results_listbox.item(item, "values")[0]
            for dharna in self.dharnas:
                if dharna["title"] == dharna_title:
                    # display punjabi lines in lines_listbox
                    for i, line in enumerate(dharna["punjabi"].split("\n"), start=1):
                        self.lines_listbox.insert("", "end", text=str(i), values=(line,))
                    self.lines_listbox.bind("<<TreeviewSelect>>", self.on_line_select)
                    return dharna
                
    def search_dharna(self):
        """Search for dharnas based on the search bar input and display the results in the listbox"""

        # Clear the listbox
        self.results_listbox.delete(*self.results_listbox.get_children())

        # Get the search bar input
        search_input = self.search_bar.get().lower()

        # Split the search input into individual letters
        search_letters = search_input.split() #doesn't exactly work
        print(search_letters)

        # Search for dharnas that match the first letters of each word in the title
        matches = []
        for dharna in self.dharnas:
            title_words = dharna["title"].lower().split()
            first_letters = [word[0] for word in title_words]
            if all(letter in first_letters for letter in search_letters):
                matches.append(dharna)

        # Display the search results in the listbox
        for dharna in matches:
            title = dharna["title"]
            self.results_listbox.insert("", "end", text="", values=(title,))


    def display_dharna(self, dharna, line_number):
        # clear the dharna display box
        for widget in self.dharna_disbox.winfo_children():
            widget.destroy()

        # read display options from the json file
        with open("display_options.json", "r") as f:
            display_options = json.load(f)

        # set the row and column configuration of the dharna_disbox frame
        self.dharna_disbox.rowconfigure(0, weight=1)
        self.dharna_disbox.rowconfigure(1, weight=1)
        self.dharna_disbox.rowconfigure(2, weight=1)
        self.dharna_disbox.columnconfigure(0, weight=1)

        # get the selected Punjabi line
        punjabi_lines = dharna["punjabi"].split("\n")
        selected_punjabi_line = punjabi_lines[line_number - 1]
        if display_options["punjabi"]:
            punjabi_label = ttk.Label(self.dharna_disbox, text=selected_punjabi_line, font=("GurbaniAkharHeavy", 20), anchor="center", justify="left", wraplength=self.paned.winfo_width())
            punjabi_label.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # get the corresponding English and transliteration lines
        english_lines = dharna["english"].split("\n")
        selected_english_line = english_lines[line_number - 1]
        
        transliteration_lines = dharna["transliteration"].split("\n")
        selected_transliteration_line = transliteration_lines[line_number - 1]

        if display_options["transliteration"]:
            transliteration_label = ttk.Label(self.dharna_disbox, text=selected_transliteration_line, font=("Helvetica", 13), anchor="center", justify="left", wraplength=self.paned.winfo_width())
            transliteration_label.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
            # gurmukhi_text = dharna["punjabi"]  # Assuming 'gurmukhi' is the key for the Gurmukhi text in the 'dharna' dictionary
            # transliterated_text = transliterate.transliterate_text(gurmukhi_text, common.LANG_GURMUKHI, common.LANG_LATIN)
            # transliteration_label = ttk.Label(self.dharna_disbox, text=transliterated_text, font=("Helvetica", 13), anchor="center", justify="left", wraplength=self.paned.winfo_width())
            # transliteration_label.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        if display_options["english"]:
            english_label = ttk.Label(self.dharna_disbox, text=selected_english_line, font=("Helvetica", 13), anchor="center", justify="left", wraplength=self.paned.winfo_width())
            english_label.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")

        # set the notebook focus to the dharna display box
        # self.notebook.select(self.dharna_disbox)

    def exit_presenter_view(self, presenter_window):
        presenter_window.destroy()
        self.presenter_button_clicked = False

    def presenter_window_created(self):
        return self.presenter_window_created

    def open_presenter_view(self, dharna, line_number):

        self.punjabi_label = None
        self.transliteration_label = None
        self.english_label = None

        if self.presenter_button_clicked:
            if not self.presenter_window_created:
                # create a new window for the presenter view
                self.presenter_window = tk.Toplevel(self.master)
                self.presenter_window.style = ttk.Style()
                self.presenter_window.title("Presenter View")
                # presenter_window.attributes("-fullscreen", True) # overlay

                presenter_window = self.presenter_window

                # add a protocol to the presenter window to handle closing
                presenter_window.protocol("WM_DELETE_WINDOW", lambda: self.exit_presenter_view(presenter_window))

                # set the presenter_window_created flag to True
                self.presenter_window_created = True

            # read display options from the json file
            with open("display_options.json", "r") as f:
                display_options = json.load(f)

            # use the existing window
            presenter_window = self.presenter_window

            for widget in presenter_window.winfo_children():
                widget.destroy()

            # create a notebook widget for the presenter view
            presenter_notebook = ttk.Notebook(presenter_window)
            presenter_notebook.pack(fill="both", expand=True)

            # create a frame to hold the dharna display box in the presenter view
            presenter_dharna_disbox = ttk.Frame(presenter_notebook)
            presenter_notebook.add(presenter_dharna_disbox, text="Dharna")

            # set the row and column configuration of the presenter_dharna_disbox frame
            presenter_dharna_disbox.rowconfigure(0, weight=1)
            presenter_dharna_disbox.rowconfigure(1, weight=1)
            presenter_dharna_disbox.rowconfigure(2, weight=1)
            presenter_dharna_disbox.columnconfigure(0, weight=1)

            # get the selected Punjabi line
            punjabi_lines = dharna["punjabi"].split("\n")
            selected_punjabi_line = punjabi_lines[line_number - 1]
            if display_options["punjabi"]:
                punjabi_label = ttk.Label(presenter_dharna_disbox, text=selected_punjabi_line, font=("GurbaniAkharHeavy", 50), anchor="center", justify="left")
                punjabi_label.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
                # presenter_window.update()  # Ensure the window has been updated and its width is accurate
                # wrap_length = presenter_window.winfo_width()
                # punjabi_label.configure(wraplength=wrap_length)

            # get the corresponding English and transliteration lines
            english_lines = dharna["english"].split("\n")
            selected_english_line = english_lines[line_number - 1]
            
            transliteration_lines = dharna["transliteration"].split("\n")
            selected_transliteration_line = transliteration_lines[line_number - 1]

            if display_options["transliteration"]:
                transliteration_label = ttk.Label(presenter_dharna_disbox, text=selected_transliteration_line, font=("Helvetica", 25), anchor="center", justify="left")
                transliteration_label.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
                # presenter_window.update()  # Ensure the window has been updated and its width is accurate
                # wrap_length = presenter_window.winfo_width()
                # transliteration_label.configure(wraplength=wrap_length)

            if display_options["english"]:
                english_label = ttk.Label(presenter_dharna_disbox, text=selected_english_line, font=("Helvetica", 25), anchor="center", justify="left")
                english_label.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")
                # presenter_window.update()  # Ensure the window has been updated and its width is accurate
                # wrap_length = presenter_window.winfo_width()
                # english_label.configure(wraplength=wrap_length)

            # set the notebook focus to the presenter dharna display box
            # presenter_notebook.select(presenter_dharna_disbox)

    def open_settings(self):
        # create a settings pop-up menu
        settings_menu = tk.Toplevel(self.master)
        settings_menu.title("Settings")
        settings_menu.style = ttk.Style()
        # settings_menu.style.theme_use("azure-light") # this breaks the app
        settings_menu.overrideredirect(True) # this takes out the usual title bar with the minimize, maximize, and close buttons.

        # create a frame to hold the checkboxes and buttons
        frame = ttk.Frame(settings_menu, padding=20)
        frame.pack(fill="both", expand=True)
        
        # load saved display options
        if os.path.exists("display_options.json"):
            with open("display_options.json", "r") as f:
                display_options = json.load(f)
        else:
            # set default options if no saved options found
            display_options = {
                "punjabi": True,
                "transliteration": True,
                "english": True,
                "theme": True
            }

        # create the checkboxes and add them to the frame
        punjabi_var = tk.BooleanVar(value=display_options["punjabi"])
        punjabi_checkbox = ttk.Checkbutton(frame, text="Punjabi", variable=punjabi_var, style="TCheckbutton")
        
        transliteration_var = tk.BooleanVar(value=display_options["transliteration"])
        transliteration_checkbox = ttk.Checkbutton(frame, text="Transliteration", variable=transliteration_var, style="TCheckbutton")
        
        english_var = tk.BooleanVar(value=display_options["english"])
        english_checkbox = ttk.Checkbutton(frame, text="English", variable=english_var, style="TCheckbutton")

        theme_var = tk.BooleanVar(value=display_options["theme"])
        theme_switch = ttk.Checkbutton(frame, text="Light/Dark", style="Switch.TCheckbutton", variable=theme_var)

        # pack the checkboxes
        punjabi_checkbox.pack(anchor="w")
        transliteration_checkbox.pack(anchor="w")
        english_checkbox.pack(anchor="w")
        theme_switch.pack(anchor="w")

        # create buttons to save or cancel changes
        button_frame = ttk.Frame(settings_menu)
        button_frame.pack(pady=10)

        def save_settings():
            # save the current display options to a file
            display_options = {
                "punjabi": punjabi_var.get(),
                "transliteration": transliteration_var.get(),
                "english": english_var.get(),
                "theme": theme_var.get()
            }
            with open("display_options.json", "w") as f:
                json.dump(display_options, f)
                # if display_options["theme"]:
                #     settings_menu.style.theme_use("azure-light")
                # else:
                #     settings_menu.style.theme_use("azure-dark")

        save_button = ttk.Button(button_frame, text="Save", command=lambda: (save_settings(), settings_menu.destroy()))
        save_button.pack(side="left", padx=10)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=settings_menu.destroy)
        cancel_button.pack(side="right", padx=10)

        dpi_scale = self.master.winfo_fpixels(1)
        width_multiplier = (1920/self.master.winfo_screenwidth())
        height_multiplier = (1080/self.master.winfo_screenheight())

        # set the size and position of the pop-up menu 
        settings_menu.geometry("{0}x{1}+{2}+{3}".format(int(300 * dpi_scale / width_multiplier), int(250 * dpi_scale / height_multiplier), int(self.master.winfo_width() / 2 - -660 * dpi_scale / width_multiplier), int(self.master.winfo_height() / 2 - -265 * dpi_scale / height_multiplier)))
        settings_menu.resizable(False, False)

        def update_display_options():
            self.display_options["punjabi"] = punjabi_var.get()
            self.display_options["transliteration"] = transliteration_var.get()
            self.display_options["english"] = english_var.get()
            self.display_options["theme"] = theme_var.get()

        settings_menu.protocol("WM_DELETE_WINDOW", lambda: (save_settings(), settings_menu.destroy()))  # save settings on closing



if __name__ == '__main__':
    root = tk.Tk()
    app = GurbaniGateway(master=root)

    # Simply set the theme
    root.tk.call("source", "azure.tcl")
    if os.path.exists("display_options.json"):
            with open("display_options.json", "r") as f:
                display_options = json.load(f)
    if display_options["theme"]:
        root.tk.call("set_theme", "dark")
    else:
        root.tk.call("set_theme", "light")
    app.pack(fill="both", expand=True)

    # Set a minsize for the window
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    # root.geometry("+{}+{}".format(x_cordinate, y_cordinate-20)) # this line places the tab in the middle i find it quite annoying
    
    ### FUTURE CODE
    # root.overrideredirect(True) # removes the existing title bar

    # def move_app(e):
    #     root.geometry(f'+{e.x_root}+{e.y_root}')

    # # create a custon title bar
    # title_bar = Frame(root, bg="black", relief="raised", bd=0)
    # title_bar.pack(expand=1, fill=X)
    # # bind the titlebar
    # title_bar.bind("<B1-Motion>", move_app)

    # # close button
    # close_label = Label(title_bar, text="  X  ", bg="black", fg= "white")
    # close_label.pack(side=RIGHT, pady=4)


    # # create the label for the title bar 
    # title_label = Label(title_bar, text="Gurbani Gateway", bg="black", fg="white")
    # title_label.pack(side=LEFT, pady=4)


    app.mainloop()