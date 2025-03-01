from flask import Flask, render_template, request, jsonify
import json
from _mmlu.mmlu_prompt import get_init_archive, get_prompt, get_reflexion_prompt
from _mmlu.search import search
import pandas as pd
import os
import argparse

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Global variable to store the last uploaded file path
last_uploaded_file = None

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def run_search():
    try:
        # Get task description from request
        data = request.json
        task_description = data.get('task', '')  # Get task from request, empty string if not provided
        
        # Create parser and set default arguments
        parser = argparse.ArgumentParser()
        
        # Use the uploaded file path if available, otherwise use default
        global last_uploaded_file
        default_data_filename = os.path.join(app.config['UPLOAD_FOLDER'], last_uploaded_file) if last_uploaded_file else "dataset/mmlu.csv"
        app.logger.info(f'Dataset file: {default_data_filename}\n')
        
        parser.add_argument('--data_filename', type=str, default=default_data_filename)
        parser.add_argument('--valid_size', type=int, default=10)
        parser.add_argument('--test_size', type=int, default=10)
        parser.add_argument('--shuffle_seed', type=int, default=0)
        parser.add_argument('--n_repreat', type=int, default=1)
        parser.add_argument('--multiprocessing', action='store_true', default=False)
        parser.add_argument('--max_workers', type=int, default=1)
        parser.add_argument('--debug', action='store_true', default=True)
        parser.add_argument('--save_dir', type=str, default='results/')
        parser.add_argument('--expr_name', type=str, default="mmlu_results")
        parser.add_argument('--n_generation', type=int, default=10)
        parser.add_argument('--debug_max', type=int, default=3)
        parser.add_argument('--model',
                        type=str,
                        default='claude-3-haiku-20240307',
                        choices=['gpt-4-turbo-2024-04-09', 'claude-3-5-haiku-latest', 'gpt-4o-2024-05-13'])
        
        # Parse the default args
        args = parser.parse_args([])  # Empty list since we're using defaults
        
        # Add task description to args
        args.task_description = task_description
        
        # Check if dataset exists
        if not os.path.exists(args.data_filename):
            return jsonify({
                'success': False,
                'error': f'Dataset file not found: {args.data_filename}. Please ensure the dataset is in the correct location.'
            })

        # Check if save directory exists, create if not
        os.makedirs(args.save_dir, exist_ok=True)
        
        # Run the search function
        try:
            search(args)
            
            # Read the results file
            results_file = os.path.join(args.save_dir, f"{args.expr_name}_run_archive.json")
            with open(results_file, 'r') as f:
                archive = json.load(f)
            
            # Find the entry with the highest median fitness
            best_agent = None
            best_median = -1
            
            for entry in archive:
                if 'fitness' in entry:
                    # Extract median from fitness string
                    # Format: "95% Bootstrap Confidence Interval: (X%, Y%), Median: Z%"
                    try:
                        median = float(entry['fitness'].split('Median: ')[-1].rstrip('%'))
                        if median > best_median:
                            best_median = median
                            best_agent = entry
                    except:
                        continue
            
            if not best_agent:
                return jsonify({
                    'success': False,
                    'error': 'No valid results found in the archive.'
                })
            
            return jsonify({
                'success': True,
                'thoughts': f'Search completed successfully. Results saved to: {results_file}',
                'bestAgent': best_agent
            })
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return jsonify({
                'success': False,
                'error': f'Search process failed: {str(e)}',
                'traceback': error_trace
            })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to initialize search: {str(e)}',
            'traceback': error_trace
        })

@app.route('/get_archive', methods=['GET'])
def get_archive():
    archive = get_init_archive()
    return jsonify(archive)

@app.route('/get_agent_response', methods=['POST'])
def get_agent_response():
    data = request.json
    current_archive = data.get('archive', [])
    
    system_prompt, prompt = get_prompt(current_archive)
    # Your agent generation logic here
    
    return jsonify({
        "system_prompt": system_prompt,
        "prompt": prompt
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'error': 'Please upload a CSV file'})
    
    try:
        # Read the CSV file
        df = pd.read_csv(file)
        
        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        df.to_csv(filepath, index=False)
        
        # Update the global last uploaded file
        global last_uploaded_file
        last_uploaded_file = file.filename
        
        # Get preview data (first 5 rows)
        preview_data = df.head(5).to_dict('records')
        
        # Return file info and basic statistics
        return jsonify({
            'success': True,
            'filename': file.filename,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'preview': preview_data
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True) 