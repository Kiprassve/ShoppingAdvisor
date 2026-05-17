# 🛒 Shopping Advisor / PriceScraper

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Framework-black?style=for-the-badge&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-PostGIS-blue?style=for-the-badge&logo=postgresql)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react&logoColor=black)

## 📝 Aprašas
Kuriama programų sistema skirta automatizuotam maisto produktų duomenų rinkimui iš trijų didžiausių Lietuvos mažmeninės prekybos tinklų – **IKI**, **Rimi** ir **Maxima**. 

Duomenų rinkimo modulis naudoja žiniatinklio turinio gavybos (angl. *web scraping*) metodus produktų pavadinimams, kainoms ir mitybinei informacijai (baltymams, angliavandeniams, riebalams, kalorijoms ir t.t.) gauti iš kiekvieno tinklo oficialios interneto svetainės. 

Surinkti duomenys integruojami į interaktyvią, žemėlapiu grįstą vartotojo sąsają, kurioje naudotojas nurodo paieškos centrą ir spindulį. Sistema automatiškai identifikuoja visas parduotuves nustatytame geografiniame spindulyje, naudodamasi **OpenStreetMap** duomenų baze, ir pateikia jose parduodamų produktų sąrašą. Rezultatus galima filtruoti ir rūšiuoti pagal pasirinktas mitybines vertybes – baltymų ar angliavandenių kiekį – suteikiant galimybę priimti informuotus pirkimo sprendimus.

---

## 👥 Komandos nariai
* Pijus Šventoraitis
* Kipras Šventoraitis
* Vilius Gailiūnas

---

## 🛠️ Techninė užduotis
Šios programų sistemos tikslas – automatizuoti maisto produktų duomenų rinkimą iš trijų didžiausių Lietuvos prekybos tinklų ir integruoti juos į interaktyvią, žemėlapiu grįstą vartotojo sąsają.

### Funkciniai reikalavimai:
1. **Duomenų rinkimas:** Automatizuotas produktų pavadinimų, kainų ir pilnos mitybinės informacijos (baltymų, angliavandenių, riebalų, kalorijų ir t.t.) išgavimas iš oficialių el. parduotuvių svetainių.
2. **Geografinė paieška:** Naudotojas sąsajoje nurodo paieškos centrą ir spindulį. Sistema pagal **OpenStreetMap** duomenų bazę identifikuoja visas prekybos vietas šiame spindulyje ir pateikia jose parduodamų produktų sąrašą.
3. **Duomenų filtravimas ir rūšiavimas:** Galimybė filtruoti ir rūšiuoti maisto produktus pagal pasirinktas mitybines vertes (baltymų, angliavandenių kiekį) ar kainą, leidžiant priimti informuotus pirkimo sprendimus.

---

## 🏗️ Architektūra
Projektas realizuotas naudojant **Flask** (Python) backend serverį, **React.js** frontendą ir **PostgreSQL** duomenų bazę su **PostGIS** plėtiniu, užtikrinančiu efektyvias geografines užklausas.

---

### 📂 Komponentai ir failų struktūra

* **`app.py` (Flask serveris):**
    * `/api/scrape`: Apdoroja produktų užklausas, filtruoja duomenis pagal pasirinktus tinklus (`?rimi=true&iki=true`) ir grąžina iki 100 naujausių prekių su suderintais logotipais.
    * `/api/stores`: Priima koordinates (`lat`, `lon`) bei spindulį (`radius`). Naudoja PostGIS funkcijas (`ST_DWithin`, `ST_Transform`) realaus laiko parduotuvių paieškai OSM taškuose ir poligonuose.
* **`Crawler.py` (Duomenų rinkiklis):**
    * **Rimi:** Vykdo tradicinę žiniatinklio gavybą (angl. *HTML scraping*) naudojant *BeautifulSoup* ir reguliariąsias išraiškas (RegEx), pasiekia paslėptus kodo skriptus mitybinėms vertėms gauti.
    * **IKI:** Siunčia tiesiogines POST užklausas į LastMile API paslaugą, automatiškai surinkdamas kategorijų bei subkategorijų ID identifikatorius.
    * **Automatizacija:** Paleidimo metu atlieka pirminį duomenų atnaujinimą, o vėliau veikia cikle ir kasdien nustatytu laiku (pvz., 06:30) automatiškai atnaujina duomenis. Atlieka atminties stebėjimą per `tracemalloc`.
* **`database.py`:** Atsakingas už prisijungimą prie PostgreSQL duomenų bazės per `psycopg2` tvarkyklę. Sukuria prekių lentelę (`products`), prieš įrašant naujus duomenis automatiškai išvalo senus tos parduotuvės įrašus, konvertuoja kainas ir validuoja mitybinių verčių tipus.
* **`Product.py`:** Duomenų modelio klasė, aprašanti prekės struktūrą (pavadinimą, kainas, svorį, mitybines vertes bei nuorodas).

---

## 📖 Trumpa naudotojo dokumentacija

Ši dokumentacija skirta greitam sistemos serverio dalies (Backend) paleidimui lokaliame kompiuteryje bei susipažinimui su pateikiamais API galiniais taškais (Endpoints).

---

### ⚙️ 1. Aplinkos konfigūracija (`.env`)

Prieš paleidžiant serverį, pagrindiniame projekto aplanke (`/PriceScraper`) būtina sukurti failą pavadinimu **`.env`** ir jame nurodyti prisijungimo prie PostgreSQL (su PostGIS plėtiniu) duomenis:

```env
DB_HOST=localhost
DB_NAME=map_demo
DB_USER=postgres
DB_PASS=tavo_duomenu_bazes_slaptazodis
DB_PORT=5432
