import argparse
from _mmlu.search import search

parser = argparse.ArgumentParser()
args = parser.parse_args([])
args.data_filename = "dataset/mmlu.csv"
args.is_multiple_choice = True
args.valid_size = 100
args.test_size = 800
args.shuffle_seed = 0
args.n_repreat = 1
args.multiprocessing = False
args.max_workers = 1
args.debug = True
args.save_dir = 'results/'
args.expr_name = "mmlu_gpt3.5_results"
args.n_generation = 30
args.debug_max = 3
args.model = 'claude-3-5-haiku-latest'

search(args)