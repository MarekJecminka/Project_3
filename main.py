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
        vsechna_mesta = ["vysledky_praha.csv"]
        for item in okresy_url:
            rozdelene_html = bs(get(item).text, features="html.parser")
            vsechny_h3 = rozdelene_html.find_all("h3")
            for tag in vsechny_h3:
                if "Okres: " in str(tag):
                    vsechna_mesta.append(f"vysledky_{str(tag)[12:-6].lower()}.csv")
        return vsechna_mesta    

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
    
    print("Ověřuji systémové argumenty...")
    okresy = najdi_uzemni_celky()
    jmena_okresu_csv = vytvor_jmena_csv(okresy)
    jmena_okresu_csv_bez_diakritiky = odstran_diakritiku(jmena_okresu_csv)
    prihlasovaci_udaje = vytvor_prihlasovaci_udaje(okresy, jmena_okresu_csv_bez_diakritiky)
    spravne_udaje = over_prihlasovaci_udaje(prihlasovaci_udaje)
    
    if spravne_udaje == True:
        print("Ukládám data.")
    else:
        print("Nesprávné systémové argumenty. Vlož správné systémové argumenty.")

vysledky_hlasovani()


#Nefunguje případ, kdy systemový argument 1 je prázdný - OPRAVIT!!

#python a.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=1&xnumnuts=1100" "vysledky_praha.csv"

#https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101 - okres Benešov
#https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj=2&xobec=529303&xvyber=2101 - obec Benešov
