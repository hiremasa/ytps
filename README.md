# YTPS(Young Transiting Planets Survey)
# Overall TESS Pipeline to Search for Transiting Planets in Young Stars
## This is the repository to search for young active stars from [TESS](https://tess.mit.edu/) light curve files & search for transiting exoplanet candidates.
This project consits of 2 parts: 
1. search for young active stars (GLS pipeline) 
2. search transiting signals (TLS pipeline)


[![GitHub issues](https://img.shields.io/github/issues/hiremasa/ytps)](https://github.com/hiremasa/ytps/issues)
[![GitHub license](https://img.shields.io/github/license/hiremasa/ytps)](https://github.com/hiremasa/ytps)
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/metabolize/rq-dashboard-on-heroku)
<!-- - [Directory](#directory)
- [Tasks](#tasks)
- [References](#references)
- [Paper List](#paper_list)
---
<a name="directory"></a>
# Directory description of this repository

<pre>
.
├── homeworks
├── output (all outputs are stored here)
│   ├── all_df.csv (concatenated from all df in dataframes/)
│   ├── all_df_sort_pmax.csv (sorted all_df.csv by pmax)
│   ├── compare_df.csv
│   ├── dataframes/
│   └── images/
├── requirements.txt
└── src (main working dir)
    ├── Simple_Preprocessing_GLS.py (for make 4 lc plots && make dataframes)
    ├── gls.py
    ├── make_batch_script.py
    ├── make_compare_df.py
    ├── get_tois.py
    ├── batch_script.txt
    └── working_notebook.ipynb
</pre>
---
<a name="tasks"></a>
# Tasks
### 7/5: Lightkurve tutorial by making Line Curve of "TOI-519" & "55 Cancri"
### 7/12, 20: exoplanet tutorial
### 8/30-9/17: make a pipeline to run scripts on all TOIs -->

---
<a name="Setup Environment"></a>
# 0. Environment Setup
1. Create an environment for this repo, by running the following at the terminal:
```
$ conda create --name Your_Favorite_Environment_Name
```
2. Now activate the environment with:
```
$ conda activate Your_Favorite_Environment_Name python=3 jupyter 
```
3. Then install packeges:
```
$ pip install requirements.txt
```
4. Finaly, get the neccesary file(Important):
```
$ cd ./src
$ python get_tois.py
```

<a name="Basic Usage"></a>
# Basic Usage
## 1.1 Basic Usage to search for young active stars
Running the below command(TIC ID is 123456789 in this example), you will get GLS results as image & csv format. You can check them in ```./output/sector0/images/``` &  ```./output/sector0/dataframes/``` respectively. Pmax from 0.5 to 0.9 is preferred value for young planets.
```
$ python simple_preprocessing_gls.py --TIC 123456789 --sector 0 --experiment_name sector0 --verbose
```
<img src="https://user-images.githubusercontent.com/61959411/152975807-ae9db51d-e7a2-4841-8265-a3d952b271c1.png" width="700px">

## 1.2 Basic Usage to search for transit signals
Running the below command(TIC ID is 123456789 in this example), you will get TLS(Transit Least Squares) results as image & HDF5 format. You can check them in ```./output/sector0/tls_images/``` &  ```./output/sector0/tls_hdf5/``` respectively. 

Here is GP method:
```
$ python execute_wotan_gls.py --TIC 123456789 --sector 0 --experiment_name sector0 --method gp --kernel squared_exp --kernel_size 2.0
```
Here is window based method:
```
$ python execute_wotan_gls.py --TIC 123456789 --sector 0 --experiment_name sector0 --method biweight --window_lenght 0.3
```
<img src="https://user-images.githubusercontent.com/61959411/149708121-08d4a241-45ae-4f98-8e27-f2730127de84.png" width="700px">

<a name="Practice for GLS on a new sector"></a>
# 2. Practice for new sector
## 2.1 Practice for executeing GLS on new sector
This section supposes that it takses TIC number and returns P_max, P_rot, and Light Curve Figures like below.

1. Firstly, download target text file from the [official web site](https://tess.mit.edu/observations/target-lists/). Note: You are supposed to be in the ```scr/``` directory. Here is the example of downloading text file of sector 45 with 120 seconds cadence.
```
$ cd ./src/
$ wget -P txt_file https://tess.mit.edu/wp-content/uploads/all_targets_S045_v1.txt
```

2. Secondly, make batch file for executing python GLS script on new TIC targets. Please run ```txt_file/mkbf.sh```. This example is for sector 45. Fix ```xxx.txt``` and sector number respectively if neccesary, see [mkbf.sh](https://github.com/hiremasa/B4_research/blob/main/src/txt_file/mkbf.sh).
```
$ ./txt_file/mkbf.sh
```

3. Thirdly, call batch file that executes python scripts. Befere you run the below script, you may need to fix error to delete top 6 lines that say ```--TIC #```.
``` 
$ cat txt_file/sector45.batch | parallel
```
After this, a lot of images and dataframes will be produced. Please check them in ```./output/sector45/```.

4. Finaly, concatenate all the produced dataframes and sort by Pmax.
```
$ python simple_preprocessing_gls.py --collect True  --experiment_name sector45
```

<a name="Practice for Wotan Flatteing & TLS search on new sector"></a>
## 2.2 Practice for Wotan Flatteing & TLS search on new sector
After runing the below command, you will get transit images like below in ```./output/sector45/tls_images``` directory in this example.

```
$ python make_wotantls_src.py --upper_thresh 1.0 --lower_thresh 0.9 --experiment_name sector45 --sector_number 45 | bash
```

Note: If you want to run on another sector, please change ```--experiment_name```, ```--sector_number``` values respectively.

---
<a name="references"></a>
# References

## Library
- [Lightkurve](https://docs.lightkurve.org/reference/lightcurve.html)
- [Astropy](https://www.astropy.org/)
- [exoplanet](https://docs.exoplanet.codes/en/latest/)
- [Generalized LombScargle](https://arxiv.org/abs/0901.2573)(astro-ph.IM)
- [Transit Least Square](https://github.com/hippke/tls)
- [Wotan](https://github.com/hippke/wotan)
## Documentation
- [TESS](https://tess.mit.edu/science/data/)
- [ExoFOP-TESS](https://exofop.ipac.caltech.edu/tess/)
- [SYSTEMATIC CLASSIFICATION OF TESS ECLIPSING BINARIES](https://jbirky.github.io/content/AAS_235_Poster.pdf)
- [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView?app=ExoTbls&config=PS)

---
<a name="paper_list"></a>
# Paper List
- [Exoplanet Detection using Machine Learning](https://arxiv.org/abs/2011.14135)
- [Optimized transit detection algorithm to search forperiodic transits of small planets](https://arxiv.org/pdf/1901.02015.pdf)
- [60 VALIDATED PLANETS FROMK2CAMPAIGNS 5–8](https://arxiv.org/pdf/1810.04074.pdf)
- [TESS DISCOVERY OF A TRANSITING SUPER-EARTH IN THEπMENSAE SYSTEM](https://arxiv.org/pdf/1809.05967.pdf)
- [A 38 Million Year Old Neptune-Sized Planet in the Kepler Field](https://arxiv.org/pdf/2112.14776.pdf)
- [The Early Evolution of Stars and ExoplanetSystems: Exploring and Exploiting Nearby,Young Stars](https://surveygizmoresponseuploads.s3.amazonaws.com/fileuploads/623127/4458621/198-9e85837dc24da47f3e7d9b53c4734218_KastnerJoelH.pdf)
- [Understanding Exoplanet Atmospheres withUV Observations I: NUV and Blue/Optical](http://surveygizmoresponseuploads.s3.amazonaws.com/fileuploads/623127/4458621/250-06161a4e8722fa4ad92563b30046b976_exoplanet_uv_white_paper.pdf)
- [The TESS Objects of Interest Catalog from the TESS Prime Mission](https://arxiv.org/pdf/2103.12538.pdf)
- [Cluster Difference Imaging Photometric Survey. II. TOI 837: A Young Validated Planet in IC 2602](https://arxiv.org/pdf/2009.07845.pdf)
- [Zodiacal Exoplanets in Time (ZEIT) V: A Uniform Search for Transiting Planets in Young Clusters Observed by K2
](https://arxiv.org/abs/1709.09670)
