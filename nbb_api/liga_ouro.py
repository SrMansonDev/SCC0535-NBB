import pandas as pd
import numpy as np
from .strings import Strings

# Dicionários de suporte
season_dict = {
    '2014': '19', '2015': '24', '2016': '32',
    '2017': '39', '2018': '44', '2019': '51',
    '2025': '93'
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

    if season == '2025':
        url = 'https://lnb.com.br/liga-ouro/'
    else:
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
        raise ValueError(f"{season} não é um valor válido. Tente um de: " + ", ".join(seasons))
    if fase not in fases:
        raise ValueError(f"{fase} não é um valor válido. Tente um de: " + ", ".join(fases))

    season2 = season_dict[str(season)]
    fase_code = fase_dict[fase]

    if fase_code != fase_dict['total']:  # total
        url = (
            'https://lnb.com.br/liga-ouro/tabela-de-jogos/'
            f'?season%5B%5D={season2}&phase%5B%5D={fase_code}'
        )
    else:
        url = f'https://lnb.com.br/liga-ouro/tabela-de-jogos/?season%5B%5D={season2}'

    try:
        df = pd.read_html(url)[0]
        df = df.dropna(how='all', axis=1)

        # Tentativa de remover colunas extras que variam
        try:
            df = df.drop(columns=['#', 'CASA', 'Unnamed: 15', 'GINÁSIO', 'RODADA'])
        except KeyError:
            try:
                df = df.drop(columns=['#', 'CASA', 'Unnamed: 14', 'GINÁSIO', 'RODADA'])
            except Exception:
                pass

        df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y  %H:%M', errors='coerce')

        df = df.rename(columns={
            'TRANSMISSÃO': 'GINASIO',
            'FASE': 'RODADA',
            'CAMPEONATO': 'FASE',
            'Unnamed: 3': Strings.equipe_casa,
            'Unnamed: 7': Strings.equipe_visitante,
            'Unnamed: 5': Strings.placar_raw
        })

        df[Strings.placar_raw] = df[Strings.placar_raw].str.replace('  VER RELATÓRIO', '')
        df[Strings.placar_casa] = df[Strings.placar_raw].str.extract(r'^(\d+)')
        df[Strings.placar_visitante] = df[Strings.placar_raw].str.extract(r'X (\d+)$')

        df[Strings.placar_casa] = pd.to_numeric(df[Strings.placar_casa], errors='coerce')
        df[Strings.placar_visitante] = pd.to_numeric(df[Strings.placar_visitante], errors='coerce')

        df['VENCEDOR'] = np.where(df[Strings.placar_casa] > df[Strings.placar_visitante],
                                  df[Strings.equipe_casa], df[Strings.equipe_visitante])

        df['VENCEDOR'] = df['VENCEDOR'].where(~df[Strings.placar_casa].isna())

        df['TEMPORADA'] = season

        colunas_finais = [
            'DATA', 'EQUIPE CASA', 'PLACAR CASA', 'PLACAR VISITANTE',
            'EQUIPE VISITANTE', 'VENCEDOR', 'RODADA', 'FASE', 'GINASIO', 'TEMPORADA'
        ]
        return df[[col for col in colunas_finais if col in df.columns]]
    except Exception:
        print(msg_erro)
        return pd.DataFrame(columns=[
            'DATA', 'EQUIPE CASA', 'PLACAR CASA', 'PLACAR VISITANTE',
            'EQUIPE VISITANTE', 'VENCEDOR', 'RODADA', 'FASE', 'GINASIO', 'TEMPORADA'
        ])

    return df
