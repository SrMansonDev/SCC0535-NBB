import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import importlib

# Força carregamento do parser html5lib se possível
try:
    importlib.import_module("html5lib")
except ImportError:
    messagebox.showerror("Erro", "Dependência 'html5lib' ausente. Instale com: pip install html5lib")
    exit(1)

from nbb_api import nbb, liga_ouro, ldb

def main():
    ligas = {
        'NBB': nbb,
        'Liga Ouro': liga_ouro,
        'LDB': ldb
    }

    nome_para_funcao = {
        'Classificação': 'get_classificacao',
        'Placar': 'get_placares',
        'Estatísticas': 'get_stats'
    }

    funcao_para_nome = {v: k for k, v in nome_para_funcao.items()}

    funcoes_parametros = {
        'get_classificacao': ['temporada'],
        'get_placares': ['temporada', 'fase'],
        'get_stats': {
            'NBB': ['temporada', 'fase', 'categoria', 'tipo', 'quem', 'mandante', 'sofrido'],
            'Liga Ouro': ['temporada', 'fase', 'categoria', 'tipo', 'quem', 'sofrido'],
            'LDB': ['temporada', 'fase', 'categoria', 'tipo', 'quem', 'sofrido']
        }
    }

    valores_parametros = {
        'fase': ["Regular", "Playoffs", "Total"],
        'categoria': {
            'NBB': ["Pontos", "Rebotes", "Assistências", "Arremessos", "Bolas-Recuperadas", "Tocos", "Erros", "Eficiência", "Duplos-Duplos", "Enterradas"],
            'Liga Ouro': ["Cestinhas", "Rebotes", "Assistências", "Arremessos", "Bolas-Recuperadas", "Tocos", "Erros", "Eficiência", "Duplos-Duplos", "Enterradas"],
            'LDB': ["Cestinhas", "Rebotes", "Assistências", "Arremessos", "Bolas-Recuperadas", "Tocos", "Erros", "Eficiência", "Duplos-Duplos", "Enterradas"]
        },
        'tipo': ["Média", "Soma"],
        'quem': ["Jogadores", "Equipes"],
        'sofrido': ["False", "True"],
        'mandante': ["Ambos", "Mandante", "Visitante"]
    }

    def obter_temporadas(liga_nome, funcao):
        try:
            if liga_nome == 'NBB':
                return ligas[liga_nome].seasons_classification if funcao == 'get_classificacao' else ligas[liga_nome].seasons
            else:
                return ligas[liga_nome].seasons
        except Exception:
            return []

    def atualizar_campos_parametros(*args):
        for widget in parametros_frame.winfo_children():
            widget.destroy()

        funcao_nome = funcao_cb.get()
        funcao = nome_para_funcao[funcao_nome]
        liga = liga_cb.get()
        parametros = funcoes_parametros[funcao] if funcao != 'get_stats' else funcoes_parametros[funcao][liga]

        for i, param in enumerate(parametros):
            label = ttk.Label(parametros_frame, text=param.capitalize() + ":")
            label.grid(row=i, column=0, sticky="w", pady=2)
            if param == "sofrido":
                var = tk.BooleanVar(value=False)
                chk = ttk.Checkbutton(parametros_frame, variable=var)
                chk.grid(row=i, column=1, sticky="w", pady=2)
                campos[param] = var
            else:
                cb = ttk.Combobox(parametros_frame, state="readonly", width=20)
                cb.grid(row=i, column=1, sticky="w", pady=2)
                campos[param] = cb

                if param == "temporada":
                    temporadas = obter_temporadas(liga, funcao)
                    cb['values'] = temporadas
                    if temporadas:
                        cb.set(temporadas[-1])
                elif param in valores_parametros:
                    if isinstance(valores_parametros[param], dict):
                        opcoes = valores_parametros[param][liga]
                        cb['values'] = opcoes
                        cb.set(opcoes[0])
                    else:
                        cb['values'] = valores_parametros[param]
                        cb.set(valores_parametros[param][0])

    tabela_janela = None

    def mostrar_resultado_em_tabela(df):
        nonlocal tabela_janela
        if tabela_janela and tabela_janela.winfo_exists():
            tabela_janela.destroy()

        tabela_janela = tk.Toplevel(janela)
        tabela_janela.title("Resultado")

        tree = ttk.Treeview(tabela_janela, columns=list(df.columns), show='headings')
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=max(80, min(150, len(col)*10)), anchor='center')

        for _, row in df.iterrows():
            tree.insert('', 'end', values=list(row))

        tree.pack(fill='both', expand=True)
        scrollbar = ttk.Scrollbar(tabela_janela, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def executar():
        try:
            liga_nome = liga_cb.get()
            liga = ligas[liga_nome]
            funcao_nome = funcao_cb.get()
            funcao = nome_para_funcao[funcao_nome]
            parametros = funcoes_parametros[funcao] if funcao != 'get_stats' else funcoes_parametros[funcao][liga_nome]
            args = []

            for param in parametros:
                if param == "sofrido":
                    val = campos[param].get()
                else:
                    val = campos[param].get()

                    if param == "tipo":
                        val = "avg" if val == "Média" else "sum"
                    elif param == "quem":
                        val = "athletes" if val == "Jogadores" else "teams"
                    elif param == "fase":
                        val = val.lower()
                    elif param == "categoria":
                        val = val.lower().replace("ç", "c").replace("á", "a").replace("é", "e").replace("ê", "e").replace("-", "-").replace(" ", "-")
                    elif param == "mandante":
                        val = val.lower()

                args.append(val)

            resultado = getattr(liga, funcao)(*args)
            mostrar_resultado_em_tabela(resultado)

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    janela = tk.Tk()
    janela.title("NBB - Analisador de Estatísticas (Simplificado)")
    janela.geometry("420x500")
    janela.resizable(False, False)

    style = ttk.Style()
    style.theme_use('clam')

    ttk.Label(janela, text="Liga:").pack(pady=4)
    liga_cb = ttk.Combobox(janela, values=list(ligas.keys()), state="readonly")
    liga_cb.set("NBB")
    liga_cb.pack()

    ttk.Label(janela, text="Função:").pack(pady=4)
    funcao_cb = ttk.Combobox(janela, values=list(nome_para_funcao.keys()), state="readonly")
    funcao_cb.set("Classificação")
    funcao_cb.pack()

    parametros_frame = tk.Frame(janela)
    parametros_frame.pack(pady=10)

    campos = {}
    funcao_cb.bind("<<ComboboxSelected>>", atualizar_campos_parametros)
    liga_cb.bind("<<ComboboxSelected>>", atualizar_campos_parametros)

    ttk.Button(janela, text="Executar", command=executar).pack(pady=10)

    atualizar_campos_parametros()
    janela.mainloop()

if __name__ == "__main__":
    main()
