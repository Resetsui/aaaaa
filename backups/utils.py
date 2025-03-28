import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import random

# Importar o logotipo
from assets.logo import LOGO_SVG, ICON_SVG

# Função para carregar CSS personalizado
def load_css():
    """Load custom CSS for the dashboard"""
    st.markdown("""
    <style>
    /* Cores da WE PROFIT:
       - Dourado principal: #F5B841
       - Dourado mais escuro: #D4A12C
       - Dourado claro: #FFDB8C
       - Fundo escuro: #1A1A1A
       - Texto claro: #F9F9F9
    */
    
    /* Estilos globais */
    .main {
        background-color: #1A1A1A;
        color: #F9F9F9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Estilo do header */
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 30px;
        justify-content: center;
    }
    
    .guild-logo {
        max-width: 120px;
        filter: drop-shadow(0px 0px 10px rgba(245, 184, 65, 0.5));
    }
    
    /* Estilo das abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: #222222;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px;
        padding: 10px 25px;
        background-color: #2A2A2A;
        color: #CCCCCC;
        font-weight: 500;
        transition: all 0.3s ease;
        border: 1px solid #333333;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #F5B841;
        color: #000000 !important;
        font-weight: 600;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(245, 184, 65, 0.3);
        border: none;
    }
    
    /* Cartões de estatísticas */
    .stat-card {
        padding: 25px;
        border-radius: 12px;
        background-color: #242424;
        margin-bottom: 25px;
        border-left: 4px solid #F5B841;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        border-left: 6px solid #F5B841;
    }
    
    /* Cartões de batalha */
    .battle-card {
        padding: 18px;
        border-radius: 12px;
        background-color: #242424;
        margin-bottom: 15px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid #333333;
        position: relative;
        overflow: hidden;
    }
    
    .battle-card:hover {
        border-left: 5px solid #F5B841;
        transform: translateX(5px);
        background-color: #2A2A2A;
    }
    
    .battle-card:after {
        content: '';
        position: absolute;
        bottom: 0;
        right: 0;
        width: 25%;
        height: 3px;
        background: linear-gradient(90deg, transparent, #F5B841);
    }
    
    /* Customização de botões */
    button[kind="primary"] {
        background-color: #F5B841 !important;
        color: #000000 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 10px rgba(245, 184, 65, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(245, 184, 65, 0.4) !important;
    }
    
    /* Customização dos headers */
    h1, h2, h3 {
        color: #F5B841;
        font-weight: 600;
        margin-bottom: 15px;
        position: relative;
    }
    
    h1:after, h2:after {
        content: '';
        position: absolute;
        bottom: -8px;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #F5B841, transparent);
    }
    
    /* Barras de progresso e spinners */
    .stProgress .st-eh {
        background-color: #F5B841 !important;
    }
    
    /* Alertas e notificações */
    .stAlert {
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Customização dos inputs */
    input, select, textarea {
        border-radius: 8px !important;
        border: 1px solid #333333 !important;
        background-color: #2A2A2A !important;
        color: #F9F9F9 !important;
    }
    
    /* Customização dos sliders */
    .stSlider [data-baseweb="slider"] {
        height: 6px !important;
    }
    
    .stSlider [data-baseweb="thumb"] {
        height: 20px !important;
        width: 20px !important;
        background-color: #F5B841 !important;
        box-shadow: 0 2px 10px rgba(245, 184, 65, 0.3) !important;
    }
    
    /* Estilos para divisores */
    hr {
        border-color: #333333 !important;
        margin: 25px 0 !important;
    }
    
    /* Estilos para gráficos */
    .plotly-graph {
        border-radius: 12px !important;
        background-color: #242424 !important;
        padding: 15px !important;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Função para exibir o logotipo da guild
def display_logo():
    """Display the guild logo centered at the top of the page"""
    st.markdown(f"""
    <div class="header-container">
        {LOGO_SVG}
        <h1>WE PROFIT</h1>
    </div>
    """, unsafe_allow_html=True)

# Função para formatar números com separadores de milhar
def format_number(num):
    """Format numbers with commas for thousands"""
    return "{:,}".format(num)

# Função para criar um gráfico de calibre para K/D ratio
def create_kd_gauge(kills, deaths):
    """Create a KD ratio gauge chart"""
    kd_ratio = kills / max(1, deaths)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=kd_ratio,
        number={'suffix': " K/D", 'font': {'size': 25, 'color': '#F5B841'}},
        gauge={
            'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "#FFFFFF", 'tickfont': {'color': '#AAAAAA'}},
            'bar': {'color': get_kd_color(kd_ratio)},
            'bgcolor': "#2A2A2A",
            'borderwidth': 2,
            'bordercolor': "#3A3A3A",
            'steps': [
                {'range': [0, 1], 'color': 'rgba(255, 82, 82, 0.3)'},
                {'range': [1, 3], 'color': 'rgba(255, 193, 7, 0.3)'},
                {'range': [3, 10], 'color': 'rgba(76, 175, 80, 0.3)'}
            ]
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=30, b=10),
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F9F9F9'}
    )
    
    return fig

# Função para criar um gráfico de calibre para taxa de vitórias
def create_win_rate_gauge(win_rate):
    """Create a win rate gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=win_rate,
        number={'suffix': "%", 'font': {'size': 25, 'color': '#F5B841'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#FFFFFF", 'tickfont': {'color': '#AAAAAA'}},
            'bar': {'color': get_win_rate_color(win_rate)},
            'bgcolor': "#2A2A2A",
            'borderwidth': 2,
            'bordercolor': "#3A3A3A",
            'steps': [
                {'range': [0, 40], 'color': 'rgba(255, 82, 82, 0.3)'},
                {'range': [40, 60], 'color': 'rgba(255, 193, 7, 0.3)'},
                {'range': [60, 100], 'color': 'rgba(76, 175, 80, 0.3)'}
            ]
        }
    ))
    
    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=30, b=10),
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#F9F9F9'}
    )
    
    return fig

# Função para criar um gráfico de linha para estatísticas diárias
def create_daily_stats_chart(daily_stats):
    """Create a line chart for daily kills and deaths"""
    if daily_stats.empty:
        return None
    
    # Converter para datetime para melhor formatação
    daily_stats['date'] = pd.to_datetime(daily_stats['date'])
    
    fig = go.Figure()
    
    # Adicionar linha para kills com design mais moderno
    fig.add_trace(go.Scatter(
        x=daily_stats['date'],
        y=daily_stats['kills'],
        name='Kills',
        line=dict(color='#F5B841', width=3, shape='spline', smoothing=1.3),
        fill='tozeroy',
        fillcolor='rgba(245, 184, 65, 0.1)',
        mode='lines+markers',
        marker=dict(size=8, symbol='circle', color='#F5B841', 
                  line=dict(width=2, color='#1A1A1A'))
    ))
    
    # Adicionar linha para mortes com design correspondente
    fig.add_trace(go.Scatter(
        x=daily_stats['date'],
        y=daily_stats['deaths'],
        name='Mortes',
        line=dict(color='#9E9E9E', width=3, shape='spline', smoothing=1.3),
        fill='tozeroy',
        fillcolor='rgba(158, 158, 158, 0.1)',
        mode='lines+markers',
        marker=dict(size=8, symbol='circle', color='#9E9E9E', 
                  line=dict(width=2, color='#1A1A1A'))
    ))
    
    # Melhorar layout geral
    fig.update_layout(
        title=None,  # Remover título para um visual mais clean
        xaxis_title=None,
        yaxis_title=None,
        template='plotly_dark',
        height=300,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.1,
            xanchor="center",
            x=0.5,
            font=dict(size=14)
        )
    )
    
    # Customizar eixos
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
        tickfont=dict(size=12)
    )
    
    return fig

# Função para criar um gráfico de barras para métricas de jogadores
def create_player_chart(players_data, metric="kills"):
    """Create a horizontal bar chart for player metrics"""
    if not players_data:
        return None
    
    # Converter para DataFrame
    df = pd.DataFrame(players_data)
    
    # Ordenar por métrica
    df = df.sort_values(metric, ascending=True)
    
    # Limitar a 10 jogadores
    df = df.tail(10)
    
    # Criar gráfico
    if metric == 'kd_ratio':
        fig = px.bar(
            df,
            x=metric,
            y='name',
            orientation='h',
            title=f"Top Jogadores por {metric.upper()}",
            labels={'name': 'Jogador', metric: metric.upper()},
            text=df[metric].apply(lambda x: f"{x:.2f}"),
            color=metric,
            color_continuous_scale=['#2A2A2A', '#F5B841'],
            hover_data={'kills': True, 'deaths': True}
        )
    else:
        fig = px.bar(
            df,
            x=metric,
            y='name',
            orientation='h',
            title=f"Top Jogadores por {metric.capitalize()}",
            labels={'name': 'Jogador', metric: metric.capitalize()},
            text=metric,
            color=metric,
            color_continuous_scale=['#2A2A2A', '#F5B841'],
            hover_data={'kills': True, 'deaths': True, 'kd_ratio': ':.2f'}
        )
    
    fig.update_layout(
        template='plotly_dark',
        height=400,
        margin=dict(l=10, r=10, t=40, b=20)
    )
    
    return fig

# Função para criar um gráfico de comparação entre guildas
def create_guild_comparison_chart(guild_stats, enemy_stats, metric="kd_ratio"):
    """Create a comparison chart between guild and enemy guilds"""
    if not enemy_stats:
        return None
    
    # Preparar dados
    guilds = [guild_stats['name']]
    values = [guild_stats[metric]]
    
    # Adicionar dados de guildas inimigas (agora enemy_stats é um dicionário)
    for guild_name, stats in enemy_stats.items():
        guilds.append(stats['name'])
        values.append(stats[metric])
    
    # Definir cores (destacar a guild principal com a cor dourada)
    colors = ['#F5B841'] + ['#2E2E2E'] * len(enemy_stats)
    
    # Formatar valores para exibição no gráfico
    if metric == 'kd_ratio':
        formatted_values = [f"{v:.2f}" for v in values]
    elif metric in ['kills', 'deaths', 'fame']:
        formatted_values = [f"{int(v):,}" for v in values]
    else:
        formatted_values = [str(v) for v in values]
    
    # Criar gráfico
    fig = go.Figure(go.Bar(
        x=guilds,
        y=values,
        marker_color=colors,
        text=formatted_values,
        textposition='auto'
    ))
    
    # Customizar layout
    title_map = {
        'kd_ratio': 'K/D Ratio',
        'kills': 'Total de Kills',
        'deaths': 'Total de Mortes',
        'fame': 'Fame Total'
    }
    
    fig.update_layout(
        title=f"Comparação de {title_map.get(metric, metric)}",
        xaxis_title='Guilds',
        yaxis_title=title_map.get(metric, metric),
        template='plotly_dark',
        height=400,
        margin=dict(l=10, r=10, t=40, b=20)
    )
    
    return fig

# Função para obter cor com base no K/D ratio
def get_kd_color(kd_ratio):
    """Get color based on KD ratio"""
    if kd_ratio < 1:
        return '#FF5252'  # Vermelho
    elif kd_ratio < 3:
        return '#FFC107'  # Amarelo
    else:
        return '#4CAF50'  # Verde

# Função para obter cor com base na taxa de vitórias
def get_win_rate_color(win_rate):
    """Get color based on win rate"""
    if win_rate < 40:
        return '#FF5252'  # Vermelho
    elif win_rate < 60:
        return '#FFC107'  # Amarelo
    else:
        return '#4CAF50'  # Verde

# Função para exibir um card de batalha
def display_battle_card(battle, guild_name):
    """Display a single battle card with basic info"""
    # Calcular valores relevantes
    kd = battle['kills'] / max(1, battle['deaths'])
    result = "Vitória" if battle['kills'] > battle['deaths'] else "Derrota"
    result_color = "#4CAF50" if result == "Vitória" else "#FF5252"
    battle_time = battle['time'].strftime("%d/%m/%Y %H:%M")
    
    # Lista de jogadores para mostrar (limitado a 3)
    top_players = []
    player_count = 0
    
    try:
        if 'details' in battle and 'guilds' in battle['details']:
            for guild, guild_stats in battle['details']['guilds'].items():
                if guild_name.lower() in guild.lower():
                    players = sorted(guild_stats['players'], key=lambda p: p['kills'], reverse=True)
                    for p in players[:3]:
                        top_players.append({
                            'name': p['name'],
                            'kills': p['kills'],
                            'deaths': p['deaths']
                        })
                    player_count = len(guild_stats['players'])
                    break
    except Exception:
        # Em caso de erro, continuamos com a lista vazia
        pass
    
    # Partes do HTML para montar o card
    top_players_html = ""
    if top_players:
        players_items = []
        for p in top_players:
            player_color = "#4CAF50" if p["kills"] > p["deaths"] else "#FF5252"
            kd_ratio = p["kills"] / max(1, p["deaths"])
            player_html = f'<div style="background-color: rgba(245, 184, 65, 0.1); border-radius: 6px; padding: 5px 10px; font-size: 12px; position: relative; border-left: 3px solid {player_color};"><span style="color: #F5B841; font-weight: bold;">{p["name"]}</span><div style="display: flex; gap: 10px; margin-top: 2px;"><span style="color: #4CAF50;">{p["kills"]} K</span><span style="color: #FF5252;">{p["deaths"]} D</span><span style="color: #F5B841;">{kd_ratio:.1f} K/D</span></div></div>'
            players_items.append(player_html)
        
        players_list = "".join(players_items)
        top_players_html = f'<div style="margin-top: 15px; background-color: rgba(0,0,0,0.15); padding: 12px; border-radius: 8px;"><div style="font-size: 14px; color: #F5B841; margin-bottom: 10px; font-weight: bold;"><svg width="16" height="16" style="vertical-align: middle; margin-right: 5px;" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" fill="#F5B841"/></svg>Top Players</div><div style="display: flex; flex-wrap: wrap; gap: 10px;">{players_list}</div></div>'
    
    # HTML do card principal
    html = f'''
    <div style="background-color: rgba(30, 30, 40, 0.4); padding: 18px; border-radius: 10px; margin: 15px 0; border: 1px solid rgba(245, 184, 65, 0.15); position: relative; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);">
        <div style="position: absolute; top: 0; left: 0; width: 5px; height: 100%; background-color: {result_color};"></div>
        <div style="position: absolute; top: 0; right: 0; width: 100px; height: 100px; background: radial-gradient(circle at top right, rgba(245, 184, 65, 0.15), transparent 70%); border-radius: 50%;"></div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <div>
                <span style="color: #AAAAAA; font-size: 12px;">{battle_time}</span>
                <div style="font-weight: bold; margin-top: 5px; color: #F5B841; font-size: 16px;">{player_count} jogadores</div>
            </div>
            <div>
                <span style="background-color: {result_color}; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold;">{result}</span>
            </div>
        </div>
        <div style="display: flex; justify-content: space-between; margin: 15px 0; background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px;">
            <div style="text-align: center; padding: 0 15px;">
                <div style="font-size: 22px; font-weight: bold; color: #4CAF50;">{battle['kills']}</div>
                <div style="font-size: 12px; color: #AAAAAA;">Kills</div>
            </div>
            <div style="text-align: center; padding: 0 15px; border-left: 1px solid rgba(255,255,255,0.1); border-right: 1px solid rgba(255,255,255,0.1);">
                <div style="font-size: 22px; font-weight: bold; color: #FF5252;">{battle['deaths']}</div>
                <div style="font-size: 12px; color: #AAAAAA;">Mortes</div>
            </div>
            <div style="text-align: center; padding: 0 15px;">
                <div style="font-size: 22px; font-weight: bold; color: #F5B841;">{kd:.2f}</div>
                <div style="font-size: 12px; color: #AAAAAA;">K/D</div>
            </div>
        </div>
        {top_players_html}
    </div>
    '''
    
    # Renderizar o HTML
    st.markdown(html, unsafe_allow_html=True)