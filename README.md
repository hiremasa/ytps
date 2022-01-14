# B4_research
- [Directory](#directory)
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
### 8/30-9/17: make a pipeline to run scripts on all TOIs

---
<a name="Setup for GLS on a new sector"></a>
# Setup for GLS on new sector
1. Firstly, downloading target text file from the (official web site)[https://tess.mit.edu/observations/target-lists/]. Note: You are supposed to be in the ```scr/``` directory. Here is the example of downloading text file of sector 46 for 120 seconds cadence.
```
$ wget -P txt_file https://tess.mit.edu/wp-content/uploads/all_targets_S046_v1.txt
```

2. Secondly, make batch file for executing python GLS script on new TIC targets. Please run ```txt_file/mkbf.sh```. This example is for sector 46. Fix ```xxx.txt``` and sector number respectively if neccesary. (mkbf.sh)[https://github.com/hiremasa/B4_research/blob/main/src/txt_file/mkbf.sh]
```
$ ./txt_file/mkbf.sh
```

3. Finaly, call batch file. Befere you run the below script, you may need to fix error to delete top 6 lines that says ```--TIC #```.
``` 
$ cat txt_file/sector46.batch | parallel
```

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
