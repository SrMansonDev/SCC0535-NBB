from nbb_api import nbb

def tests_get_stats():
    stats = nbb.get_stats(season="2022-23", fase="regular", categ="cestinhas")
    assert isinstance(stats, list) or isinstance(stats, dict)
    assert len(stats) > 0

def tests_get_classificacao():
    classificacao = nbb.get_classificacao(season="2022-23")
    assert isinstance(classificacao, list) or isinstance(classificacao, dict)
    assert len(classificacao) > 0

def tests_get_placares():
    placares = nbb.get_placares(season="2022-23", fase="regular")
    assert isinstance(placares, list) or isinstance(placares, dict)
    assert len(placares) > 0
