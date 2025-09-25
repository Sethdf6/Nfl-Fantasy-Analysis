# Nfl Player and Team Analysis 
by Seth Fried
## Background
The purpose of this project was to practice gathering data, manipulating data, and drawing conclusions from the data that can inform Fantasy managers while drafting NFL players. Instead of doing a straightforward analysis one one dataset the goal was to use mutliple sources (see acknowledments) and combine them to find correlations that might not be immediatly obvious. The scope of this analysis covers both NFL players and NFL teams from 2006-2024. 

## Data
For this project I collected average draft positions (ADP) data and player game logs to see if they under or overperformed their expected value, player's college stats and combines to see if there was any correlation between their pre NFL stats and their NFL success, and finally team game logs to see how teams performed across the two decade timeline. The players that were included in this analysis were the ones that were fantasy relevant meaning they are either a tight end, wide reciever, quarter back, or running back and they played at least one snap in a season. There are also a few other pieces of data (like stadiums) that I included in the repo as I intend to do more analysis with them.
## Analysis
For the analysis I will break it up into four parts for the four jupyter notebooks I used to calculate statistics and make graphs. The four notebooks cover the ADP, combine, draft position, and team analysis.

#### ADP Analysis
The purpose of the ADP analysis was to look at a players projected Fantasy draft position and compare it to their actual ranking after the season. I got the ADP values from each year from FantasyPros and the stats from pro Football Reference. For the ADP data I had to clean the data by removing some null values, fixing some of the column names, and splitting some of the columns as the data initially had draft position, team, and round all in the same column with some unnecessary text. For the stats data I had to remove all the irrelevant players and clean up the columns as there was a lot of data that wasn't useful for my analysis. Once this was done I was able to conduct my analysis on which players under and over performed and which patterns could be found to indicate why players did better or worse. 

The first thing I looked into was the distribution of players under or overperforming:
![rank distribution](images/rank_diff_distribution_histogram.png)
We can see the curve is roughly centered on 0 which makes sense as we would expect roughly the same amount of players to underperform as players who overperform. 
![position variance](images/positional_variation.png)
![10 overvalued players in 2023](images/over_valued_players_2023.png)
![10 undervalued players in 2023](images/under_valued_players_2023.png)


#### Combine Analysis
![40yd Dash analysis](images/40ydDash.png)
#### Draft Analysis
#### Team Analysis

## Conclusion
## Acknowledgments
