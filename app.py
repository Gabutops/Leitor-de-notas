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

def open_pdf(files):
    BUGS = []
    # Verifica se a pasta Resultados existe
    if not os.path.exists("Resultados"):
        os.makedirs("Resultados")
    # Cria o DataFrame para receber os dados
    df = pd.DataFrame(columns=["Numero_Nota", "Valor_Total"])
    # Para cada arquivo, extrai o .pdf e faz o processo de leitura
    for file in files:
        leitor = PyPDF2.PdfReader(f"Pasta de pesquisa/{file}")
        total_paginas = len(leitor.pages)

        # Para cada página, extrai o texto e encontra o valor total
        for num_pagina in range(total_paginas):
            pagina = leitor.pages[num_pagina]
            texto_pagina = extrair_texto_pagina(pagina)

            # Regex do numero da nota
            regex_numero = r"\d{3}\.\d{3}\.\d{3}"
            resultado_nota = re.search(regex_numero, texto_pagina)
            numero_nota =resultado_nota.group(0)

            # Extrai a parte desejada do texto
            parte_desejada = re.search(r"VALOR DO FRETE.*VALOR TOTAL DA NOTA.*\n([\d, ]+)", texto_pagina).group(1)
            if parte_desejada:

                # Cria o regex para retornar os valores
                valores_regex = re.findall(r"[\d,]+", parte_desejada)
                if valores_regex:
                    valores = [float(valor.replace(',', '.')) for valor in valores_regex]
                    if valores[-1] == 0:
                        valores.pop(-1)
                    valor_monetario = valores[-1]

                    # Adiciona os dados ao DataFrame
                    dados = {"Numero_Nota": [numero_nota], "Valor_Total": [valor_monetario]}
                    new_df = pd.DataFrame(dados)
                    df = pd.concat([df, new_df])
                    print(f"File:{file} | Nr. Nota: {numero_nota} | Vlr. Nota: {valor_monetario}")
                
            else:
                parte_valores = re.search(r'VALOR DO FRETE.*?CÁLCULO DO IMPOSTO', texto_pagina, re.DOTALL).group(0)

                # Extrair os valores em uma lista
                valores = re.findall(r'\d+,\d+', parte_valores)
                
                # Converter os valores para float
                valores = [float(valor.replace(',', '.')) for valor in valores]
                valores.pop(-1)
                valor_monetario = valores[-1]
                
                # Adiciona os dados ao DataFrame
                dados = {"Numero_Nota": [numero_nota], "Valor_Total": [valor_monetario]}
                new_df = pd.DataFrame(dados)
                df = pd.concat([df, new_df])
                print(f"File:{file} | Nr. Nota: {numero_nota} | Vlr. Nota: {valor_monetario}")
            
            with open("log.txt",mode="w") as l:
                l.write(f"{date_str} -> {BUGS}")
    df.to_csv(f'Resultados/{date_str}.csv',sep=";", index=False)
    
def processar_dados():

    # Cria um input para receber os .pdf's
    files = file_upload("Selecione as notas:", accept="application/pdf", multiple=True)
    
    # Lista de pdf's
    pdfs = []
    
    #para cada arquivo recebido, armazena o arquivo na lista pdfs
    for pdf in files:
        pdfs.append(pdf['filename'])
    open_pdf(pdfs)
    toast(f'Arquivo CSV salvo com sucesso em Resultados/{date_str}.csv!',duration= 25)
    
if __name__ == "__main__":
    from datetime import date
    global date_str,df
    today = date.today()
    date_str = today.strftime("%d-%m-%Y")
    start_server(applications=processar_dados,host="0.0.0.0",port=7000)
