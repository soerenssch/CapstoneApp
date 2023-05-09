import pickle
from pathlib import Path
from turtle import shapesize
import streamlit as st
from streamlit_option_menu import option_menu
from outscraper import ApiClient
import pandas as pd
import os
import openai
import requests
from tqdm import tqdm
import time
import datetime
import base64
import subprocess
subprocess.run(['pip', 'install', 'openpyxl'])
from docx import Document
from docx.shared import Inches
import io
from io import BytesIO
import matplotlib.pyplot as plt



# Define the file download function
def download_file(file):
    b = BytesIO()
    file.savefig(b, format='png')
    b.seek(0)
    return b

# Main code
file = st.file_uploader("Lade deine Datei hier hoch:", type=["csv"])
if file is not None:
    df = pd.read_csv(file)
    df = df.dropna()

    if "Datum" in df.columns:

        # add checkbox to allow manual date selection
        manual_date_selection = st.checkbox("Den Analysezeitraum manuell festlegen")
        df["Datum"] = pd.to_datetime(df["Datum"])
        if manual_date_selection:

            
            # start_date = st.date_input("Start date")
            # end_date = st.date_input("End date")
            start_date = st.date_input("Start der Auswertung:", value=pd.to_datetime(df['Datum']).min().date())
            end_date = st.date_input("Ende der Auswertung:", value=pd.to_datetime(df['Datum']).max().date())

            # mask = (df["date"] >= start_date) & (df["date"] <= end_date)
            mask = (pd.to_datetime(df['Datum']).dt.date >= start_date) & (pd.to_datetime(df['Datum']).dt.date <= end_date)
            df = df.loc[mask]

    st.dataframe(df)

    if "Rating" in df.columns:
            
        
        def generate_plot(df):
            fig, ax = plt.subplots(figsize=(12, 8))
            counts, bins, patches = ax.hist(df['Rating'], bins=5, color='#132f55', edgecolor='white')
            ax.set_xlabel('Bewertung')
            ax.set_ylabel('Anzahl')
            ax.set_title('Verteilung der Bewertungen')
            tick_labels = ['1 Stern', '2 Sterne', '3 Sterne', '4 Sterne', '5 Sterne']
            tick_positions = [1.415, 2.25, 3, 3.85, 4.63]
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, ha='center') # Set horizontal alignment to center
            return fig
    
        fig = generate_plot(df)
        st.pyplot(fig)
        st.write(f"Die durchschnittliche Bewertung beträgt {round(df['Rating'].mean(), 2)} bei {round(df['Rating'].count(), 2)} Bewertungen")
        

        download = download_file(fig)
        st.download_button(
            label='Download plot',
            data=download,
            file_name='plot.png',
            mime='image/png'
        )
        




    
    Spalte = st.text_input("Wie heisst die Spalte, die du auswerten möchtest?")
    if not Spalte:
        Spalte = "Review"

    st.write("Melde dich mit dem nachfolgenden Link bei OpenAI an, um deinen API-Key zu erstellen: https://chat.openai.com/auth/login")
    OpenAI_API = st.text_input("Gib hier deinen OpenAI API-Key an:")
    
    openai.api_key = OpenAI_API
    GPT_API_URL = "https://api.openai.com/v1/chat/completions"
    all_reviews = "\n".join(df[Spalte].tolist())
    if st.button("Sentiment-Analyse starten"):

        @st.cache_data(ttl=600)
        def generate_proscons_list(text):
            word_blocks = text.split(' ')
            block_size = 1750
            blocks = [' '.join(word_blocks[i:i + block_size]) for i in range(0, len(word_blocks), block_size)]

            proscons = []

            for block in tqdm(blocks, desc="Processing blocks", unit="block"):
                messages = [
                    {"role": "system", "content": "Du bist ein KI-Sprachmodell, das darauf trainiert ist, eine Liste der häufigsten Stärken und Schwächen einer Tierarztpraxis auf der Grundlage von Google Bewertungen zu erstellen."},
                    {"role": "user", "content": f"Erstelle auf der Grundlage der folgenden Google-Bewertungen eine Liste mit den häufigsten Stärken und Schwächen der Tierarztpraxis: {block}"}
                ]

                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    # You can change the max_tokens amount to increase or decrease the length of the results pros and cons list. If you increase it too much, you will exceed chatGPT's limits though.
                    max_tokens=250,
                    n=1,
                    stop=None,
                        # You can adjust how "creative" (i.e. true to the original reviewer's intent) chatGPT will be with it's summary be adjusting this temperature value. 0.7 is usually a safe amount
                    temperature=0.7
                )

                procon = completion.choices[0].message.content
                proscons.append(procon)

                # Gefundene Stärken und Schwächen in einer Liste zusammenfassen 
            combined_proscons = "\n\n".join(proscons)
            return combined_proscons
        summary_proscons = generate_proscons_list(all_reviews)

        df_proscons = pd.DataFrame()
        list_proscons = []
        list_proscons.append(summary_proscons)
        df_proscons["pros_cons"] = list_proscons

        # Create Word document
        document = Document()
        document.add_heading("Stärken und Schwächen Zusammenfassung", level=0)
        table = document.add_table(rows=len(df_proscons.index), cols=1)
        for i, row in df_proscons.iterrows():
            table.cell(i, 0).text = row["pros_cons"]
        document.add_page_break()

        # Download Word document
        with io.BytesIO() as output:
            document.save(output)
            if st.download_button(label='Download', data=output.getvalue(), file_name='Ergebnisse.docx', mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'):
                pass






