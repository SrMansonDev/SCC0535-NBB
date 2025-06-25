import unittest
from unittest.mock import patch
import pandas as pd
from nbb_api import nbb

class TestNBBFuncoes(unittest.TestCase):

    @patch('nbb_api.nbb.pd.read_html')
    def test_get_stats_valido(self, mock_read_html):
        dummy_df = pd.DataFrame({
            'Jogador': ['Jogador X #12'],
            'Pontos': [18],
            'Pos.': [1]
        })
        mock_read_html.return_value = [dummy_df]

        df = nbb.get_stats("2022-23", "regular", "cestinhas")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('Jogador', df.columns)
        self.assertGreater(len(df), 0)

    @patch('nbb_api.nbb.pd.read_html')
    def test_get_classificacao_valido(self, mock_read_html):
        dummy_df = pd.DataFrame({'EQUIPES': ['01 Flamengo'], 'P': [32]})
        mock_read_html.return_value = [dummy_df]

        df = nbb.get_classificacao("2022-23")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('EQUIPES', df.columns)
        self.assertGreater(len(df), 0)

    @patch('nbb_api.nbb.pd.read_html')
    def test_get_placares_valido(self, mock_read_html):
        dummy_df = pd.DataFrame({
            'DATA': ['01/03/2023  19:30'],
            'Unnamed: 3': ['Time A'],
            'Unnamed: 5': ['88 X 79  VER RELATÓRIO'],
            'Unnamed: 7': ['Time B'],
            'FASE': ['Regular'],
            'CAMPEONATO': ['NBB'],
            '#': [1],
            'CASA': ['x'],
            'GINASIO': ['Ginásio XPTO'],  # Corrigido: sem acento
            'RODADA': [1],
            'Unnamed: 15': ['x']
        })
        mock_read_html.return_value = [dummy_df]

        df = nbb.get_placares("2022-23", "regular")
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('EQUIPE CASA', df.columns)
        self.assertIn('VENCEDOR', df.columns)
        self.assertGreater(len(df), 0)

if __name__ == '__main__':
    unittest.main()
