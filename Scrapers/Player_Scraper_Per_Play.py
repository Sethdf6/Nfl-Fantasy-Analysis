import pandas as pd
from functools import reduce

# — Step 0: Load pbp + roster (now with rookie_year) —
df      = pd.read_csv('your_data.csv', low_memory=False, parse_dates=['game_date'])
roster  = pd.read_csv('roster.csv', dtype={'player_id': str})
# roster must now have: player_id, position, rookie_year

# Pull out season as an integer
df['season'] = df['game_date'].dt.year.astype(int)

# — Group keys (now include season and posteam) —
group_keys = [
    'player_id','player_name','season','game_id',
    'home_team','away_team','season_type','week','game_date','posteam'
]

# — 1) PASSERS (including only those fumbles they themselves commit) —
pass_df = (
    df[df.passer_player_id.notna()]
      .assign(player_id     = lambda d: d.passer_player_id,
              player_name   = lambda d: d.passer_player_name)
      .groupby(group_keys)
      .agg(
          pass_attempts     = ('pass_attempt', 'sum'),
          passing_yards     = ('passing_yards', 'sum'),
          pass_touchdowns   = ('pass_touchdown', 'sum'),
          interceptions     = ('interception', 'sum'),
          sacks             = ('sack', 'sum'),
          fumbles_committed = ('fumble', 'sum'),
          shotgun_plays     = ('shotgun', 'sum'),
          no_huddle_plays   = ('no_huddle', 'sum'),
          dropbacks         = ('qb_dropback', 'sum'),
          scrambles         = ('qb_scramble', 'sum'),
          avg_air_yards     = ('air_yards', 'mean'),
      )
      .reset_index()
)

# — 2) RECEIVERS —
recv_df = (
    df[df.receiver_player_id.notna()]
      .assign(player_id     = lambda d: d.receiver_player_id,
              player_name   = lambda d: d.receiver_player_name)
      .groupby(group_keys)
      .agg(
          receptions         = ('complete_pass', 'sum'),
          receiving_yards    = ('receiving_yards', 'sum'),
          yac                = ('yards_after_catch', 'sum'),
          rec_touchdowns     = ('touchdown', 'sum'),
          fumbles_committed  = ('fumble', 'sum'),
      )
      .reset_index()
)

# — 3) RUSHERS —
rush_df = (
    df[df.rusher_player_id.notna()]
      .assign(player_id     = lambda d: d.rusher_player_id,
              player_name   = lambda d: d.rusher_player_name)
      .groupby(group_keys)
      .agg(
          rush_attempts      = ('rush_attempt', 'sum'),
          rushing_yards      = ('rushing_yards', 'sum'),
          rush_touchdowns    = ('rush_touchdown', 'sum'),
          fumbles_committed  = ('fumble', 'sum'),
      )
      .reset_index()
)

# — 4) KICKERS —
kick_df = (
    df[df.kicker_player_id.notna()]
      .assign(player_id     = lambda d: d.kicker_player_id,
              player_name   = lambda d: d.kicker_player_name)
      .groupby(group_keys)
      .agg(
          fg_made            = ('field_goal_result', lambda x: (x=='made').sum()),
          total_fg_distance  = ('kick_distance', 'sum'),
          xp_made            = ('extra_point_result', lambda x: (x=='good').sum()),
      )
      .reset_index()
)

# — 5) Merge all roles together —
agg_df = reduce(
    lambda left, right: pd.merge(left, right, on=group_keys, how='outer'),
    [pass_df, recv_df, rush_df, kick_df]
).fillna(0)

# — 6) Derived metrics + total fumbles —
agg_df['pass_completion_pct']   = agg_df['receptions'] / agg_df['pass_attempts'].replace(0, pd.NA)
agg_df['yards_per_pass']        = agg_df['passing_yards'] / agg_df['pass_attempts'].replace(0, pd.NA)
agg_df['yards_per_rush']        = agg_df['rushing_yards'] / agg_df['rush_attempts'].replace(0, pd.NA)
agg_df['total_fumbles_committed'] = (
    agg_df['fumbles_committed_x'] +  # from pass_df
    agg_df['fumbles_committed_y'] +  # from recv_df
    agg_df['fumbles_committed']      # from rush_df (merged last)
)

# — 7) Add position + rookie_year → compute nfl_year —
agg_df = agg_df.merge(
    roster[['player_id','position','rookie_year']],
    on='player_id', how='left'
)
agg_df['nfl_year'] = agg_df['season'] - agg_df['rookie_year'] + 1

# — 8) Add head‐coach & opp coach —
coach_info = df[['game_id','home_coach','away_coach']].drop_duplicates('game_id')
agg_df = agg_df.merge(coach_info, on='game_id', how='left')
agg_df['head_coach']     = agg_df.apply(lambda r: r.home_coach if r.posteam==r.home_team else r.away_coach, axis=1)
agg_df['opp_head_coach'] = agg_df.apply(lambda r: r.away_coach if r.posteam==r.home_team else r.home_coach, axis=1)

# — 9) Reorder/export —
cols = [
    'player_id','player_name','position','nfl_year','season','game_id',
    'home_team','away_team','season_type','week','game_date',
    'head_coach','opp_head_coach',
    # … followed by all your numeric stats …
]
final = agg_df[cols + [c for c in agg_df.columns if c not in cols]]
final.to_csv('player_game_offensive_summary.csv', index=False)
