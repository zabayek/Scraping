# https://www.youtube.com/watch?v=XQgXKtPSzUI&t=1703s

import urllib
import urllib.request
import os # aby mozna bylo eksportowac do plikow
import sqlite3 # polaczenie z baza
import datetime
import time
import re # aby regularne wyrazenia dzialaly
import MechanicalSoup

from bs4 import BeautifulSoup

conn = sqlite3.connect('krajowagieldadlugow.db')
c = conn.cursor()

def tworz_tbl():
    c.execute('CREATE TABLE IF NOT EXISTS Dluznicy_BD (Id INT, Datestamp TEXT, DluznikNazwa TEXT, DluznikLink TEXT, DluznikKwotaDlugu TEXT, DluznikNIP TEXT, DluznikMiejscowosc TEXT)')

def dodaj_dane():
    unix = time.time()
    data = str(datetime.datetime.fromtimestamp(unix).strftime('%Y-%m-%d %H-%M-%S'))
    c.execute("INSERT INTO Dluznicy_BD (Datestamp, DluznikNazwa, DluznikLink, DluznikKwotaDlugu, DluznikNIP, DluznikMiejscowosc) VALUES (?,?,?,?,?,?)", (data, dluznik_nazwa, dluznik_link, dluznik_kwota, dluznik_nip, dluznik_miasto))
    conn.commit()

def make_soup(url):
    thepage = urllib.request.urlopen(url)
    soupdata = BeautifulSoup(thepage, "html.parser") # parser wbudowany w pythona
    return soupdata

# Podaj glowny link do pierwszej strony
soup_poczatek = make_soup("https://www.krajowagieldadlugow.pl/wierzytelnosci?page=1")

lista_ilosc_stron = soup_poczatek.find("div",{"class":"pagination pagination-centered"})
for link in soup_poczatek.findAll('a', href=True, text='>>'):
    link = link.get('href')
    lista_max_strona = int(re.findall(r'[0-9]{1,4}', link)[0])

tworz_tbl()

for i in range(1,lista_max_strona+1):
    url = "https://www.krajowagieldadlugow.pl/wierzytelnosci?page="+ str(i)
    soup = make_soup(url)

    dluznicy_lista = soup.findAll("article",{"class":"clearfix without-controls"}) # odwolanie do kontenera z dluzniekiem
    # print(len(dluznicy_lista)) # policz ile kontenerow znaleziono - tu niepotrzebne


    for dluznik in dluznicy_lista:
        # Nazwa
        dluznik_nazwa = dluznik.hgroup.h2.a["title"].strip() # nazwa dluznika, bez znakow spacji - strip()

        # Link do podstrony dlugu
        dluznik_link = "https://www.krajowagieldadlugow.pl" + dluznik.hgroup.h2.a["href"]

        # Kwota
        dluznik_kwota_kontener = dluznik.findAll("div",{"class":"price"})
        dluznik_kwota = dluznik_kwota_kontener[0].text.strip()
        dluznik_kwota = re.findall(r'(?<=gu: )(.*)\,', dluznik_kwota)[0] # text pomiedzy 'gu: ' a ','
        # dluznik_kwota2 = dluznik_kwota.replace(",", "|") # replace cos nie dziala
        # fixme: naprawic replace, czemu nie dziala. moze trzeba dodac jakis modul?
        # fixme: usunac wyswietlanie nawiasow i ciapkow w kwotach ['32,902.51 zł']

        # NIP
        dluznik_nip_kontener = dluznik.findAll("p",{"class":"nip"})
        dluznik_nip = dluznik_nip_kontener[0].text.strip()
        dluznik_nip = re.findall(r'(?<=NIP: )(.*)', dluznik_nip)[0]  # zwraca sam nr NIP

        # Miejscowosc
        dluznik_miasto_kontener = dluznik.findAll("span",{"class":"city"})
        dluznik_miasto = dluznik_miasto_kontener[0].text.strip()

        # Wyswietlanie danych
        # print(dluznik_link)
        # print(dluznik_nazwa)
        # print(dluznik_kwota)
        # print(dluznik_nip)
        # print(dluznik_miasto)

        # dluznik_wpis = str(dluznik_nazwa)+"|"+str(dluznik_kwota)+"|"+str(dluznik_nip)+"|"+str(dluznik_miasto)
        # print(dluznik_wpis)

        dodaj_dane()

c.close()
conn.close()


"""
# wyswietl linki do podstron z licytacjami
for link in soup.findAll('a'):
    if "pokaz" in link.get("href"):
        # print(link.get('href'))
        # print(link.text).strip()

        link_l = "https://www.krajowagieldadlugow.pl" + link.get('href')
        link_t = link.text.strip()

        for kwota in soup.findAll('div',{"class":"price"}):
            playerdata = ""
            for kwota_dl in soup.findAll('p'):
                playerdata = playerdata + "|" + kwota_dl.text
                print(playerdata)



        # print(link_l+" | "+link_t + kwota)
"""

"""
#Nazwa
print(soup.findAll('h1')[1].text)

# Kod pocztowy
print(soup.find('p',{"class":"postal-code"}).text)

# Miasto
print(soup.find('p',{"class":"region"}).text)

# Ulica
print(soup.find('p',{"class":"street-address"}).text)

#Nip
print(soup.findAll('p')[10].text)

#Kwota dlugu
print(soup.find('h4').text)


# Data dlugu
print(soup.findAll('div',{"class":"events clearfix"}))
"""





# playerdatasaved=""
# ##1044
# for i in range(5):
#     soup = make_soup("http://foxberg.pl/gielda,2-"+ str(i) +",Lista-wierzytelnosci.html")
#
#     for record in soup.findAll('tr'):
#         playerdata=""
#         for data in record.findAll('td'):
#             playerdata=playerdata+"|"+data.text
#         if len(playerdata)>20:
#             playerdatasaved = playerdatasaved + "\n" + playerdata[1:]
#
# header="LP|Nazwa|NIP|Miejscowosc|Wojewodztwo|Kwota|Akcja"
# file = open(os.path.expanduser("wyjscie.txt"),"wb")
# file.write(bytes(header, encoding="ascii",errors='ignore'))
# file.write(bytes(playerdatasaved, encoding="ascii",errors='ignore'))
#
# print(playerdatasaved)
#
#
