from pywebio.input import input,file_upload, actions, NUMBER, FLOAT
from pywebio.output import put_file, toast, put_markdown,put_text
from pywebio import start_server
import re
import PyPDF2
import pandas as pd
import os
import webbrowser



def extrair_texto_pagina(pagina):
    texto = pagina.extract_text()
    return texto
def open_pdf(file):
    global df
    BUGS = []
    df = pd.DataFrame(columns=["Numero_Nota", "Valor_Total"])
    leitor = PyPDF2.PdfReader(f"Pasta de pesquisa/{file}")
    total_paginas = len(leitor.pages)
    # para cada página, extrair o texto e encontrar o valor total
    for num_pagina in range(total_paginas):
        pagina = leitor.pages[num_pagina]
        texto_pagina = extrair_texto_pagina(pagina)
        regex_numero = r"\d{3}\.\d{3}\.\d{3}"
        resultado_nota = re.search(regex_numero, texto_pagina)
        numero_nota =resultado_nota.group(0)
        regex_valor = r'Total: R\$\d+,\d{2}'
        resultado = re.search(regex_valor, texto_pagina)
        if resultado:
            valor_total = resultado.group(0)
            regex_valor_monetario = r"\d+,\d{2}"
            resultado_valor_monetario = re.search(regex_valor_monetario, valor_total)
            if resultado_valor_monetario:
                valor_monetario = resultado_valor_monetario.group(0)
                # adicionar os dados ao DataFrame
                dados = {"Numero_Nota": [numero_nota], "Valor_Total": [valor_monetario]}
                new_df = pd.DataFrame(dados)
                df = pd.concat([df, new_df])
                print(f"Nr. Nota: {numero_nota} | Vlr. Nota: {valor_monetario}")
            else:
                BUGS.append("Não foi possível encontrar o valor monetário.")
        else:
            texto = "VALOR DO FRETE VALOR DO SEGURO DESCONTO OUTRAS DESPESAS ACESSÓRIAS VALOR DO IPI VALOR TOTAL DA NOTA0,00 0,00 0,00 0,00 89,90 0,00"
            padrao = r'(\d+,\d{2})'
            resultado = re.findall(padrao, texto)
            valor_total = resultado[-1]  # obter o último valor encontrado
            regex_valor_monetario = r"\d+,\d{2}"
            resultado_valor_monetario = re.search(regex_valor_monetario, valor_total)
            if resultado_valor_monetario:
                valor_monetario = resultado_valor_monetario.group(0)
                # adicionar os dados ao DataFrame
                dados = {"Numero_Nota": [numero_nota], "Valor_Total": [valor_monetario]}
                new_df = pd.DataFrame(dados)
                df = pd.concat([df, new_df])
            else:
                BUGS.append("Não foi possível encontrar o valor monetário.")
        with open("log.txt",mode="w") as l:
            l.write(f"{date_str} -> {BUGS}")
def processar_dados():
    files = file_upload("Selecione as notas:", accept="application/pdf", multiple=True)
    for pdf in files:
        open_pdf(pdf['filename'])
    df.to_csv(f'Resultados/{date_str}.csv',sep=";", index=False)
    
    def open_file(path):
        webbrowser.open(path)
    toast(f'Arquivo CSV salvo cocm sucesso em Resultados/{date_str}.csv!\nClique aqui para conferir o arquivo',duration= 25,onclick=lambda: open_file(f'Resultados/{date_str}.csv'))

if __name__ == "__main__":
    from datetime import date
    global date_str,df
    today = date.today()
    date_str = today.strftime("%d-%m-%Y")
    start_server(applications=processar_dados,host="0.0.0.0")