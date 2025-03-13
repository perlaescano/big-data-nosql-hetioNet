
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tkinter as tk
from tkinter import ttk, scrolledtext
from scripts.queries import get_disease_info, find_new_drugs

class App(tk.Tk):
    """
    The main application class that manages GUI navigation.
    """
    def __init__(self):
        super().__init__()
        self.title("Hetio Data Analysis on Neo4j Database")
        self.geometry("700x600")
        
        # Container for different pages
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        # Dictionary to hold pages
        self.pages = {}
        for Page in (InitPage, Query1Page, Query2Page):
            page = Page(self.container, self)
            self.pages[Page] = page
            page.grid(row=0, column=0, sticky="nsew")
        
        self.show_page(InitPage)
    
    def show_page(self, page_class):
        """
        Displays the requested page by raising it to the front.
        :param page_class: The class of the page to display.
        """
        page = self.pages[page_class]
        page.tkraise()

class InitPage(tk.Frame):
    """
    The initial page (Main menu) that provides navigation options for different queries.
    """
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Centering Frame for Buttons
        center_frame = tk.Frame(self)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')  
        center_frame.pack(expand=True)

        # Query 1 description
        text_query1 = ("Query 1\n"
            "   Given a disease id, what is its name,\n"
            "   what are drug names that can treat or palliate this disease,\n"
            "   what are gene names that cause this disease, and\n"
            "   where this disease occurs?\n"
            "   Obtain and output this information in a single query.")

        # Query 2 description
        text_query2 = ("Query 2\n"
            "   We assume that a compound can treat a disease \n"
            "   if the compound up-regulates/down-regulates a gene, \n"
            "   but the location down-regulates/up-regulates the gene \n"
            "   in an opposite direction where the disease occurs. \n"
            "   Find all compounds that can treat a new disease \n"
            "   (i.e. the missing edges between compound and disease excluding existing drugs). \n"
            "   Obtain and output all drugs in a single query.")

        # Button for Query 1
        button1 = tk.Button(center_frame, text=text_query1, width=70, height=5, anchor='nw', justify='left', 
                            command=lambda: controller.show_page(Query1Page), font=("Arial", 14))
        button1.pack(padx=30, pady=20)

        # Button for Query 2
        button2 = tk.Button(center_frame, text=text_query2, width=70, height=5, anchor='nw', justify='left',  
                            command=lambda: controller.show_page(Query2Page), font=("Arial", 14))
        button2.pack(padx=30, pady=20)
        
class Query1Page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = tk.Label(self, text="Enter the disease id", font=("Arial", 14))
        label.pack(padx=30, pady=10)

        # Entry widget for user input
        self.entry = tk.Entry(self, font=("Arial", 14))
        self.entry.pack(padx=30, pady=10)

        # Button to get the input and display it
        button1 = tk.Button(self, text="Execute Query 1", command=self.get_query_result, font=("Arial", 14))
        button1.pack(padx=30, pady=10)

        button2 = tk.Button(self, text="Back to Main Page", command=lambda: controller.show_page(InitPage), font=("Arial", 14))
        button2.pack(padx=30, pady=10)

        # Create Text widget for displaying content
        self.text_widget = scrolledtext.ScrolledText(self, wrap="word", font=("Arial", 14), padx=10, pady=10, height=15)
        self.text_widget.config(state="disabled")

        # Layout configuration
        self.text_widget.pack(padx=10, pady=10, expand=True, fill="both")

    def get_query_result(self):
        #print("Result of Query 1")
        disease_id = self.entry.get().strip()

        if not disease_id.startswith("Disease::"):
            output_text = "Invalid Disease ID format. Use 'Disease::<ID>'."
        else:
            output_text = get_disease_info(disease_id)  

        self.update_output(output_text)

    def update_output(self, text):
        # Enable text widget to insert new content
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)  # Clear existing text
        self.text_widget.insert("1.0", text)    # Insert new text
        self.text_widget.config(state="disabled")   # Disable editing again

class Query2Page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        button1 = tk.Button(self, text="Execute Query 2", command=self.get_query_result, font=("Arial", 14))
        button1.pack(padx=30, pady=10)

        button2 = tk.Button(self, text="Back to Main Page", command=lambda: controller.show_page(InitPage), font=("Arial", 14))
        button2.pack(padx=30, pady=10)

        self.text_widget = scrolledtext.ScrolledText(self, wrap="word", font=("Arial", 14), padx=10, pady=10, height=15)
        self.text_widget.config(state="disabled")

        self.text_widget.pack(padx=10, pady=10, expand=True, fill="both")

    def get_query_result(self):
        output_text = find_new_drugs()  
        self.update_output(output_text)

    def update_output(self, text):
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)  # Clear existing text
        self.text_widget.insert("1.0", text)    # Insert new text
        self.text_widget.config(state="disabled")   # Disable editing again

if __name__ == "__main__":
    app = App()
    app.mainloop()
