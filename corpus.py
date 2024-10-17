from collections import Counter
import streamlit as st
#import spacy_streamlit

import pandas as pd
from PIL import Image
import urllib

import datetime

import dhlab as dh
import dhlab.api.dhlab_api as api
from dhlab.text.nbtokenizer import tokenize
# for excelnedlastning
from io import BytesIO

st.set_page_config(page_title="Korpus", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

max_size_corpus = 100000
max_rows = 1200
min_rows = 800
default_size = 10  # percent of max_size_corpus

def to_excel(df):
    """Make an excel object out of a dataframe as an IO-object"""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    worksheet = writer.sheets['Sheet1']
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def v(x):
    if x != "":
        res = x
    else:
        res = None
    return res

### Headers

col_zero, col_two, col_three = st.columns([4, 1, 1])
with col_zero:
    st.subheader('Nettaviser - Bygg korpus')
with col_three:
    st.markdown("""<style>
img {
  opacity: 0.6;
}
</style><a href="https://nb.no/dhlab">
  <img src="https://github.com/NationalLibraryOfNorway/DHLAB-apps/raw/main/corpus/DHlab_logo_web_en_black.png" style="width:250px"></a>""", unsafe_allow_html=True)

st.write("---")

col2, col3 = st.columns([1, 3])

doctype = "nettavis"

with col2:
    lang = st.multiselect(
        "Språk", 
        ["nob", "nno", "sma", "sme", "smj", "fkv", "eng", "dan", "swe", "fra", "spa", "ger"],  
        help="Velg fra listen"
    )
    lang = " AND ".join(list(lang))
    if lang == "":
        lang = None

with col3:
    today = datetime.date.today()
    year = today.year
    years = st.slider(
    'Årsspenn',
    2019, year, (2022, year))


#st.subheader("Forfatter og tittel") ###################################################
cola, colb = st.columns(2)
with cola:
    publisher = st.text_input("Publisher", "",
                           help="Angi domenenavn",

with colb:
    title = st.text_input("Tittel", "",
                          help="Søk etter titler. For aviser vil tittel matche avisnavnet.")

#st.subheader("Meta- og innholdsdata") ##########################################################

cold, cole, colf = st.columns(3)
with cold:        
    fulltext = st.text_input(
        "Ord eller fraser i teksten", 
        "", 
        help="Matching på innholdsord skiller ikke mellom stor og liten bokstav."
             " Trunkert søk er mulig, slik at demokrat* vil finne bøker som inneholder demokrati og demokratisk blant andre treff",
    )


df_defined = False
st.write("---")
st.subheader("Lag korpuset og last ned") ######################################################################

with st.form(key='my_form'): 
    
    colx, col_order, coly = st.columns([2, 2, 4])
    with colx:
        limit = st.number_input(f"Maks antall, inntil {max_size_corpus}", min_value=1, max_value=max_size_corpus, value=int(default_size * max_size_corpus / 100))
    with col_order:
        ordertype = st.selectbox("Metode for uthenting", ['first', 'rank', 'random'], help="Metode 'first' er raskest, og velger dokument etter hvert som de blir funnet, mens 'rank' gir en rask ordning på dokumenter om korpuset er definert med et fulltekstsøk og sorterer på relevans, siste valg er 'random' som først samler inn hele korpuset og gjør et vilkårlig utvalg av tekster derfra.")
    with coly:
        filnavn = st.text_input("Filnavn for nedlasting", "korpus.xlsx")

    submit_button = st.form_submit_button(label="Trykk her når korpusdefinisjonen er klar")
    
    if submit_button:
        # For "nettavis", we define the corpus based on the fields relevant for newspapers
        df = dh.Corpus(doctype=v(doctype), fulltext=v(fulltext), from_year=years[0], to_year=years[1], title=v(title), limit=limit, order_by=ordertype)
        columns = ['urn', 'title', 'year', 'timestamp', 'city']
        
        st.markdown(f"Fant totalt {df.size} dokumenter")
            
        if df.size >= max_rows:
            st.markdown(f"Viser {min_rows} rader.")
            st.dataframe(df.corpus.sample(min(min_rows, max_rows)))
        else:
            st.dataframe(df.corpus[columns])
        df_defined = True

if df_defined:
    if st.download_button('Last ned data i excelformat', to_excel(df.corpus), filnavn, help="Åpnes i Excel eller tilsvarende"):
        pass
