import re
import pandas as pd
import numpy as np
from .strings import Strings

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
seasons_classification = {
    '2008-2009', '2009-2010', '2010-2011', '2011-2012',
    '2012-2013', '2013-2014', '2014-2015', '2015-2016',
    '2016-2017', '2017-2018', '2018-2019', '2019-2020',
    '2020-2021', '2021-2022', '2022-2023', '2023-2024'
}
fases = list(fase_dict.keys())
categs = [
    'pontos', 'rebotes', 'assistencias', 'arremessos', 'bolas-recuperadas',
    'tocos', 'erros', 'eficiencia', 'duplos-duplos', 'enterradas'
]
tipos = ['avg', 'sum']
quems = ['athletes', 'teams']
sofridos = [True, False]
mandantes = list(mandante_dict.keys())

def get_stats(season, fase, categ, tipo='avg', quem='athletes', mandante='ambos', sofrido=False):
    if season not in seasons:
        valid = '", "'.join(seasons)
        raise ValueError(f'{season}{Strings.erro_valor_invalido}"{valid}".')
    if fase not in fases:
        valid = '", "'.join(fases)
        raise ValueError(f'{fase}{Strings.erro_valor_invalido}"{valid}".')
    if categ not in categs:
        valid = '", "'.join(categs)
        raise ValueError(f'{categ}{Strings.erro_valor_invalido}"{valid}".')
    if tipo not in tipos:
        valid = '", "'.join(tipos)
        raise ValueError(f'{tipo}{Strings.erro_valor_invalido}"{valid}".')
    if quem not in quems:
        valid = '", "'.join(quems)
        raise ValueError(f'{quem}{Strings.erro_valor_invalido}"{valid}".')
    if sofrido not in sofridos:
        raise ValueError(f"{sofrido} não é válido. Use True ou False.")
    if mandante not in mandantes:
        valid = '", "'.join(mandantes)
        raise ValueError(f'{mandante}{Strings.erro_valor_invalido}"{valid}".')

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
    raw = season
    if re.match(r'^\d{4}-\d{2}$', season):
        start, suffix = season.split('-')
        season = f"{start}-{start[:2] + suffix}"
    if season not in seasons_classification:
        valid = '", "'.join(seasons_classification)
        raise ValueError(f'{raw}{Strings.erro_valor_invalido}"{valid}".')

    url = f"https://lnb.com.br/nbb/{season}"
    df = pd.read_html(url)[0]
    df = df.iloc[::2].reset_index(drop=True)
    df = df.dropna(how='all', axis=1)
    df['EQUIPES'] = df['EQUIPES'].str[3:]
    df['TEMPORADA'] = raw
    return df

def get_placares(season, fase):
    if season not in seasons:
        valid = '", "'.join(seasons)
        raise ValueError(f'{season}{Strings.erro_valor_invalido}"{valid}".')
    if fase not in fases:
        valid = '", "'.join(fases)
        raise ValueError(f'{fase}{Strings.erro_valor_invalido}"{valid}".')

    season_code = season_dict[season]
    fase_code = fase_dict[fase]
    url = f"https://lnb.com.br/nbb/tabela-de-jogos/?season%5B%5D={season_code}"
    if fase != 'total':
        url += f"&phase{fase_code}"

    df = pd.read_html(url)[0]

    # descartamos colunas desnecessárias, ignorando se alguma não existir
    drop_cols = ['#', 'CASA', 'GINÁSIO', 'GINASIO', 'RODADA']
    unnamed_col = 'Unnamed: 14' if season == '2008-09' else 'Unnamed: 15'
    drop_cols.insert(2, unnamed_col)
    df = df.drop(columns=drop_cols, errors='ignore')

    df = df.dropna(how='all', axis=1)
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y  %H:%M', errors='coerce')

    df = df.rename(columns={
        'TRANSMISSÃO': 'GINASIO',
        'FASE': 'RODADA',
        'CAMPEONATO': 'FASE',
        'Unnamed: 3': 'EQUIPE CASA',
        'Unnamed: 7': Strings.equipe_visitante
    })

    df[Strings.unnamed_5] = df[Strings.unnamed_5].str.replace('  VER RELATÓRIO', '', regex=False)
    df[Strings.placar_casa] = df[Strings.unnamed_5].str[:2]
    df[Strings.placar_visitante] = df[Strings.unnamed_5].str[-2:]
    df[Strings.placar_casa] = pd.to_numeric(df[Strings.placar_casa], errors='coerce')
    df[Strings.placar_visitante] = pd.to_numeric(df[Strings.placar_visitante], errors='coerce')
    df = df.drop(columns=[Strings.unnamed_5], errors='ignore')

    df['VENCEDOR'] = np.where(
        df[Strings.placar_casa] > df[Strings.placar_visitante],
        df['EQUIPE CASA'],
        df[Strings.equipe_visitante]
    )
    df['VENCEDOR'] = np.where(
        df[Strings.placar_casa].isna(),
        np.nan,
        df['VENCEDOR']
    )

    df['TEMPORADA'] = season
    cols = [
        'DATA', 'EQUIPE CASA', Strings.placar_casa,
        Strings.placar_visitante, Strings.equipe_visitante,
        'VENCEDOR', 'RODADA', 'FASE', 'GINASIO', 'TEMPORADA'
    ]
    if season == '2008-09':
        cols.remove('GINASIO')
    return df[cols]
