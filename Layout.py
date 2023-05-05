import pickle
from pathlib import Path
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
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
import stauth



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