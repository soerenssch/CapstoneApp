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
from docx import Document
from docx.shared import Inches
import io


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

st.write(input_Outscraper)