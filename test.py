from runner import create_filename_dict
datasets = create_filename_dict("dataset_files")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
fig,ax = plt.subplots(1,1)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
dim_match_summary = datasets['dim_match_summary'].copy()
dim_players = datasets['dim_players'].copy()
fact_bating_summary = datasets['fact_bating_summary'].copy()
fact_bowling_summary = datasets['fact_bowling_summary'].copy()

# Merging and processing dataframes to get top 10 batsmen based on runs
batting_summary = fact_bating_summary.groupby(['player_id']).agg({'runs': 'sum'}).reset_index()
batting_summary = batting_summary.merge(dim_players[['player_id', 'player_name']], on='player_id', how='left')
top_10_batsmen = batting_summary.nlargest(10, 'runs')

# Plotting the data
sns.barplot(x='runs', y='player_name', data=top_10_batsmen, ax=ax)
ax.set_xlabel('Total Runs')
ax.set_ylabel('Batsman')
ax.set_title('Top 10 Batsmen')

# Set figure suptitle as empty
fig.suptitle('')

# Display the plot
plt.show()