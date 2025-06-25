import pandas as pd
import numpy as np

season_dict = {
    '2008-09': '1', '2009-10': '2', '2010-11': '3', '2011-12': '4',
    '2012-13': '8', '2013-14': '15', '2014-15': '20', '2015-16': '27',
    '2016-17': '34', '2017-18': '41', '2018-19': '47', '2019-20': '54',
    '2020-21': '59', '2021-22': '63', '2022-23': '71', '2023-24': '80'
}

fase_dict = {
    'regular': '%5B%5D=1',
    'playoffs': '%5B%5D=2',
    'total': '=on&phase%5B%5D=1&phase%5B%5D=2'
}

sofrido_dict = {False: '0', True: '1'}
mandante_dict = {'ambos': '-1', 'mandante': '1', 'visitante': '2'}

seasons = list(season_dict.keys())
seasons_classification = [s.replace('-', '-') for s in season_dict.keys()]
fases = list(fase_dict.keys())
categs = ['pontos', 'rebotes', 'assistencias', 'arremessos', 'bolas-recuperadas',
          'tocos', 'erros', 'eficiencia', 'duplos-duplos', 'enterradas']
tipos = ['avg', 'sum']
quems = ['athletes', 'teams']
sofridos = [True, False]
mandantes = list(mandante_dict.keys())

def get_stats(season, fase, categ, tipo='avg', quem='athletes', mandante='ambos', sofrido=False):
    if season not in seasons:
        raise ValueError(f"{season} não é válido. Tente: {', '.join(seasons)}")
    if fase not in fases:
        raise ValueError(f"{fase} não é válido. Tente: {', '.join(fases)}")
    if categ not in categs:
        raise ValueError(f"{categ} não é válido. Tente: {', '.join(categs)}")
    if tipo not in tipos:
        raise ValueError(f"{tipo} não é válido. Tente: {', '.join(tipos)}")
    if quem not in quems:
        raise ValueError(f"{quem} não é válido. Tente: {', '.join(quems)}")
    if sofrido not in sofridos:
        raise ValueError(f"{sofrido} não é válido. Use True ou False.")
    if mandante not in mandantes:
        raise ValueError(f"{mandante} não é válido. Tente: {', '.join(mandantes)}")

    url = (
        f"https://lnb.com.br/nbb/estatisticas/{categ}/?"
        f"aggr={tipo}&type={quem}&suffered_rule={sofrido_dict[sofrido]}"
        f"&season%5B%5D={season_dict[season]}&phase{fase_dict[fase]}"
        f"&wherePlaying={mandante_dict[mandante]}"
    )

    df = pd.read_html(url)[0]

    if quem == 'athletes':
        df[['Jogador', 'Camisa']] = df['Jogador'].str.extract(r"(.+?)\s+#(\d+)", expand=True)

    df = df.drop(columns=['Pos.'], errors='ignore')
    df['Temporada'] = season

    return df


def get_classificacao(season):
    if season not in seasons_classification:
        raise ValueError(f"{season} não é válido. Tente: {', '.join(seasons_classification)}")

    url = f"https://lnb.com.br/nbb/{season}"
    df = pd.read_html(url)[0]

    df = df.iloc[::2].reset_index(drop=True)
    df = df.dropna(how='all', axis=1)
    df['EQUIPES'] = df['EQUIPES'].str[3:]
    df['TEMPORADA'] = season

    return df


def get_placares(season, fase):
    if season not in seasons:
        raise ValueError(f"{season} não é válido. Tente: {', '.join(seasons)}")
    if fase not in fases:
        raise ValueError(f"{fase} não é válido. Tente: {', '.join(fases)}")

    season_code = season_dict[season]
    fase_code = fase_dict[fase]

    url = (
        f"https://lnb.com.br/nbb/tabela-de-jogos/?season%5B%5D={season_code}"
        + (f"&phase{fase_code}" if fase != 'total' else "")
    )

    df = pd.read_html(url)[0]

    try:
        drop_cols = ['#', 'CASA', 'Unnamed: 15', 'GINÁSIO', 'RODADA']
        if season == '2008-09':
            drop_cols[2] = 'Unnamed: 14'
        df = df.drop(columns=drop_cols, errors='ignore')
        df = df.dropna(how='all', axis=1)
    except Exception:
        raise ValueError("Erro ao processar a tabela. Pode ser que os dados ainda não estejam disponíveis.")

    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y  %H:%M', errors='coerce')

    df = df.rename(columns={
        'TRANSMISSÃO': 'GINASIO',
        'FASE': 'RODADA',
        'CAMPEONATO': 'FASE',
        'Unnamed: 3': 'EQUIPE CASA',
        'Unnamed: 7': 'EQUIPE VISITANTE'
    })

    df['Unnamed: 5'] = df['Unnamed: 5'].str.replace('  VER RELATÓRIO', '', regex=False)
    df['PLACAR CASA'] = df['Unnamed: 5'].str[:2]
    df['PLACAR VISITANTE'] = df['Unnamed: 5'].str[-2:]

    df['PLACAR CASA'] = pd.to_numeric(df['PLACAR CASA'], errors='coerce')
    df['PLACAR VISITANTE'] = pd.to_numeric(df['PLACAR VISITANTE'], errors='coerce')

    df['VENCEDOR'] = np.where(
        df['PLACAR CASA'] > df['PLACAR VISITANTE'], df['EQUIPE CASA'], df['EQUIPE VISITANTE']
    )
    df['VENCEDOR'] = df.apply(
        lambda row: np.nan if pd.isna(row['PLACAR CASA']) or pd.isna(row['PLACAR VISITANTE']) else row['VENCEDOR'],
        axis=1
    )

    df = df.drop(columns=['Unnamed: 5'], errors='ignore')
    df['TEMPORADA'] = season

    final_cols = [
        'DATA', 'EQUIPE CASA', 'PLACAR CASA', 'PLACAR VISITANTE', 'EQUIPE VISITANTE',
        'VENCEDOR', 'RODADA', 'FASE', 'GINASIO', 'TEMPORADA'
    ]
    df = df[[col for col in final_cols if col in df.columns]]

    return df
