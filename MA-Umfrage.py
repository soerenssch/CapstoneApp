import pandas as pd
import numpy
import matplotlib.pyplot as plt
import scipy
from scipy import stats
from datetime import date

# Die Funktion wurde jetzt für die Google Forms MA Umfrage angepasst, sodass die Fragen
# gleich sinnvoll umbenannt wurden für die Auswertung. Kickt einfach den Timestamp,
# die Frage zur Funktion und die offene Frage.
def cleaning(dataframe):
    dataframe = dataframe.drop(dataframe.columns[[0,1,15]], axis=1 )
    dataframe.columns.values[0] = "Wertschätzung"
    dataframe.columns.values[1] = "Team"
    dataframe.columns.values[2] = "Ausgeglichenheit"
    dataframe.columns.values[3] = "Zufriedenheit als Mitarbeiter"
    dataframe.columns.values[4] = "Weiterempfehlung als Arbeitgeber"
    dataframe.columns.values[5] = "Zufriedenheit der Kunden"
    dataframe.columns.values[6] = "Weiterempfehlung als Tierarztpraxis/-klinik"
    dataframe.columns.values[7] = "Kennen der Werte"
    dataframe.columns.values[8] = "Identifikation mit Werten"
    dataframe.columns.values[9] = "Anweisungen"
    dataframe.columns.values[10] = "Image in der CH"
    dataframe.columns.values[11] = "Kommunikation Head Office"
    dataframe.columns.values[12] = "Weiterbildungen und Karriere"
    return dataframe

# Hier werden die linearen Regressionen erstellt. Jede Spalte x Spalte und dann
# als Dataframe mit dem r (zusammenhang) und p (signifikanz) Wert dargestellt.
# Wird momentan als zwei verschiedene excel gespeichert, dort wo auch immer gearbeitet wird.
# Muss man hier vlt. noch spezifizieren wo es gespeichert werden soll oder wie hast du
# es bei der Sentimentanalyse gemacht? 
def regressionen(dataframe):
    p_total = pd.DataFrame()
    r_total = pd.DataFrame()
    complete = pd.DataFrame()
    today = date.today()
    for column_x in dataframe:
        p_dict = {}
        r_dict = {}
        for column_y in dataframe:
            df_copy = dataframe.dropna(subset=[column_x, column_y])
            x = df_copy[column_x]
            y = df_copy[column_y]  
            y = y.dropna()
            slope, intercept, r, p, std_err = stats.linregress(x, y)    
            p_dict['{} vs. {}'.format(column_x, column_y)] = p
            r_dict['{} vs. {}'.format(column_x, column_y)] = r 
        p_df = pd.DataFrame.from_dict(p_dict, orient='index')
        r_df = pd.DataFrame.from_dict(r_dict, orient='index')
        p_total = p_total.append(p_df)
        r_total = r_total.append(r_df)
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
    complete.to_excel("Alle Regressionen {}.xlsx".format(today)) 
    signifikant = complete[complete.p <= 0.05]
    # Hier nur die signifikanten unter p wert von 5%
    signifikant.to_excel("Signifikante Regressionen {}.xlsx".format(today))
    return complete, signifikant

# vlt. könnte man das auch noch auf die webseite packen, es muss einfach die
# spaltennamen und der dataframe angegeben werden, dann wird ein plot erstellt
def create_plots(column_x, column_y, dataframe):
    x = dataframe[column_x]
    y = dataframe[column_y] 
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

# habe momentan das working directory nicht spezifiziert

dataframe = pd.read_csv('Mitarbeiterumfrage der VetTrust.csv')   
dataframe = cleaning(dataframe)      
regressionen(dataframe)
# Beispiel für eine regression
create_plots("Wertschätzung", "Team", dataframe)

# stell so viel um wie sein muss / wie du willst :) und sag falls ich dir helfen kann
# danke!