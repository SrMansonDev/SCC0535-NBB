import pandas as pd
import numpy as np
from .strings import Strings

# Dicionários de suporte
season_dict = {
    '2014': '19', '2015': '24', '2016': '32',
    '2017': '39', '2018': '44', '2019': '51'
}

fase_dict = {
    'regular': '1',
    'playoffs': '2',
    'total': '=on&phase%5B%5D=1&phase%5B%5D=2'
}

# Valores válidos
seasons = list(season_dict.keys()) + ['2025']  # 2025 incluído como placeholder
fases = list(fase_dict.keys())

msg_erro = "Erro ao carregar os dados da Liga Ouro. Verifique se a temporada está disponível ou tente novamente mais tarde."


# ============================================================
# Classificação
# ============================================================
def get_classificacao(season):
    if str(season) not in seasons:
        raise ValueError(f"{season} não é um valor válido. Tente um de: " + ", ".join(seasons))

    url = f'https://lnb.com.br/liga-ouro/liga-ouro-{season}'

    try:
        df = pd.read_html(url)[0]
        df = df.iloc[::2].reset_index(drop=True)
        df = df.dropna(how='all', axis=1)

        df['EQUIPES'] = df['EQUIPES'].str[3:]
        df['TEMPORADA'] = season

        return df
    except Exception:
        print(msg_erro)
        return pd.DataFrame(columns=['EQUIPES', 'TEMPORADA'])


# ============================================================
# Placar
# ============================================================
def get_placares(season, fase):
    
    if str(season) not in seasons:
        raise ValueError(str(season) + Strings.erro_valor_invalido + '", "'.join(seasons) + '".')
    
    if fase not in fases:
        raise ValueError(str(fase) + Strings.erro_valor_invalido + '", "'.join(fases) + '".')
    
    season2 = season_dict[str(season)]
    fase = fase_dict[fase]
    
    if fase != '=on&phase%5B%5D=1&phase%5B%5D=2':  # total
        url = 'https://lnb.com.br/liga-ouro/tabela-de-jogos/?season%5B%5D=' + season2 + '&phase%5B%5D=' + fase
    else:
        url = 'https://lnb.com.br/liga-ouro/tabela-de-jogos/?season%5B%5D=' + season2
    
    df = pd.read_html(url)[0]
    
    df = df.drop(columns=['#', 'CASA', 'Unnamed: 15', 'GINÁSIO', 'RODADA'])
    df = df.dropna(how='all', axis=1)
    
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y  %H:%M')
    
    df = df.rename(columns={
        'TRANSMISSÃO': 'GINASIO',
        'FASE': 'RODADA',
        'CAMPEONATO': 'FASE',
        'Unnamed: 3': Strings.equipe_casa,
        'Unnamed: 7': Strings.equipe_visitante
    })
    
    df[Strings.unnamed_5] = df[Strings.unnamed_5].str.replace('  VER RELATÓRIO', '')
    df[Strings.placar_casa] = df[Strings.unnamed_5].str[:2]
    df[Strings.placar_visitante] = df[Strings.unnamed_5].str[-2:]
    
    df[Strings.placar_casa] = df[Strings.placar_casa].apply(lambda x: np.nan if 'X' in str(x) else x)
    df[Strings.placar_visitante] = df[Strings.placar_visitante].apply(lambda x: np.nan if 'X' in str(x) else x)
    
    df = df.drop(columns=[Strings.unnamed_5])
    
    df['VENCEDOR'] = np.where(df[Strings.placar_casa] > df[Strings.placar_visitante], df[Strings.equipe_casa], df[Strings.equipe_visitante])
    df['VENCEDOR'] = np.where(df[Strings.placar_casa] == np.nan, np.nan, df['VENCEDOR'])
    
    df['TEMPORADA'] = season
    
    df = df[['DATA', Strings.equipe_casa, Strings.placar_casa, Strings.placar_visitante, Strings.equipe_visitante,
             'VENCEDOR', 'RODADA', 'FASE', 'GINASIO', 'TEMPORADA']]