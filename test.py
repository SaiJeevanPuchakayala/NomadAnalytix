import pandas as pd
import matplotlib.pyplot as plt
datasets={}
datasets["Movies"] = pd.read_csv("movies.csv")
fig,ax = plt.subplots(1,1,figsize=(10,4))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
df=datasets["Movies"].copy()
df_r=df[df["Content Rating"]=="R"].sort_values(by="Worldwide Gross",ascending=False).head(10)
ax.barh(df_r["Title"],df_r["Worldwide Gross"])
ax.set_xlabel("Worldwide Gross (in millions)")
ax.set_ylabel("Movie Title")
ax.set_title("Top 10 R-Rated Movies by Worldwide Gross")
fig.suptitle("")
plt.show()