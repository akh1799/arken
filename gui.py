import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
from _mmlu.search import search, AgentSystem, bootstrap_confidence_interval
import argparse
import threading

class SearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MMLU Search GUI")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Task Description
        ttk.Label(main_frame, text="Task Description:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.task_text = scrolledtext.ScrolledText(main_frame, height=10, width=80)
        self.task_text.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Example Input/Output
        ttk.Label(main_frame, text="Example Input/Output:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.example_text = scrolledtext.ScrolledText(main_frame, height=10, width=80)
        self.example_text.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Progress
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, text="Status:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Results
        ttk.Label(main_frame, text="Best Model:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.results_text = scrolledtext.ScrolledText(main_frame, height=10, width=80)
        self.results_text.grid(row=6, column=0, columnspan=2, pady=5)
        self.results_text.configure(state='disabled')
        
        # Search Button
        self.search_button = ttk.Button(main_frame, text="Start Search", command=self.start_search)
        self.search_button.grid(row=7, column=0, columnspan=2, pady=10)

    def start_search(self):
        if not self.task_text.get("1.0", tk.END).strip():
            messagebox.showerror("Error", "Please enter a task description")
            return
            
        self.search_button.state(['disabled'])
        self.progress_var.set("Searching...")
        
        # Create thread for search
        thread = threading.Thread(target=self.run_search)
        thread.daemon = True
        thread.start()

    def run_search(self):
        try:
            # Setup args
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
            
            # Run search
            search(args)
            
            # Get results
            file_path = os.path.join(args.save_dir, f"{args.expr_name}_run_archive.json")
            with open(file_path, 'r') as json_file:
                archive = json.load(json_file)
            
            # Find best model
            best_fitness = -1
            best_model = None
            for solution in archive:
                if 'fitness' in solution:
                    fitness_str = solution['fitness']
                    # Extract mean from confidence interval string
                    mean = float(fitness_str.split('±')[0].strip())
                    if mean > best_fitness:
                        best_fitness = mean
                        best_model = solution
            
            if best_model:
                self.results_text.configure(state='normal')
                self.results_text.delete("1.0", tk.END)
                self.results_text.insert(tk.END, f"Best Model (Fitness: {best_model['fitness']}):\n\n")
                self.results_text.insert(tk.END, best_model['code'])
                self.results_text.configure(state='disabled')
            
            self.progress_var.set("Search Complete!")
            
        except Exception as e:
            self.progress_var.set("Error occurred!")
            messagebox.showerror("Error", str(e))
        finally:
            self.search_button.state(['!disabled'])

def main():
    root = tk.Tk()
    app = SearchGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 