import sys
import csv

from requests import get
from bs4 import BeautifulSoup as bs

def vysledky_hlasovani():
    base_url = "https://www.volby.cz/pls/ps2017nss/"
    url = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"

    def rozdel_html(odkaz):
        return bs(get(odkaz).text, features="html.parser")
    
    def najdi_celky(celky):
        uzemni_celky = []
        for a_tag in celky:
            if "xnumnuts" in str(a_tag):
                uzemni_celky.append(a_tag.attrs.get("href", "chybí odkaz"))
        return uzemni_celky
    
    def najdi_relevantni_okresy(celky):
        okresy = list()
        for item in celky:
            if "ps32" in item:
                okresy.append(base_url + item)
        return okresy

    def najdi_uzemni_celky():
        rozdelene_html = rozdel_html(url)
        vsechny_celky = rozdelene_html.find_all("a")
        celky = najdi_celky(vsechny_celky)
        okresy = najdi_relevantni_okresy(celky)
        return okresy

    def vytvor_jmena_csv(okresy_url):
        vsechny_okresy = ["vysledky_praha.csv"]
        for item in okresy_url:
            rozdelene_html = bs(get(item).text, features="html.parser")
            vsechny_h3 = rozdelene_html.find_all("h3")
            for tag in vsechny_h3:
                if "Okres: " in str(tag):
                    vsechny_okresy.append(f"vysledky_{str(tag)[12:-6].lower()}.csv")
        return vsechny_okresy    

    def odstran_diakritiku(jmena_okresu_csv):
        bez_diakritiky = list()
        odstranit_diakritiku = {"á": "a", "č": "c", "ď": "d", "é": "e", "ě": "e", "í": "i", "ň": "n", "ó": "o", "ř": "r", "š": "s", "ť": "t", "ú": "u", "ů": "u", "ý": "y", "ž": "z",}
        for item in jmena_okresu_csv:
            csv = ""
            for char in item:
                if char in odstranit_diakritiku:
                    csv += odstranit_diakritiku[char]
                else:
                    csv += char
            bez_diakritiky.append(csv)
        return bez_diakritiky
    
    def vytvor_prihlasovaci_udaje(okresy_pro_prihlaseni, csv_pro_prihlaseni):
        prihlasovaci_udaje = dict()
        for klic, hodnota in zip(okresy_pro_prihlaseni, csv_pro_prihlaseni):
            prihlasovaci_udaje[klic] = hodnota
        return prihlasovaci_udaje

    def over_prihlasovaci_udaje(udaje):
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
    
    def najdi_linky_obci():
        rozdelene_html = bs(get(sys.argv[1]).text, features="html.parser")
        a_tagy = rozdelene_html.find_all("a")
        base_url = "https://www.volby.cz/pls/ps2017nss/"
        linky_obci = []
        linky = []
        for a_tag in a_tagy:
            if "ps311" in str(a_tag):
                linky_obci.append(base_url + a_tag.attrs.get("href"))
        for link in linky_obci:
            if link in linky:
                continue
            else:
                linky.append(link)
        return linky
    
    def najdi_code_a_location():
        rozdelene_html = bs(get(sys.argv[1]).text, features="html.parser")
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
    
    def najdi_volebni_ucast(linky_obci):
        volebni_ucast = []
        for link in linky_obci:
            url_obce = link
            rozdelene_html = bs(get(url_obce).text, features="html.parser")
            vsechny_table = rozdelene_html.find_all("table", {"class":"table"})
            vsechny_tr = vsechny_table[0].find_all("tr")
            td_na_radku = vsechny_tr[2].find_all("td")
            volebni_ucast_obce = []
            volebni_ucast_obce.append(td_na_radku[3].text)
            volebni_ucast_obce.append(td_na_radku[4].text)
            volebni_ucast_obce.append(td_na_radku[7].text)
            volebni_ucast.append(volebni_ucast_obce)
        return volebni_ucast
    
    def najdi_hlasy_stran(linky_obci):
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

    def spoj_data_obci(code_a_location_obci, volebni_ucast_obci, hlasy_stran_obci):
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

    def prirad_klice_k_datum(klice_dat, data):
        data_obci = []
        for obec in data:
            data_obce = {}
            for klic, hodnota in zip(klice_dat, obec):
                data_obce[klic] = hodnota
            data_obci.append(data_obce)
        return data_obci
    
    def zapis_data_do_csv(data_csv, klice_csv):
        soubor_csv = open(f"{sys.argv[2]}", mode="w", newline="", encoding="utf-8-sig")
        zahlavi = klice_csv
        zapisovac = csv.DictWriter(soubor_csv, fieldnames=zahlavi)
        zapisovac.writeheader()
        zapisovac.writerows(data_csv)
        soubor_csv.close()

    def uloz_volebni_data():
        linky = najdi_linky_obci()
        code_a_location = najdi_code_a_location()
        volebni_ucast = najdi_volebni_ucast(linky)
        hlasy_stran = najdi_hlasy_stran(linky)[0]
        klice = najdi_hlasy_stran(linky)[1]
        data_list = spoj_data_obci(code_a_location, volebni_ucast, hlasy_stran)
        data = prirad_klice_k_datum(klice, data_list)
        zapis_data_do_csv(data, klice)

    print("Ověřuji systémové argumenty...")
    okresy = najdi_uzemni_celky()
    jmena_okresu_csv = vytvor_jmena_csv(okresy)
    jmena_okresu_csv_bez_diakritiky = odstran_diakritiku(jmena_okresu_csv)
    prihlasovaci_udaje = vytvor_prihlasovaci_udaje(okresy, jmena_okresu_csv_bez_diakritiky)
    spravne_udaje = over_prihlasovaci_udaje(prihlasovaci_udaje)
    
    if spravne_udaje:
        print("Ukládám data.")
        uloz_volebni_data()
    else:
        print("Nesprávné systémové argumenty. Vlož správné systémové argumenty.")

vysledky_hlasovani()



#python project_3.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=1&xnumnuts=1100" "vysledky_praha.csv"

#python project_3.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101" "vysledky_benesov.csv"

#python project_3.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2112" "vysledky_rakovnik.csv"

#python project_3.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=14&xnumnuts=8103" "vysledky_karvina.csv"

ZKRÁCENÍ KÓDU
ZKRÁCENÍ KÓDU
ZKRÁCENÍ KÓDU
ZKRÁCENÍ KÓDU
ZKRÁCENÍ KÓDU
ZKRÁCENÍ KÓDU


import sys
import csv

from requests import get
from bs4 import BeautifulSoup as bs

def vysledky_hlasovani():
    base_url = "https://www.volby.cz/pls/ps2017nss/"
    url = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"

    def najdi_uzemni_celky():
        rozdelene_html = bs(get(url).text, features="html.parser")
        vsechny_celky = rozdelene_html.find_all("a")
        celky = [a_tag.attrs.get("href", "chybí odkaz") if "xnumnuts" in str(a_tag) for a_tag in celky]
        okresy = [base_url + item if "ps32" in item for item in celky]
        return okresy

    def vytvor_jmena_csv(okresy_url):
        vsechny_okresy = ["vysledky_praha.csv"]
        for item in okresy_url:
            rozdelene_html = bs(get(item).text, features="html.parser")
            vsechny_h3 = rozdelene_html.find_all("h3")
            for tag in vsechny_h3:
                if "Okres: " in str(tag):
                    vsechny_okresy.append(f"vysledky_{str(tag)[12:-6].lower()}.csv")
        return vsechny_okresy    

    def odstran_diakritiku(jmena_okresu_csv):
        bez_diakritiky = []
        odstranit_diakritiku = {"á": "a", "č": "c", "ď": "d", "é": "e", "ě": "e", "í": "i", "ň": "n", "ó": "o", "ř": "r", "š": "s", "ť": "t", "ú": "u", "ů": "u", "ý": "y", "ž": "z",}
        for item in jmena_okresu_csv:
            csv = "".join(
            for char in item:
                if char in odstranit_diakritiku:
                    csv += odstranit_diakritiku[char]
                else:
                    csv += char
            bez_diakritiky.append(csv)
        return bez_diakritiky
    
    def vytvor_prihlasovaci_udaje(okresy_pro_prihlaseni, csv_pro_prihlaseni):
        prihlasovaci_udaje = {prihlasovaci_udaje[klic] = hodnota for klic, hodnota in zip(okresy_pro_prihlaseni, csv_pro_prihlaseni)}
        return prihlasovaci_udaje

    def over_prihlasovaci_udaje(udaje):
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
    
    def najdi_linky_obci():
        rozdelene_html = bs(get(sys.argv[1]).text, features="html.parser")
        a_tagy = rozdelene_html.find_all("a")
        base_url = "https://www.volby.cz/pls/ps2017nss/"
        linky_obci = [base_url + a_tag.attrs.get("href") if "ps311" in str(a_tag) for a_tag in a_tagy]
        linky = [continue if link in linky else link for link in linky_obci]    
        return linky
    
    def najdi_code_a_location():
        rozdelene_html = bs(get(sys.argv[1]).text, features="html.parser")
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
    
    def najdi_volebni_ucast(linky_obci):
        volebni_ucast = []
        for link in linky_obci:
            url_obce = link
            rozdelene_html = bs(get(url_obce).text, features="html.parser")
            vsechny_table = rozdelene_html.find_all("table", {"class":"table"})
            vsechny_tr = vsechny_table[0].find_all("tr")
            td_na_radku = vsechny_tr[2].find_all("td")
            volebni_ucast_obce = []
            volebni_ucast_obce.append(td_na_radku[3].text)
            volebni_ucast_obce.append(td_na_radku[4].text)
            volebni_ucast_obce.append(td_na_radku[7].text)
            volebni_ucast.append(volebni_ucast_obce)
        return volebni_ucast
    
    def najdi_hlasy_stran(linky_obci):
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

    def spoj_data_obci(code_a_location_obci, volebni_ucast_obci, hlasy_stran_obci):
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

    def prirad_klice_k_datum(klice_dat, data):
        data_obci = []
        for obec in data:
            data_obce = {data_obce[klic] = hodnota for klic, hodnota in zip(klice_dat, obec)}
            data_obci.append(data_obce)
        return data_obci
    
    def zapis_data_do_csv(data_csv, klice_csv):
        soubor_csv = open(f"{sys.argv[2]}", mode="w", newline="", encoding="utf-8-sig")
        zahlavi = klice_csv
        zapisovac = csv.DictWriter(soubor_csv, fieldnames=zahlavi)
        zapisovac.writeheader()
        zapisovac.writerows(data_csv)
        soubor_csv.close()

    def uloz_volebni_data():
        linky = najdi_linky_obci()
        code_a_location = najdi_code_a_location()
        volebni_ucast = najdi_volebni_ucast(linky)
        hlasy_stran = najdi_hlasy_stran(linky)[0]
        klice = najdi_hlasy_stran(linky)[1]
        data_list = spoj_data_obci(code_a_location, volebni_ucast, hlasy_stran)
        data = prirad_klice_k_datum(klice, data_list)
        zapis_data_do_csv(data, klice)

    print("Ověřuji systémové argumenty...")
    okresy = najdi_uzemni_celky()
    jmena_okresu_csv = vytvor_jmena_csv(okresy)
    jmena_okresu_csv_bez_diakritiky = odstran_diakritiku(jmena_okresu_csv)
    prihlasovaci_udaje = vytvor_prihlasovaci_udaje(okresy, jmena_okresu_csv_bez_diakritiky)
    spravne_udaje = over_prihlasovaci_udaje(prihlasovaci_udaje)
    
    if spravne_udaje:
        print("Ukládám data.")
        uloz_volebni_data()
    else:
        print("Nesprávné systémové argumenty. Vlož správné systémové argumenty.")

vysledky_hlasovani()


