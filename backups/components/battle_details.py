import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import format_number, create_kd_gauge

def show_battle_details(battle_data, guild_name, alliance_name):
    """Display detailed information about a specific battle"""
    st.header("🏆 Battle Details")
    
    # Battle header with time
    battle_time = battle_data['time'].strftime('%Y-%m-%d %H:%M')
    st.subheader(f"Battle on {battle_time}")
    
    # Find our guild in the battle
    guild_stats = None
    enemy_guilds = {}
    alliance_guilds = {}
    guild_key = ''
    
    for guild, stats in battle_data['guilds'].items():
        if guild_name.lower() in guild.lower():
            guild_stats = stats
            guild_key = guild
        elif alliance_name and alliance_name.lower() in guild.lower():
            alliance_guilds[guild] = stats
        else:
            enemy_guilds[guild] = stats
    
    if not guild_stats:
        st.error(f"Guild '{guild_name}' not found in this battle")
        return
    
    # Calculate battle stats
    guild_kills = guild_stats['total_kills']
    guild_deaths = guild_stats['total_deaths']
    guild_fame = guild_stats['total_fame']
    guild_kd = guild_kills / max(1, guild_deaths)
    guild_players = len(guild_stats['players'])
    
    enemy_kills = sum(stats['total_kills'] for stats in enemy_guilds.values())
    enemy_deaths = sum(stats['total_deaths'] for stats in enemy_guilds.values())
    enemy_fame = sum(stats['total_fame'] for stats in enemy_guilds.values())
    enemy_kd = enemy_kills / max(1, enemy_deaths)
    enemy_players = sum(len(stats['players']) for stats in enemy_guilds.values())
    
    alliance_kills = sum(stats['total_kills'] for stats in alliance_guilds.values())
    alliance_deaths = sum(stats['total_deaths'] for stats in alliance_guilds.values())
    alliance_fame = sum(stats['total_fame'] for stats in alliance_guilds.values())
    alliance_players = sum(len(stats['players']) for stats in alliance_guilds.values())
    
    # Determine victory
    friendly_kd = (guild_kills + alliance_kills) / max(1, guild_deaths + alliance_deaths)
    victory = friendly_kd > enemy_kd
    
    # Painel de resumo da batalha
    outcome = "VITÓRIA" if victory else "DERROTA"
    outcome_color = "#50fa7b" if victory else "#ff5555"
    
    st.markdown(f"""
    <div style="background-color: #7E57C220; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0;">Detalhes da Batalha</h3>
                <p>Data: {battle_time}</p>
            </div>
            <div style="text-align: right;">
                <h2 style="color: {outcome_color}; margin: 0;">{outcome}</h2>
                <p>K/D: {friendly_kd:.2f}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Battle overview
    st.markdown(f"""
    <div style="background-color: #2d2d42; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
        <h2 style="text-align: center; color: {'#50fa7b' if victory else '#ff5555'}">
            {'VICTORY' if victory else 'DEFEAT'}
        </h2>
        <div style="display: flex; justify-content: space-around; text-align: center;">
            <div>
                <h3>{guild_name}</h3>
                <p>Players: {guild_players}</p>
                <p>K/D: {guild_kd:.2f}</p>
                <p>Kills: {guild_kills}</p>
                <p>Deaths: {guild_deaths}</p>
                <p>Fame: {format_number(guild_fame)}</p>
            </div>
            <div>
                <h3>Alliance</h3>
                <p>Players: {alliance_players}</p>
                <p>K/D: {(alliance_kills / max(1, alliance_deaths)):.2f}</p>
                <p>Kills: {alliance_kills}</p>
                <p>Deaths: {alliance_deaths}</p>
                <p>Fame: {format_number(alliance_fame)}</p>
            </div>
            <div>
                <h3>Enemies</h3>
                <p>Players: {enemy_players}</p>
                <p>K/D: {enemy_kd:.2f}</p>
                <p>Kills: {enemy_kills}</p>
                <p>Deaths: {enemy_deaths}</p>
                <p>Fame: {format_number(enemy_fame)}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Guild KD gauge chart
    st.plotly_chart(create_kd_gauge(guild_kills, guild_deaths), use_container_width=True)
    
    # Player performance
    st.subheader("🎮 Player Performance")
    
    # Create DataFrame for players
    players_df = pd.DataFrame(guild_stats['players'])
    
    # Add KD ratio
    if not players_df.empty:
        players_df['kd_ratio'] = players_df['kills'] / players_df['deaths'].replace(0, 1)
        
        # Sort by kills
        players_df = players_df.sort_values('kills', ascending=False)
        
        # Top players
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Top Killers")
            top_killers = players_df.head(3)
            for i, (_, player) in enumerate(top_killers.iterrows()):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
                st.markdown(f"""
                <div style="background-color: #2d2d42; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <h4>{medal} {player['name']}</h4>
                    <div style="display: flex; justify-content: space-between;">
                        <div>Kills: {player['kills']}</div>
                        <div>Deaths: {player['deaths']}</div>
                        <div>K/D: {player['kd_ratio']:.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.subheader("💀 Most Deaths")
            top_deaths = players_df.sort_values('deaths', ascending=False).head(3)
            for i, (_, player) in enumerate(top_deaths.iterrows()):
                medal = "💀" if i == 0 else "☠️" if i == 1 else "👻"
                st.markdown(f"""
                <div style="background-color: #2d2d42; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <h4>{medal} {player['name']}</h4>
                    <div style="display: flex; justify-content: space-between;">
                        <div>Deaths: {player['deaths']}</div>
                        <div>Kills: {player['kills']}</div>
                        <div>K/D: {player['kd_ratio']:.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Player performance charts
        st.subheader("📊 Player Statistics")
        
        # Create kills chart
        fig_kills = px.bar(
            players_df.head(10),
            x='name',
            y='kills',
            title="Top 10 Players by Kills",
            color='kills',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        
        fig_kills.update_layout(
            xaxis_title="Player",
            yaxis_title="Kills",
            paper_bgcolor="#2d2d42",
            plot_bgcolor="#1e1e2e",
            font=dict(color="#f8f8f2")
        )
        
        st.plotly_chart(fig_kills, use_container_width=True)
        
        # Create KD ratio chart
        fig_kd = px.bar(
            players_df.sort_values('kd_ratio', ascending=False).head(10),
            x='name',
            y='kd_ratio',
            title="Top 10 Players by K/D Ratio",
            color='kd_ratio',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        
        fig_kd.update_layout(
            xaxis_title="Player",
            yaxis_title="K/D Ratio",
            paper_bgcolor="#2d2d42",
            plot_bgcolor="#1e1e2e",
            font=dict(color="#f8f8f2")
        )
        
        st.plotly_chart(fig_kd, use_container_width=True)
    
    # Participating Guilds
    st.subheader("⚔️ Participating Guilds")
    
    # Create guild comparison data
    guild_comparison = []
    
    # Add our guild
    guild_comparison.append({
        'name': guild_key,
        'players': guild_players,
        'kills': guild_kills,
        'deaths': guild_deaths,
        'kd_ratio': guild_kd,
        'fame': guild_fame,
        'type': 'Guild'
    })
    
    # Add alliance guilds
    for name, stats in alliance_guilds.items():
        alliance_kd = stats['total_kills'] / max(1, stats['total_deaths'])
        guild_comparison.append({
            'name': name,
            'players': len(stats['players']),
            'kills': stats['total_kills'],
            'deaths': stats['total_deaths'],
            'kd_ratio': alliance_kd,
            'fame': stats['total_fame'],
            'type': 'Alliance'
        })
    
    # Add enemy guilds
    for name, stats in enemy_guilds.items():
        enemy_guild_kd = stats['total_kills'] / max(1, stats['total_deaths'])
        guild_comparison.append({
            'name': name,
            'players': len(stats['players']),
            'kills': stats['total_kills'],
            'deaths': stats['total_deaths'],
            'kd_ratio': enemy_guild_kd,
            'fame': stats['total_fame'],
            'type': 'Enemy'
        })
    
    # Create DataFrame
    guild_df = pd.DataFrame(guild_comparison)
    
    # Create guild comparison chart
    fig_guild = px.bar(
        guild_df,
        x='name',
        y='kills',
        color='type',
        title="Guild Comparison - Kills",
        color_discrete_map={
            'Guild': '#9b59b6',
            'Alliance': '#8be9fd',
            'Enemy': '#ff5555'
        },
        hover_data=['players', 'deaths', 'kd_ratio']
    )
    
    fig_guild.update_layout(
        xaxis_title="Guild",
        yaxis_title="Kills",
        paper_bgcolor="#2d2d42",
        plot_bgcolor="#1e1e2e",
        font=dict(color="#f8f8f2")
    )
    
    st.plotly_chart(fig_guild, use_container_width=True)
    
    # Guild KD ratio chart
    fig_guild_kd = px.bar(
        guild_df,
        x='name',
        y='kd_ratio',
        color='type',
        title="Guild Comparison - K/D Ratio",
        color_discrete_map={
            'Guild': '#9b59b6',
            'Alliance': '#8be9fd',
            'Enemy': '#ff5555'
        },
        hover_data=['players', 'kills', 'deaths']
    )
    
    fig_guild_kd.update_layout(
        xaxis_title="Guild",
        yaxis_title="K/D Ratio",
        paper_bgcolor="#2d2d42",
        plot_bgcolor="#1e1e2e",
        font=dict(color="#f8f8f2")
    )
    
    st.plotly_chart(fig_guild_kd, use_container_width=True)