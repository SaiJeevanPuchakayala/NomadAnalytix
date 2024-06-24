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

fact_bowling_summary = fact_bowling_summary.merge(dim_match_summary, on = 'match_id').merge(dim_players, left_on='bowlerName',right_on='name')
fact_bowling_summary['year'] = pd.to_datetime(fact_bowling_summary['matchDate']).dt.year
bowlers_performance = fact_bowling_summary[fact_bowling_summary['year']>=2020].groupby(['bowlerName','year'])['runs','wickets','overs'].sum().reset_index()
bowlers_performance = bowlers_performance[bowlers_performance['overs']>=10]
bowlers_performance['bowling_average'] = bowlers_performance['runs']/bowlers_performance['wickets']
bowlers_avg = bowlers_performance.groupby('bowlerName')['bowling_average'].mean().sort_values().reset_index()
bowlers_avg = bowlers_avg.head(10)
plt.barh(bowlers_avg['bowlerName'],bowlers_avg['bowling_average'],color=['#00a9b5','#00a9b5','#00a9b5','#00a9b5','#00a9b5','#00a9b5','#00a9b5','#00a9b5','#00a9b5','#750d37'])
plt.xlabel('Bowling Average')
plt.ylabel('Bowler Name')
plt.title('Top 10 bowlers based on past 3 years bowling average',loc='left')
plt.show()
