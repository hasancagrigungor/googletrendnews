import streamlit as st
import xml.etree.ElementTree as et
import sqlitecloud
import sqlite3
import requests
from datetime import date
from google import genai
from pydantic import BaseModel

def trendgetir(ulke="TR"):
    conn=sqlitecloud.connect('sqlitecloud://cwcgjb0ahz.g1.sqlite.cloud:8860/chinook.sqlite?apikey=DaG8uyqMPa9GdxoR7ObMoajHIdfUOrc7B0mF0IrU6Y0')
    c=conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS trendler(isim TEXT,trafik INT,tarih TEXT,dil TEXT,isimtr TEXT)")
    conn.commit()

    c.execute("CREATE TABLE IF NOT EXISTS haberler(trend_id INT,baslik TEXT,link TEXT UNIQUE,resim TEXT,kaynak TEXT,basliktr TEXT)")
    conn.commit()


    r=requests.get(f'https://trends.google.com/trending/rss?geo={ulke}')
    veri=r.text
    haberler=et.fromstring(veri)
    haberler=haberler[0]

    for i in haberler.findall('item'):
        title=i.find('title').text
        trafik=int(i[1].text.replace("+",""))
        print(title,trafik)
        tarih=str(date.today())

        c.execute("SELECT * FROM trendler WHERE isim=? AND tarih=?",(title,tarih))
        if len(c.fetchall())==0:
            c.execute("INSERT INTO trendler VALUES(?,?,?,?,?)",(title,trafik,tarih,ulke,None))
            id=c.lastrowid
            conn.commit()
        else:
            c.execute("SELECT rowid FROM trendler WHERE isim=? AND tarih=?",(title,tarih))

            deger=c.fetchone()
            if deger==None:
                id=0
            else:
                id=deger[0]
            conn.commit()


        for m in i:
            if "news_item" in m.tag:
                baslik=m[0].text
                link=m[2].text
                resim=m[3].text
                kaynak=m[4].text

                c.execute("INSERT OR IGNORE INTO haberler VALUES(?,?,?,?,?,?)",(id,baslik,link,resim,kaynak,None))
                conn.commit()

def geminicevir(basliklar):
    class Ceviri(BaseModel):
        ceviri: list[str]


    prompt=str(basliklar)+"--->bu konuları veya haberler başlıklarını türkçeye çevir"

    client = genai.Client(api_key="AIzaSyALuc_PAmFOK34wChTvnq6D3v3uknZtL4A")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": Ceviri,
        },
    )
    # Use the response as a JSON string.
    #print(response.text)

    # Use instantiated objects.
    ceviri: Ceviri = response.parsed.ceviri

    return ceviri


def trendcevir(limit=15):
    conn=sqlitecloud.connect('sqlitecloud://cwcgjb0ahz.g1.sqlite.cloud:8860/chinook.sqlite?apikey=DaG8uyqMPa9GdxoR7ObMoajHIdfUOrc7B0mF0IrU6Y0')
    c=conn.cursor()

    c.execute("SELECT rowid,* FROM trendler WHERE isimtr IS NULL OR isimtr='' ")
    veri=c.fetchall()

    idler=[]
    basliklar=[]
    basliklartr=[]

    haberidler=[]
    haberbasliklar=[]
    haberbasliklartr=[]

    for i in veri:
        if i[4]!="TR":
            idler.append(i[0])
            basliklar.append(i[1])

            c.execute("SELECT rowid,* FROM haberler WHERE trend_id=? AND basliktr IS NULL ",(i[0],))
            veri2=c.fetchall()

            for j in veri2:
                haberidler.append(j[0])
                haberbasliklar.append(j[1])

    idler=idler[:limit]
    basliklar=basliklar[:limit]

    haberidler=haberidler[:limit]
    haberbasliklar=haberbasliklar[:limit]

    basliklartr=geminicevir(basliklar)
    haberbasliklartr=geminicevir(haberbasliklar)



    for i in range(len(idler)):
        c.execute("UPDATE trendler SET isimtr=? WHERE rowid=?",(basliklartr[i],idler[i]))
        conn.commit()

    for i in range(len(haberidler)):
        c.execute("UPDATE haberler SET basliktr=? WHERE rowid=?",(haberbasliklartr[i],haberidler[i]))
        conn.commit()

    print(haberidler,haberbasliklar)

    return veri


def habercevir(haber_id):
    conn=sqlitecloud.connect('sqlitecloud://cwcgjb0ahz.g1.sqlite.cloud:8860/chinook.sqlite?apikey=DaG8uyqMPa9GdxoR7ObMoajHIdfUOrc7B0mF0IrU6Y0')

    c=conn.cursor()

    c.execute("SELECT basliktr,baslik FROM haberler WHERE rowid=?",(haber_id,))
    veri=c.fetchone()

    if veri[0]==None:
        import google.generativeai as genai
        genai.configure(api_key="AIzaSyALuc_PAmFOK34wChTvnq6D3v3uknZtL4A")
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(f" {veri[1]} ---> metni türkçeye çevir sadece çeviriyi yaz")

        c.execute("UPDATE haberler SET basliktr=? WHERE rowid=?",(response.text,haber_id))
        conn.commit()

    else:
        return veri[0]

    return response.text


def gununozeti(gun=""):
    conn=sqlitecloud.connect('sqlitecloud://cwcgjb0ahz.g1.sqlite.cloud:8860/chinook.sqlite?apikey=DaG8uyqMPa9GdxoR7ObMoajHIdfUOrc7B0mF0IrU6Y0')

    c=conn.cursor()

    if gun=="":
        bugun=str(date.today())
        c.execute("SELECT rowid,* FROM trendler WHERE tarih=?",(bugun,))
        trendler=c.fetchall()
    else:
        c.execute("SELECT rowid,* FROM trendler WHERE tarih=?",(gun,))
        trendler=c.fetchall()


    haberlist=[]
    for i in trendler:
        conn=sqlitecloud.connect('sqlitecloud://cwcgjb0ahz.g1.sqlite.cloud:8860/chinook.sqlite?apikey=DaG8uyqMPa9GdxoR7ObMoajHIdfUOrc7B0mF0IrU6Y0')

        c=conn.cursor()
        c.execute("SELECT h.* FROM trendler INNER JOIN haberler h ON h.trend_id=trendler.rowid WHERE trendler.rowid=?",(i[0],))
        haberler=c.fetchall()
        conn.close()

        for x in haberler:
            haberlist.append(x[1])

    import google.generativeai as genai
    genai.configure(api_key="AIzaSyALuc_PAmFOK34wChTvnq6D3v3uknZtL4A")
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(f" {str(haberlist)} ---> bu günün haberlerini incele ve bu haberlere ait bir türkçe günün özeti çıkar")
    return response.text