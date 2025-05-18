import streamlit as st
import xml.etree.ElementTree as et
import sqlitecloud
import sqlite3
import requests
from datetime import date
from google import genai
from pydantic import BaseModel


conn=sqlitecloud.connect('sqlitecloud://cwcgjb0ahz.g1.sqlite.cloud:8860/chinook.sqlite?apikey=DaG8uyqMPa9GdxoR7ObMoajHIdfUOrc7B0mF0IrU6Y0')
c=conn.cursor()

c.execute("SELECT * FROM haberler ORDER BY trend_id DESC LIMIT 99")
haberler=c.fetchall()

for i in range(0,len(haberler),3):
    col1,col2,col3=st.columns(3)
    with col1:
        st.image(haberler[i][3])
        st.write(haberler[i][1])
        st.link_button("Habere Git",haberler[i][2])
    with col2:
        st.image(haberler[i+1][3])
        st.write(haberler[i+1][1])
        st.link_button("Habere Git",haberler[i+1][2])
    with col3:
        st.image(haberler[i+2][3])
        st.write(haberler[i+2][1])
        st.link_button("Habere Git",haberler[i+2][2])
