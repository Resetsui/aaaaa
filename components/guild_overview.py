import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
    
    # Resumo mais compact e elegante
    st.markdown("""
    <div style="background: linear-gradient(90deg, rgba(245, 184, 65, 0.1) 0%, rgba(0, 0, 0, 0) 100%);
         padding: 12px 15px; border-radius: 8px; margin-bottom: 15px; 
         border-left: 3px solid #F5B841; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
        <h2 style="color: #F5B841; margin: 0; font-size: 20px; margin-bottom: 3px;">Resumo de Performance</h2>
        <p style="color: #777777; margin: 0; font-size: 12px;">
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
    
    # Criando estilo para métricas mais compacto
    st.markdown("""
    <style>
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin-bottom: 15px;
    }
    .metric-card {
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 6px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(245, 184, 65, 0.15);
        position: relative;
        overflow: hidden;
    }
    .metric-title {
        color: #AAAAAA;
        font-size: 12px;
        margin-bottom: 2px;
        font-weight: normal;
    }
    .metric-value {
        color: #F5B841;
        font-size: 18px;
        font-weight: bold;
        margin: 0;
    }
    .metric-subtitle {
        color: #777777;
        font-size: 10px;
        margin-top: 2px;
    }
    .metric-icon {
        position: absolute;
        top: 10px;
        right: 10px;
        color: rgba(245, 184, 65, 0.2);
        font-size: 16px;
    }
    .metric-small {
        grid-column: span 1;
    }
    .metric-medium {
        grid-column: span 2;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Formatar os valores para exibição
    kd_ratio = total_kills / max(1, total_deaths)
    win_rate_formatted = f"{win_rate:.1f}"
    kd_ratio_formatted = f"{kd_ratio:.2f}"
    total_kills_formatted = format_number(total_kills)
    total_deaths_formatted = format_number(total_deaths)
    total_fame_formatted = format_number(total_fame)
    active_players = len(total_players)
    
    # Usando colunas do Streamlit para criar um layout de métricas mais confiável
    # Primeira linha
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Battles</div>
            <div class="metric-value">{total_battles}</div>
            <div class="metric-icon">⚔️</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Players</div>
            <div class="metric-value">{active_players}</div>
            <div class="metric-icon">👥</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Battles Won</div>
            <div class="metric-value">{battles_won}</div>
            <div class="metric-subtitle">Win Rate: {win_rate_formatted}%</div>
            <div class="metric-icon">🏆</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Overall K/D</div>
            <div class="metric-value">{kd_ratio_formatted}</div>
            <div class="metric-icon">📊</div>
        </div>
        """, unsafe_allow_html=True)

    # Segunda linha
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Kills</div>
            <div class="metric-value">{total_kills_formatted}</div>
            <div class="metric-icon">⚔️</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Deaths</div>
            <div class="metric-value">{total_deaths_formatted}</div>
            <div class="metric-icon">💀</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Fame</div>
            <div class="metric-value">{total_fame_formatted}</div>
            <div class="metric-icon">✨</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gauge charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_kd_gauge(total_kills, total_deaths), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_win_rate_gauge(win_rate, battles_won, total_battles), use_container_width=True)
    
    # Daily performance chart
    st.subheader("📈 Performance Diária")
    
    # Configurar seletor de período para análise
    col1, col2 = st.columns([3, 1])
    with col2:
        period_options = {
            "7 dias": 7,
            "14 dias": 14,
            "30 dias": 30,
            "60 dias": 60,
            "90 dias": 90
        }
        selected_period = st.selectbox("Período de análise", list(period_options.keys()))
        selected_days = period_options[selected_period]
    
    # Obter estatísticas diárias usando a função melhorada do data_processor
    from data_processor import get_daily_stats
    daily_df = get_daily_stats(battles_df, guild_name, days=selected_days)
    
    # Criar abas para diferentes visualizações
    performance_tabs = st.tabs(["Kills e Mortes", "K/D Ratio", "Win Rate"])
    
    with performance_tabs[0]:
        # Gráfico principal de kills e mortes
        fig = create_daily_stats_chart(daily_df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Adicionar métricas de resumo abaixo do gráfico
        col1, col2, col3 = st.columns(3)
        with col1:
            total_kills = daily_df['kills'].sum()
            avg_kills = total_kills / max(1, len(daily_df))
            st.metric("Total de Kills", f"{total_kills:.0f}", f"Média: {avg_kills:.1f}/dia")
        
        with col2:
            total_deaths = daily_df['deaths'].sum()
            avg_deaths = total_deaths / max(1, len(daily_df))
            st.metric("Total de Mortes", f"{total_deaths:.0f}", f"Média: {avg_deaths:.1f}/dia")
        
        with col3:
            avg_kd = total_kills / max(1, total_deaths)
            st.metric("K/D Ratio Médio", f"{avg_kd:.2f}")
    
    with performance_tabs[1]:
        # Gráfico de K/D ratio diário
        fig = make_subplots()
        
        # Adicionar linha para K/D ratio
        fig.add_trace(go.Scatter(
            x=daily_df['date'],
            y=daily_df['kd_ratio'],
            name='K/D Ratio',
            line=dict(color='#50fa7b', width=3, shape='spline', smoothing=1.3),
            fill='tozeroy',
            fillcolor='rgba(80, 250, 123, 0.1)',
            mode='lines+markers',
            marker=dict(size=10, symbol='diamond', color='#50fa7b', 
                      line=dict(width=2, color='#1A1A1A'))
        ))
        
        # Adicionar linha de referência para K/D = 1.0
        fig.add_shape(
            type="line",
            x0=daily_df['date'].min(),
            x1=daily_df['date'].max(),
            y0=1.0,
            y1=1.0,
            line=dict(
                color="rgba(255,255,255,0.3)",
                width=1,
                dash="dash",
            ),
        )
        
        # Melhorar layout
        fig.update_layout(
            title="K/D Ratio Diário",
            title_font=dict(size=18, color='#F5B841'),
            xaxis_title=None,
            yaxis_title="K/D Ratio",
            template='plotly_dark',
            height=400,
            margin=dict(l=10, r=10, t=50, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation="h",
                yanchor="top",
                y=1.1,
                xanchor="center",
                x=0.5,
                font=dict(size=12)
            ),
            annotations=[
                dict(
                    x=0.02,
                    y=0.95,
                    xref="paper",
                    yref="paper",
                    text="Performance de K/D da Guild nos Últimos 7 Dias",
                    showarrow=False,
                    font=dict(color="#AAA", size=12)
                )
            ]
        )
        
        fig.update_xaxes(
            showgrid=False,
            showline=True,
            linecolor='rgba(255,255,255,0.2)',
            tickformat='%d/%m',
            tickfont=dict(size=12)
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            showline=False,
            tickfont=dict(size=12),
            title_font=dict(color="#50fa7b")
        )
        
        # Adicionar rótulos para valores importantes
        if not daily_df.empty:
            max_kd_idx = daily_df['kd_ratio'].argmax()
            min_kd_idx = daily_df['kd_ratio'].argmin()
            
            # Rótulo para máximo K/D
            fig.add_annotation(
                x=daily_df['date'].iloc[max_kd_idx],
                y=daily_df['kd_ratio'].iloc[max_kd_idx],
                text=f"Melhor: {daily_df['kd_ratio'].iloc[max_kd_idx]:.2f}",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#50fa7b",
                font=dict(size=10, color="#50fa7b"),
                bgcolor="rgba(0,0,0,0.7)",
                bordercolor="#50fa7b",
                borderwidth=1,
                borderpad=4
            )
            
            # Rótulo para mínimo K/D
            fig.add_annotation(
                x=daily_df['date'].iloc[min_kd_idx],
                y=daily_df['kd_ratio'].iloc[min_kd_idx],
                text=f"Pior: {daily_df['kd_ratio'].iloc[min_kd_idx]:.2f}",
                showarrow=True,
                arrowhead=2,
                arrowcolor="#ff5555",
                font=dict(size=10, color="#ff5555"),
                bgcolor="rgba(0,0,0,0.7)",
                bordercolor="#ff5555",
                borderwidth=1,
                borderpad=4
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Adicionar métricas resumidas
        col1, col2, col3 = st.columns(3)
        with col1:
            if not daily_df.empty:
                max_kd = daily_df['kd_ratio'].max()
                st.metric("Melhor K/D", f"{max_kd:.2f}")
            else:
                st.metric("Melhor K/D", "N/A")
        
        with col2:
            if not daily_df.empty:
                min_kd = daily_df['kd_ratio'].min()
                st.metric("Pior K/D", f"{min_kd:.2f}")
            else:
                st.metric("Pior K/D", "N/A")
        
        with col3:
            if not daily_df.empty:
                avg_kd = daily_df['kd_ratio'].mean()
                st.metric("K/D Médio", f"{avg_kd:.2f}")
            else:
                st.metric("K/D Médio", "N/A")
    
    with performance_tabs[2]:
        # Gráfico de Win Rate diário
        if not daily_df.empty and 'win_rate' in daily_df.columns:
            fig = make_subplots()
            
            # Adicionar linha para Win Rate
            fig.add_trace(go.Scatter(
                x=daily_df['date'],
                y=daily_df['win_rate'],
                name='Win Rate',
                line=dict(color='#F5B841', width=3, shape='spline', smoothing=1.3),
                fill='tozeroy',
                fillcolor='rgba(245, 184, 65, 0.1)',
                mode='lines+markers',
                marker=dict(size=10, symbol='star', color='#F5B841', 
                          line=dict(width=2, color='#1A1A1A'))
            ))
            
            # Adicionar linha de referência para Win Rate = 50%
            fig.add_shape(
                type="line",
                x0=daily_df['date'].min(),
                x1=daily_df['date'].max(),
                y0=50,
                y1=50,
                line=dict(
                    color="rgba(255,255,255,0.3)",
                    width=1,
                    dash="dash",
                ),
            )
            
            # Melhorar layout
            fig.update_layout(
                title="Win Rate Diário",
                title_font=dict(size=18, color='#F5B841'),
                xaxis_title=None,
                yaxis_title="Win Rate (%)",
                template='plotly_dark',
                height=400,
                margin=dict(l=10, r=10, t=50, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=1.1,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=12)
                ),
                yaxis=dict(
                    range=[0, 100]
                ),
                annotations=[
                    dict(
                        x=0.02,
                        y=0.95,
                        xref="paper",
                        yref="paper",
                        text="Taxa de Vitórias nos Últimos 7 Dias",
                        showarrow=False,
                        font=dict(color="#AAA", size=12)
                    )
                ]
            )
            
            fig.update_xaxes(
                showgrid=False,
                showline=True,
                linecolor='rgba(255,255,255,0.2)',
                tickformat='%d/%m',
                tickfont=dict(size=12)
            )
            
            fig.update_yaxes(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                showline=False,
                tickfont=dict(size=12),
                title_font=dict(color="#F5B841")
            )
            
            # Adicionar informações sobre o número de batalhas por dia
            for i, (date, win_rate, battles) in enumerate(zip(daily_df['date'], daily_df['win_rate'], daily_df['battles'])):
                if battles > 0:
                    fig.add_annotation(
                        x=date,
                        y=win_rate,
                        text=f"{battles} batalhas",
                        showarrow=False,
                        yshift=20,
                        font=dict(size=9, color="#AAA")
                    )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Adicionar métricas resumidas
            col1, col2, col3 = st.columns(3)
            with col1:
                total_battles = daily_df['battles'].sum()
                st.metric("Total de Batalhas", f"{total_battles:.0f}")
            
            with col2:
                total_wins = daily_df['wins'].sum()
                st.metric("Vitórias", f"{total_wins:.0f}")
            
            with col3:
                if total_battles > 0:
                    overall_win_rate = (total_wins / total_battles) * 100
                    st.metric("Win Rate Geral", f"{overall_win_rate:.1f}%")
                else:
                    st.metric("Win Rate Geral", "N/A")
        else:
            st.info("Dados de Win Rate não disponíveis.")
    
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
