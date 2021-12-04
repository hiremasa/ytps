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
from wotan import flatten
from transitleastsquares import transitleastsquares, catalog_info
import h5py
import deepdish

from plot_tls import get_transit_mask, plot_tls
sys.path.append("../wotan/wotan")
from wotan import flatten
parser = argparse.ArgumentParser(description='Download lc, then preprocess, applying wotan and TLS')
parser.add_argument('--TOI', type=int, default=None, help='TOI (default: None)')
parser.add_argument('--TIC', type=int, default=None, help='TIC (default: None)')
parser.add_argument('--author', type=str, default="SPOC", help='author (default: "SPOC")')
parser.add_argument('--exptime', type=int, default=120, help='exposure time')
parser.add_argument('--sigma_lower', type=int, default=20, help='sigma_lower for remove outliers (default: 20)')
parser.add_argument('--sigma_upper', type=int, default=10, help='sigma_upper for remove outliers (default: 10)')
parser.add_argument('--verbose', action="store_true", default=False, help='verbose (default: False)')
parser.add_argument('--experiment_name', type=str, default=None, help='folder under output dir according to the experiment')
parser.add_argument('--sector_number', type=int, default=None, help='the number of sector')
parser.add_argument('--method', type=str, default='biweight', help='the method for wotan.flatten(default: biweight)')
parser.add_argument('--window_length', type=float, default=0.3, help='the value for the arguent of wotan.flatten')
parser.add_argument('--kernel', type=str, default='squared_exp', help='select one kernel(e.g squared_exp, matern)')
parser.add_argument('--kernel_size', type=int, default=1, help='select kernel size')
parser.add_argument('--period_min', type=float, default=0.5, help='min Minimum trial period (in units of days). If none is given, the limit is derived from the Roche limit')
parser.add_argument('--tag', type=str, default=None, help='tag for output file name')

args = parser.parse_args()

assert os.getcwd() == '/home/kobayashi/project/B4_research/src', \
                'cwd is incorrect(expected: /home/kobayashi/project/B4_research/src/)'
                
if not os.path.exists(f"../output/{args.experiment_name}"):
    raise ValueError('No existing experiment, set proper experiment_name')

if not os.path.exists(f'../output/{args.experiment_name}/tls_images'):
    os.makedirs(f'../output/{args.experiment_name}/tls_images')
    os.makedirs(f'../output/{args.experiment_name}/tls_hdf5') 
if __name__ == "__main__":
    print("==================================================")

    try:
        #load lc
        if args.TOI is not None:
            target_star = f'TOI {args.TOI}'
        elif args.TIC is not None:
            target_star = f'TIC {args.TIC}'
        if args.verbose:
            print(f"***Searching for {target_star}")
        lc_item = lk.search_lightcurve(target_star, author=args.author, exptime=args.exptime, sector=args.sector_number)
        if args.TOI is not None:
            name = f"TOI{str(args.TOI).zfill(4)}"
        else:
            name = target_star.replace(" ", "")
        if not lc_item:
            raise ValueError("Warning: No Light Curves found")

        lc = lc_item.download()
        lc_clean = lc.normalize().remove_nans().remove_outliers(sigma_lower=args.sigma_lower, sigma_upper=args.sigma_upper)
        print(f"Successfully downloaded the Light Curve of {name}")


        #execute Wotan
        print('Preparing Wotan...')
        time = lc_clean.time.value
        flux = lc_clean.flux.value
        if args.method == 'gp':
            flatten_lc, trend_lc = flatten(time, flux, return_trend=True, method=args.method, kernel=args.kernel, kernel_size=args.kernel_size, robust=True)
        else:
            flatten_lc, trend_lc = flatten(time, flux, window_length=args.window_length, return_trend=True, method=args.method, robust=True)
        print('Executed the Wotan flat')
        
        ab, R_star, R_star_min, R_star_max, M_star, M_star_min, M_star_max = catalog_info(TIC_ID=lc_clean.TICID) 
        print(catalog_info(TIC_ID=lc_clean.TICID))
        #execute TLS
        print('Preparing TLS..')
        model = transitleastsquares(time, flatten_lc)
        results = model.power(
            M_star_min=M_star - M_star_min,
            R_star_min=R_star - R_star_min,
            R_star_max=R_star + R_star_max,
            M_star_max=M_star + M_star_max,
            R_star=R_star,
            M_star=M_star,
            period_min=args.period_min,
            #period_max=10,
            )
        print("successfully finished TLS")
        #save the results
        sector = str(lc.sector).zfill(2)
        fig = plot_tls(lc_clean, flatten_lc, trend_lc, results, args)
#        results['time_raw'] = lc_clean.time
        if args.method == 'gp':
            fig.savefig(f"../output/{args.experiment_name}/tls_images/{name}_SECTOR{sector}_Method_GP_{args.kernel}__{args.tag}.png")
            print("saved figure!")
        else:
            fig.savefig(f"../output/{args.experiment_name}/tls_images/{name}_SECTOR{sector}_Method_{args.method}__{args.tag}.png")
            print("saved figure!")
        plt.close()
#        results['flux_raw'] = lc_clean.flux
#        results['flux_flat'] = flatten_lc
        results['ticid'] = lc_clean.TICID
#        results['sector'] = sector
        
        if args.method == "gp":
            h5_path = f'../output/{args.experiment_name}/tls_hdf5/{name}_SECTOR{sector}_Method_{args.method}_Kernel_{args.kernel}_{args.tag}.h5'
        else:
            h5_path = f'../output/{args.experiment_name}/tls_hdf5/{name}_SECTOR{sector}_Method_{args.method}_{args.tag}.h5'

#        with h5py.File(h5_path, 'w') as f:
#            f.create_dataset("outputs", data=results)
        print(results)
        deepdish.io.save(h5_path, results)
        print(f'Saved {h5_path.split("/")[-1]}')

        print("Successfully Finished!!")
    except Exception as e:
         print(e)
print("==================================================")
