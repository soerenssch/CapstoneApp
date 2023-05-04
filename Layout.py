import streamlit as st
from streamlit_option_menu import option_menu
from outscraper import ApiClient
import pandas as pd
import os
import openai
import requests
from tqdm import tqdm
import time
import docx
import datetime
import base64



st.write("Lade hier die CSV Datei hoch, die du auswerten willst.")
try:
    file = st.file_uploader("Upload file", type=["csv"])
    if file is not None:
        df = pd.read_csv(file)
        df = df.dropna()
        st.dataframe(df)


        OpenAI_API = st.text_input("Gib hier deinen OpenAI API Key an")
        openai.api_key = OpenAI_API
        GPT_API_URL = "https://api.openai.com/v1/chat/completions"
        Spalte = st.text_input("Wie heisst die Spalte, die du auswerten möchtest?")
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

            output_file_proscons = "reviews_analyzed_negative_proscons.xlsx"
            df_proscons.to_excel(output_file_proscons, index=False)

            def generate_csv(df):
                return df.to_csv(index=False)
            if st.download_button(label='Download Ergebnisse', data=generate_csv(df_proscons), file_name='Ergebnisse.csv', mime='text/csv'):
                pass

    else:
        st.write("Lade deine CSV hier hoch!")
except Exception as e:
    st.write("Error:", e)



        

