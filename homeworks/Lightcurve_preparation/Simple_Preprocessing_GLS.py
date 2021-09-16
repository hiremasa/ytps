import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  

import gc
import sys
sys.path.append('../../GLS/python/')

import lightkurve as lk
from astropy.timeseries import LombScargle
import astropy.units as u
from gls import Gls
import argparse


parser = argparse.ArgumentParser(description='Output Fig & CSV file from one star by\
                    Simple Preprocessing and GLS')
parser.add_argument('--target_star', type=str, default="TOI540",
                    help='the name of target star (default: "TOI540")')
parser.add_argument('--author', type=str, default="SPOC",
                    help='author (default: "SPOC")')
parser.add_argument('--exptime', type=int, default=120,
                    help='exposure time')
parser.add_argument('--sigma', type=int, default=10,
                    help='sigma for remove outliers (default: 10)')
parser.add_argument('--Pbeg', type=float, default=0.1,
                    help='minimumn P(period) value (default: 0.1)')
parser.add_argument('--Pend', type=float, default=10,
                    help='maximumn P(period) value (default: 10)')

args = parser.parse_args()

def plot_4figures(lc, lc_clean, gls, preds):
    fig, axes = plt.subplots(2, 2, figsize=(10,10), tight_layout=True, facecolor="whitesmoke")
    fig.suptitle(f"TIC {lc.TICID}, sector {lc.SECTOR}", fontsize=30)
    axes = axes.flatten()
    ax = axes[0]
    ax.plot(lc.time.value, lc.flux.value)
    ax.set_title("Raw Light Curve", fontsize=20)
    ax.set_xlabel("Time [JD - 2457000]", fontsize=12)
    ax.set_ylabel("Raw Flux", fontsize=12)


    ax = axes[1]
    ax.plot(lc_clean.time.value, lc_clean.flux.value)
    ax.set_title("Clean Light Curve", fontsize=20)
    ax.set_xlabel("Time [JD - 2457000]", fontsize=12)
    ax.set_ylabel("Normalized Flux", fontsize=12)

    ax = axes[2]
    ax.plot(1/gls.freq, gls.power)
    #ax.scatter(preds["P"], gls.pmax, color="r", s=40, label="$P_{max}=$"+f"{gls.pmax:.2f}")
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

    ax = axes[3]
    phase = ((lc_clean.time.value - preds["T0"]) / preds["P"])%1 
    y = preds["offset"] + preds["amp"] * np.sin(2*np.pi*phase + preds["ph"])
    ax.scatter(phase*preds["P"], lc_clean.flux.value, s=10)
    ax.scatter(phase*preds["P"], y, color='r', s=10)
    ax.set_title("Folded Light Curve", fontsize=20)
    ax.set_xlabel("Phase [day]", fontsize=12)
    ax.set_ylabel("Normalized Flux", fontsize=12)


    return fig


if __name__ == "__main__":
    target_star = args.target_star
    lc_file = lk.search_lightcurve(args.target_star, author=args.author, exptime=args.exptime)
    lc = lc_file[0].download()
    lc_clean = lc.normalize().remove_nans().remove_outliers(sigma=args.exptime)

    df = [lc_clean.time.value, lc_clean.flux.value, lc_clean.flux_err.value]
    gls = Gls(df, Pbeg=args.Pbeg, Pend=args.Pend)
    preds = gls.best

    #save the results
    fig = plot_4figures(lc, lc_clean, gls, preds)
    fig.savefig(f"{args.target_star}_{lc.SECTOR}.png")
    pd.Series(preds).to_csv(f"{args.target_star}.csv")

