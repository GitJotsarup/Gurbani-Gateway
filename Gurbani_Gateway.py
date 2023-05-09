import json
from tkinter import *
import tkinter as tk
from tkinter import ttk
import os

# Saving the python script as '.pyw' file instead of '.py' will remove command window.

class GurbaniGateway(ttk.Frame):

    def __init__(self, master=None):

        super().__init__(master)
        self.master = master
        self.master.title("Gurbani Gateway")
        self.master.configure(background="black")
        self.master.geometry("1920x1080")

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
        self.search_label.place(x=20, y=50)

        # create a search bar and a search button
        self.search_bar = ttk.Entry(self.master, font=("Arial Bold", 11))
        self.search_bar.place(x=145, y=45)
        self.search_button = ttk.Button(self.master, text="Search", command=self.search_dharna)
        self.search_button.place(x=332, y=45)

        # create a listbox for displaying search results
        self.results_listbox = ttk.Treeview(self.master, columns=("title"), selectmode="browse")
        self.results_listbox.column("#0", width=0, stretch="no")
        self.results_listbox.column("title", width=528)
        # self.results_listbox.heading("title", text="Title")
        self.results_listbox.place(x=20, y=84)
        self.results_listbox.configure(height=7)

        # create the lines_listbox Treeview
        self.lines_listbox = ttk.Treeview(self, columns=("Punjabi Line",), selectmode="browse")
        self.lines_listbox.column("#0", width=20, anchor="w")
        self.lines_listbox.column("Punjabi Line", width=508, anchor="w")
        self.lines_listbox.heading("Punjabi Line", text="Dharna Lines") # anchor="w"
        self.lines_listbox.place(x=20, y=400)
        self.lines_listbox.configure(height=8)
        self.results_listbox.bind("<<TreeviewSelect>>", self.display_punjabi_lines)
        
        # 1275 is the width
        # Panedwindow
        self.paned = ttk.PanedWindow(self)
        self.paned.place(x=650, y=52.5, height=350, width=610)
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
        self.presenter_button.place(x=1145, y=50)

        # create checkboxes for display options
        self.display_options = {"punjabi": tk.BooleanVar(value=True),
                                "transliteration": tk.BooleanVar(value=True),
                                "english": tk.BooleanVar(value=True)}
        
        # create settings button for display options
        self.settings_button = ttk.Button(self.master, text="Settings", command=self.open_settings)
        self.settings_button.place(x=1180, y=700)

        # load dharnas from the JSON file
        with open("dharnas.json", "r", encoding="utf-8") as file:
            self.dharnas = json.load(file)

        # defining the dharna frame widget
        self.dharna_frame = ttk.Frame(self.master)

        self.presenter_window_created = False # to check if a window is already created or not

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

        # clear the listbox
        self.results_listbox.delete(*self.results_listbox.get_children())

        # get the search bar input
        search_input = self.search_bar.get().lower()

        # search for dharnas that match the search input
        matches = []
        for dharna in self.dharnas:
            if search_input in dharna["title"].lower():
                matches.append(dharna)

        # display the search results in the listbox
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
            transliteration_label = ttk.Label(self.dharna_disbox, text=selected_transliteration_line, font=("Helvetica", 12), anchor="center", justify="left", wraplength=self.paned.winfo_width())
            transliteration_label.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        if display_options["english"]:
            english_label = ttk.Label(self.dharna_disbox, text=selected_english_line, font=("Helvetica", 12), anchor="center", justify="left", wraplength=self.paned.winfo_width())
            english_label.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")

        # set the notebook focus to the dharna display box
        self.notebook.select(self.dharna_disbox)

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
                print("created")
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
                punjabi_label = ttk.Label(presenter_dharna_disbox, text=selected_punjabi_line, font=("GurbaniAkharHeavy", 20), anchor="center", justify="left")
                punjabi_label.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

            # get the corresponding English and transliteration lines
            english_lines = dharna["english"].split("\n")
            selected_english_line = english_lines[line_number - 1]
            
            transliteration_lines = dharna["transliteration"].split("\n")
            selected_transliteration_line = transliteration_lines[line_number - 1]

            if display_options["transliteration"]:
                transliteration_label = ttk.Label(presenter_dharna_disbox, text=selected_transliteration_line, font=("Helvetica", 12), anchor="center", justify="left")
                transliteration_label.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

            if display_options["english"]:
                english_label = ttk.Label(presenter_dharna_disbox, text=selected_english_line, font=("Helvetica", 12), anchor="center", justify="left")
                english_label.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")

            # set the notebook focus to the presenter dharna display box
            presenter_notebook.select(presenter_dharna_disbox)

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
                "punjabi": False,
                "transliteration": False,
                "english": True
            }

        # create the checkboxes and add them to the frame
        punjabi_var = tk.BooleanVar(value=display_options["punjabi"])
        punjabi_checkbox = ttk.Checkbutton(frame, text="Punjabi", variable=punjabi_var, style="TCheckbutton")
        
        transliteration_var = tk.BooleanVar(value=display_options["transliteration"])
        transliteration_checkbox = ttk.Checkbutton(frame, text="Transliteration", variable=transliteration_var, style="TCheckbutton")
        
        english_var = tk.BooleanVar(value=display_options["english"])
        english_checkbox = ttk.Checkbutton(frame, text="English", variable=english_var, style="TCheckbutton")
        
        # pack the checkboxes
        punjabi_checkbox.pack(anchor="w")
        transliteration_checkbox.pack(anchor="w")
        english_checkbox.pack(anchor="w")

        # create buttons to save or cancel changes
        button_frame = ttk.Frame(settings_menu)
        button_frame.pack(pady=10)

        def save_settings():
            # save the current display options to a file
            display_options = {
                "punjabi": punjabi_var.get(),
                "transliteration": transliteration_var.get(),
                "english": english_var.get()
            }
            with open("display_options.json", "w") as f:
                json.dump(display_options, f)

        save_button = ttk.Button(button_frame, text="Save", command=lambda: (save_settings(), settings_menu.destroy()))
        save_button.pack(side="left", padx=10)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=settings_menu.destroy)
        cancel_button.pack(side="right", padx=10)

        # set the size and position of the pop-up menu
        settings_menu.geometry("300x200+{0}+{1}".format(int(self.master.winfo_width()/2 - -350), int(self.master.winfo_height()/2 - -125)))
        settings_menu.resizable(False, False)

        def update_display_options():
            self.display_options["punjabi"] = punjabi_var.get()
            self.display_options["transliteration"] = transliteration_var.get()
            self.display_options["english"] = english_var.get()

        settings_menu.protocol("WM_DELETE_WINDOW", lambda: (save_settings(), settings_menu.destroy()))  # save settings on closing



if __name__ == '__main__':
    root = tk.Tk()
    app = GurbaniGateway(master=root)

    # Simply set the theme
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")
    app.pack(fill="both", expand=True)

    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))

    app.mainloop()