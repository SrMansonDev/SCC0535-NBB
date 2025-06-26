import unittest
from unittest.mock import patch
import pandas as pd
from nbb_api import nbb

class TestNBBFuncoes(unittest.TestCase):

    @patch('nbb_api.nbb.pd.read_html')
    def test_get_stats_outros_argumentos(self, mock_read_html):
        dummy_df = pd.DataFrame({
            'Jogador': ['Atleta Y #7'],
            'Cestinhas': [24],
            'Pos.': [2]
        })
        mock_read_html.return_value = [dummy_df]

        df = nbb.get_stats("2021-22", "playoffs", "cestinhas", tipo='sum', quem='teams', sofrido=True)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('Temporada', df.columns)
        self.assertEqual(df['Temporada'][0], "2021-22")

    @patch('nbb_api.nbb.pd.read_html')
    def test_get_stats_valido(self, mock_read_html):
        dummy_df = pd.DataFrame({
            'Jogador': ['Jogador X #12'],
            'Pontos': [18],
            'Pos.': [1]
        })
        mock_read_html.return_value = [dummy_df]

        df = nbb.get_stats("2022-23", "regular", "tocos")
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

if __name__ == '__main__':
    unittest.main()
