import pickle
from pathlib import Path
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


st.set_page_config(
    page_title="Sentiment Analyse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",    
)

logo_left_container = st.container()
with logo_left_container:
    st.image("VT_logo.png", use_column_width=False, width=150)

st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        right: 0;
        font-size: 12px;
        padding: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="footer">© 2023 Capstone Gruppe Research. All rights reserved.</div>',
    unsafe_allow_html=True,
)


WebScraping = "Schritt 1: Web Scraping"
SentimentAnalyse = "Schritt 2: Sentiment-Analyse"
Anleitung = "Beschreibung & Kontakt"

st.sidebar.title("Wähle die Inputmethode")
input_method = st.sidebar.radio("Wähle eine Option:", (WebScraping, SentimentAnalyse, Anleitung))


# Depending on which option is selected, display the appropriate information
if input_method == WebScraping:
    with st.sidebar:
        st.header("Beschreibung: Web Scraping")
        st.write("Im ersten Schritt werden die Reviews der verschiedenen Standorte dir per Web Scraping zum Download zur Verfügung gestellt.")
        # Add any additional information or instructions for this option

elif input_method == SentimentAnalyse:
    with st.sidebar:
        st.header("Beschreibung: Sentiment-Analyse")
        st.write("In diesem Schritt werden die Daten hochgeladen und ausgewertet.")

elif input_method == Anleitung:
    with st.sidebar:
        st.write("Hier findest du einen Überblick über die Funktionsweise und die einzelnen Schritte der Sentiment-Analyse. Ausserdem ein Kontaktformular, solltest du Fragen haben.")


### WebScraping
ID_MAP = {
    "Flint's Praxis für Kleintiere": "ChIJg9LTCjq2kUcRlNmsxEGdNoc",
    'Tierhotel Clinica Alpina Ramosch': "ChIJn9GuzVU3g0cRZAPoW82_WZ0",
    'Tierklinik Clinica Alpina Celerina': "ChIJi2rFwxh9g0cRKh_m8hTN8SA",
    'Tierklinik Clinica Alpina Scuol': "ChIJhf6QYJBHg0cRIe8DYQz8JV8",
    'Kleintierklinik am Damm, Gossau': "ChIJsXk3JcvgmkcRmMwJslg2xcU",
    'Kleintierpraxis Aabach Uster': "ChIJE9cxb6CkmkcRH3ybj-adIbE",
    'Kleintierpraxis Au': "ChIJm8-ANlQRm0cRnd3hTS279ag",
    'Kleintierpraxis Bachmatt Eschenbach': "ChIJnU4TOnT9j0cR6HQvLSgsS5Q",
    'Kleintierpraxis Basel Central': "ChIJAR4_G0-4kUcRQAgkjVkUSek",
    'Kleintierpraxis Basel Spalen': "ChIJqRyBUAG5kUcRVcVH76IXaFE",
    'Kleintierpraxis Bülach': "ChIJS9aRbdJ1kEcRhKrcNtRWsuA",
    'Kleintierpraxis Fällanden': "ChIJzZH-veOjmkcR7GUzmVWaezY",
    'Kleintierpraxis Glattbrugg': "ChIJ9UNysAigmkcR5QgQSw4lpiY",
    'Kleintierpraxis Gümligen': "ChIJv5D40wE3jkcRFKWuw1rHTtE",
    'Kleintierpraxis im Bahnhof, Aathal': "ChIJ6Z-zRnG7mkcRPBbZp4n8iww",
    'Kleintierpraxis Küssnacht am Rigi': "ChIJHY_A-m7_j0cRHUpOOIwa8Yo",
    'Kleintierpraxis Mühlebach Oftringen': "ChIJf_mbzJQvkEcRicJ5NcgPDuE",
    'Kleintierpraxis Münchenstein': "ChIJvwTRBxe4kUcRfEUl0F_UF4Y",
    'Kleintierpraxis Muri': "ChIJ5-00QTwFkEcRG9Hk9XEzIM8",
    'Kleintierpraxis Oensingen': "ChIJg3c2oE7SkUcRy_Yz-zeQUww",
    'Kleintierpraxis Regensdorf': "ChIJF5STJ2cLkEcRDRye_BfHcDc",
    'Kleintierpraxis Schlieren': "ChIJERk9VbMNkEcRPy81sQi1wic",
    'Kleintierpraxis St. Gallen Ost': "ChIJTeRhD_Qem0cRdZHi-gV_KQc",
    'Kleintierpraxis Stansstad': "ChIJO7t-Rkb3j0cRhQ4zkf4JuBs",
    'Kleintierpraxis Telli Aarau': "ChIJaZqDHPw7kEcR-Fp5zfYNNdI",
    'Kleintierpraxis Therwil': "ChIJdUCYp3bHkUcRnqgwh2XgkjI",
    'Kleintierpraxis Trimbach': "ChIJlxwBXNMxkEcRVFq9hfD4rYc",
    'Kleintierpraxis Turbenthal': "ChIJGyWX2Q2WmkcRx1gLsoFhMz8",
    'Kleintierpraxis Wettingen': "ChIJGY-uTiltkEcR5qPVT9EHlVU",
    'Kleintierpraxis Winterthur im Zentrum': "ChIJK9ieJXmZmkcRHtJtVS47ZwE",
    'Kleintierpraxis Zug': "ChIJtSFUYUWqmkcRnQZS-2NJx-w",
    'Kleintierpraxis Zuzwil': "ChIJPWi96nfpmkcRMxRLWqMgC5s",
    'Tierklinik Basel': "ChIJpSNsIru5kUcRx-XRYVJBeU4",
    'Tierklinik Nesslau': "ChIJb_dA_kPXmkcRAGqsVT1wLFE",
    'Tierklinik Oberland Pfäffikon': "ChIJkTyE5WG8mkcR9FjBoEAKIEE",
    'Tierklinik Oberland Saland': "ChIJ2RDiJW6-mkcRRKSDQ0onkc4",
    'Tierklinik Zürich': "ChIJNXoM5QOhmkcRBNaok_HRShE",
    'Zentrum für Tiermedizin Klettgau': "ChIJH2Ls-3Z8kEcRvq0oZ5ctkrk",
}

input_Outscraper = []
checkbox_states = {label: False for label in ID_MAP.keys()}
checkbox_states["Select all"] = False

def update_selection(ID_MAP, checkbox_states, key):
    checkbox_states[key] = not checkbox_states[key]  # toggle the state of the clicked checkbox
    if key == "Select all":
        for label in ID_MAP.keys():
            checkbox_states[label] = checkbox_states[key]
    else:
        if not checkbox_states[key]:
            checkbox_states["Select all"] = False  # if any checkbox is unchecked, uncheck "Select all"
        else:
            checkbox_states["Select all"] = all(checkbox_states.values())  # if all checkboxes are checked, check "Select all"
    return checkbox_states

if input_method == WebScraping:
    st.write("Mithilfe von Webscraping werden ab einem ausgewählten Zeitpunkt alle Google Reviews der gewählten Standorte zum Download bereitgestellt.")


    select_all = st.checkbox("Alle Standorte auswählen")

    place_checkboxes = {}
    for place in ID_MAP:
        if select_all:
            place_checkboxes[place] = st.checkbox(place, value=True)
            input_Outscraper.append(ID_MAP[place])
        else:
            place_checkboxes[place] = st.checkbox(place)
        
        if place_checkboxes[place]:
            place_id = ID_MAP[place]
            if place_id not in input_Outscraper:
                input_Outscraper.append(place_id)
        else:
            place_id = ID_MAP[place]
            if place_id in input_Outscraper:
                input_Outscraper.remove(place_id)

    
    date_input = st.date_input('Gib das Datum an, ab dem du die Reviews exportieren willst')
    if date_input > datetime.datetime.today().date():
        st.error('Fehler: Datum darf nicht in der Zukunft liegen!')
    else:
        year = date_input.year
        month = date_input.month
        day = date_input.day

    my_date = datetime.datetime(year, month, day)
    timestamp = my_date.timestamp()
    timestamp = int(timestamp)
    st.session_state.timestamp = timestamp

    st.write("Melde dich mit dem nachfolgenden Link bei Outscraper an, um deinen eigenen API-Key zu erstellen: https://outscraper.com/refer?referrer=YXV0aDB8NjQwMWIzZGNiZmMzM2FhMmM5ODA4ZWFm")
    
    Outscraper_APIKey = st.text_input("Gib hier deinen Outscraper API Key an")
    client = ApiClient(api_key=Outscraper_APIKey)

    

    submit = st.button("Webscraping durchführen")
    if submit: 
        st.write("WebScraping wird durchgeführt!")
        @st.cache_data(ttl=600)
        def scrape_google_reviews(query, timestamp):
            results = client.google_maps_reviews([query], sort='newest', cutoff=timestamp, reviews_limit=100, language='de')
            return results


        results = scrape_google_reviews(input_Outscraper, timestamp)

        data = []
        for place in results:
            name = place['name']
            for review in place.get('reviews_data', []):
                review_text = review['review_text']
                data.append({'name': name, 'review': review_text})
        df = pd.DataFrame(data)
        st.dataframe(df)

        def generate_csv(df):
            return df.to_csv(index=False)

        if st.download_button(label='Download CSV', data=generate_csv(df), file_name='data.csv', mime='text/csv'):
            pass

### SentimentAnalyse  
if input_method == SentimentAnalyse:
    file = st.file_uploader("Datei hochladen", type=["xlsx", "xls"])
    if file is not None:
            df = pd.read_excel(file)
            df = df.dropna()
            st.dataframe(df)



            Spalte = st.text_input("Wie heisst die Spalte, die du auswerten möchtest?")
            if not Spalte:
                Spalte = "review"

            st.write("Melde dich mit dem nachfolgenden Link bei OpenAI an, um deinen API-Key zu erstellen: https://chat.openai.com/auth/login")
            OpenAI_API = st.text_input("Gib hier deinen OpenAI API Key an")
            
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

if input_method == Anleitung:
    st.title("Beschreibung & Kontakt")
    st.write("""Um das Tool optimal nutzen zu können, musst du dir bei Outscraper und OpenAI einen Account anlegen und einen API-Key erstellen. Gib deinen Key nicht an Dritte weiter! 
    Die Links zur Anmeldung findest du hier:

    \n\nOutscraper: https://outscraper.com/refer?referrer=YXV0aDB8NjQwMWIzZGNiZmMzM2FhMmM5ODA4ZWFm

    \n\nOpenAI: https://chat.openai.com/auth/login


    \n\n\n\nSchritt 1: Webscraping

    \n\nInnerhalb von Schritt 1, dem Webscraping, greift das Programm auf die Google-Maps Bewertungen zu und fasst sie innerhalb einer .csv („comma-seperated-values“) Datei zusammen, die du einfach in Excel öffnen kannst. Dazu musst du angeben, von welchen Standorten du die Exporte benötigst und ab welchem Zeitpunkt. Abschliessend wird noch dein API-Key benötigt. Je nach Anzahl der Standorte und Zeitraum dauert das Scrapen dann wenige Sekunden bis einige Minuten. Das Ergebnis kannst du dann ganz einfach downloaden, um es entweder manuell zu betrachten oder im zweiten Schritt zu analysieren. 


    \n\n\n\nSchritt 2: Sentiment Analyse

    \n\nHier lädst du zunächst die .csv Datei hoch, die du auswerten möchtest. Das Modell ist darauf ausgerichtet, die im ersten Schritt gescrapten Daten zu analysieren, jedoch ist es auch möglich, andere Datensätze zu analysieren. Dabei ist wichtig, dass alle Texte in der gleichen Spalte sind, da sie sonst für die Analyse nicht erfasst werden. Nach dem Upload der Daten musst du angeben, wie die Spalte heisst, die ausgewertet werden soll. Die Spalte der in Schritt 1 exportierten Daten heisst immer „review“, jedoch kann dies bei eigenen Datensätzen abweichen. Abschliessend muss auch hier wieder der passende API-Key angegeben werden. Die Auswertung dauert je nach Grösse des Datensatzes dann wieder einige Sekunden bis Minuten. Das Ergebnis kannst du dann einfach als Word-Datei downloaden, in der die Stärken und Schwächen bzw. positiven und negativen Aspekte der Bewertungen aufgelistet sind.
    """)
    

    st.header("Kontaktformular")

    contact_form = """
    <form action="https://formsubmit.co/soeren.schlisske@web.de" method="POST">
        <input type="text" name="name" placeholder="Dein Name" required>
        <input type="email" name="email" placeholder="Deine Email" required>
        <textarea name="message" placeholder="Deine Nachricht"></textarea>
        <button type="submit">Send</button>
    </form>
    """

    st.markdown(contact_form, unsafe_allow_html=True)

    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    local_css("style/style.css")


   