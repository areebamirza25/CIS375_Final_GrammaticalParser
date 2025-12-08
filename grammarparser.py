"""
Title: CIS 375 Software Engineering I - Final Project - Tiny Tool
        Grammar Parser
Authors: Areeba Mirza, Natalie Kim, Myriam Hazime, Ciaran Grabowski, Jeff Clark
Date: 11/24/2025
"""

# Source for Multi-Page function - https://stackoverflow.com/a
# Posted by Bryan Oakley, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-13, License - CC BY-SA 4.0

# Source for binding keys and mouse buttons:
# https://stackoverflow.com/questions/66512222/how-do-i-enable-right-click-in-entry-and-output-widget-for-pasting-and-copying-r
# Retrieved 2025-11-25

# Documentations used:
# https://tkdocs.com/tutorial/menus.html
# https://docs.python.org/3/library/tkinter.scrolledtext.html
# https://www.nltk.org/
# https://pypi.org/project/pyperclip/
# https://www.pythontutorial.net/tkinter/tkinter-event-binding/
# Retrieved 2025-11-24, 2025-11-25


# ------------------ Import Required Libraries ------------------
import json                                             # For Session Data
import os.path                                          # For Session File
import tkinter as tk                                    # For creating the GUI
from datetime import datetime                           # For timestamp on export header
from tkinter import ttk, font, messagebox, filedialog   # For creating the GUI
from tkinter import scrolledtext                        # For creating the GUI
import nltk                                             # For finding nouns and verbs
import pyperclip                                        # Lets the user copy and paste text in tkinter window
from nltk.downloader import update

# Download NLTK resources
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

# ------------------ Parsing Engine Class ------------------
class ParsingEngine:

    @staticmethod
    def parse_text(text: str):
        # Tokenize text into a list of words
        tokens = nltk.word_tokenize(text)

        # Use pos_tag function to categorize each word into grammatical categories
        tagged_words = nltk.pos_tag(tokens)

        # Find nouns and verbs in text without duplicates
        nouns = []
        verbs = []
        for word, category in tagged_words:
            if category.startswith('NN') and word not in nouns:  # Finds words in a Noun category
                nouns.append(word)
            elif category.startswith('VB') and word not in verbs:  # Finds words in a Verb category
                verbs.append(word)

        return sorted(nouns), sorted(verbs)

# ------------------ Text Manager Class ------------------
class TextManager:
    def __init__(self):
        self.nouns = []         # List of Nouns
        self.verbs = []         # List of Verbs

        self.narratives = {}    # List of Narratives

    def set_narratives(self, word: str, text: str):
        # Store a narrative and a description for a noun or verb
        self.narratives[word] = text

    def get_narrative(self, word: str) -> str:
        # Retrieve narrative text for a selected word
        return self.narratives.get(word, "")

    def remove_narrative(self, word: str):
        # Delete a narrative from the internal table
        if word in self.narratives:
            del self.narratives[word]

    # Inputs: List of either Nouns or Verbs
    #         Integer representing which textbox the text is coming from
    # Function: Update the list of Nouns or Verbs
    def update_list(self, word_list, list_ID):
        match list_ID:
            # Nouns
            case 0:
                self.nouns = sorted(set(word_list))
            # Verbs
            case 1:
                self.verbs = sorted(set(word_list))

    # Inputs: Integer representing which textbox the text is coming from
    # Function: Reset the contents of the Noun or Verb list
    def clear(self, list_ID):
        match list_ID:
            case 0:
                self.nouns = []
            case 1:
                self.verbs = []


    # Inputs: Text from a textbox in the GUI and
    #         Integer representing which textbox the text is coming from
    # Function: Converts text into a list and uses it to update the list of
    #           nouns or verbs. It then turns it back into string
    # Outputs: Updated text to be sent to the textbox
    def apply_edits(self, text, list_ID):
        match list_ID:
            # Nouns
            case 0:
                # Remove all the text not part of the list
                text = text.replace("Nouns Found in Text: ", "").strip()

                # Update the list of Nouns based on user edits
                self.nouns = sorted({w.strip() for w in text.split(",") if w.strip()})

                # Reformat the text to be sent to the textbox
                updated_text = "Nouns Found in Text: " + ", ".join(self.nouns)

                return updated_text
            # Verbs
            case 1:
                # Remove all the text not part of the list
                text = text.replace("Verbs Found in Text: ", "").strip()

                # Update the list of Verbs based on user edits
                self.verbs = sorted({w.strip() for w in text.split(",") if w.strip()})

                # Reformat the text to be sent to the textbox
                updated_text = "Verbs Found in Text: " + ", ".join(self.verbs)

                return updated_text

# ------------------ Exporter Class ------------------
class Exporter:

    @staticmethod
    def format_export(noun_text: str, verb_text: str) -> str:
        # Set timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format Header
        header = (
            "Grammar Parser Tiny Tool: Export\n"
            f"Timestamp: {timestamp}\n"
            "----------------------------------------\n\n"
        )

        return header + noun_text + "\n\n" + verb_text + "\n"

    # Inputs: Text taken from the two textboxes
    # Function: Export the text as a .txt file
    @staticmethod
    def export(text: str, filename: str):
        # Export text to user-specified file
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:
            raise RuntimeError(f"Error saving file:{e}")

# ------------------ Session Manager Class ------------------
class SessionManager:
    SESSION_FILE = "session.json"   # File for saving session data

    @staticmethod
    def save_session(nouns, verbs, narratives):
        # Save information from current session

        data = {
            "nouns": nouns,
            "verbs": verbs,
            "narratives": narratives
        }

        try:
            with open(SessionManager.SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            raise RuntimeError(f"Failed to save session: {e}")

    # Loads Session Data
    @staticmethod
    def load_session():
        # If no session data exists
        if not os.path.exists(SessionManager.SESSION_FILE):
            return [], [], {}

        try:
            with open(SessionManager.SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("nouns", []), data.get("verbs", []), data.get("narratives", {})
        except:
            # Corrupted Session File
            messagebox.showwarning(
                "Corrupted Session",
                "Your session file is corrupted. Starting fresh."
            )
            return [], [], {}

# ------------------ Create GUI for Grammar Parser ------------------
class GrammarParser(tk.Tk):
    def __init__(self):
        super().__init__()

        # Initialize a TextManager object to hold the lists of Nouns, Verbs, and Narratives
        self.pos_lists = TextManager()

        # ------------------ Setup and Top Area: Welcome Labels ------------------

        # Set the style for ttk buttons
        style = ttk.Style()
        style.configure("Custom.TButton", font=("SegoeUI", 12, "bold"))

        # Create the main window
        self.title("Tiny Tool: Grammar Parser")  # Set title
        self.geometry("600x925")  # Set window size

        # Create the main frame to contain all widgets
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Create welcome label
        self.welcome_label = tk.Label(self.container, text="Welcome to Grammar Parser!", font=("SegoeUI", 16, "bold"))
        self.welcome_label.pack(side="top", fill="x", pady=10)

        # Create instructions label
        self.instructions_label = tk.Label(self.container, text="Enter text for Grammar Parsing:", font=("SegoeUI",13))
        self. instructions_label.pack(pady=5)

        # ------------------ Mid Section: Textbox and Buttons ------------------

        # Create text widget with scrollbar
        self.textbox = scrolledtext.ScrolledText(self.container, wrap=tk.WORD, width=60, height=15,  font=("Arial", 11),
                                                 undo=True, autoseparators=True)
        self.textbox.pack(padx=10, pady=10)

        # Let user copy and paste in GUI and text widget
        ## using right-click menu and Ctrl+C and Ctrl+V
        self.textbox.bind("<Button-3>", lambda event: self.show_context_menu(event))
        self.textbox.bind("<Control-KeyPress-c>", lambda event: self.copy(self.textbox))
        self.textbox.bind("<Control-KeyPress-v>", lambda event: self.paste(self.textbox))
        self.textbox.bind("<Control-z>", lambda event: self.undo(self.textbox))
        self.textbox.bind("<Control-y>", lambda event: self.redo(self.textbox))

        # Create context menu for user
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=lambda: self.copy(self.textbox))
        self.context_menu.add_separator()  # Optional separator
        self. context_menu.add_command(label="Paste", command=lambda: self.paste(self.textbox))

        # Create a sub frame to contain the buttons
        self.button_row = tk.Frame(self.container)
        self.button_row.pack(pady=10)

        # Create buttons to use tool
        self.parse_button = tk.Button(self.button_row, text="Parse Text", font=("SegoeUI", 12, "bold"), bg="lightblue",
                                      command=lambda: self.parse_text(self.textbox))
        self.parse_button.pack(side="left", padx=10)
        self.export_button = tk.Button(self.button_row, text="Save as TXT File", font=("SegoeUI", 12, "bold"), bg="yellow2",
                                       command=lambda: self.export_text(self.textbox))
        self.export_button.pack(side="left", padx=10)
        self.erase_button = tk.Button(self.button_row, text="Erase Text", font=("SegoeUI", 12, "bold"), bg="brown1",
                                      command=lambda: self.erase_text(self.textbox))
        self.erase_button.pack(side="left", padx=10)

        # ------------------ Lower Area: Notebook for Noun/Verb Lists ------------------

        # Create sub frame for part of Speech Lists
        self.lists_frame = (tk.Frame(self.container))
        self.lists_frame.pack(pady=10)

        # Create Notebook to hold the Part of Speech Lists
        self.notebook = ttk.Notebook(self.lists_frame, width= 400, height=300)
        self.notebook.pack()

        self.noun_frame = tk.Frame(self.notebook)      # Tab for list of Nouns
        self.verb_frame = tk.Frame(self.notebook)      # Tab for list of Verbs

        self.notebook.add(self.noun_frame, text="List of Nouns")    # Add Tab for Nouns
        self.notebook.add(self.verb_frame, text="List of Verbs")    # Add Tab for Verbs

        # Create Textbox for Part of Speech Lists
        self.noun_box = scrolledtext.ScrolledText(self.noun_frame, wrap=tk.WORD, width= 40, height=6, font=("Arial", 11))
        self.noun_box.pack(expand=True, fill="both")

        self.verb_box = scrolledtext.ScrolledText(self.verb_frame, wrap=tk.WORD, width= 40, height=6, font=("Arial", 11))
        self.verb_box.pack(expand=True, fill="both")

        # Let user copy and paste in GUI and text widget
        ## using right-click menu and Ctrl+C and Ctrl+V
        self.noun_box.bind("<Button-3>", lambda event: self.show_context_menu(event))           # List of Nouns
        self.noun_box.bind("<Control-KeyPress-c>", lambda event: self.copy(self.noun_box))
        self.noun_box.bind("<Control-KeyPress-v>", lambda event: self.paste(self.noun_box))
        self.noun_box.bind("<Control-z>", lambda event: self.undo(self.noun_box))
        self.noun_box.bind("<Control-y>", lambda event: self.redo(self.noun_box))

        # Let user copy and paste in GUI and text widget
        ## using right-click menu and Ctrl+C and Ctrl+V
        self.verb_box.bind("<Button-3>", lambda event: self.show_context_menu(event))           # List of Verbs
        self.verb_box.bind("<Control-KeyPress-c>", lambda event: self.copy(self.noun_box))
        self.verb_box.bind("<Control-KeyPress-v>", lambda event: self.paste(self.noun_box))
        self.verb_box.bind("<Control-z>", lambda event: self.undo(self.verb_box))
        self.verb_box.bind("<Control-y>", lambda event: self.redo(self.verb_box))

        # Create Button to Update Noun List
        self.update_nouns_button = ttk.Button(self.noun_frame, text="Update Noun List", style="Custom.TButton",
                                              command=lambda: self.update_pos_list(self.noun_box))
        self.update_nouns_button.pack(pady=5)

        # Create Button to Update Verb List
        self.update_verbs_button = ttk.Button(self.verb_frame, text="Update Verb List", style="Custom.TButton",
                                              command=lambda: self.update_pos_list(self.verb_box))
        self.update_verbs_button.pack(pady=5)

        # Create Button to Clear the Noun List
        self.noun_clear_button = ttk.Button(self.noun_frame, text="Clear Noun List", style="Custom.TButton",
                                            command=lambda: self.clear_noun_list(self.noun_box))
        self.noun_clear_button.pack(pady=5)

        # Create Button to Clear the Verb List
        self.verb_clear_button = ttk.Button(self.verb_frame, text="Clear Verb List", style="Custom.TButton",
                                            command=lambda: self.clear_verb_list(self.verb_box))
        self.verb_clear_button.pack(pady=5)

        # ------------------ Upper Bottom Area: Reset All and Save Session Buttons ------------------

        # Create frame to hold the Reset All and Save Session Buttons
        self.bottom_button_frame = tk.Frame(self.container)
        self.bottom_button_frame.pack(pady=5)

        # Create Save Session button
        self.save_session_button = tk.Button(self.bottom_button_frame, text="Save Session", font=("SegoeUI", 12, "bold"),
                                          bg="ivory3", command=lambda: self.save_current_session())
        self.save_session_button.pack(side="left", padx=10)

        # Create Reset All button
        self.reset_all_button = tk.Button(self.bottom_button_frame, text="Reset All", font=("SegoeUI", 12, "bold"),
                                          bg="ivory3", command=lambda: self.erase_all())
        self.reset_all_button.pack(side="left", padx=10)


        # ------------------ Bottom Area: Note Label ------------------

        note_text = "Note: The program returns a list of verbs and nouns in " \
                                              "accordance with the NLTK database. The text returned may be edited after the list is presented." \
                                              " Please ensure correct punctuation for the best results."
        # Create note label
        note_label = tk.Label(self.container, text=note_text, font=("SegoeUI", 10), justify="center", wraplength=300)
        note_label.pack(pady=10)
        note_label.config(state=tk.DISABLED, disabledforeground="black")

        # ------------------ Session Information ------------------

        # Retrieve Session Data
        saved_nouns, saved_verbs, saved_narratives = SessionManager.load_session()
        self.pos_lists.nouns = saved_nouns
        self.pos_lists.verbs = saved_verbs
        self.pos_lists.narratives = saved_narratives

        # Load the GUI with A Saved State
        if saved_nouns:
            self.noun_box.insert("1.0", "Nouns Found in Text: " + ", ".join(saved_nouns))
        if saved_verbs:
            self.verb_box.insert("1.0", "Verbs Found in Text: " + ", ".join(saved_verbs))

        self.update_tab_titles()

    # ------------------ Define Helper Functions for Grammar Parser ------------------
    def get_text(self, textbox):
        # Accepts a tkinter text widget as input
        # Returns the text in the text widget as a string

        # Check if input is a text widget
        if isinstance(textbox, tk.Entry):
            text = textbox.get()
        elif isinstance(textbox, scrolledtext.ScrolledText):
            text = textbox.get("1.0", tk.END)
        else:
            return "Empty"

        return text

    # Ended up not using this method
    def return_text(self, textbox, text):
        # Accepts a tkinter text widget and a string as input
        # Prints the string to the text widget

        # Check if input is a text widget and a string
        if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
            if isinstance(text, str):
                self.erase_text(textbox)
                textbox.insert(tk.END, text)

        return

    def export_text(self, textbox):
        # Accepts a tkinter text widget as input
        # Writes the text in the text widget to a TXT file

        # Check if input is a text widget
        if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
            # Get text from the text widget
            noun_text = self.get_text(self.noun_box).strip()
            verb_text = self.get_text(self.verb_box).strip()

            # Show error if you're trying to export when both lists are empty
            if not noun_text and not verb_text:
                messagebox.showerror("Error", "Nothing to Export")

            # Format the text for export
            text = Exporter.format_export(noun_text, verb_text)

            # Get Filename
            filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Text files", "*.txt")])

            # Return if no filename
            if not filename:
                return

            try:
                # Export
                Exporter.export(text, filename)
                messagebox.showinfo("Exported",f"Text saved as {filename}")
            except RuntimeError as e:
                messagebox.showerror("Error",f"Error saving file: {e}")

        return

    def show_context_menu(self, event):

        # Show the context menu
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()  # Release the grab when the menu is dismissed

    def copy(self, textbox):
        # Accepts a tkinter text widget as input
        # Lets the user copy the text in the text widget

        # Check if input is a text widget
        if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
            text = self.get_text(textbox)  # Get the text inside entry widget
            self.clipboard_clear()  # Clear the tkinter clipboard
            self.clipboard_append(text)  # Append to system clipboard

    def paste(self, textbox):
        # Accepts a tkinter text widget as input
        # Lets the user paste text to the text widget

        # Check if input is a text widget
        if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
            # clipboard = main_window.clipboard_get()  # Get the copied item from system clipboard
            clipboard = pyperclip.paste()
            textbox.insert(tk.END, clipboard)  # Insert the item into the entry widget

        return "break"

    def undo(self, textbox):
        # Check if input is a text widget
        if not (isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText)):
            return

        try:
            textbox.edit_undo()
        except tk.TclError:
            # nothing to undo
            pass

    def redo(self, textbox):
        # Check if input is a text widget
        if not (isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText)):
            return

        try:
            textbox.edit_redo()
        except tk.TclError:
            # nothing to redo
            pass

    def parse_text(self, textbox):
        # Accepts a tkinter text widget as input
        # Reads the text from the widget
        # Prints the list of nouns and verbs to the text widget

        # Check if input is a text widget
        if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
            # Get text from the text widget
            text = self.get_text(textbox)

            # Check if text was input
            if not text.strip():
                messagebox.showerror("Error", "You must enter text before parsing")
                return

            # Check for punctuation
            if not any(p in text for p in ".?!"):
                messagebox.showwarning("Possible Issue",
                                       "Text contains little or no punctuation; parsing accuracy may be reduced.")

            # Normalize input before tokenizing
            text = " ".join(text.split())

            # Parse the text
            nouns, verbs = ParsingEngine.parse_text(text)
            self.pos_lists.update_list(nouns, 0)    # Update Nouns
            self.pos_lists.update_list(verbs, 1)    # Update Verbs

            # If text has already been parsed, replace program-provided text
            text = text.replace("Nouns found in text: ", "")
            text = text.replace("Verbs found in text: ", "")

            # Turn lists into string
            nn_list = ', '.join(self.pos_lists.nouns)
            vb_list = ', '.join(self.pos_lists.verbs)

            noun_text = f"Nouns Found in Text ({len(self.pos_lists.nouns)}): " + nn_list
            verb_text = f"Verbs Found in Text ({len(self.pos_lists.verbs)}): " + vb_list

            self.erase_text(self.noun_box)
            self.erase_text(self.verb_box)
            self.noun_box.insert(tk.END, noun_text)
            self.verb_box.insert(tk.END, verb_text)

            # Reset POS count on Notebook Tabs
            self.update_tab_titles()


        return

    def erase_text(self, textbox):
        # Accepts a tkinter text widget as input
        # Erases the text in the text widget

        # Check if input is a text widget
        if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
            textbox.delete(1.0, tk.END)

            # Clear Undo history
            textbox.edit_reset()
        return

    def clear_noun_list(self, textbox):
        # Accepts a tkinter text widget as input
        # Erases the text in the textbox and Clears the contents of the list of Nouns
        if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
            self.erase_text(textbox)
            self.pos_lists.clear(0)
            self.update_tab_titles()

    def clear_verb_list(self, textbox):
        # Accepts a tkinter text widget as input
        # Erases the text in the textbox and Clears the contents of the list of Nouns
        if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
            self.erase_text(textbox)
            self.pos_lists.clear(1)
            self.update_tab_titles()

    def update_pos_list(self, textbox):
        # Accepts a tkinter text widget as input
        # Updates the list of words to reflect edits made by the user
        if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
            match textbox:
                case (self.noun_box):
                    # Get text from the textbox
                    edited_text = self.get_text(self.noun_box)

                    updated_text = self.pos_lists.apply_edits(edited_text, 0)

                    # Print the new list to the screen
                    self.erase_text(self.noun_box)
                    self.noun_box.insert(tk.END, updated_text)
                    self.update_tab_titles()


                case (self.verb_box):
                    # Get text from the textbox
                    edited_text = self.get_text(self.verb_box)

                    # Turn the list back into string for the textbox
                    updated_text = self.pos_lists.apply_edits(edited_text, 1)

                    # Print the new list to the screen
                    self.erase_text(self.verb_box)
                    self.verb_box.insert(tk.END, updated_text)
                    self.update_tab_titles()
            return

    def save_current_session(self):
        # Save data from the current session
        SessionManager.save_session(
            self.pos_lists.nouns,
            self.pos_lists.verbs,
            self.pos_lists.narratives
        )

    def erase_all(self):
        # Erase main textbox, noun/verb boxes, internal lists, narratives
        if not messagebox.askyesno("Confirm Erase All", "Erase all text, lists, narratives, and session state?"):
            return

        # Clear Textboxes
        self.erase_text(self.textbox)
        self.erase_text(self.noun_box)
        self.erase_text(self.verb_box)

        # Clear Lists
        self.pos_lists.clear(0)
        self.pos_lists.clear(1)
        self.pos_lists.narratives = {}

        # Clear Undo History
        self.textbox.edit_reset()
        self.noun_box.edit_reset()
        self.verb_box.edit_reset()

        # Reset POS count on Notebook Tabs
        self.update_tab_titles()

    def update_tab_titles(self):
        # Update the count of each list shown on the tabs of the notebook
        self.notebook.tab(self.noun_frame, text=f"List of Nouns ({len(self.pos_lists.nouns)})")
        self.notebook.tab(self.verb_frame, text=f"List of Verbs ({len(self.pos_lists.verbs)})")

# ------------------ Run the Grammar Parser ------------------
if __name__ == "__main__":
    app = GrammarParser()
    app.protocol("WM_DELETE_WINDOW", lambda: (app.save_current_session(), app.destroy()))
    app.mainloop()

