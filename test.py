from runner import create_filename_dict
datasets = create_filename_dict("files")

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
#Filtering Players
batters = dim_players[dim_players['playingRole'].str.contains('Batter')]
bowlers = dim_players[dim_players['playingRole'].str.contains('Bowler')]
allrounders = dim_players[dim_players['playingRole'].str.contains('Allrounder')]

#Grouping Players by Team
batters_grouped = batters.groupby('team')['name'].count().reset_index()
bowlers_grouped = bowlers.groupby('team')['name'].count().reset_index()
allrounders_grouped = allrounders.groupby('team')['name'].count().reset_index()

#Merging Player Counts by Team
team_players = pd.merge(batters_grouped, bowlers_grouped, on='team', suffixes=('_batters', '_bowlers'))
team_players = pd.merge(team_players, allrounders_grouped, on='team')

#Plotting Graph
sns.set(style="whitegrid")
bar_width = 0.3
index = np.arange(len(team_players['team']))

plt.bar(index, team_players['name_batters'], bar_width, label='Batters')
plt.bar(index + bar_width, team_players['name_bowlers'], bar_width, label='Bowlers')
plt.bar(index + (bar_width*2), team_players['name'], bar_width, label='Allrounders')

plt.xlabel('Teams')
plt.ylabel('Number of Players')
plt.title('Team Composition')
plt.xticks(index + bar_width, team_players['team'])
plt.legend()

plt.show()