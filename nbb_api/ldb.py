import pandas as pd
import warnings
import numpy as np

# constantes de mensagens e nomes de colunas
INVALID_VALUE_MSG = ' não é um valor válido. Tente um de: '
COL_PLACAR_VISITANTE = 'PLACAR VISITANTE'
COL_PLACAR_CASA = 'PLACAR CASA'
FIELD_UNNAMED = 'Unnamed: 5'
COL_EQUIPE_VISITANTE = 'EQUIPE VISITANTE'

season_dict = {
    '2011':'5','2012':'10','2013':'14',
    '2014':'21','2015':'29','2016':'36','2017':'42',
    '2018':'48','2019':'53','2021':'64','2022':'69','2023':'78'
}

fase_dict = {
    'regular':'%5B%5D=1',
    'total':'%5B%5D=1&phase%5B%5D=2&phase%5B%5D=3&phase%5B%5D=4'
}

seasons = ['2011','2012','2013','2014','2015','2016','2017','2018','2019','2021','2022','2023']
fases = ['regular','total']
sofrido_dict = {False:'0', True:'1'}  # só muda p/times
categs = ['cestinhas','rebotes','assistencias','arremessos','bolas-recuperadas','tocos',
          'erros','eficiencia','duplos-duplos','enterradas']
tipos = ['avg','sum']
quems = ['athletes','teams']
sofridos = [True, False]
msg_erro = "O site da LNB está com problemas nos dados da LDB, por hora não vai funcionar. Use outras ligas!"

def get_classificacao(season):
    if str(season) not in seasons:
        allowed = '", "'.join(seasons)
        raise ValueError(f'{season}{INVALID_VALUE_MSG}"{allowed}".')
    
    if season in ["2023", "2024"]:
        url = 'https://lnb.com.br/ldb/temporada-' + str(season)
        df = pd.read_html(url)[0]
        df = df.iloc[::2].reset_index(drop=True)
        df = df.dropna(how='all', axis=1)
        df['EQUIPES'] = df['EQUIPES'].str[3:]
        df['TEMPORADA'] = season
        return df
    else:
        print(msg_erro)  # mensagem de aviso pq o site da LNB não está funcionando corretamente

def get_stats(season, fase, categ, tipo='avg', quem='athletes', sofrido=False):
    if str(season) not in seasons:
        allowed = '", "'.join(seasons)
        raise ValueError(f'{season}{INVALID_VALUE_MSG}"{allowed}".')
    if fase not in fases:
        allowed = '", "'.join(fases)
        raise ValueError(f'{fase}{INVALID_VALUE_MSG}"{allowed}".')
    if categ not in categs:
        allowed = '", "'.join(categs)
        raise ValueError(f'{categ}{INVALID_VALUE_MSG}"{allowed}".')
    if tipo not in tipos:
        allowed = '", "'.join(tipos)
        raise ValueError(f'{tipo}{INVALID_VALUE_MSG}"{allowed}".')
    if quem not in quems:
        allowed = '", "'.join(quems)
        raise ValueError(f'{quem}{INVALID_VALUE_MSG}"{allowed}".')
    if sofrido not in sofridos:
        allowed = '", "'.join(str(x) for x in sofridos)
        raise ValueError(f'{sofrido}{INVALID_VALUE_MSG}"{allowed}".')

    season2 = season_dict[str(season)]
    sofrido_flag = sofrido_dict[sofrido]
    fase_flag = fase_dict[fase]

    url = (
        'https://lnb.com.br/ldb/estatisticas/' + categ +
        '/?aggr=' + tipo +
        '&type=' + quem +
        '&suffered_rule=' + sofrido_flag +
        '&season%5B%5D=' + season2 +
        '&phase' + fase_flag
    )

    df = pd.read_html(url)[0]

    if quem == 'athletes':
        df['Camisa'] = df['Jogador'].str.split(' #').str[1]
        df['Jogador'] = df['Jogador'].str.split(' #').str[0]

    df = df.drop(columns=['Pos.'])
    df['Temporada'] = season
    return df

def get_placares(season, fase):
    if str(season) not in seasons:
        allowed = '", "'.join(seasons)
        raise ValueError(f'{season}{INVALID_VALUE_MSG}"{allowed}".')
    if fase not in fases:
        allowed = '", "'.join(fases)
        raise ValueError(f'{fase}{INVALID_VALUE_MSG}"{allowed}".')

    season2 = season_dict[str(season)]
    fase_flag = fase_dict[fase]

    if fase_flag != fase_dict['total']:
        url = (
            'https://lnb.com.br/ldb/tabela-de-jogos/' +
            '?season%5B%5D=' + season2 +
            '&phase' + fase_flag
        )
    else:
        url = 'https://lnb.com.br/ldb/tabela-de-jogos/?season%5B%5D=' + season2

    df = pd.read_html(url)[0]

    try:
        df = df.drop(columns=['#', 'CASA', 'Unnamed: 15', 'GINÁSIO', 'RODADA'])
    except KeyError:
        df = df.drop(columns=['#', 'CASA', 'Unnamed: 14', 'GINÁSIO', 'RODADA'])

    df = df.dropna(how='all', axis=1)
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y  %H:%M')

    df = df.rename(columns={
        'TRANSMISSÃO': 'GINASIO',
        'FASE': 'RODADA',
        'CAMPEONATO': 'FASE',
        'Unnamed: 3': 'EQUIPE CASA',
        'Unnamed: 7': COL_EQUIPE_VISITANTE
    })

    df[FIELD_UNNAMED] = df[FIELD_UNNAMED].str.replace('  VER RELATÓRIO','')
    df[COL_PLACAR_CASA] = df[FIELD_UNNAMED].str[:2]
    df[COL_PLACAR_VISITANTE] = df[FIELD_UNNAMED].str[-2:]

    df[COL_PLACAR_CASA] = df[COL_PLACAR_CASA].apply(lambda x: np.nan if 'X' in x else x)
    df[COL_PLACAR_VISITANTE] = df[COL_PLACAR_VISITANTE].apply(lambda x: np.nan if 'X' in x else x)

    df = df.drop(columns=[FIELD_UNNAMED])

    df['VENCEDOR'] = np.where(
        df[COL_PLACAR_CASA] > df[COL_PLACAR_VISITANTE],
        df['EQUIPE CASA'],
        df[COL_EQUIPE_VISITANTE]
    )
    df['VENCEDOR'] = np.where(
        df[COL_PLACAR_CASA].isna(),
        np.nan,
        df['VENCEDOR']
    )

    df['TEMPORADA'] = season

    try:
        df = df[
            ['DATA', 'EQUIPE CASA', COL_PLACAR_CASA, COL_PLACAR_VISITANTE,
             COL_EQUIPE_VISITANTE, 'VENCEDOR', 'RODADA', 'FASE', 'GINASIO', 'TEMPORADA']
        ]
    except KeyError:
        df = df[
            ['DATA', 'EQUIPE CASA', COL_PLACAR_CASA, COL_PLACAR_VISITANTE,
             COL_EQUIPE_VISITANTE, 'VENCEDOR', 'RODADA', 'FASE', 'TEMPORADA']
        ]

    return df
