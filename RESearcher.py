import os
import tkinter as tk
from tkinter import filedialog, messagebox
import nbformat
import subprocess
import urllib.parse

class NotebookSearcher:
    def __init__(self, directory, search_text, file_type):
        self.directory = directory
        self.search_text = search_text
        self.file_type = file_type

    def search_in_notebook(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                notebook = nbformat.read(f, as_version=4)
                for cell in notebook.cells:
                    if cell.cell_type in ['markdown', 'code']:
                        if self.search_text in cell.source:
                            return True
        except Exception as e:
            print(f"Processing file error {file_path}: {e}")
        return False

    def search(self):
        results = []
        for root, _, files in os.walk(self.directory):
            for file in files:
                if file.endswith(self.file_type):
                    file_path = os.path.join(root, file)
                    if self.search_in_notebook(file_path):
                        results.append(file_path)
        return results


class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RESearcher")

        self.directory = tk.StringVar()
        self.search_text = tk.StringVar()
        self.file_type = tk.StringVar(value=".ipynb")
        self.open_with = tk.StringVar(value="VSCode")

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(padx=10, pady=10)

        # Entry for the directory
        label_directory = tk.Label(frame, text="Search in:")
        label_directory.grid(row=0, column=0, pady=5)
        entry_directory = tk.Entry(frame, textvariable=self.directory, width=40)
        entry_directory.grid(row=0, column=1, pady=5)
        btn_browse = tk.Button(frame, text="Explore...", command=self.browse_directory)
        btn_browse.grid(row=0, column=2, padx=5)

        # Entry for the search text
        label_text = tk.Label(frame, text="Search for:")
        label_text.grid(row=1, column=0, pady=5)
        entry_text = tk.Entry(frame, textvariable=self.search_text, width=40)
        entry_text.grid(row=1, column=1, pady=5)

        # Entry for the file type
        label_file_type = tk.Label(frame, text="File type:")
        label_file_type.grid(row=2, column=0, pady=5)
        entry_file_type = tk.Entry(frame, textvariable=self.file_type, width=40)
        entry_file_type.grid(row=2, column=1, pady=5)

        # Open with dropdown
        label_open_with = tk.Label(frame, text="Open with:")
        label_open_with.grid(row=3, column=0, pady=5)
        dropdown_open_with = tk.OptionMenu(frame, self.open_with, "VSCode", "Jupyter Notebook", "Show path")
        dropdown_open_with.grid(row=3, column=1, pady=5)

        # Results listbox
        label_results = tk.Label(frame, text="Results:")
        label_results.grid(row=4, column=0, pady=5)
        self.results_listbox = tk.Listbox(frame, width=60, height=10)
        self.results_listbox.grid(row=4, column=1, columnspan=2, pady=5)

        # Buttons to search and open
        btn_search = tk.Button(frame, text="Search", command=self.search)
        btn_search.grid(row=5, column=0, columnspan=1, pady=10)

        btn_open = tk.Button(frame, text="Open", command=self.open_selected_file)
        btn_open.grid(row=5, column=1, columnspan=2, pady=10)

    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select directory")
        if directory:
            self.directory.set(directory)

    def search(self):
        # Get input values
        directory = self.directory.get()
        search_text = self.search_text.get()
        file_type = self.file_type.get()

        if not directory or not search_text or not file_type:
            messagebox.showwarning("Error", "Please fill the blanks.")
            return

        # Search files
        searcher = NotebookSearcher(directory, search_text, file_type)
        results = searcher.search()

        # Display results
        self.results_listbox.delete(0, tk.END)
        for result in results:
            self.results_listbox.insert(tk.END, result)

    def open_selected_file(self):
        selected_file = self.results_listbox.get(tk.ANCHOR)  # Get selected file
        if not selected_file:
            messagebox.showwarning("Error", "No file was selected.")
            return

        open_with = self.open_with.get()
        if open_with == "VSCode":
            os.system(f'code "{selected_file}"')
        elif open_with == "Jupyter Notebook":
            url = self.generate_jupyter_url(selected_file)
            subprocess.run(["start", url], shell=True)  # Open the link in the browser
        elif open_with == "Show path":
            messagebox.showinfo("File path", f"Selected path:\n{selected_file}")

    @staticmethod
    def generate_jupyter_url(file_path):
        # Convert the path to a URL format compatible with Jupyter
        relative_path = os.path.relpath(file_path, start=os.path.expanduser("~"))
        url_path = urllib.parse.quote(relative_path.replace("\\", "/"))
        return f"http://localhost:8889/lab/tree/{url_path}"


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()