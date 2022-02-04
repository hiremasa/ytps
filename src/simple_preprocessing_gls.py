"""
This script takes TIC ID or TOI ID, then executes GLS(generalized lomb scargle and returns result figures and csv files.
If args.collect=True, this code summarize all outputs from TIC results within the same sector into 1 dataframe.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  
import math
import gc
import sys
import warnings
warnings.simplefilter('ignore')
from tqdm import tqdm

import lightkurve as lk
import astropy.units as u
import argparse
from glob import glob
from gls import Gls


parser = argparse.ArgumentParser(description='Output Fig & CSV file from one star by\
                    Simple Preprocessing and GLS')
parser.add_argument('--target_star', type=str, default="TOI 540", help='the name of target star (default: "TOI540")')
parser.add_argument('--NAME', type=str, default=None, help='name of the target (default: None)')
parser.add_argument('--TOI', type=int, default=None, help='TOI (default: None)')
parser.add_argument('--TIC', type=int, default=None, help='TIC (default: None)')
parser.add_argument('--author', type=str, default="SPOC", help='author (default: "SPOC")')
parser.add_argument('--exptime', type=int, default=120, help='exposure time')
parser.add_argument('--sigma_lower', type=int, default=3, help='sigma_lower for remove outliers (default: 3)')
parser.add_argument('--sigma_upper', type=int, default=3, help='sigma_upper for remove outliers (default: 3)')
parser.add_argument('--Pbeg', type=float, default=0.01, help='minimumn P(period) value (default: 0.1)')
parser.add_argument('--Pend', type=float, default=10, help='maximumn P(period) value (default: 10)')
parser.add_argument('--verbose', action="store_true", default=False, help='verbose (default: False)')
parser.add_argument('--collect', type=bool, default=False, help='collect all outputs (default: False)')
parser.add_argument('--sector_all', type=bool, default=False, help='select lc from all sectors or only one sector (default: True)')
parser.add_argument('--experiment_name', type=str, default=None, help='folder under output dir according to the experiment')
parser.add_argument('--sector_number', type=int, default=None, help='the number of sector')
args = parser.parse_args()

if not os.path.exists(f"../output/{args.experiment_name}"):
    os.makedirs(f"../output/{args.experiment_name}")
    os.makedirs(f"../output/{args.experiment_name}/images")
    os.makedirs(f"../output/{args.experiment_name}/dataframes")

def plot_4figures(args, lc, lc_clean, gls, preds):
    fig, axes = plt.subplots(2, 2, figsize=(10, 10), tight_layout=True, facecolor="whitesmoke")
    fig.suptitle(f"TOI {args.TOI}, TIC {lc.TICID}, sector {lc.SECTOR}", fontsize=30)
    axes = axes.flatten()

    #plot raw flux
    ax = axes[0]
    ax.plot(lc.time.value, lc.flux.value)
    ax.set_title("Raw Light Curve", fontsize=20)
    ax.set_xlabel("Time [JD - 2457000]", fontsize=12)
    ax.set_ylabel("Raw Flux", fontsize=12)

    #plot clear flux
    ax = axes[1]
    ax.plot(lc_clean.time.value, lc_clean.flux.value)
    ax.set_title("Clean Light Curve", fontsize=20)
    ax.set_xlabel("Time [JD - 2457000]", fontsize=12)
    ax.set_ylabel("Normalized Flux", fontsize=12)

    #plot power
    ax = axes[2]
    ax.plot(1/gls.freq, gls.power)
    ax.scatter(preds["P"], gls.pmax, color="green", s=40)#, label="$P_{max}=$"+f"{gls.pmax:.2f}")
    for m in range(1, int(max(1/gls.freq)//preds["P"]) + 1):
        if m == 1:
            ax.axvline(x=preds["P"], color="red", label ="$P_{rot}=$"+f"{preds['P']:.2f}", )
        else:
            ax.axvline(x=preds["P"]*m , linestyle=":", color="black")
            ax.axvline(x=preds["P"]/m , linestyle=":", color="black")
    ax.legend()

    ax.set_title("Peridogram", fontsize=20)
    ax.set_xlabel("Time [day]", fontsize=12)
    ax.set_ylabel("Power", fontsize=12)

    #plot folded light curve
    ax = axes[3]
    phase = ((lc_clean.time.value - preds["T0"]) / preds["P"])%1 
    y = preds["offset"] + preds["amp"] * np.sin(2*np.pi*phase + preds["ph"])
    cb = ax.scatter(phase*preds["P"], lc_clean.flux.value, s=10, c=lc_clean.time.value)
    plt.colorbar(cb, label="Time [JD - 2457000]")
    ax.scatter(phase*preds["P"], y, color='r', s=10)
    ax.set_title("Folded Light Curve", fontsize=20)
    ax.set_xlabel("Phase [day]", fontsize=12)
    ax.set_ylabel("Normalized Flux", fontsize=12)


    return fig


def Execute_GLS(lc_clean):
    df = [lc_clean.time.value, lc_clean.flux.value, lc_clean.flux_err.value]
    if args.verbose:
        print("Running GLS")
    gls = Gls(df, Pbeg=args.Pbeg, Pend=args.Pend)
    preds = gls.best
    preds["pmax"] = gls.pmax

    return gls, preds


if __name__ == "__main__":
    print("==================================================")
    if args.collect:
        files = glob(f"../output/{args.experiment_name}/dataframes/*.csv")
        files.sort()

        ss = []
        for f in tqdm(files):
            s = pd.read_csv(f, squeeze=True, index_col=0)
            ss.append(s)

        all_df = pd.concat(ss, axis=1)
        all_df.to_csv(f"../output/{args.experiment_name}/all_df.csv")

        df_all = pd.read_csv(f"../output/{args.experiment_name}/all_df.csv", index_col=0)
        df_all = df_all.transpose()
        all_df_sort_pmax = df_all.sort_values("pmax", ascending=False)
        all_df_sort_pmax.to_csv(f"../output/{args.experiment_name}/all_df_sort_pmax.csv")

    else:
        try:
            #set up for arguments
            if args.NAME is not None:
                target_star = args.NAME
            elif args.TOI is not None:
                target_star = f"TOI {args.TOI}"
            elif args.TIC is not None:
                target_star = f"TIC {args.TIC}"
            else:
                 target_star = args.target_star

            if args.TOI is not None:
                name = f"TOI{str(args.TOI).zfill(4)}"
            else:
                name = target_star.replace(" ", "")

            if args.TOI is None and args.TIC is not None:
                try:
                    df_tois = pd.read_csv("dataframe/TOIs.csv")
                    args.TOI = math.floor(df_tois[df_tois["TIC ID"]==args.TIC]["TOI"].unique()[0])
                except:
                    pass

            #search lc 
            if args.verbose:
                print(f"***Searching for {target_star}")
            lc_file = lk.search_lightcurve(target_star, author=args.author, exptime=args.exptime, sector=args.sector_number)
            if not lc_file:
                raise ValueError("Warning: No Light Curves found")


            if args.sector_all:
                for lc_item in lc_file:
                    lc = lc_item.download()
                    lc_clean = lc.normalize().remove_nans().remove_outliers(sigma_lower=args.sigma_lower, sigma_upper=args.sigma_upper)
                    print(f"Successfully downloaded the Light Curve of {name}")
                    gls, preds = Execute_GLS(lc_clean=lc_clean)
                    print('GLS has done')

                    #save the results
                    fig = plot_4figures(args, lc, lc_clean, gls, preds)
                    sector = str(lc.sector).zfill(2)
                    fig.savefig(f"../output/{args.experiment_name}/images/{name}_SECTOR{sector}.png".replace(" ", ""))
                    plt.close()
                    pd.Series(preds, name=f"{name}_SECTOR{sector}").to_csv(f"../output/{args.experiment_name}/dataframes/{name}_SECTOR{sector}.csv".replace(" ", ""))
                    print("Successfully Finished!!")
            else: #args.sector_all==False
                lc = lc_file[0].download()
                lc_clean = lc.normalize().remove_nans().remove_outliers(sigma_lower=args.sigma_lower, sigma_upper=args.sigma_upper)
                print(f"Successfully downloaded the Light Curve of {name}")

                gls, preds = Execute_GLS(lc_clean=lc_clean)
                print('GLS has done;')

                #save the results
                fig = plot_4figures(args, lc, lc_clean, gls, preds)
                sector = str(lc.sector).zfill(2)
                fig.savefig(f"../output/{args.experiment_name}/images/{name}_SECTOR{sector}.png")
                plt.close()
                pd.Series(preds, name=f"{name}_SECTOR{sector}").to_csv(f"../output/{args.experiment_name}/dataframes/{name}_SECTOR{sector}.csv".replace(" ", ""))
                print("Successfully Finished!!")
        except Exception as e:
            print(e)
        print("==================================================")
