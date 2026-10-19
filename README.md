# 🛒 Shopping Advisor / PriceScraper

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Framework-black?style=for-the-badge&logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-PostGIS-blue?style=for-the-badge&logo=postgresql)

## 📝 Aprašas
Kuriama programų sistema skirta automatizuotam maisto produktų duomenų rinkimui iš trijų didžiausių Lietuvos mažmeninės prekybos tinklų – **IKI**, **Rimi** ir **Maxima**. 

Duomenų rinkimo modulis naudoja *web scraping* metodus produktų pavadinimams, kainoms ir mitybinei informacijai (baltymams, angliavandeniams, riebalams, kalorijoms ir t.t.) gauti iš kiekvieno tinklo oficialios interneto svetainės. 

Surinkti duomenys integruojami į interaktyvią, žemėlapiu grįstą vartotojo sąsają, kurioje naudotojas nurodo paieškos centrą ir spindulį. Sistema automatiškai identifikuoja visas parduotuves nustatytame geografiniame spindulyje, naudodamasi **OpenStreetMap** duomenų baze, ir pateikia jose parduodamų produktų sąrašą. Rezultatus galima filtruoti ir rūšiuoti pagal pasirinktas mitybines vertybes – baltymų ar angliavandenių kiekį – suteikiant galimybę priimti informuotus pirkimo sprendimus.

---

## 👥 Komandos nariai
* Pijus Šventoraitis (Crawler)
* Kipras Šventoraitis(Maps/Frontedn)
* Vilius Gailiūnas (Frontend/Backend)

---

## 🛠️ Techninė užduotis
Šios programų sistemos tikslas – automatizuoti maisto produktų duomenų rinkimą iš trijų didžiausių Lietuvos prekybos tinklų ir integruoti juos į interaktyvią, žemėlapiu grįstą vartotojo sąsają.

### Funkciniai reikalavimai:
1. **Duomenų rinkimas:** Automatizuotas produktų pavadinimų, kainų ir pilnos mitybinės informacijos (baltymų, angliavandenių, riebalų, kalorijų ir t.t.) išgavimas iš oficialių el. parduotuvių svetainių.
2. **Geografinė paieška:** Naudotojas sąsajoje nurodo paieškos centrą ir spindulį. Sistema pagal **OpenStreetMap** duomenų bazę identifikuoja visas prekybos vietas šiame spindulyje ir pateikia jose parduodamų produktų sąrašą.
3. **Duomenų filtravimas ir rūšiavimas:** Galimybė filtruoti ir rūšiuoti maisto produktus pagal pasirinktas mitybines vertes (baltymų, angliavandenių kiekį) ar kainą, leidžiant priimti informuotus pirkimo sprendimus.

---

## 🏗️ Architektūra
Projektas realizuotas naudojant **Flask** (Python) backend serverį ir **PostgreSQL** duomenų bazę su **PostGIS** plėtiniu, užtikrinančiu efektyvias geografines užklausas.

---

### 📂 Komponentai ir failų struktūra

* **`app.py` (Flask serveris):**
    * `/api/scrape`: Apdoroja produktų užklausas, filtruoja duomenis pagal pasirinktus tinklus (`?rimi=true&iki=true`) ir grąžina iki 100 naujausių prekių su suderintais logotipais.
    * `/api/stores`: Priima koordinates (`lat`, `lon`) bei spindulį (`radius`). Naudoja PostGIS funkcijas (`ST_DWithin`, `ST_Transform`) realaus laiko parduotuvių paieškai OSM taškuose ir poligonuose.
- **`Crawler.py` (Duomenų rinkiklis):**
    * **Rimi:** Vykdo tradicinę žiniatinklio gavybą (angl. *HTML scraping*) naudojant *BeautifulSoup* ir reguliariąsias išraiškas (RegEx), pasiekia paslėptus kodo skriptus mitybinėms vertėms gauti.
    * **IKI:** Siunčia tiesiogines POST užklausas į LastMile API paslaugą, automatiškai surinkdamas kategorijų bei subkategorijų ID identifikatorius.
    * **Maxima (Barbora):** Iteruoja per prekių kategorijų puslapius, naudodamas reguliariąsias išraiškas (RegEx) paslėptų JSON objektų (`window.b_productList` ir `window.product`) išgavimui tiesiai iš HTML kodo. Turi integruotus saugiklius apsaugai nuo begalinių ciklų bei dublikatų, o prekės svorį/tūrį ir matavimo vienetus išskaito tiesiai iš pavadinimo teksto.
    * **Automatizacija:** Paleidimo metu atlieka pirminį duomenų atnaujinimą, o vėliau veikia cikle ir kasdien nustatytu laiku (pvz., 06:30) automatiškai atnaujina duomenis. Atlieka atminties stebėjimą per `tracemalloc`. Užklausų srautas valdomas naudojant `time.sleep()`, siekiant neapkrauti serverių.
* **`database.py`:** Atsakingas už prisijungimą prie PostgreSQL duomenų bazės per `psycopg2` tvarkyklę. Sukuria prekių lentelę (`products`), prieš įrašant naujus duomenis automatiškai išvalo senus tos parduotuvės įrašus, konvertuoja kainas ir validuoja mitybinių verčių tipus.
* **`Product.py`:** Duomenų modelio klasė, aprašanti prekės struktūrą (pavadinimą, kainas, svorį, mitybines vertes bei nuorodas).

---

## 📖 Trumpa naudotojo dokumentacija

### ⚙️ 1. Aplinkos konfigūracija (`.env`)

Prieš paleidžiant serverį, pagrindiniame projekto aplanke (`/PriceScraper`) būtina sukurti failą pavadinimu **`.env`** ir jame nurodyti prisijungimo prie PostgreSQL (su PostGIS plėtiniu) duomenis:

```env
DB_HOST=localhost
DB_NAME=map_demo
DB_USER=postgres
DB_PASS=tavo_duomenu_bazes_slaptazodis
DB_PORT=5432
```
### 🚀 2. Projekto paleidimas naudojant Docker

Jei jūsų kompiuteryje įdiegtas **Docker**, visą sistemą (Flask serverį ir PostgreSQL su PostGIS duomenų baze) galite pakelti viena komanda pagrindiniame aplanke:

```bash
docker-compose up --build
```
Ši komanda automatiškai atsiųs reikiamus atvaizdus, sukonfigūruos tinklą, paleis duomenų bazę ir pakels Flask serverį adresu: http://localhost:5000.

### 💻 3. Naudojimasis sistema per sąsają (Frontend)

Atsidarykite naršyklę ir eikite adresu http://localhost:5000 (arba jūsų nurodytu Flask adresu):

1. **Pažymėkite savo vietą žemėlapyje:**
    * Spustelkite kairiuoju pelės klavišu du kartus bet kurioje interaktyvaus žemėlapio vietoje, kad nustatytumėte savo paieškos centrą.
2. **Nustatykite paieškos spindulį:**
    * Įveskite norimą atstumą metrais. Pagal **OpenStreetMap** duomenis sistema automatiškai suras visas šiame apskritime esančias prekybos vietas.
3. **Filtruokite ir rūšiuokite prekes:**
    * Skydelyje pasirinkite norimą rikiavimo kriterijų. Galite akimirksniu surikiuoti visus aplinkinių parduotuvių produktus pagal:
        * **Kainą** (ieškant pigiausių alternatyvų).
        * **Mitybinę vertę** (rūšiuojant pagal didžiausią *baltymų* arba mažiausią *angliavandenių* bei *riebalų* kiekį 100-ame gramų).
