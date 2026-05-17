Kuriama programų sistema skirta automatizuotam maisto produktų duomenų rinkimui iš trijų didžiausių Lietuvos mažmeninės prekybos tinklų – IKI, Rimi ir Maxima. 
Duomenų rinkimo modulis naudoja žiniatinklio turinio gavybos (angl. web scraping) metodus produktų pavadinimams, kainoms ir mitybinei informacijai (baltymams, angliavandenžams, riebalams, kalorijoms ir t.t.)
gauti iš kiekvieno tinklo oficialios interneto svetainės. 
Surinkti duomenys integruojami į interaktyvią, žemėlapiu grįstą vartotojo sąsają, kurioje naudotojas nurodo paieškos centrą ir spindulį.
Sistema automatiškai identifikuoja visas parduotuves nustatytame geografiniame spindulyje, naudodamasi OpenStreetMap duomenų baze, ir pateikia jose parduodamų produktų sąrašą.
Rezultatus galima filtruoti ir rūšiuoti pagal pasirinktas mitybines vertybes – baltymų ar angliavandenžų kiekį – suteikiant galimybę priimti informuotus pirkimo sprendimus.


Docker naudojimas:
1. Parsisiųskite Docker Desktop
2. Right click ant projekto aplankalo -> Open in Terminal
3. Įveskite komandą: docker-compose up --build

Jei norite sustabdyti per terminal įveskite docker-compose down
