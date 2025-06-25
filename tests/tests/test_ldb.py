import unittest
from unittest.mock import patch
import pandas as pd
from nbb_api.ldb import get_classificacao, get_stats, get_placares

class TestLDBFuncoes(unittest.TestCase):

    @patch('pandas.read_html')
    def test_get_classificacao_valido(self, mock_read_html):
        # Testa se get_classificacao retorna colunas esperadas e remove prefixos de equipe corretamente
        dummy_df = pd.DataFrame({'EQUIPES': ['01 Flamengo', '02 Paulistano']})
        mock_read_html.return_value = [dummy_df]

        df = get_classificacao('2023')
        self.assertIn('EQUIPES', df.columns)
        self.assertIn('TEMPORADA', df.columns)
        self.assertEqual(df['TEMPORADA'].iloc[0], '2023')
        self.assertEqual(df['EQUIPES'].iloc[0], 'Flamengo')

    def test_get_classificacao_invalido(self):
        # Testa se get_classificacao levanta erro para temporada inválida
        with self.assertRaises(ValueError):
            get_classificacao('2020')

    @patch('pandas.read_html')
    def test_get_stats_athletes_avg(self, mock_read_html):
        # Testa se get_stats para atletas (avg) retorna colunas esperadas e extrai "Camisa" corretamente
        dummy_df = pd.DataFrame({
            'Jogador': ['Fulano #10', 'Beltrano #5'],
            'Pontos': [20, 15],
            'Pos.': [1, 2]
        })
        mock_read_html.return_value = [dummy_df]

        df = get_stats('2023', 'regular', 'cestinhas', tipo='avg', quem='athletes')
        self.assertIn('Jogador', df.columns)
        self.assertIn('Camisa', df.columns)
        self.assertEqual(df['Jogador'].iloc[0], 'Fulano')
        self.assertEqual(df['Camisa'].iloc[0], '10')

    def test_get_stats_erro_temporada_invalida(self):
        # Testa se get_stats levanta erro para temporada inválida
        with self.assertRaises(ValueError):
            get_stats('2020', 'regular', 'cestinhas')

    def test_get_stats_erro_fase_invalida(self):
        # Testa se get_stats levanta erro para fase inválida
        with self.assertRaises(ValueError):
            get_stats('2023', 'fase_errada', 'cestinhas')

    def test_get_stats_erro_categoria_invalida(self):
        # Testa se get_stats levanta erro para categoria inválida
        with self.assertRaises(ValueError):
            get_stats('2023', 'regular', 'xuxu')

    def test_get_stats_erro_tipo_invalido(self):
        # Testa se get_stats levanta erro para tipo inválido
        with self.assertRaises(ValueError):
            get_stats('2023', 'regular', 'cestinhas', tipo='media')

    def test_get_stats_erro_quem_invalido(self):
        # Testa se get_stats levanta erro para tipo de entidade inválido (quem)
        with self.assertRaises(ValueError):
            get_stats('2023', 'regular', 'cestinhas', quem='jogadores')

    def test_get_stats_erro_sofrido_invalido(self):
        # Testa se get_stats levanta erro para valor inválido no parâmetro sofrido
        with self.assertRaises(ValueError):
            get_stats('2023', 'regular', 'cestinhas', sofrido='talvez')

    @patch('pandas.read_html')
    def test_get_placares_valido(self, mock_read_html):
        # Testa se get_placares retorna as colunas esperadas e extrai corretamente o placar e vencedor
        dummy_df = pd.DataFrame({
            'DATA': ['01/03/2023  19:30'],
            'Unnamed: 3': ['Time A'],
            'Unnamed: 5': ['75 X 70  VER RELATÓRIO'],
            'Unnamed: 7': ['Time B'],
            'FASE': ['Regular'],
            'CAMPEONATO': ['LDB'],
            'TRANSMISSÃO': ['Ginásio ABC'],
            '#': [1],
            'CASA': ['x'],
            'GINÁSIO': ['x'],
            'RODADA': [1],
            'Unnamed: 15': ['x']
        })
        mock_read_html.return_value = [dummy_df]

        df = get_placares('2023', 'regular')
        self.assertIn('EQUIPE CASA', df.columns)
        self.assertIn('PLACAR CASA', df.columns)
        self.assertIn('VENCEDOR', df.columns)
        self.assertEqual(df['TEMPORADA'].iloc[0], '2023')
        self.assertEqual(df['EQUIPE CASA'].iloc[0], 'Time A')

    def test_get_placares_invalido(self):
        # Testa se get_placares levanta erro para temporada e fase inválidas
        with self.assertRaises(ValueError):
            get_placares('2020', 'regular')
        with self.assertRaises(ValueError):
            get_placares('2023', 'fase_errada')

if __name__ == '__main__':
    unittest.main()
