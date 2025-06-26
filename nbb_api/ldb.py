import pandas as pd
import warnings
import numpy as np
from .strings import Strings

# Dicionários de suporte
season_dict = {
    '2011': '5', '2012': '10', '2013': '14', '2014': '21',
    '2015': '29', '2016': '36', '2017': '42', '2018': '48',
    '2019': '53', '2021': '64', '2022': '69', '2023': '78'
}

fase_dict = {
    'regular': '%5B%5D=1',
    'total': '%5B%5D=1&phase%5B%5D=2&phase%5B%5D=3&phase%5B%5D=4'
}

sofrido_dict = {False: '0', True: '1'}

# Listas de valores válidos
seasons = list(season_dict.keys())
fases = list(fase_dict.keys())
categs = ['cestinhas', 'rebotes', 'assistencias', 'arremessos', 'bolas-recuperadas',
          'tocos', 'erros', 'eficiencia', 'duplos-duplos', 'enterradas']
tipos = ['avg', 'sum']
quems = ['athletes', 'teams']
sofridos = [True, False]

msg_erro = "O site da LNB está com problemas nos dados da LDB, por hora não vai funcionar. Use outras ligas!"


# ==========================================
# CLASSIFICAÇÃO
# ==========================================

def get_classificacao(season):
    if str(season) not in seasons:
        raise ValueError(str(season)+Strings.erro_valor_invalido+'", "'.join(seasons)+'".')

    season2 = season_dict[str(season)]
    url = f'https://lnb.com.br/liga-ouro/?season={season2}'

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


# ==========================================
# ESTATÍSTICAS
# ==========================================

def get_stats(season, fase, categ, tipo='avg', quem='athletes', sofrido=False):
    if str(season) not in seasons:
        raise ValueError(str(season)+Strings.erro_valor_invalido+'", "'.join(seasons)+'".')

    if fase not in fases:
        raise ValueError(str(fase)+Strings.erro_valor_invalido+'", "'.join(fases)+'".')

    if categ not in categs:
        raise ValueError(str(categ)+Strings.erro_valor_invalido+'", "'.join(categs)+'".')

    if tipo not in tipos:
        raise ValueError(str(tipo)+Strings.erro_valor_invalido+'", "'.join(tipos)+'".')

    if quem not in quems:
        raise ValueError(str(quem)+Strings.erro_valor_invalido+'", "'.join(quems)+'".')

        raise ValueError(f"{quem} não é um valor válido. Tente um de: " + ", ".join(quems))
    if sofrido not in sofridos:
        raise ValueError(f"{sofrido} não é um valor válido. Tente True ou False.")

    season2 = season_dict[str(season)]
    fase_encoded = fase_dict[fase]
    sofrido_val = sofrido_dict[sofrido]

    url = (f'https://lnb.com.br/ldb/estatisticas/{categ}/?aggr={tipo}&type={quem}'
           f'&suffered_rule={sofrido_val}&season%5B%5D={season2}&phase{fase_encoded}')

    try:
        df = pd.read_html(url)[0]
        if quem == 'athletes':
            df['Camisa'] = df['Jogador'].str.extract(r'#(\d+)$')
            df['Jogador'] = df['Jogador'].str.replace(r' #\d+$', '', regex=True)
        if 'Pos.' in df.columns:
            df = df.drop(columns=['Pos.'])
        df['Temporada'] = season
        return df
    except Exception:
        print(msg_erro)
        return pd.DataFrame(columns=['Jogador' if quem == 'athletes' else 'Equipe', 'Temporada'])


# ==========================================
# PLACARES
# ==========================================

def get_placares(season, fase):
    if str(season) not in seasons:
        raise ValueError(str(season)+Strings.erro_valor_invalido+'", "'.join(seasons)+'".')

    if fase not in fases:
        raise ValueError(str(fase)+Strings.erro_valor_invalido+'", "'.join(fases)+'".')

    season2 = season_dict[str(season)]

    fase_encoded = fase_dict[fase]

    if fase_encoded != '%5B%5D=1&phase%5B%5D=2&phase%5B%5D=3&phase%5B%5D=4':
        url = f'https://lnb.com.br/liga-ouro/tabela-de-jogos/?season%5B%5D={season2}&phase{fase_encoded}'
    else:
        url = f'https://lnb.com.br/liga-ouro/tabela-de-jogos/?season%5B%5D={season2}'

    try:
        df = pd.read_html(url)[0]
        df = df.dropna(how='all', axis=1)

        # Tentativa de remoção de colunas extras
        try:
            df = df.drop(columns=['#', 'CASA', 'Unnamed: 15', 'GINÁSIO', 'RODADA'])
        except KeyError:
            try:
                df = df.drop(columns=['#', 'CASA', 'Unnamed: 14', 'GINÁSIO', 'RODADA'])
            except Exception:
                pass  # Continua mesmo que não consiga

        df['DATA'] = pd.to_datetime(df['DATA'], errors='coerce', format='%d/%m/%Y  %H:%M')

        df = df.rename(columns={
            'Unnamed: 3': 'EQUIPE CASA',
            'Unnamed: 7': 'EQUIPE VISITANTE',
            'Unnamed: 5': 'PLACAR RAW',
            'TRANSMISSÃO': 'GINASIO',
            'FASE': 'RODADA',
            'CAMPEONATO': 'FASE'
        })

        df['PLACAR RAW'] = df['PLACAR RAW'].str.replace('  VER RELATÓRIO', '')
        df['PLACAR CASA'] = df['PLACAR RAW'].str.extract(r'^(\d+)')
        df['PLACAR VISITANTE'] = df['PLACAR RAW'].str.extract(r'X (\d+)$')

        df['VENCEDOR'] = np.where(df['PLACAR CASA'].astype(float) > df['PLACAR VISITANTE'].astype(float),
                                  df['EQUIPE CASA'], df['EQUIPE VISITANTE'])
        df['TEMPORADA'] = season

        cols_final = ['DATA', 'EQUIPE CASA', 'PLACAR CASA', 'PLACAR VISITANTE',
                      'EQUIPE VISITANTE', 'VENCEDOR', 'RODADA', 'FASE', 'GINASIO', 'TEMPORADA']
        return df[[col for col in cols_final if col in df.columns]]
    except Exception:
        print(msg_erro)
        return pd.DataFrame(columns=[
            'DATA', 'EQUIPE CASA', 'PLACAR CASA', 'PLACAR VISITANTE',
            'EQUIPE VISITANTE', 'VENCEDOR', 'RODADA', 'FASE', 'GINASIO', 'TEMPORADA'
        ])
