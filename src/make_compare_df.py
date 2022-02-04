import os
import sys
import pandas as pd
import argparse
parser = argparse.ArgumentParser(description='summarize all dataframes into all_df.csv')
parser.add_argument('--experiment_name', type=str, default=None, help='folder name under .output/ according to the experiment')
args = parser.parse_args()
if __name__ == "__main__":
    df_all = pd.read_csv(f"../output/{args.experiment_name}/all_df.csv", index_col=0)
    df_all = df_all.transpose()

    df_all["TOI"] = df_all.index.map(lambda x: x.split("_")[0])

    df_temp = df_all.groupby("TOI").mean()["P"]
    df_compare = pd.DataFrame(index=df_temp.index)
    df_compare["P_mean"] = df_temp.values
    df_compare["P_std"] = df_all.groupby("TOI").std(ddof=0)["P"].values

    df_compare.to_csv(f"../output/{args.experiment_name}/compare_df.csv")
