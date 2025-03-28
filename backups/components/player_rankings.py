import streamlit as st
import pandas as pd
import plotly.express as px
from utils import create_player_chart

def show_player_rankings(battles_df, guild_name):
    """Display player rankings with various metrics"""
    st.header("👑 Player Rankings")
    
    # Informações de destaque dos jogadores
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown(f"""
        <div style="background-color: #7E57C220; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <h3 style="color: #7E57C2; margin: 0;">Ranking de Jogadores</h3>
            <p>Análise detalhada da performance individual dos membros de <strong>{guild_name}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Pequena dica explicativa
        st.info("""
        **Como usar os rankings:**
        - Selecione o mínimo de batalhas para filtrar jogadores ocasionais
        - Compare diferentes métricas para avaliar o desempenho
        """)
    
    if battles_df.empty:
        st.warning("No battle data available for player rankings.")
        return
    
    # Process player data from battles
    players_data = {}
    
    for _, battle in battles_df.iterrows():
        details = battle['details']
        
        for guild, stats in details['guilds'].items():
            if guild_name.lower() in guild.lower():
                for player in stats['players']:
                    name = player['name']
                    if name not in players_data:
                        players_data[name] = {
                            'name': name,
                            'kills': 0,
                            'deaths': 0,
                            'fame': 0,
                            'battles': 0,
                            'avg_kills': 0,
                            'avg_deaths': 0
                        }
                    
                    players_data[name]['kills'] += player['kills']
                    players_data[name]['deaths'] += player['deaths']
                    players_data[name]['fame'] += player['fame']
                    players_data[name]['battles'] += 1
    
    # Calculate derived metrics
    for name, data in players_data.items():
        battles = max(1, data['battles'])
        data['avg_kills'] = data['kills'] / battles
        data['avg_deaths'] = data['deaths'] / battles
        data['kd_ratio'] = data['kills'] / max(1, data['deaths'])
    
    # Convert to DataFrame
    players_df = pd.DataFrame(list(players_data.values()))
    
    if players_df.empty:
        st.warning("No player data available.")
        return
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        min_battles = st.slider("Minimum Battles", 1, 10, 1)
    
    with col2:
        sort_by = st.selectbox(
            "Sort By",
            options=["kills", "deaths", "kd_ratio", "fame", "battles", "avg_kills", "avg_deaths"],
            format_func=lambda x: {
                'kills': 'Total Kills',
                'deaths': 'Total Deaths',
                'kd_ratio': 'K/D Ratio',
                'fame': 'Fame',
                'battles': 'Battles Participated',
                'avg_kills': 'Average Kills per Battle',
                'avg_deaths': 'Average Deaths per Battle'
            }[x]
        )
    
    # Filter and sort players
    filtered_players = players_df[players_df['battles'] >= min_battles].copy()
    filtered_players = filtered_players.sort_values(sort_by, ascending=False)
    
    if filtered_players.empty:
        st.warning(f"No players found with at least {min_battles} battles.")
        return
    
    # Display player rankings
    st.subheader(f"Rankings by {sort_by.replace('_', ' ').title()}")
    
    # Create chart
    fig = create_player_chart(filtered_players.to_dict('records'), sort_by)
    st.plotly_chart(fig, use_container_width=True)
    
    # Display detailed player table
    st.subheader("Detailed Player Statistics")
    
    # Format the DataFrame for display
    display_df = filtered_players[['name', 'kills', 'deaths', 'kd_ratio', 'fame', 'battles', 'avg_kills', 'avg_deaths']].copy()
    
    # Format the columns
    display_df['kd_ratio'] = display_df['kd_ratio'].round(2)
    display_df['avg_kills'] = display_df['avg_kills'].round(2)
    display_df['avg_deaths'] = display_df['avg_deaths'].round(2)
    
    # Rename columns for better display
    display_df.columns = [
        'Player',
        'Kills',
        'Deaths',
        'K/D Ratio',
        'Fame',
        'Battles',
        'Avg Kills',
        'Avg Deaths'
    ]
    
    # Display the table
    st.dataframe(
        display_df,
        use_container_width=True,
        height=500
    )
    
    # Top performer highlights
    st.subheader("🏆 Top Performers")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Top killer
        top_killer = filtered_players.loc[filtered_players['kills'].idxmax()]
        st.markdown(f"""
        <div style="background-color: #2d2d42; padding: 15px; border-radius: 5px; text-align: center;">
            <h3>🎯 Kill Master</h3>
            <h2>{top_killer['name']}</h2>
            <p>Total Kills: {top_killer['kills']}</p>
            <p>K/D Ratio: {top_killer['kd_ratio']:.2f}</p>
            <p>Battles: {top_killer['battles']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Best K/D (minimum 3 battles)
        kd_players = filtered_players[filtered_players['battles'] >= 3]
        if not kd_players.empty:
            best_kd = kd_players.loc[kd_players['kd_ratio'].idxmax()]
            st.markdown(f"""
            <div style="background-color: #2d2d42; padding: 15px; border-radius: 5px; text-align: center;">
                <h3>🏆 MVP</h3>
                <h2>{best_kd['name']}</h2>
                <p>K/D Ratio: {best_kd['kd_ratio']:.2f}</p>
                <p>Kills: {best_kd['kills']}</p>
                <p>Deaths: {best_kd['deaths']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        # Most active
        most_active = filtered_players.loc[filtered_players['battles'].idxmax()]
        st.markdown(f"""
        <div style="background-color: #2d2d42; padding: 15px; border-radius: 5px; text-align: center;">
            <h3>⚔️ Most Active</h3>
            <h2>{most_active['name']}</h2>
            <p>Battles: {most_active['battles']}</p>
            <p>Total Kills: {most_active['kills']}</p>
            <p>Total Deaths: {most_active['deaths']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Player efficiency chart
    st.subheader("Player Efficiency Analysis")
    
    # Create scatter plot of kills vs deaths
    fig = px.scatter(
        filtered_players,
        x='deaths',
        y='kills',
        size='battles',
        color='kd_ratio',
        hover_name='name',
        text='name',
        color_continuous_scale=px.colors.sequential.Viridis,
        title="Player Efficiency (Kills vs Deaths)"
    )
    
    # Add diagonal line for K/D = 1
    max_val = max(filtered_players['kills'].max(), filtered_players['deaths'].max())
    fig.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=max_val,
        y1=max_val,
        line=dict(color="white", width=1, dash="dash")
    )
    
    fig.update_layout(
        xaxis_title="Deaths",
        yaxis_title="Kills",
        paper_bgcolor="#2d2d42",
        plot_bgcolor="#1e1e2e",
        font=dict(color="#f8f8f2")
    )
    
    st.plotly_chart(fig, use_container_width=True)
