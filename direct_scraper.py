import requests
import pandas as pd
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BATTLES_URL = "https://gameinfo.albiononline.com/api/gameinfo/battles?range=week&offset=0&limit=51&sort=totalfame&guildId=gUFLG-kcRFC1iOJDdwW2BQ"
GUILD_NAME = "We Profit"
GUILD_ID = "gUFLG-kcRFC1iOJDdwW2BQ"

def get_battle_data(force_refresh=False):
    try:
        if not force_refresh:
            try:
                with open('data.json', 'r') as f:
                    response = json.load(f)
                logging.info("Dados carregados do arquivo local")
            except:
                logging.info("Arquivo local não encontrado, buscando da API")
                response = requests.get(BATTLES_URL).json()
                with open('data.json', 'w') as f:
                    json.dump(response, f)
        else:
            response = requests.get(BATTLES_URL).json()
            with open('data.json', 'w') as f:
                json.dump(response, f)

        processed_battles = []

        for battle in response:
            try:
                guild_players = []
                guild_kills = 0
                guild_deaths = 0
                guild_fame = 0

                # Processar jogadores
                for player_id, player_data in battle.get('players', {}).items():
                    if player_data.get('guildId') == GUILD_ID:
                        guild_players.append({
                            'name': player_data.get('name'),
                            'kills': player_data.get('kills', 0),
                            'deaths': player_data.get('deaths', 0),
                            'fame': player_data.get('killFame', 0)
                        })
                        guild_kills += player_data.get('kills', 0)
                        guild_deaths += player_data.get('deaths', 0)
                        guild_fame += player_data.get('killFame', 0)

                if guild_players:  # Só adicionar batalhas com jogadores da guild
                    battle_id = battle.get('id')
                    battle_time = datetime.fromisoformat(battle.get('startTime').replace('Z', '+00:00'))
                    # Structure battle data with guilds information
                    battle_details = {
                        'battle_id': battle_id,
                        'time': battle_time,
                        'players': len(guild_players),
                        'kills': guild_kills,
                        'deaths': guild_deaths,
                        'fame': guild_fame,
                        'details': {
                            'id': battle_id,
                            'time': battle_time,
                            'guilds': {
                                'We Profit': {
                                    'players': guild_players,
                                    'total_kills': guild_kills,
                                    'total_deaths': guild_deaths,
                                    'total_fame': guild_fame
                                }
                            },
                            'totalKills': battle.get('totalKills'),
                            'totalFame': battle.get('totalFame')
                        }
                    }
                    processed_battles.append(battle_details)
            except Exception as e:
                logging.error(f"Erro ao processar batalha {battle.get('id')}: {str(e)}")
                continue

        battles_df = pd.DataFrame(processed_battles)
        logging.info(f"Processadas {len(battles_df)} batalhas")
        return battles_df

    except Exception as e:
        logging.error(f"Erro ao processar dados: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    df = get_battle_data(force_refresh=True)
    print(f"Batalhas encontradas: {len(df)}")