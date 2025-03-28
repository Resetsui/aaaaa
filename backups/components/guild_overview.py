import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils import (
    create_kd_gauge,
    create_win_rate_gauge,
    create_daily_stats_chart,
    display_battle_card,
    format_number
)

def show_guild_overview(battles_df, guild_name, alliance_name):
    """Display guild overview with summary statistics and recent battles"""
    
    # Resumo mais clean e elegante
    st.markdown(f"""
    <div style="background-color: rgba(245, 184, 65, 0.1); 
         padding: 20px; border-radius: 10px; margin-bottom: 30px; 
         border: 1px solid rgba(245, 184, 65, 0.2); 
         box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);">
        <h2 style="color: #F5B841; margin: 0; text-align: center; 
             font-size: 24px; margin-bottom: 5px;">Resumo de Performance</h2>
        <p style="text-align: center; color: #AAAAAA; margin-top: 0;">
            Estatísticas consolidadas de batalhas com 20+ membros
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if battles_df.empty:
        st.warning("No battle data available for overview.")
        return
    
    # Calculate overall guild stats
    total_battles = len(battles_df)
    total_kills = 0
    total_deaths = 0
    total_fame = 0
    battles_won = 0
    total_players = set()
    
    # Process each battle
    for _, battle in battles_df.iterrows():
        details = battle['details']
        guild_stats = None
        enemies_stats = {}
        
        # Find our guild and enemies
        for guild, stats in details['guilds'].items():
            if guild_name.lower() in guild.lower():
                guild_stats = stats
                # Add players to the set
                for player in stats['players']:
                    total_players.add(player['name'])
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
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Battles", total_battles)
    
    with col2:
        st.metric("Active Players", len(total_players))
    
    with col3:
        st.metric("Battles Won", f"{battles_won} ({win_rate:.1f}%)")
    
    with col4:
        kd_ratio = total_kills / max(1, total_deaths)
        st.metric("Overall K/D", f"{kd_ratio:.2f}")
    
    # Additional metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Kills", format_number(total_kills))
    
    with col2:
        st.metric("Total Deaths", format_number(total_deaths))
    
    with col3:
        st.metric("Total Fame", format_number(total_fame))
    
    # Gauge charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_kd_gauge(total_kills, total_deaths), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_win_rate_gauge(win_rate), use_container_width=True)
    
    # Daily performance chart
    st.subheader("📈 Daily Performance")
    
    # Prepare daily stats data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)  # Last 7 days
    date_range = pd.date_range(start=start_date, end=end_date)
    
    daily_stats = {
        'date': date_range,
        'kills': [0] * len(date_range),
        'deaths': [0] * len(date_range)
    }
    
    # Populate with battle data
    for _, battle in battles_df.iterrows():
        battle_date = battle['time'].date()
        
        if battle_date < start_date or battle_date > end_date:
            continue
        
        details = battle['details']
        
        for guild, stats in details['guilds'].items():
            if guild_name.lower() in guild.lower():
                date_idx = (battle_date - start_date).days
                if 0 <= date_idx < len(date_range):
                    daily_stats['kills'][date_idx] += stats['total_kills']
                    daily_stats['deaths'][date_idx] += stats['total_deaths']
    
    # Create daily stats chart
    daily_df = pd.DataFrame(daily_stats)
    fig = create_daily_stats_chart(daily_df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Recent battles section
    st.markdown("""
    <div style="background-color: rgba(245, 184, 65, 0.05); padding: 15px; 
         border-radius: 10px; margin: 20px 0; 
         border-left: 3px solid #F5B841;">
        <h3 style="color: #F5B841; margin-top: 0;">⚔️ Batalhas Recentes</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Sort battles by time (most recent first)
    recent_battles = battles_df.sort_values('time', ascending=False)
    
    # Criamos um container para encapsular as batalhas com um visual limpo
    with st.container():
        # Show battle cards
        for idx, (_, battle) in enumerate(recent_battles.head(3).iterrows()):
            # Adicionamos uma separação sutil entre as batalhas
            if idx > 0:
                st.markdown("<hr style='margin: 10px 0; border-color: #333333;'>", unsafe_allow_html=True)
            display_battle_card(battle, guild_name)
    
    # Top performers section
    st.markdown("""
    <div style="background-color: rgba(245, 184, 65, 0.05); padding: 15px; 
         border-radius: 10px; margin: 20px 0; 
         border-left: 3px solid #F5B841;">
        <h3 style="color: #F5B841; margin-top: 0;">🏆 Top Performers</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Process player data
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
    
    # Convert to DataFrame
    players_df = pd.DataFrame.from_dict(players_data, orient='index')
    players_df['name'] = players_df.index
    
    # Add KD ratio
    players_df['kd_ratio'] = players_df['kills'] / players_df['deaths'].replace(0, 1)
    
    # Display top performers
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<h4 style='text-align: center; color: #F5B841;'>🎯 Top Killers</h4>", unsafe_allow_html=True)
        top_killers = players_df.sort_values('kills', ascending=False).head(3)
        for i, (_, player) in enumerate(top_killers.iterrows()):
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            
            # Calculamos uma porcentagem para mostrar em uma barra de progresso
            max_kills = top_killers.iloc[0]['kills']
            progress_percent = (player['kills'] / max_kills) * 100 if max_kills > 0 else 0
            
            st.markdown(f"""
            <div style="background-color: rgba(40, 40, 60, 0.3); 
                 padding: 12px; border-radius: 8px; margin-bottom: 12px;
                 border: 1px solid rgba(245, 184, 65, 0.2);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-size: 16px; font-weight: bold; color: #F5B841;">{medal} {player['name']}</div>
                    <div style="font-size: 14px; color: white;">{player['kills']} kills</div>
                </div>
                <div style="width: 100%; background-color: #444; height: 6px; border-radius: 3px;">
                    <div style="width: {progress_percent}%; background-color: #F5B841; height: 6px; border-radius: 3px;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px; color: #AAA;">
                    <div>K/D: {player['kd_ratio']:.2f}</div>
                    <div>Mortes: {player['deaths']}</div>
                    <div>Batalhas: {player['battles']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h4 style='text-align: center; color: #F5B841;'>💀 Mais Mortes</h4>", unsafe_allow_html=True)
        top_deaths = players_df.sort_values('deaths', ascending=False).head(3)
        for i, (_, player) in enumerate(top_deaths.iterrows()):
            medal = "💀" if i == 0 else "☠️" if i == 1 else "👻"
            
            # Calculamos uma porcentagem para mostrar em uma barra de progresso
            max_deaths = top_deaths.iloc[0]['deaths']
            progress_percent = (player['deaths'] / max_deaths) * 100 if max_deaths > 0 else 0
            
            st.markdown(f"""
            <div style="background-color: rgba(40, 40, 60, 0.3); 
                 padding: 12px; border-radius: 8px; margin-bottom: 12px;
                 border: 1px solid rgba(245, 184, 65, 0.2);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-size: 16px; font-weight: bold; color: #F5B841;">{medal} {player['name']}</div>
                    <div style="font-size: 14px; color: white;">{player['deaths']} mortes</div>
                </div>
                <div style="width: 100%; background-color: #444; height: 6px; border-radius: 3px;">
                    <div style="width: {progress_percent}%; background-color: #F5B841; height: 6px; border-radius: 3px;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px; color: #AAA;">
                    <div>K/D: {player['kd_ratio']:.2f}</div>
                    <div>Kills: {player['kills']}</div>
                    <div>Batalhas: {player['battles']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("<h4 style='text-align: center; color: #F5B841;'>🌟 Melhor K/D</h4>", unsafe_allow_html=True)
        # Filter players with minimum battles
        active_players = players_df[players_df['battles'] >= 3]
        top_kd = active_players.sort_values('kd_ratio', ascending=False).head(3)
        for i, (_, player) in enumerate(top_kd.iterrows()):
            medal = "🏆" if i == 0 else "🏅" if i == 1 else "🎖️"
            
            # Calculamos uma porcentagem para mostrar em uma barra de progresso
            max_kd = top_kd.iloc[0]['kd_ratio']
            progress_percent = (player['kd_ratio'] / max_kd) * 100 if max_kd > 0 else 0
            
            st.markdown(f"""
            <div style="background-color: rgba(40, 40, 60, 0.3); 
                 padding: 12px; border-radius: 8px; margin-bottom: 12px;
                 border: 1px solid rgba(245, 184, 65, 0.2);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-size: 16px; font-weight: bold; color: #F5B841;">{medal} {player['name']}</div>
                    <div style="font-size: 14px; color: white;">K/D: {player['kd_ratio']:.2f}</div>
                </div>
                <div style="width: 100%; background-color: #444; height: 6px; border-radius: 3px;">
                    <div style="width: {progress_percent}%; background-color: #F5B841; height: 6px; border-radius: 3px;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px; color: #AAA;">
                    <div>Kills: {player['kills']}</div>
                    <div>Mortes: {player['deaths']}</div>
                    <div>Batalhas: {player['battles']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
