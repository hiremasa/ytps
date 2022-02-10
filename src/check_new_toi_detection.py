import os
import sys
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='check if this pipeline detected newly found TOI')
parser.add_argument('--date', type=str, default='2022-02-08', help='the date for TOI added')
args = parser.parse_args()

f = lambda x: str(x).split('.')[0]

if __name__ == '__main__':
    df_tois = pd.read_csv('./dataframe/TOIs.csv', index_col=0)
    df_tois_date = df_tois[df_tois['Date TOI Updated (UTC)']==args.date]

    with open(f'../log/{args.date}.txt', mode='a') as l:
        for _, row in df_tois_date.iterrows():
            toi = f(row.TOI)
            tic = row['TIC ID']
            # print(toi) returns TOI number 
            s = os.system(f'find ../output/sector*/tls_images/*/ -name \*png | grep {tic} \n')
            if s==0:
                l.write(str(toi) + '\n')


            




    

