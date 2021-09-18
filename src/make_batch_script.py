import pandas as pd
import numpy as np

tois = pd.read_csv("TOIs.csv")

command=[]
for i,row in tois.iterrows():
    command.append(f"python Simple_Preprocessing_GLS.py --TOI {int(row.TOI)} --verbose --sector_all True")

fp = "batch_script.txt"
np.savetxt(fp, command, fmt='%s')
print("Saved: ", fp)
