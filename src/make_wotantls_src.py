import os
import numpy as np
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Make GP wotan & TLS python script from "output/sectorxx/all_df_sort_pmax.csv"')
parser.add_argument('--upper_thresh', type=float, default=1.0, help='upper threshold of Pmax value')
parser.add_argument('--lower_thresh', type=float, default=0.8, help='lower threshold of Pmax value')
parser.add_argument('--experiment_name', type=str, default=None, help='folder under output dir according to the experiment')
parser.add_argument('--sector_number', type=int, default=None, help='the number of sector')
args = parser.parse_args()

if __name__ == '__main__':
    all_sorted_df = pd.read_csv(f'../output/{args.experiment_name}/all_df_sort_pmax.csv', index_col=0)
    select_df = all_sorted_df[(args.upper_thresh >= all_sorted_df['pmax']) &  (all_sorted_df['pmax'] >= args.lower_thresh)]
    for idx, (tic_id, row) in enumerate(select_df.iterrows()):
        tic_number = tic_id.split('_')[0].split('TIC')[1]
        #print(f'python execute_wotan_tls.py --TIC {tic_number} --sector_number {args.sector_number} --experiment_name {args.experiment_name} --method gp --kernel squared_exp --kernel_size 2 --tag {idx + 1}')
        print(f'python execute_wotan_tls.py --TIC {tic_number} --sector_number {args.sector_number} --experiment_name {args.experiment_name} --method hspline --window_length 0.3 --tag {idx + 1}')


