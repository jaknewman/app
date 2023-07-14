# -*- coding: utf-8 -*-
"""RMJA_propluvia.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SEryK1P4VlVjG7s2HL5jSobVNYy-fUlp
"""

import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import requests
from bs4 import BeautifulSoup

def read_excel_file(file):
  df = pd.read_excel(file)
  return df

def to_excel(df):
  output = BytesIO()
  writer = pd.ExcelWriter(output, engine='xlsxwriter')
  df.to_excel(writer, index=False, sheet_name='Feuille1')
  workbook = writer.book
  worksheet = writer.sheets['Feuille1']
  writer.save()
  processed_data = output.getvalue()
  return processed_data

uploaded_file = st.file_uploader("Glissez et déposez un fichier XLSX ici", type="xlsx")

if uploaded_file is not None:
    df_uploaded = read_excel_file(uploaded_file)
    st.write(df_uploaded.head())  # Afficher les premières lignes du DataFrame

if st.button("Rechercher mise à jour"):
    restrictMaxDep = []
    Dep = []
    Zones = []
    dateDebut = []
    dateFin= []

    indices = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    k = 1

    while True:
        index_dep = str(k).rjust(2, '0')
        url = f"http://propluvia.developpement-durable.gouv.fr/?idDep={index_dep}"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        tableau = soup.find_all("table", {"class":"table"})

        if k > 95:
            break

        for element in tableau:
            for i in indices:
                col1 = element.find('span', {'id': f"_id0:_id36:_id172:_id173:_id175:{i}:_id182:oid182Value"})
                num = col1.text.strip() if col1 is not None else np.nan

                col2 = element.find('span', {'id': f"_id0:_id36:_id172:_id173:_id175:{i}:_id184:oid184Value"})
                dep = col2.text.strip() if col2 is not None else np.nan

                col3 = element.find('span', {'id': f"_id0:_id36:_id172:_id173:_id175:{i}:_id186:oid186Value"})
                zone = col3.text.strip() if col3 is not None else np.nan

                col4 = element.find('span', {'id': f"_id0:_id36:_id172:_id173:_id175:{i}:_id188:oid188Value"})
                datedebut = col4.text.strip() if col4 is not None else np.nan

                col5 = element.find('span', {'id': f"_id0:_id36:_id172:_id173:_id175:{i}:_id190:oid190Value"})
                datefin = col5.text.strip() if col5 is not None else np.nan

                restrictMaxDep.append(num)
                Dep.append(dep)
                Zones.append(zone)
                dateDebut.append(datedebut)
                dateFin.append(datefin)

        k +=1

    df_scraped = pd.DataFrame({'Niveau Max': restrictMaxDep,
                                'Departement': Dep,
                                'Zones': Zones,
                                'Debut': dateDebut,
                                'Fin': dateFin})
    df_scraped.dropna(inplace=True)

    if len(df_scraped) == len(df_uploaded):
        st.write("Il n'y a pas de nouveaux éléments pour l'instant. Votre dernier fichier est à jour.")
    elif len(df_scraped) > len(df_uploaded):
      st.write("J'ai trouvé des nouvelles informations.")
      st.write(df_scraped.head())
      df_xlsx = to_excel(df_scraped)
      st.download_button(label="Télécharger", data = df_xlsx, file_name="fichier_propluvia_MAJ.xlsx")
      st.success("Téléchargement terminé !")

if __name__ == "__main__":
    st.title("Application de mise à jour")
    st.sidebar.title("Paramètres")
    st.set_option("deprecation.showfileUploaderEncoding", False)
    st.sidebar.info("Glissez et déposez un fichier XLSX pour commencer.")
