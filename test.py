from runner import create_filename_dict
datasets = create_filename_dict("files")

import pandas as pd
import matplotlib.pyplot as plt
fig,ax = plt.subplots(1,1)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
dim_match_summary = datasets['dim_match_summary'].copy()
dim_players = datasets['dim_players'].copy()
fact_bating_summary = datasets['fact_bating_summary'].copy()
fact_bowling_summary = datasets['fact_bowling_summary'].copy()

# Merge datasets to get runs scored by KKR and bowling economy
merged_df = fact_bating_summary.merge(fact_bowling_summary, on='match_id', suffixes=('_batting', '_bowling'))
kkr_runs_economy = merged_df[(merged_df['teamInnings'] == 'KKR') & (merged_df['bowlingTeam'] == 'KKR')][['runs_batting', 'economy']]

# Create the scatter plot
plt.scatter(kkr_runs_economy['runs_batting'], kkr_runs_economy['economy'], s=50)

# Set labels and title
plt.xlabel('Runs Scored by KKR')
plt.ylabel('Bowling Economy')
plt.title('Runs Scored by KKR vs Bowling Economy')

# Set the fig suptitle as empty
fig.suptitle('')

# Show the plot
plt.show()
