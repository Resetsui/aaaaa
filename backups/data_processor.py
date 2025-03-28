import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_battles_with_min_members(battles_df, guild_name, min_members=20, days=7):
    """
    Filter battles to include only those with minimum number of guild members
    and within the specified number of days
    """
    if battles_df.empty:
        return pd.DataFrame()
    
    # Filter by date
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_battles = battles_df[battles_df['time'] >= cutoff_date].copy()
    
    if recent_battles.empty:
        return pd.DataFrame()
    
    # Filter by guild member count
    filtered_battles = []
    
    for _, battle in recent_battles.iterrows():
        details = battle['details']
        guild_found = False
        
        # Check each guild in the battle
        for guild, stats in details['guilds'].items():
            if guild_name.lower() in guild.lower():
                guild_found = True
                # Check if the guild has enough members
                if len(stats['players']) >= min_members:
                    filtered_battles.append(battle)
                break
        
    return pd.DataFrame(filtered_battles)

def get_guild_stats(battles_df, guild_name, alliance_name=None):
    """Calculate overall statistics for a guild from battle data"""
    if battles_df.empty:
        return {}
    
    total_battles = len(battles_df)
    total_kills = 0
    total_deaths = 0
    total_fame = 0
    battles_won = 0
    players_data = {}
    
    for _, battle in battles_df.iterrows():
        details = battle['details']
        guild_stats = None
        enemies_stats = {}
        
        # Find the specified guild and alliance members
        for guild, stats in details['guilds'].items():
            if guild_name.lower() in guild.lower():
                guild_stats = stats
                # Process player data
                for player in stats['players']:
                    name = player['name']
                    if name not in players_data:
                        players_data[name] = {
                            'kills': 0,
                            'deaths': 0,
                            'fame': 0,
                            'battles': 0
                        }
                    
                    players_data[name]['kills'] += player['kills']
                    players_data[name]['deaths'] += player['deaths']
                    players_data[name]['fame'] += player['fame']
                    players_data[name]['battles'] += 1
            elif alliance_name and alliance_name.lower() in guild.lower():
                # This is an alliance guild
                pass
            else:
                # This is an enemy guild
                enemies_stats[guild] = stats
        
        if guild_stats:
            total_kills += guild_stats['total_kills']
            total_deaths += guild_stats['total_deaths']
            total_fame += guild_stats['total_fame']
            
            # Determine if battle was won
            guild_kd_ratio = guild_stats['total_kills'] / max(1, guild_stats['total_deaths'])
            enemy_kills = sum(stats['total_kills'] for stats in enemies_stats.values())
            enemy_deaths = sum(stats['total_deaths'] for stats in enemies_stats.values())
            enemy_kd_ratio = enemy_kills / max(1, enemy_deaths)
            
            if guild_kd_ratio > enemy_kd_ratio:
                battles_won += 1
    
    # Calculate win rate
    win_rate = (battles_won / total_battles) * 100 if total_battles > 0 else 0
    
    # Create stats dictionary
    guild_stats = {
        'total_battles': total_battles,
        'battles_won': battles_won,
        'win_rate': win_rate,
        'total_kills': total_kills,
        'total_deaths': total_deaths,
        'kd_ratio': total_kills / max(1, total_deaths),
        'total_fame': total_fame,
        'players_data': players_data
    }
    
    return guild_stats

def get_recent_battles(battles_df, days=7):
    """Get battles from the last X days and sort them by time"""
    if battles_df.empty:
        return pd.DataFrame()
    
    # Utilizando timezone UTC para garantir compatibilidade com datetime64[ns, UTC]
    from datetime import timezone
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Converter para o mesmo tipo se necessário
    if 'time' in battles_df.columns and battles_df['time'].dtype.name.startswith('datetime64'):
        # Se 'time' já é um datetime64, devemos garantir que cutoff_date também seja
        recent_battles = battles_df[battles_df['time'] >= pd.Timestamp(cutoff_date)].copy()
    else:
        # Abordagem padrão
        recent_battles = battles_df[battles_df['time'] >= cutoff_date].copy()
    
    # Sort by time (most recent first)
    recent_battles = recent_battles.sort_values('time', ascending=False)
    
    return recent_battles

def get_battle_details(battles_df, battle_id):
    """Extract details for a specific battle"""
    if battles_df.empty:
        return None
    
    battle = battles_df[battles_df['battle_id'] == battle_id]
    
    if battle.empty:
        return None
    
    return battle.iloc[0]['details']

def get_top_players(battles_df, guild_name, metric='kills', limit=3):
    """Get top players by a specific metric (kills, deaths, fame)"""
    if battles_df.empty:
        return []
    
    players_data = {}
    
    for _, battle in battles_df.iterrows():
        details = battle['details']
        
        for guild, stats in details['guilds'].items():
            if guild_name.lower() in guild.lower():
                for player in stats['players']:
                    name = player['name']
                    if name not in players_data:
                        players_data[name] = {
                            'kills': 0,
                            'deaths': 0,
                            'fame': 0,
                            'battles': 0
                        }
                    
                    players_data[name]['kills'] += player['kills']
                    players_data[name]['deaths'] += player['deaths']
                    players_data[name]['fame'] += player['fame']
                    players_data[name]['battles'] += 1
    
    # Convert to DataFrame for easier sorting
    players_df = pd.DataFrame.from_dict(players_data, orient='index')
    players_df['name'] = players_df.index
    
    # Sort by the specified metric
    if metric in players_df.columns:
        players_df = players_df.sort_values(metric, ascending=False)
    
    # Get top N players
    top_players = players_df.head(limit).to_dict('records')
    
    return top_players

def get_daily_stats(battles_df, guild_name, days=7):
    """Get daily statistics for kills and deaths"""
    if battles_df.empty:
        return pd.DataFrame()
    
    # Initialize date range com timezone UTC para compatibilidade
    from datetime import timezone
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days-1)
    date_range = pd.date_range(start=start_date, end=end_date)
    
    # Initialize stats with zeros for all dates
    daily_stats = {
        'date': date_range,
        'kills': [0] * len(date_range),
        'deaths': [0] * len(date_range)
    }
    
    # Populate stats from battle data
    for _, battle in battles_df.iterrows():
        # Garantir que estamos tratando a data corretamente, independente do timezone
        if isinstance(battle['time'], pd.Timestamp):
            battle_date = battle['time'].date()
        else:
            # Caso não seja um Timestamp, converter para datetime antes
            from datetime import timezone
            if hasattr(battle['time'], 'tzinfo') and battle['time'].tzinfo is not None:
                battle_date = battle['time'].date()
            else:
                # Se não tiver timezone, assumir UTC para compatibilidade
                battle_date = battle['time'].replace(tzinfo=timezone.utc).date()
        
        if battle_date < start_date or battle_date > end_date:
            continue
        
        details = battle['details']
        
        for guild, stats in details['guilds'].items():
            if guild_name.lower() in guild.lower():
                # Find the index for this date
                date_idx = (battle_date - start_date).days
                if 0 <= date_idx < len(date_range):
                    daily_stats['kills'][date_idx] += stats['total_kills']
                    daily_stats['deaths'][date_idx] += stats['total_deaths']
    
    return pd.DataFrame(daily_stats)

def get_enemy_guilds(battles_df, guild_name, alliance_name=None):
    """Get list of enemy guilds and their stats"""
    if battles_df.empty:
        return {}
    
    enemy_guilds = {}
    
    for _, battle in battles_df.iterrows():
        details = battle['details']
        
        for guild, stats in details['guilds'].items():
            # Skip if this is our guild or alliance
            if guild_name.lower() in guild.lower():
                continue
            if alliance_name and alliance_name.lower() in guild.lower():
                continue
            
            # Add or update enemy guild stats
            if guild not in enemy_guilds:
                enemy_guilds[guild] = {
                    'battles': 0,
                    'total_kills': 0,
                    'total_deaths': 0,
                    'total_fame': 0
                }
            
            enemy_guilds[guild]['battles'] += 1
            enemy_guilds[guild]['total_kills'] += stats['total_kills']
            enemy_guilds[guild]['total_deaths'] += stats['total_deaths']
            enemy_guilds[guild]['total_fame'] += stats['total_fame']
    
    # Calculate KD ratio
    for guild in enemy_guilds:
        enemy_guilds[guild]['kd_ratio'] = (
            enemy_guilds[guild]['total_kills'] / 
            max(1, enemy_guilds[guild]['total_deaths'])
        )
    
    return enemy_guilds
