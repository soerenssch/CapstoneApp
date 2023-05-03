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


# Set the page configuration

st.set_page_config(page_title="Sentiment Analysis", page_icon="🔥", layout="wide")

st.button("Re-run")
st.write("## Sentiment Analysis")
