\# Shopping Advisor



\# Aprašas

Kuriama programų sistema skirta automatizuotam maisto produktų duomenų rinkimui iš trijų didžiausių Lietuvos mažmeninės prekybos tinklų – IKI, Rimi ir Maxima. 

Duomenų rinkimo modulis naudoja žiniatinklio turinio gavybos (angl. web scraping) metodus produktų pavadinimams, kainoms ir mitybinei informacijai (baltymams, angliavandenžams, riebalams, kalorijoms ir t.t.)

gauti iš kiekvieno tinklo oficialios interneto svetainės. 

Surinkti duomenys integruojami į interaktyvią, žemėlapiu grįstą vartotojo sąsają, kurioje naudotojas nurodo paieškos centrą ir spindulį.

Sistema automatiškai identifikuoja visas parduotuves nustatytame geografiniame spindulyje, naudodamasi OpenStreetMap duomenų baze, ir pateikia jose parduodamų produktų sąrašą.

Rezultatus galima filtruoti ir rūšiuoti pagal pasirinktas mitybines vertybes – baltymų ar angliavandenžų kiekį – suteikiant galimybę priimti informuotus pirkimo sprendimus.



\## Komandos nariai

\* Pijus Šventoraitis

\* Kipras Šventoraitis

\* Vilius Gailiūnas



\## Techninė užduotis

Šios programų sistemos tikslas – automatizuoti maisto produktų duomenų rinkimą iš trijų didžiausių Lietuvos prekybos tinklų (\*\*IKI\*\*, \*\*Rimi\*\* ir \*\*Maxima\*\*) bei integruoti juos į interaktyvią, žemėlapiu grįstą vartotojo sąsają\[cite: 1].



\### Funkciniai reikalavimai:

1\. \*\*Duomenų rinkimas:\*\* Automatizuotas produktų pavadinimų, kainų ir pilnos mitybinės informacijos (baltymų, angliavandenių, riebalų, kalorijų ir t.t.) išgavimas iš oficialių el. parduotuvių svetainių\[cite: 1].

2\. \*\*Geografinė paieška:\*\* Naudotojas sąsajoje nurodo paieškos centrą ir spindulį\[cite: 1]. Sistema pagal \*\*OpenStreetMap\*\* duomenų bazę identifikuoja visas prekybos vietas šiame spindulyje ir pateikia jose parduodamų produktų sąrašą\[cite: 1].

3\. \*\*Duomenų filtravimas ir rūšiavimas:\*\* Galimybė filtruoti ir rūšiuoti maisto produktus pagal pasirinktas mitybines vertes (baltymų, angliavandenių kiekį) ar kainą, leidžiant priimti informuotus pirkimo sprendimus\[cite: 1].



\---



\## Architektūra

\## Architektūra

Projektas realizuotas naudojant \*\*Flask\*\* (Python) backend serverį, \*\*React.js\*\* frontendą ir \*\*PostgreSQL\*\* duomenų bazę su \*\*PostGIS\*\* plėtiniu, užtikrinančiu efektyvias geografines užklausas.



\[ Duomenų rinkimo modulis (Crawler.py) ]

│

▼

\[ PostgreSQL + PostGIS (DB) ] <─── ( planet\_osm\_point / polygon )

▲

│ (psycopg2 užklausos)

▼

\[ Flask API (app.py) ]

▲

│ (REST / JSON)

▼

\[ Frontend (Vartotojas) ]



\### Komponentai ir failų struktūra:

\* \*\*`app.py` (Flask serveris):\*\* \* `/api/scrape`: Apdoroja produktų užklausas, filtruoja pagal pasirinktus tinklus (`?rimi=true\&iki=true`) ir grąžina iki 100 naujausių prekių su suderintais logotipais.

&#x20; \* `/api/stores`: Priima koordinates (`lat`, `lon`) bei spindulį (`radius`). Naudoja PostGIS funkcijas (`ST\_DWithin`, `ST\_Transform`) realaus laiko parduotuvių paieškai OSM taškuose ir poligonuose.

\* \*\*`Crawler.py` (Duomenų rinkiklis):\*\* \* \*\*Rimi:\*\* Vykdo tradicinę žiniatinklio gavybą (angl. \*HTML scraping\*) naudojant \*BeautifulSoup\* ir reguliariąsias išraiškas (RegEx), pasiekia paslėptus kodo skriptus mitybinėms vertėms gauti.

&#x20; \* \*\*IKI:\*\* Siunčia tiesiogines POST užklausas į LastMile API paslaugą, automatiškai surinkdamas kategorijų bei subkategorijų ID identifikatorius.

&#x20; \* \*\*Automatizacija:\*\* Paleidimo metu atlieka pirminį duomenų atnaujinimą, o vėliau veikia cikle ir kasdien nustatytu laiku (pvz., 06:30) automatiškai atnaujina duomenis. Atlieka atminties stebėjimą per `tracemalloc`.

\* \*\*`database.py`:\*\* Atsakingas už prisijungimą prie PostgreSQL per `psycopg2`. Sukuria prekių lentelę (`products`), prieš įrašant naujus duomenis automatiškai išvalo senus tos parduotuvės įrašus, konvertuoja kainas ir validuoja mitybinių verčių tipus.

\* \*\*`Product.py`:\*\* Duomenų modelio klasė, aprašanti prekės struktūrą (pavadinimą, kainas, svorį, mitybines vertes bei nuorodas).



\---



\## Testavimas ir jo rezultatai

Sistemos stabilumui bei duomenų vientisumui užtikrinti taikomas automatizuotas kodo vykdymas ir sekimas:

\* \*\*Duomenų validacija (`database.py`):\*\* Integruota `clean\_float` funkcija, užtikrinanti, kad neteisingi ar trūkstami mitybinių verčių formatai (pvz., kableliai vietoj taškų) nesulaužytų duomenų bazės struktūros ir būtų sėkmingai konvertuojami.

\* \*\*Atminties nutekėjimo testavimas:\*\* `Crawler.py` integruotas `tracemalloc` funkcionalumas, kuris po kiekvieno duomenų rinkimo ciklo konsolėje išveda TOP 10 daugiausiai resursų sunaudojusių kodo eilučių ataskaitą.



> 📊 \*\*Detalesnes testavimo skriptų ataskaitas ir kodo aprėpties rezultatus rasite saugyklos faile:\*\* `TESTING.md` (arba `/tests` aplanke).



\---



\## Trumpa naudotojo dokumentacija



\### Aplinkos kintamieji (`.env`)

Prieš paleidžiant projektą, pagrindiniame aplanke sukurkite `.env` failą ir nustatykite konfigūraciją:

```env

DB\_HOST=localhost

DB\_NAME=map\_demo

DB\_USER=postgres

DB\_PASS=tavo\_slaptazodis

DB\_PORT=5432





\## Kaip paleisti Backend serverį lokaliai:

Klonuokite saugyklą ir įsidiekite priklausomybes:



git clone \[https://github.com/Kiprassve/ShoppingAdvisor.git](https://github.com/Kiprassve/ShoppingAdvisor.git)

cd PriceScraper

pip install -r requirements.txt

