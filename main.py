from requests import get
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

    def vytvor_jmena_csv(okresy):
        vsechna_mesta = ["vysledky_praha.csv"]
        for item in okresy:
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
                                "ý": "y",
                                "ž": "z",
                                }
        for item in jmena_okresu_csv:
            okres_csv = list()
            for char in item:
                csv = ""
                if char in odstranit_diakritiku:
                    csv += odstranit_diakritiku[char]
                else:
                    csv += char
                okres_csv.append(csv)
            bez_diakritiky.append(okres_csv)
        return bez_diakritiky

    okresy = najdi_uzemni_celky()
    jmena_okresu_csv = vytvor_jmena_csv(okresy)
    jmena_okresu_csv_bez_diakritiky = odstran_diakritiku(jmena_okresu_csv)
    #print(okresy)
    print(jmena_okresu_csv_bez_diakritiky)


    


if __name__ == "__main__":
    vysledky_hlasovani()




"""
    def vytvor_jmena_csv(okresy):
        vsechna_mesta = list()
        for item in okresy:
            rozdelene_html = bs(get(item).text, features="html.parser")
            vsechny_h3 = rozdelene_html.find_all("h3")
            for tag in vsechny_h3:
                if "Okres: " in str(tag):
                    vsechna_mesta.append(f"vysledky_{str(tag)[12:-6].lower()}.csv")
        return vsechna_mesta
"""
