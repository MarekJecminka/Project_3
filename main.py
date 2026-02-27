"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Marek Ječmínka
email: jecminkam@seznam.cz
"""

import sys
import csv

from requests import get
from bs4 import BeautifulSoup as bs

def vysledky_hlasovani():

    def najdi_uzemni_celky(url: str) -> list:
        "Funkce najde všechny možné územní celky - okresy."
        
        rozdelene_html = bs(get("https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ").text, features="html.parser")
        vsechny_celky = rozdelene_html.find_all("a")
        celky = [a_tag.attrs.get("href", "chybí odkaz") for a_tag in vsechny_celky if "xnumnuts" in str(a_tag)]
        return [url + item for item in celky if "ps32" in item]

    def vytvor_jmena_csv(okresy_url: list) -> list:
        "Funkce vytvoří všechny názvy csv souborů pro porovnání správnosti systémových argumentů."

        vsechny_okresy = ["vysledky_praha.csv"]
        for item in okresy_url:
            rozdelene_html = bs(get(item).text, features="html.parser")
            vsechny_h3 = rozdelene_html.find_all("h3")
            for tag in vsechny_h3:
                if "Okres: " in str(tag):
                    vsechny_okresy.append(f"vysledky_{str(tag)[12:-6].lower()}.csv")
        return vsechny_okresy    

    def odstran_diakritiku(jmena_okresu_csv: list) -> list:
        "Funkce pro odstranění diakritiky."

        bez_diakritiky = []
        odstranit_diakritiku = {"á":"a","č":"c","ď":"d","é":"e","ě":"e","í":"i","ň":"n","ó":"o",
                                "ř":"r","š":"s","ť":"t","ú":"u","ů":"u","ý":"y","ž":"z"}
        for item in jmena_okresu_csv:
            csv = "".join(odstranit_diakritiku[char] if char in odstranit_diakritiku else char for char in item)
            bez_diakritiky.append(csv)
        return bez_diakritiky

    def over_prihlasovaci_udaje(udaje: dict) -> bool:
        "Funkce porovnává zda se systémové argumenty shodují s předdefinovanými a vrací hodnoty True nebo False."

        try:
            udaje[sys.argv[1]] == sys.argv[2]
        except KeyError:
            return False
        except:
            return False
        else:
            if udaje[sys.argv[1]] == sys.argv[2]:
                return True
            else:
                return False
    
    def najdi_linky_obci(base_url_obci: str) -> list:
        "Funkce najde všehny linky obcí okresu, který si uživatel vybral pomocí systémového argumentu 1."

        url = sys.argv[1]
        rozdelene_html = bs(get(url).text, features="html.parser")
        a_tagy = rozdelene_html.find_all("a")
        linky_obci = [base_url_obci + a_tag.attrs.get("href") for a_tag in a_tagy if "ps311" in str(a_tag)]
        linky = []
        for link in linky_obci:
            if link in linky:
                continue
            else:
                linky.append(link)
        return linky
    
    def najdi_code_a_location() -> list:
        "Funkce najde code a location pro všechny obce okresu a uloží je do listu."

        url_okresu = sys.argv[1]
        rozdelene_html = bs(get(url_okresu).text, features="html.parser")
        vsechny_table = rozdelene_html.find_all("table", {"class": "table"})
        code_a_location_tabulek = []
        for table in vsechny_table:
            vsechny_tr = table.find_all("tr")
            for tr in vsechny_tr[2:]:
                code_a_location_radku = []
                td_na_radku = tr.find_all("td")
                if td_na_radku[0].text != "-":
                    code_a_location_radku.append(td_na_radku[0].text)
                if td_na_radku[1].text != "-":
                    code_a_location_radku.append(td_na_radku[1].text)
                code_a_location_tabulek.append(code_a_location_radku)
        return code_a_location_tabulek
    
    def najdi_volebni_ucast(linky_obci: list) -> list:
        "Funkce najde volební účast pro všechny obce okresu a uloží je do listu."

        volebni_ucast = []
        for link in linky_obci:
            url_obce = link
            rozdelene_html = bs(get(url_obce).text, features="html.parser")
            vsechny_table = rozdelene_html.find_all("table", {"class":"table"})
            vsechny_tr = vsechny_table[0].find_all("tr")
            td_na_radku = vsechny_tr[2].find_all("td")
            volebni_ucast_obce = [td_na_radku[3].text, td_na_radku[4].text, td_na_radku[7].text]
            volebni_ucast.append(volebni_ucast_obce)
        return volebni_ucast
    
    def najdi_hlasy_stran(linky_obci: list) -> list:
        "Funkce najde hlasy pro všechny obce okresu a uloží je do listu."
        "Také najde názvy všech kandidujících stran a uloží je do listu."

        hlasy_stran = []
        klice = []
        for link in linky_obci:
            url_obce = link
            rozdelene_html = bs(get(url_obce).text, features="html.parser")
            vsechny_table = rozdelene_html.find_all("table", {"class":"table"})
            hlasy_stran_obce = []
            klice_obce = ["code", "location", "registered", "envelopes", "valid"]
            tabulka_s_hlasy = vsechny_table[1:]
            for table in tabulka_s_hlasy:
                vsechny_tr = table.find_all("tr")
                for tr in vsechny_tr[2:]:
                    td_na_radku = tr.find_all("td")
                    if td_na_radku[1].text != "-":
                        hlasy_stran_obce.append(td_na_radku[2].text)
                    if td_na_radku[1].text != "-":
                        klice_obce.append(td_na_radku[1].text)
            hlasy_stran.append(hlasy_stran_obce)
            klice.append(klice_obce)
        return [hlasy_stran, klice[0]]

    def spoj_data_obci(code_a_location_obci: list, volebni_ucast_obci: list, hlasy_stran_obci: list) -> list:
        "Funkce spojí code, location, volební účast a hlasy stran pro všechny obce okresu a uloží je do listu."

        data_obci = []
        for code, ucast, hlasy in zip(code_a_location_obci, volebni_ucast_obci, hlasy_stran_obci):
            data_obce = []
            for item in code:
                data_obce.append(item)
            for item in ucast:
                data_obce.append(item)
            for item in hlasy:
                data_obce.append(item)
            data_obci.append(data_obce)
        return data_obci

    def prirad_klice_k_datum(klice_dat: list, data: list) -> list[dict]:
        "Funkce vytvoří z klíčů a dat pro jednotlivé obce okresu list dictu pro zápis do csv souboru."

        data_obci = []
        for obec in data:
            data_obce = {klic: hodnota for klic, hodnota in zip(klice_dat, obec)}
            data_obci.append(data_obce)
        return data_obci
    
    def zapis_data_do_csv(data_csv: list[dict], klice_csv: list):
        "Funkce vytvoří csv soubor, do kterého zapíše veškerá data obcí zvoleného okresu."

        soubor_csv = open(f"{sys.argv[2]}", mode="w", newline="", encoding="utf-8-sig")
        zahlavi = klice_csv
        zapisovac = csv.DictWriter(soubor_csv, fieldnames=zahlavi)
        zapisovac.writeheader()
        zapisovac.writerows(data_csv)
        soubor_csv.close()

    def uloz_volebni_data(base_url_dat: str):
        "Funkce najde všechny linky obcí okresu a z nich uloží a zapíše všechny data do csv souboru."

        linky = najdi_linky_obci(base_url_dat)
        code_a_location = najdi_code_a_location()
        volebni_ucast = najdi_volebni_ucast(linky)
        hlasy_stran = najdi_hlasy_stran(linky)[0]
        klice = najdi_hlasy_stran(linky)[1]
        data_list = spoj_data_obci(code_a_location, volebni_ucast, hlasy_stran)
        data = prirad_klice_k_datum(klice, data_list)
        zapis_data_do_csv(data, klice)

    print("Ověřuji systémové argumenty...")
    base_url = "https://www.volby.cz/pls/ps2017nss/"
    okresy = najdi_uzemni_celky(base_url)
    jmena_okresu_csv = vytvor_jmena_csv(okresy)
    jmena_okresu_csv_bez_diakritiky = odstran_diakritiku(jmena_okresu_csv)
    prihlasovaci_udaje = {klic: hodnota for klic, hodnota in zip(okresy, jmena_okresu_csv_bez_diakritiky)}
    spravne_udaje = over_prihlasovaci_udaje(prihlasovaci_udaje)
    
    if spravne_udaje:
        print("Ukládám data...")
        uloz_volebni_data(base_url)
        print("Ukládání dokončeno!")
    else:
        print("Nesprávné systémové argumenty. Vlož správné systémové argumenty.")

if __name__ == "__main__":
    vysledky_hlasovani()
