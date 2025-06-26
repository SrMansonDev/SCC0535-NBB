import pandas as pd
import numpy as np
from .strings import Strings

season_dict = {
    '2008-09': '1', '2009-10': '2', '2010-11': '3', '2011-12': '4',
    '2012-13': '8', '2013-14': '15', '2014-15': '20', '2015-16': '27',
    '2016-17': '34', '2017-18': '41', '2018-19': '47', '2019-20': '54',
    '2020-21': '59', '2021-22': '63', '2022-23': '71', '2023-24': '80',
    '2024-25': '88'
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

def _validate_choice(value, allowed, is_boolean=False):
    if value not in allowed:
        if is_boolean:
            raise ValueError(str(value) + Strings.error_valor_invalido_boolean)
        allowed_str = '", "'.join(allowed)
        raise ValueError(f'{value}{Strings.erro_valor_invalido}"{allowed_str}".')

def get_stats(season, fase, categ, tipo='avg', quem='athletes', mandante='ambos', sofrido=False):
    _validate_choice(season, seasons)
    _validate_choice(fase, fases)
    _validate_choice(categ, categs)
    _validate_choice(tipo, tipos)
    _validate_choice(quem, quems)
    _validate_choice(sofrido, sofridos, is_boolean=True)
    _validate_choice(mandante, mandantes)

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
    _validate_choice(season, seasons_classification)

    start, end = season.split('-')        # e.g. ["2023","24"]
    full_end = start[:2] + end            # "20" + "24" → "2024"
    season_url = f"{start}-{full_end}"    # "2023-2024"

    url = f"https://lnb.com.br/nbb/{season_url}"

    df = pd.read_html(url)[0]

    df = df.iloc[::2].reset_index(drop=True)
    df = df.dropna(how='all', axis=1)
    df['EQUIPES'] = df['EQUIPES'].str[3:]
    df['TEMPORADA'] = season

    return df


def get_placares(season, fase):
    _validate_choice(season, seasons)
    _validate_choice(fase, fases)

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
        'Unnamed: 3': Strings.equipe_casa,
        'Unnamed: 7': Strings.equipe_visitante
    })

    df[Strings.unnamed_5] = df[Strings.unnamed_5].str.replace('  VER RELATÓRIO', '', regex=False)
    df[Strings.placar_casa] = df[Strings.unnamed_5].str[:2]
    df[Strings.placar_visitante] = df[Strings.unnamed_5].str[-2:]

    df[Strings.placar_casa] = pd.to_numeric(df[Strings.placar_casa], errors='coerce')
    df[Strings.placar_visitante] = pd.to_numeric(df[Strings.placar_visitante], errors='coerce')

    df['VENCEDOR'] = np.where(
        df[Strings.placar_casa] > df[Strings.placar_visitante], df[Strings.equipe_casa], df[Strings.equipe_visitante]
    )
    df['VENCEDOR'] = df.apply(
        lambda row: np.nan if pd.isna(row[Strings.placar_casa]) or pd.isna(row[Strings.placar_visitante]) else row['VENCEDOR'],
        axis=1
    )

    df = df.drop(columns=[Strings.unnamed_5], errors='ignore')
    df['TEMPORADA'] = season
    
    if season!='2008-09':
        df = df[['DATA',Strings.equipe_casa,Strings.placar_casa,Strings.placar_visitante,Strings.equipe_visitante,
                 'VENCEDOR','RODADA','FASE','GINASIO','TEMPORADA']]
    else:
        df = df[['DATA',Strings.equipe_casa,Strings.placar_casa,Strings.placar_visitante,Strings.equipe_visitante,
             'VENCEDOR','RODADA','FASE','TEMPORADA']]
        
    return df
