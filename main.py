from requests import get
from bs4 import BeautifulSoup as bs

def vysledky_hlasovani()
    base_url = "https://www.volby.cz/pls/ps2017nss/"
    url = "https://www.volby.cz/pls/ps2017nss/ps3?xjazyk=CZ"

    def najdi_uzemni_celky():
        rozdelene_html = rozdel_html(url)
    
    def rozdel_html(odkaz):
        return bs(get(odkaz).text, features="html.parser")

    vsechny_uzemni_celky = rozdelene_html.find_all("a")

    uzemni_celky = list()
    for a_tag in vsechny_uzemni_celky:
        if "xnumnuts" in str(a_tag):
            uzemni_celky.append(a_tag.attrs.get("href", "chybí odkaz"))

    vsechny_uzemni_celky = list()
    for item in uzemni_celky:
        if "ps32" in item:
            vsechny_uzemni_celky.append(base_url + item)

if __name__ == "__main__":
    vysledky_hlasovani()
