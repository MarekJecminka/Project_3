# Project 3: Elections Scraper (Výsledky voleb 2017)

Tento projekt slouží ke stahování a zpracování výsledků voleb do Poslanecké sněmovny ČR z roku 2017 pro vybraný územní celek přímo z webu [volby.cz](https://www.volby.cz/).

## Instalace knihoven

Pro správný chod skriptu je nutné mít nainstalované knihovny ze souboru `requirements.txt` a rovněž je nutné vytvořit a aktivovat virtuální prostředí:

```bash
# Vytvoření virtuálního prostředí
python -m venv venv

# Aktivace (Windows)
.\venv\Scripts\activate

# Aktivace (Linux / macOS)
source venv/bin/activate

# Instalace potřebných knihoven
pip install -r requirements.txt

# Spuštění projektu
Skript se spouští z příkazové řádky a vyžaduje přesně 2 argumenty:

  1) Odkaz na územní celek (URL v uvozovkách z webu volby.cz).
  2) Název výstupního .csv souboru, do kterého se výsledky uloží.

# Formát spuštění

Bash
python main.py "<URL_UZEMNIHO_CELKU>" "<NAZEV_VYSTUPNIHO_SOUBORU.csv>"

# Ukázka použití

Příklad pro stahování výsledků pro územní celek Prostějov:

Bash
python main.py "[https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103](https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103)" "vysledky_prostejov.csv"

Průběh a výstup:
  1) Skript ověří platnost zadaných argumentů,
  2) Stáhne data o jednotlivých obcích daného okresu (kód, název, voliči, obálky, platné hlasy a hlasy pro jednotlivé strany),
  3) Výsledek uloží do souboru vysledky_prostejov.csv.
