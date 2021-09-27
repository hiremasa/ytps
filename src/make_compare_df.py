import pandas as pd

df_all = pd.read_csv("../output/all_df.csv", index_col=0)
df_all = df_all.transpose()

df_all["TOI"] = df_all.index.map(lambda x: x.split("_")[0])

df_temp = df_all.groupby("TOI").mean()["P"]
df_compare = pd.DataFrame(index=df_temp.index)
df_compare["P_mean"] = df_temp.values
df_compare["P_std"] = df_all.groupby("TOI").std(ddof=0)["P"].values

df_compare.to_csv("../outputs/compare_df.csv")