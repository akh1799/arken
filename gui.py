import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
import argparse
import threading
import ttkbootstrap as tb
from ttkbootstrap.constants import *    
from _mmlu.search import search, AgentSystem, bootstrap_confidence_interval    

class SearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MMLU Search GUI")
        self.root.state("zoomed")  

        # Set dark theme colors
        bg_color = '#2E2E2E'  # Dark grey
        text_color = 'white'
        
        # Configure root window background
        self.root.configure(bg=bg_color)

        # Set default font size and styles
        default_font = ('TkDefaultFont', 14)
        text_font = ('TkTextFont', 14)
        
        # Initialize style with dark theme
        style = ttk.Style()
        style.theme_use('darkly')  # Changed from theme= to theme_use()
        style.configure('.', font=default_font)
        style.configure('TLabel', font=default_font)
        style.configure('TButton', font=default_font)

        main_frame = ttk.Frame(root, padding="10", style='TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        # Configure text widgets with dark theme
        text_config = {
            'font': text_font,
            'bg': bg_color,
            'fg': text_color,
            'insertbackground': text_color,
            'selectbackground': '#404040',
            'selectforeground': text_color,
            'relief': 'solid',
            'borderwidth': 1
        }

        # Example Input/Output at the top
        ttk.Label(main_frame, text="Example Input/Output:", style='TLabel').grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        self.example_text = scrolledtext.ScrolledText(main_frame, height=10, width=80, **text_config)
        self.example_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Results in the middle
        ttk.Label(main_frame, text="Best Model:", style='TLabel').grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        self.results_text = scrolledtext.ScrolledText(main_frame, height=10, width=80, **text_config)
        self.results_text.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Status bar
        status_frame = ttk.Frame(main_frame, style='TFrame')
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Label(status_frame, text="Status:", style='TLabel').pack(side=tk.LEFT)
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.progress_var, style='TLabel').pack(side=tk.LEFT, padx=(5, 0))

        # Bottom frame
        bottom_frame = ttk.Frame(main_frame, style='TFrame')
        bottom_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        bottom_frame.grid_columnconfigure(0, weight=1)

        # Task description
        ttk.Label(bottom_frame, text="Task Description:", style='TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.task_text = tk.Text(bottom_frame, height=1, width=80, wrap=tk.WORD, **text_config)
        self.task_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.task_text.bind("<KeyRelease>", self.adjust_textbox_height)

        # Search button
        self.search_button = ttk.Button(bottom_frame, text="Search", command=self.start_search)
        self.search_button.pack(side=tk.LEFT, padx=(0, 5))

    def adjust_textbox_height(self, event=None):
        content = self.task_text.get("1.0", "end-1c")
        num_lines = int(self.task_text.index("end-1c").split(".")[0])

        min_lines = 1
        max_lines = 10

        new_height = min(max(num_lines, min_lines), max_lines)
        self.task_text.config(height=new_height)

    def start_search(self):
        if not self.task_text.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "Please enter a task description")
            return

        self.search_button.state(['disabled'])
        self.progress_var.set("Searching...")

        thread = threading.Thread(target=self.run_search)
        thread.daemon = True
        thread.start()

    def run_search(self):
        try:
            parser = argparse.ArgumentParser()
            args = parser.parse_args([])
            args.data_filename = "dataset/mmlu.csv"
            args.valid_size = 128
            args.test_size = 800
            args.shuffle_seed = 0
            args.n_repreat = 1
            args.multiprocessing = True
            args.max_workers = 48
            args.debug = True
            args.save_dir = 'results/'
            args.expr_name = "mmlu_gpt3.5_results"
            args.n_generation = 30
            args.debug_max = 3
            args.model = 'gpt-3.5-turbo-0125'

            search(args)

            file_path = os.path.join(args.save_dir, f"{args.expr_name}_run_archive.json")
            with open(file_path, 'r') as json_file:
                archive = json.load(json_file)

            best_fitness = -1
            best_model = None
            for solution in archive:
                if 'fitness' in solution:
                    fitness_str = solution['fitness']
                    mean = float(fitness_str.split('±')[0].strip())
                    if mean > best_fitness:
                        best_fitness = mean
                        best_model = solution

            if best_model:
                self.results_text.delete("1.0", tk.END)
                self.results_text.insert(tk.END, f"Best Model (Fitness: {best_model['fitness']}):\n\n")
                self.results_text.insert(tk.END, best_model['code'])

            self.progress_var.set("Search Complete!")

        except Exception as e:
            self.progress_var.set("Error occurred!")
            messagebox.showerror("Error", str(e))
        finally:
            self.search_button.state(['!disabled'])

def main():
    root = tb.Window(themename="darkly")  # Changed from tk.Tk() to tb.Window()
    app = SearchGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
