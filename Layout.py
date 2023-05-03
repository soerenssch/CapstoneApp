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



ID_MAP = {
    "Flint's Praxis für Kleintiere": "ChIJg9LTCjq2kUcRlNmsxEGdNoc",
    'Tierhotel Clinica Alpina Ramosch': "ChIJn9GuzVU3g0cRZAPoW82_WZ0",
    'Tierklinik Clinica Alpina Celerina': "ChIJi2rFwxh9g0cRKh_m8hTN8SA",
    'Tierklinik Clinica Alpina Scuol': "ChIJhf6QYJBHg0cRIe8DYQz8JV8"
}

input_Outscraper = []


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

Outscraper_APIKey = st.text_input("Gib hier deinen Outscraper API Key an")
client = ApiClient(api_key=Outscraper_APIKey)

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

submit = st.button("Submit")
if submit: 
    st.write("WebScraping wird durchgeführt!")
    @st.cache_data(ttl=600)
    def scrape_google_reviews(query, timestamp):
        results = client.google_maps_reviews([query], sort='newest', cutoff=timestamp, reviews_limit=1, language='de')
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