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

import tkinter as tk # For creating the GUI
from tkinter import ttk, font, messagebox, filedialog # For creating the GUI
from tkinter import scrolledtext # For creating the GUI
import nltk # For finding nouns and verbs
import pyperclip # Lets the user copy and paste text in tkinter window

# Download NLTK resources
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

# ------------------ Define Functions for Grammar Parser ------------------

def get_text(textbox):
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

def parse_text(textbox):
    # Accepts a tkinter text widget as input
    # Reads the text from the widget
    # Prints the list of nouns and verbs to the text widget

    # Check if input is a text widget
    if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
        # Get text from the text widget
        text = get_text(textbox)

        # If text has already been parsed, replace program-provided text
        text = text.replace("Nouns found in text: ", "")
        text = text.replace("Verbs found in text: ", "")
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

        # Turn lists into string
        noun_list = ', '.join(nouns)
        verb_list = ', '.join(verbs)
        parsed_text = "Nouns found in text: " + noun_list + "\n\nVerbs found in text: " + verb_list

        erase_text(textbox)
        textbox.insert(tk.END, parsed_text)

    return

# Ended up not using this method
def return_text(textbox, text):
    # Accepts a tkinter text widget and a string as input
    # Prints the string to the text widget

    # Check if input is a text widget and a string
    if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
        if isinstance(text, str):
            erase_text(textbox)
            textbox.insert(tk.END, text)

    return

def erase_text(textbox):
    # Accepts a tkinter text widget as input
    # Erases the text in the text widget

    # Check if input is a text widget
    if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
        textbox.delete(1.0, tk.END)

    return

def export_text(textbox):
    # Accepts a tkinter text widget as input
    # Writes the text in the text widget to a TXT file

    # Check if input is a text widget
    if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
        # Get text from the text widget
        text = get_text(textbox)

        # Export text to user-specified file
        if text:
            filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                    filetypes=[("Text files", "*.txt")])
            if filename:
                try:
                    with open(filename, "w", encoding="utf-8") as file:
                        file.write(text)
                        messagebox.showinfo("Exported",
                                            f"Text saved as {filename}")
                except Exception as e:
                    messagebox.showinfo("Error",
                                        f"Error saving file: {e}")

    return

def show_context_menu(event):

    # Show the context menu
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()  # Release the grab when the menu is dismissed

def copy(textbox):
    # Accepts a tkinter text widget as input
    # Lets the user copy the text in the text widget

    # Check if input is a text widget
    if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
        text = get_text(textbox)  # Get the text inside entry widget
        main_window.clipboard_clear()  # Clear the tkinter clipboard
        main_window.clipboard_append(text)  # Append to system clipboard

def paste(textbox):
    # Accepts a tkinter text widget as input
    # Lets the user paste text to the text widget

    # Check if input is a text widget
    if isinstance(textbox, tk.Entry) or isinstance(textbox, scrolledtext.ScrolledText):
        #clipboard = main_window.clipboard_get()  # Get the copied item from system clipboard
        clipboard = pyperclip.paste()
        textbox.insert(tk.END, clipboard)  # Insert the item into the entry widget

    return "break"


# ------------------ Create GUI for Grammar Parser ------------------

# Create the main window
main_window = tk.Tk()  # Create the main GUI window
main_window.title("Tiny Tool: Grammar Parser")  # Set title
main_window.geometry("800x800")  # Set window size

# Create the main frame to contain all widgets
container = tk.Frame(main_window)
container.pack(side="top", fill="both", expand=True)
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

# Create welcome label
welcome_label = tk.Label(container, text="Welcome to Grammar Parser!")
welcome_label.pack(side="top", fill="x", pady=10)

# Create instructions label
instructions_label = tk.Label(container, text="Enter text for Grammar Parsing:")
instructions_label.pack(pady=20)

# Create text widget with scrollbar
textbox = scrolledtext.ScrolledText(container, wrap=tk.WORD, width=40, height=10)
textbox.pack(padx=10, pady=10)

# Let user copy and paste in GUI and text widget
## using right-click menu and Ctrl+C and Ctrl+V
textbox.bind("<Button-3>", lambda event: show_context_menu(event))
textbox.bind("<Control-KeyPress-c>", lambda event: copy(textbox))
textbox.bind("<Control-KeyPress-v>", lambda event: paste(textbox))
#textbox.bind("<Command-KeyPress-v>", lambda event: paste(textbox))

# Create context menu for user
context_menu = tk.Menu(main_window, tearoff=0)
context_menu.add_command(label="Copy", command=lambda: copy(textbox))
context_menu.add_separator()  # Optional separator
context_menu.add_command(label="Paste", command=lambda: paste(textbox))

# Create buttons to use tool
parse_button = tk.Button(container, text="Parse Text", command=lambda: parse_text(textbox))
parse_button.pack()
export_button = tk.Button(container, text="Save as TXT File", command=lambda: export_text(textbox))
export_button.pack()
erase_button = tk.Button(container, text="Erase Text", command=lambda: erase_text(textbox))
erase_button.pack()

# Create note label
note_label = tk.Label(container, text="Note: The program returns a list of verbs and nouns in " \
        "accordance with the NLTK database. The text returned may be edited after the list is presented." \
        " Please ensure correct punctuation for the best results.", wraplength=250)
note_label.pack(pady=20)
note_label.config(state=tk.DISABLED, disabledforeground="black")


# ------------------ Run the Grammar Parser ------------------

main_window.mainloop()
