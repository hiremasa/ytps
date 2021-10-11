import os
import gc
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  
import warnings
warnings.simplefilter('ignore')
from tqdm import tqdm
import argparse
from glob import glob

import lightkurve as lk
from astropy.timeseries import LombScargle
import astropy.units as u
from gls import Gls

from plot_gls import get_transit_mask, plot_tls

parser = argparse.ArgumentParser(description='Download lc, then preprocess, applying wotan and TLS')
parser.add_argument('--target_star', type=str, default=None, help='the name of target star (default: None)')
parser.add_argument('--NAME', type=str, default=None, help='name of the target (default: None)')
parser.add_argument('--TOI', type=int, default=None, help='TOI (default: None)')
parser.add_argument('--TIC', type=int, default=None, help='TIC (default: None)')
parser.add_argument('--author', type=str, default="SPOC", help='author (default: "SPOC")')
parser.add_argument('--exptime', type=int, default=120, help='exposure time')
parser.add_argument('--sigma_lower', type=int, default=20, help='sigma_lower for remove outliers (default: 20)')
parser.add_argument('--sigma_upper', type=int, default=10, help='sigma_upper for remove outliers (default: 10)')
parser.add_argument('--Pbeg', type=float, default=0.1, help='minimumn P(period) value (default: 0.1)')
parser.add_argument('--Pend', type=float, default=10, help='maximumn P(period) value (default: 10)')
parser.add_argument('--verbose', action="store_true", default=False, help='verbose (default: False)')
parser.add_argument('--experiment_name', type=str, default=None, help='folder under output dir according to the experiment')
parser.add_argument('--sector_number', type=int, default=None, help='the number of sector')
parser.add_argument('--method', type=str, default='biweight', help='the method for wotan.flatten(default: biweight)')
parser.add_argument('--window_length', type=int, default=0.3, help='the value for the arguent of wotan.flatten')

args = parser.parse_args()


if not os.path.exists(f"../output/{args.experiment_name}"):
    os.makedirs(f"../output/{args.experiment_name}")
    os.makedirs(f"../output/{args.experiment_name}/images")
    os.makedirs(f"../output/{args.experiment_name}/dataframes")

    
def Excecut_GLS(lc_clean):
    df = [lc_clean.time.value, lc_clean.flux.value, lc_clean.flux_err.value]
    if args.verbose:
        print("Running GLS")
    gls = Gls(df, Pbeg=args.Pbeg, Pend=args.Pend)
    preds = gls.best
    preds["pmax"] = gls.pmax

    return gls, preds


if __name__ == "__main__":
    print("==================================================")

    try:
        #load lc
        if args.NAME is not None:
            target_star = args.NAME
        elif args.TOI is not None:
            target_star = f'TOI {str(args.TOI).zfill(4)}'
        elif args.TIC is not None:
            target_star = f'{TIC {str(args.TIC).zfill(4)}'
        else:
             target_star = args.target_star
        if args.verbose:
            print(f"***Searching for {target_star}")
        lc_item = lk.search_lightcurve(target_star, author=args.author, exptime=args.exptime, sector=args.sector_number)
        if args.TOI is not None:
            name = f"TOI{str(args.TOI).zfill(4)}"
        else:
            name = target_star.replace(" ", "")
        if len(lc_file) < 1:
            raise ValueError("Warning: No Light Curves found")


        #args.sector_all==False
        lc = lc_item.download()
        lc_clean = lc.normalize().remove_nans().remove_outliers(sigma_lower=args.sigma_lower, sigma_upper=args.sigma_upper)
        print(f"Successfully downloaded the Light Curve of {name}")

        #execute Wotan
        print('Preparing Wotan...')
        time = lc_clean.time.value
        flux = lc_clean.flux.value
        flatten_lc, trend_lc = flatten(time, flux, window_length=args.window_length, return_trend=True, method=args.method, robust=True)
        print('Executed the Wotan flat')
        
        #execute TLS
        print('Preparing TLS..')
        model = transitleastsquares(time, flatten_lc)
        results = model.power()
        #save the results
        fig = plot_4figures(name, lc, lc_clean, gls, preds)
        sector = str(lc.sector).zfill(2)
        fig.savefig(f"../output/{args.experiment_name}/images/{name}_SECTOR{sector}.png")
        plt.close()
        pd.Series(preds, name=f"{name}_SECTOR{sector}").to_csv(f"../output/{args.experiment_name}/dataframes/{name}_SECTOR{sector}.csv".replace(" ", ""))
        print("Successfully Finished!!")
except Exception as e:
    print(e)
print("==================================================")
