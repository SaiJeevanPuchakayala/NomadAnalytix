import pandas as pd
import matplotlib.pyplot as plt
datasets = {}
datasets["Movies"] = pd.read_csv("movies.csv")
fig,ax = plt.subplots(1,1,figsize=(10,4))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
df=datasets["Movies"].copy()
df_R = df[df["Content Rating"] == "R"].sort_values(by="Worldwide Gross",ascending=False).head(10)
ax.bar(df_R["Title"], df_R["Worldwide Gross"])
ax.set_xlabel("Movie Title")
ax.set_ylabel("Worldwide Gross")
ax.set_title("Top 10 R-Rated Movies by Worldwide Gross")
fig.suptitle("")
plt.xticks(rotation=90)
plt.show()