import streamlit as st
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

# Seitentitel
st.title("Sentiment Analysis")



# Datum für Reviews
date_input = st.date_input('Gib das Datum an, ab dem du die Reviews exportieren willst')

if date_input > datetime.datetime.today().date():
    st.error('Fehler: Datum darf nicht in der Zukunft liegen!')
else:
    year = date_input.year
    month = date_input.month
    day = date_input.day

# Datetime für den 27.04.2023
my_date = datetime.datetime(year, month, day)
timestamp = my_date.timestamp()
timestamp = int(timestamp)

# API Key für Webscraping
Outscraper_APIKey = st.text_input("Gib hier deinen Outscraper API Key an")

# Google Map IDs der Standorte für Webscraping
ID_1 = "ChIJg9LTCjq2kUcRlNmsxEGdNoc"
ID_2 = "ChIJn9GuzVU3g0cRZAPoW82_WZ0"
ID_3 = "ChIJi2rFwxh9g0cRKh_m8hTN8SA"
ID_4 = "ChIJhf6QYJBHg0cRIe8DYQz8JV8"
ID_5 = "ChIJsXk3JcvgmkcRmMwJslg2xcU"
ID_6 = "ChIJE9cxb6CkmkcRH3ybj-adIbE"
ID_7 = "ChIJm8-ANlQRm0cRnd3hTS279ag"
ID_8 = "ChIJnU4TOnT9j0cR6HQvLSgsS5Q"
ID_9 = "ChIJAR4_G0-4kUcRQAgkjVkUSek"
ID_10 = "ChIJqRyBUAG5kUcRVcVH76IXaFE"
ID_11 = "ChIJS9aRbdJ1kEcRhKrcNtRWsuA"
ID_12 = "ChIJzZH-veOjmkcR7GUzmVWaezY"
ID_13 = "ChIJ9UNysAigmkcR5QgQSw4lpiY"
ID_14 = "ChIJv5D40wE3jkcRFKWuw1rHTtE"
ID_15 = "ChIJ6Z-zRnG7mkcRPBbZp4n8iww"
ID_16 = "ChIJHY_A-m7_j0cRHUpOOIwa8Yo"
ID_17 = "ChIJf_mbzJQvkEcRicJ5NcgPDuE"
ID_18 = "ChIJvwTRBxe4kUcRfEUl0F_UF4Y"
ID_19 = "ChIJ5-00QTwFkEcRG9Hk9XEzIM8"
ID_20 = "ChIJg3c2oE7SkUcRy_Yz-zeQUww"
ID_21 = "ChIJF5STJ2cLkEcRDRye_BfHcDc"
ID_22 = "ChIJERk9VbMNkEcRPy81sQi1wic"
ID_23 = "ChIJTeRhD_Qem0cRdZHi-gV_KQc"
ID_24 = "ChIJO7t-Rkb3j0cRhQ4zkf4JuBs"
ID_25 = "ChIJaZqDHPw7kEcR-Fp5zfYNNdI"
ID_26 = "ChIJdUCYp3bHkUcRnqgwh2XgkjI"
ID_27 = "ChIJlxwBXNMxkEcRVFq9hfD4rYc"
ID_28 = "ChIJGyWX2Q2WmkcRx1gLsoFhMz8"
ID_29 = "ChIJGY-uTiltkEcR5qPVT9EHlVU"
ID_30 = "ChIJK9ieJXmZmkcRHtJtVS47ZwE"
ID_31 = "ChIJtSFUYUWqmkcRnQZS-2NJx-w"
ID_32 = "ChIJPWi96nfpmkcRMxRLWqMgC5s"
ID_33 = "ChIJpSNsIru5kUcRx-XRYVJBeU4"
ID_34 = "ChIJb_dA_kPXmkcRAGqsVT1wLFE"
ID_35 = "ChIJkTyE5WG8mkcR9FjBoEAKIEE"
ID_36 = "ChIJ2RDiJW6-mkcRRKSDQ0onkc4"
ID_37 = "ChIJNXoM5QOhmkcRBNaok_HRShE"
ID_38 = "ChIJH2Ls-3Z8kEcRvq0oZ5ctkrk"


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
    'Kleintierpraxis Zug': "ChIJq6qqQZQymkcR2Z3Z0Q4Z0ZQ",
    'Kleintierpraxis Zuzwil': "ChIJq6qqQZQymkcR2Z3Z0Q4Z0ZQ",
    'Tierklinik Basel': "ChIJq6qqQZQymkcR2Z3Z0Q4Z0ZQ",
    'Tierklinik Nesslau': "ChIJq6qqQZQymkcR2Z3Z0Q4Z0ZQ",
    'Tierklinik Oberland Pfäffikon': "ChIJq6qqQZQymkcR2Z3Z0Q4Z0ZQ",
    'Tierklinik Oberland Saland': "ChIJq6qqQZQymkcR2Z3Z0Q4Z0ZQ",
    'Tierklinik Zürich': "ChIJq6qqQZQymkcR2Z3Z0Q4Z0ZQ",
    'Zentrum für Tiermedizin Klettgau': "ChIJq6qqQZQymkcR2Z3Z0Q4Z0ZQ",
}

# Checkboxen zum ankreuzen 

S25 = st.checkbox('Kleintierpraxis Telli Aarau')
S26 = st.checkbox('Kleintierpraxis Therwil')
S27 = st.checkbox('Kleintierpraxis Trimbach')
S28 = st.checkbox('Kleintierpraxis Turbenthal')
S29 = st.checkbox('Kleintierpraxis Wettingen')
S30 = st.checkbox('Kleintierpraxis Winterthur im Zentrum')
S31 = st.checkbox('Kleintierpraxis Zug')
S32 = st.checkbox('Kleintierpraxis Zuzwil')
S33 = st.checkbox('Tierklinik Basel')
S34 = st.checkbox('Tierklinik Nesslau')
S35 = st.checkbox('Tierklinik Oberland Pfäffikon')
S36 = st.checkbox('Tierklinik Oberland Saland')
S37 = st.checkbox('Tierklinik Zürich Ost')
S38 = st.checkbox('Zentrum für Tiermedizin Klettgau')


S1 = st.checkbox("Flint's Praxis für Kleintiere")
S2 = st.checkbox('Tierhotel Clinica Alpina Ramosch')
S3 = st.checkbox('Tierklinik Clinica Alpina Celerina')
S4 = st.checkbox('Tierklinik Clinica Alpina Scuol')
S5 = st.checkbox('Kleintierklinik am Damm, Gossau')
S6 = st.checkbox('Kleintierpraxis Aabach Uster')
S7 = st.checkbox('Kleintierpraxis Au')
S8 = st.checkbox('Kleintierpraxis Bachmatt Eschenbach')
S9 = st.checkbox('Kleintierpraxis Basel Central')
S10 = st.checkbox('Kleintierpraxis Basel Spalen')
S11 = st.checkbox('Kleintierpraxis Bülach')
S12 = st.checkbox('Kleintierpraxis Fällanden')
S13 = st.checkbox('Kleintierpraxis Glattbrugg')
S14 = st.checkbox('Kleintierpraxis Gümligen')
S15 = st.checkbox('Kleintierpraxis im Bahnhof, Aathal')
S16 = st.checkbox('Kleintierpraxis Küssnacht am Rigi')
S17 = st.checkbox('Kleintierpraxis Mühlebach Oftringen')
S18 = st.checkbox('Kleintierpraxis Münchenstein')
S19 = st.checkbox('Kleintierpraxis Muri')
S20 = st.checkbox('Kleintierpraxis Oensingen')
S21 = st.checkbox('Kleintierpraxis Regensdorf')
S22 = st.checkbox('Kleintierpraxis Schlieren')
S23 = st.checkbox('Kleintierpraxis St. Gallen Ost')
S24 = st.checkbox('Kleintierpraxis Stansstad')


input_Outscraper = []

if S1:
    input_Outscraper.append(ID_1)
if S2:
    input_Outscraper.append(ID_2)
if S3:
    input_Outscraper.append(ID_3)
if S4:
    input_Outscraper.append(ID_4)
if S5:
    input_Outscraper.append(ID_5)
if S6:
    input_Outscraper.append(ID_6)
if S7:
    input_Outscraper.append(ID_7)
if S8:
    input_Outscraper.append(ID_8)
if S9:
    input_Outscraper.append(ID_9)
if S10:
    input_Outscraper.append(ID_10)
if S11:
    input_Outscraper.append(ID_11)
if S12:
    input_Outscraper.append(ID_12)
if S13:
    input_Outscraper.append(ID_13)
if S14:
    input_Outscraper.append(ID_14)
if S15:
    input_Outscraper.append(ID_15)
if S16:
    input_Outscraper.append(ID_16)
if S17:
    input_Outscraper.append(ID_17)
if S18:
    input_Outscraper.append(ID_18)
if S19:
    input_Outscraper.append(ID_19)
if S20:
    input_Outscraper.append(ID_20)
if S21:
    input_Outscraper.append(ID_21)
if S22:
    input_Outscraper.append(ID_22)
if S23:
    input_Outscraper.append(ID_23)
if S24:
    input_Outscraper.append(ID_24)
if S25:
    input_Outscraper.append(ID_25)
if S26:
    input_Outscraper.append(ID_26)
if S27:
    input_Outscraper.append(ID_27)
if S28:
    input_Outscraper.append(ID_28)
if S29:
    input_Outscraper.append(ID_29)
if S30:
    input_Outscraper.append(ID_30)
if S31:
    input_Outscraper.append(ID_31)
if S32:
    input_Outscraper.append(ID_32)
if S33:
    input_Outscraper.append(ID_33)
if S34:
    input_Outscraper.append(ID_34)
if S35:
    input_Outscraper.append(ID_35)
if S36:
    input_Outscraper.append(ID_36)
if S37:
    input_Outscraper.append(ID_37)
if S38:
    input_Outscraper.append(ID_38)



# input_Outscraper = []
# for label, place_id in ID_MAP.items():
#     if st.checkbox(label):
#         input_Outscraper.append(place_id)


client = ApiClient(api_key=Outscraper_APIKey)



submit = st.button("Submit")

if submit:
    st.write("WebScraping wird durchgeführt!")

    results = client.google_maps_reviews([input_Outscraper],
                                            sort='newest', cutoff = timestamp, reviews_limit=1, language='de')

    data = []
    for place in results:
        name = place['name']
        for review in place.get('reviews_data', []):
            review_text = review['review_text']
            data.append({'name': name, 'review': review_text})
    df = pd.DataFrame(data)
    st.dataframe(df)

    if st.button('Download CSV'):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="data.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)
        

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


all_reviews = "\n".join(df["review"].tolist())

        OpenAI_API = st.text_input("Gib hier deinen OpenAI API Key an")
        if st.button("Sentiment Analyse ausführen"):

            summary_proscons = generate_proscons_list(all_reviews)

            df_proscons = pd.DataFrame()
            list_proscons = []
            list_proscons.append(summary_proscons)
            df_proscons["pros_cons"] = list_proscons

            output_file_proscons = "Reviews_StärkenSchwächen.docx"
            doc = docx.Document()


