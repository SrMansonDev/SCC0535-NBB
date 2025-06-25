import unittest
from unittest.mock import patch
import pandas as pd
from nbb_api.liga_ouro import get_placares, get_classificacao

# DataFrame fictício simulando retorno de placares
dummy_placar_df = pd.DataFrame({
    '#': [1],
    'CASA': ['Time A'],
    'Unnamed: 3': ['Time A'],
    'Unnamed: 5': ['80 X 75  VER RELATÓRIO'],
    'Unnamed: 7': ['Time B'],
    'Unnamed: 15': ['algum valor'],
    'GINÁSIO': ['Ginásio Z'],
    'RODADA': ['1ª'],
    'DATA': ['01/03/2019  20:00'],
    'TRANSMISSÃO': ['Ginásio Y'],
    'FASE': ['1ª Fase'],
    'CAMPEONATO': ['Liga Ouro']
})

# DataFrame fictício simulando retorno da classificação
dummy_class_df = pd.DataFrame({
    'EQUIPES': ['01 Botafogo'],
    'P': [60]
})


class TestLigaOuro(unittest.TestCase):

    @patch('pandas.read_html')
    def test_get_placares_valido(self, mock_read_html):
        # Testa se get_placares para 2019 retorna colunas esperadas e inclui temporada
        mock_read_html.return_value = [dummy_placar_df.copy()]
        df = get_placares('2019', 'regular')
        self.assertIn('EQUIPE CASA', df.columns)
        self.assertIn('PLACAR CASA', df.columns)
        self.assertIn('VENCEDOR', df.columns)
        self.assertEqual(df['TEMPORADA'].iloc[0], '2019')

    @patch('pandas.read_html')
    def test_get_classificacao_valido(self, mock_read_html):
        # Testa se get_classificacao retorna colunas esperadas e inclui temporada
        mock_read_html.return_value = [dummy_class_df.copy()]
        df = get_classificacao('2019')
        self.assertIn('EQUIPES', df.columns)
        self.assertIn('TEMPORADA', df.columns)
        self.assertEqual(df['TEMPORADA'].iloc[0], '2019')

    def test_get_placares_season_invalida(self):
        # Testa se get_placares levanta erro para temporada inválida
        with self.assertRaises(ValueError):
            get_placares('2022', 'regular')

    def test_get_placares_fase_invalida(self):
        # Testa se get_placares levanta erro para fase inválida
        with self.assertRaises(ValueError):
            get_placares('2019', 'fase_extra')

    def test_get_classificacao_season_invalida(self):
        # Testa se get_classificacao levanta erro para temporada inválida
        with self.assertRaises(ValueError):
            get_classificacao('2022')


if __name__ == '__main__':
    unittest.main()
