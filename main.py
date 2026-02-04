from requests import get
import sys
from bs4 import BeautifulSoup as bs


def vysledky_hlasovani():
    base_url = "https://www.volby.cz/pls/ps2017nss/"
    url = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"

    def rozdel_html(odkaz):
        return bs(get(odkaz).text, features="html.parser")
    
    def najdi_celky(celky):
        uzemni_celky = list()
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
        odstranit_diakritiku = {"á": "a",
                                "č": "c",
                                "ď": "d",
                                "é": "e",
                                "ě": "e",
                                "í": "i",
                                "ň": "n",
                                "ó": "o",
                                "ř": "r",
                                "š": "s",
                                "ť": "t",
                                "ú": "u",
                                "ů": "u",
                                "ý": "y",
                                "ž": "z",
                                }
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
        url = sys.argv[1]
        rozdelene_html = bs(get(url).text, features="html.parser")
        a_tagy = rozdelene_html.find_all("a")
        base_url = "https://www.volby.cz/pls/ps2017nss/"
        linky_obci = list()
        for a_tag in a_tagy:
            if "ps311" in str(a_tag):
                linky_obci.append(base_url + a_tag.attrs.get("href"))
        return linky_obci
    
    def najdi_code_a_location():
        url_okresu = sys.argv[1]
        rozdelene_html = bs(get(url_okresu).text, features="html.parser")
        vsechny_table = rozdelene_html.find_all("table", {"class": "table"})
        code_a_location_tabulek = []
        for table in vsechny_table:
            vsechny_tr = table.find_all("tr")
            for tr in vsechny_tr[2:]:
                code_a_location_radku = dict()
                td_na_radku = tr.find_all("td")
                if td_na_radku[0].text != "-":
                    code_a_location_radku["code"] = td_na_radku[0].text
                if td_na_radku[1].text != "-":
                    code_a_location_radku["location"] = td_na_radku[1].text
                code_a_location_radku_list = [code_a_location_radku]
                code_a_location_tabulek.append(code_a_location_radku_list)
        return code_a_location_tabulek
    
    def najdi_volebni_ucast(linky_obci):
        volebni_ucast = []
        for link in linky_obci:
            url_obce = link
            rozdelene_html = bs(get(url_obce).text, features="html.parser")
            vsechny_table = rozdelene_html.find_all("table", {"class":"table"})
            vsechny_tr = vsechny_table[0].find_all("tr")
            td_na_radku = vsechny_tr[2].find_all("td")
            volebni_ucast_obce = dict()
            volebni_ucast_obce["registered"] = str(td_na_radku[3].text)
            volebni_ucast_obce["envelopes"] = str(td_na_radku[4].text)
            volebni_ucast_obce["valid"] = str(td_na_radku[7].text)
            volebni_ucast_obce_list = [volebni_ucast_obce]
            volebni_ucast.append(volebni_ucast_obce_list)
        return volebni_ucast
    
    def najdi_hlasy_stran(linky_obci):
        hlasy_stran = []
        for link in linky_obci:
            url_obce = link
            rozdelene_html = bs(get(url_obce).text, features="html.parser")
            vsechny_table = rozdelene_html.find_all("table", {"class":"table"})
            hlasy_stran_obci = dict()
            tabulka_s_hlasy = vsechny_table[1:]
            for table in tabulka_s_hlasy:
                vsechny_tr = table.find_all("tr")
                for tr in vsechny_tr[2:]:
                    td_na_radku = tr.find_all("td")
                    if td_na_radku[1].text != "-":
                        hlasy_stran_obci[td_na_radku[1].text] = td_na_radku[2].text
            hlasy_stran_obci_list = [hlasy_stran_obci]
            hlasy_stran.append(hlasy_stran_obci_list)
        return hlasy_stran
    
    def spoj_data(code_a_location_obci, volebni_ucast_obci, hlasy_stran_obci):
        data = []
        for i in range(len(code_a_location_obci)):
            data_obce = dict()
            data_obce.update(code_a_location_obci[i])
            data_obce.update(volebni_ucast_obci[i])
            data_obce.update(hlasy_stran_obci[i])
            data.append(data_obce)
        return data

    def uloz_volebni_data():
        linky = najdi_linky_obci()
        code_a_location = najdi_code_a_location()
        volebni_ucast = najdi_volebni_ucast(linky)
        hlasy_stran = najdi_hlasy_stran(linky)
        print(hlasy_stran)
        data = spoj_data(code_a_location, volebni_ucast, hlasy_stran)
        print(data)

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
#https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=2&xobec=529303&xvyber=2101 - obec Benešov







from requests import get
import sys
from bs4 import BeautifulSoup as bs

#url = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101"
#base_url = "https://www.volby.cz/pls/ps2017nss/"

#rozdelene_html = bs(get(url).text, features="html.parser")
#a_tagy = rozdelene_html.find_all("a")

#cisla_obci = list()

#for a_tag in a_tagy:
#    if "ps311" in str(a_tag):
#        cisla_obci.append(a_tag.attrs.get("href", "chybí odkaz"))

#for neco in cisla_obci:
#    print(base_url + neco)


url_obce = "https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=3&xnumnuts=3104"

#rozdelene_html = bs(get(url_obce).text, features="html.parser")
#tag = rozdelene_html.find_all("table", {"class": "table"})
#vsechny_tr = tag[0].find_all("tr")
#td_na_radku = vsechny_tr[2].find_all("td")
#print(td_na_radku[0].text)

#print(rozdelene_html)


#https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101 - okres Benešov
#https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=2&xobec=529303&xvyber=2101 - obec Benešov

#url_okresu = "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2103"
#rozdelene_html = bs(get(url_okresu).text, features="html.parser")
#vsechny_table = rozdelene_html.find_all("table", {"class": "table"})
#cisla_a_obce = []
#for table in vsechny_table:
#    vsechny_tr = table.find_all("tr")
#    for tr in vsechny_tr[2:]:
#        td_na_radku = tr.find_all("td")
#        if td_na_radku[0].text != "-":
#            cisla_a_obce.append(td_na_radku[0].text)
#        if td_na_radku[1].text != "-":
#            cisla_a_obce.append(td_na_radku[1].text)

#print(cisla_a_obce)


url_obce = "https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=1&xobec=500054&xvyber=1100"
rozdelene_html = bs(get(url_obce).text, features="html.parser")
vsechny_table = rozdelene_html.find_all("table", {"class":"table"})
#vsechny_tr = vsechny_table[0].find_all("tr")
#td_na_radku = vsechny_tr[2].find_all("td")
volebni_ucast = dict()
#volebni_ucast["registered"] = str(td_na_radku[3].text)
#volebni_ucast["envelopes"] = str(td_na_radku[4].text)
#volebni_ucast["valid"] = str(td_na_radku[7].text)

#text = "7\\xa258"
#if "\\xa" in text:
#    novy_text = text.replace("\\xa", "")

#tabulka_s_hlasy = vsechny_table[1:]
#for table in tabulka_s_hlasy:
#    vsechny_tr = table.find_all("tr")
#    for tr in vsechny_tr[2:]:
#        td_na_radku = tr.find_all("td")
#        if td_na_radku[1].text != "-":
#            volebni_ucast[td_na_radku[1].text] = td_na_radku[2].text

#print(volebni_ucast)

code_a_location_obci = [[{"code": "123", "location": "abc"}], [{"code": "345", "location": "def"}]]
volebni_ucast_obci = [[{"registered": "123", "envelopes": "123", "valid": "123"}], [{"registered": "456", "envelopes": "456", "valid": "456"}]]
hlasy_stran_obci = [[{"ABC": "123", "DEF": "456", "GHI": "789"}], [{"JKL": "123", "MNO": "456", "PQR": "789"}]]


data = []
for i in range(1):
    data_obce = []
    for kod, ucast, hlasy in zip(code_a_location_obci[i], volebni_ucast_obci[i], hlasy_stran_obci[i]):
        data_obce.append(kod)
        data_obce.append(ucast)
        data_obce.append(hlasy)
    data.append(data_obce)
print(data)
