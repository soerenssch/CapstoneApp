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
from io import BytesIO
import matplotlib.pyplot as plt
import numpy
import scipy
from scipy import stats
from datetime import date


st.title("Automatische Auswertung der standardisierten Mitarbeiterumfrage")
st.write("Hier hochladen")

file = st.file_uploader("Lade deine Datei hier hoch:", type=["csv"])
if file is not None:
    df = pd.read_csv(file)
    
    def cleaning(df):
        df = df.drop(df.columns[[0,1,15]], axis=1 )
        df.columns.values[0] = "Wertschätzung"
        df.columns.values[1] = "Team"
        df.columns.values[2] = "Ausgeglichenheit"
        df.columns.values[3] = "Zufriedenheit als Mitarbeiter"
        df.columns.values[4] = "Weiterempfehlung als Arbeitgeber"
        df.columns.values[5] = "Zufriedenheit der Kunden"
        df.columns.values[6] = "Weiterempfehlung als Tierarztpraxis/-klinik"
        df.columns.values[7] = "Kennen der Werte"
        df.columns.values[8] = "Identifikation mit Werten"
        df.columns.values[9] = "Anweisungen"
        df.columns.values[10] = "Image in der CH"
        df.columns.values[11] = "Kommunikation Head Office"
        df.columns.values[12] = "Weiterbildungen und Karriere"
        return df
    
    

    st.dataframe(df)

    if st.button("Auswertung starten"):
        df = cleaning(df)

        @st.cache_data(ttl=600)
        def regressionen(df):
            p_total = pd.DataFrame()
            r_total = pd.DataFrame()
            complete = pd.DataFrame()
            today = date.today()
            for column_x in df:
                p_dict = {}
                r_dict = {}
                for column_y in df:
                    df_copy = df.dropna(subset=[column_x, column_y])
                    x = df_copy[column_x]
                    y = df_copy[column_y]  
                    y = y.dropna()
                    slope, intercept, r, p, std_err = stats.linregress(x, y)    
                    p_dict['{} vs. {}'.format(column_x, column_y)] = p
                    r_dict['{} vs. {}'.format(column_x, column_y)] = r 
                p_df = pd.DataFrame.from_dict(p_dict, orient='index')
                r_df = pd.DataFrame.from_dict(r_dict, orient='index')
                p_total = pd.concat([p_total, p_df])
                r_total = pd.concat([r_total, r_df])
            r_total = r_total.reset_index()
            p_total = p_total.reset_index()
            r_total = r_total.rename(columns={"index": "Parameter", 0: "r"})
            p_total = p_total.rename(columns={"index": "Parameter", 0: "p"})
            p_total= p_total.round(6)
            r_total= r_total.round(6)
            r_total = r_total.drop_duplicates(subset=["r"], keep="first")
            complete = pd.merge(r_total, p_total, on="Parameter", how="left")
            complete = complete[complete.r != 1]
            complete=complete.sort_values(by=['r'], ascending=False)
            complete = complete.reset_index()
            complete = complete.drop(columns="index")
            # Sind alle Werte und Regressionen drin
            # complete.to_excel("Alle Regressionen {}.xlsx".format(today)) 
            signifikant = complete[complete.p <= 0.05]
            # Hier nur die signifikanten unter p wert von 5%
            # signifikant.to_excel("Signifikante Regressionen {}.xlsx".format(today))
            return complete, signifikant
        
        complete, signifikant = regressionen(df)

        st.dataframe(signifikant)

        @st.cache_data(ttl=600)
        def create_plots(column_x, column_y, df):
            x = df[column_x]
            y = df[column_y] 
            slope, intercept, r, p, std_err = stats.linregress(x, y)    
            def myfunc(x):
                return slope * x + intercept
            mymodel = list(map(myfunc, x))
            plt.ylim([0, 5])
            plt.xlim([0, 5])
            plt.scatter(x, y, color=("#132f55"))
            plt.plot(x, mymodel,color=("#d52f89"))
            plt.title("{} vs. {}".format(column_x, column_y))
            plt.xlabel("{}".format(column_x))
            plt.ylabel("{}".format(column_y))
            plt.savefig(('{} vs {}'.format(column_x, column_y)), dpi=300)
            plt.show()


        plot_axis = signifikant["Parameter"]

        x_axis = []
        y_axis = []
        for description in plot_axis:
            x, y = description.split(' vs. ')
            x_axis.append(x)
            y_axis.append(y)

        for i in range(len(plot_axis)):
            x_axis = plot_axis[i].split(' vs. ')[0]
            y_axis = plot_axis[i].split(' vs. ')[1]
            st.write(f"Creating plot for {x_axis} vs {y_axis}")
            create_plots(x_axis, y_axis, df)
            

        # column_names = []
        # for column in df.columns:
        #     column_names.append(column)


        # x_axis = st.selectbox('X-Achse', column_names, key='x_axis')
        # y_axis = st.selectbox('Y-Achse', column_names, key='y_axis')


        # x_axis = st.text_input("Welche Variable soll auf der x-Achse sein?")
        # y_axis = st.text_input("Welche Variable soll auf der y-Achse sein?")

        # if st.button("Erstelle Plot"):
        #     create_plots(x_axis, y_axis, df)