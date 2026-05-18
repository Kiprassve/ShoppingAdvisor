// --- Globalūs kintamieji ---
const search_button = document.getElementById("search-btn");
const sidebar_close_button = document.getElementById("close-btn");
const sidebar = document.getElementById('sidebar');
const list = document.getElementById('resultsList');
const sortSelect = document.getElementById("sortOptions");
const radiusInput = document.getElementById('radiusInput');
const checkboxes = document.querySelectorAll('.list input[type="checkbox"]');
const firstItemBox = document.getElementById('firstItem');
const secondItemBox = document.getElementById('secondItem');
const preferenceInput = document.getElementById('Favour');

const sort_Option_One = document.getElementById("priceMassOne");
const sort_Method_One = document.getElementById("ascdescone");
const sort_Option_Two = document.getElementById("priceMassTwo");
const sort_Method_Two = document.getElementById("ascdesctwo");



let currentData = [];      // Čia saugome visus gautus produktus iš Flask
let currentPage = 1;       // Dabartinis puslapis
const itemsPerPage = 5;   // Kiek produktų rodyti viename puslapyje


// --- Rezultatų lango filtrų valdymas (Atnaujina tik prekių sąrašą) ---

// 1. Surandame mygtukus pagal tavo HTML ID (pasikeisk ID, jei jie kitokie)
const rimiCheckbox = document.getElementById("filter-rimi");     // Pakeista!
const maximaCheckbox = document.getElementById("filter-maxima"); // Pakeista!
const ikiCheckbox = document.getElementById("filter-iki");

// 2. Pagalbinė funkcija, kuri nuskaito, kas šiuo metu pažymėta rezultatų lange
function getSelectedBrandsFromUI() {
    return {
        maxima: maximaCheckbox ? maximaCheckbox.checked : true,
        rimi: rimiCheckbox ? rimiCheckbox.checked : true,
        iki: ikiCheckbox ? ikiCheckbox.checked : true
    };
}

// 3. Užregistruojame klausymą. Pasikeitus varnelei, atnaujinamas TIK prekių langas
[maximaCheckbox, rimiCheckbox, ikiCheckbox].forEach(checkbox => {
    if (checkbox) {
        checkbox.addEventListener('change', function() {
            // Saugiklis: atnaujiname sąrašą tik tada, jei vartotojas jau yra atlikęs bent vieną paiešką
            if (latitude !== 0 && longitude !== 0) {
                
                // Pasiimame naujai pažymėtas/atžymėtas parduotuves
                const currentFilters = getSelectedBrandsFromUI();
                
                // IŠKVIEDŽIAME paiešką iš naujo nuo 1-o puslapio.
                // Kadangi pirmas parametras yra "currentFilters", funkcija nebenaudos žemėlapio,
                // o tiesiog nusiųs užklausą į Flask pagal naujai pasirinktus mygtukus!
                performSearch(currentFilters, 1);
            }
        });
    }
});

// --- 1. Pagrindinė paieškos funkcija ---
// --- 1. Pagrindinė paieškos funkcija ---
async function performSearch(brands = null, pageNumber = 1) {
    // 1. Saugiai patikriname: jei brands buvo perduotas (ir nėra null), išsaugome jį
    if (brands !== null) {
        lastSearchedBrands = brands;
    }
    // Jei brands yra null (spustelėjus puslapį), kodas tiesiog naudos tai, 
    // kas jau buvo išsaugota lastSearchedBrands kintamajame!

    currentPage = pageNumber; // Atnaujiname esamą puslapį
    list.innerHTML = '<p style="padding:20px; text-align:center;">Loading products from database...</p>';
    sidebar.classList.add('open');

    try {
        // 2. KRIZINĖ VIETA: Užklausos URL dabar Saugiai naudoja "lastSearchedBrands", o ne "brands"
        const url = `http://127.0.0.1:5000/api/scrape?maxima=${lastSearchedBrands.maxima}&rimi=${lastSearchedBrands.rimi}&iki=${lastSearchedBrands.iki}&page=${currentPage}&per_page=${itemsPerPage}`;
        
        const response = await fetch(url);
        if (!response.ok) throw new Error("Serverio klaida");
        
        const result = await response.json();
        
        currentData = result.products || []; 
        
        const sortedData = sortProducts(currentData);
        renderList(sortedData);
        renderPaginationControls(result.total_items); 
        
    } catch (error) {
        console.error("Klaida gaunant duomenis:", error);
        list.innerHTML = '<p style="color:red; padding:20px;">Failed to connect to the scraper server.</p>';
    }
}

let selectedMacros=[];

checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const labelText = document.querySelector(`label[for="${this.id}"]`).innerText;
        if (this.checked) {
            // If there are ALREADY 2 items in the list...
            if (selectedMacros.length === 2) {
                // 1. Remove the oldest item (index 0) from the array
                const oldestItem = selectedMacros.shift(); 
                
                // 2. Physically uncheck that oldest item's HTML checkbox
                document.getElementById(oldestItem.id).checked = false;
            }
            
            // Add the new item to the end of the array
            selectedMacros.push({ id: this.id, name: labelText });
        } 
        else {
            // If the user manually UNCHECKS an item, remove it from the array
            selectedMacros = selectedMacros.filter(item => item.id !== this.id);
        }
        // Update the screen
        updateUI();
        updatePreferences();
    });
});

function updateUI() {
    // 1. Update the Text Boxes
    firstItemBox.value = selectedMacros[0] ? selectedMacros[0].name : ""; 
    secondItemBox.value = selectedMacros[1] ? selectedMacros[1].name : "";
    
}

function updatePreferences() {
    const count = selectedMacros.length;

    const preferenceDiv = document.querySelector('.Preference');
    const prioritiesTitle = document.querySelector('.lowerContainer > .title');

    preferenceDiv.style.display = count === 0 ? 'none' : 'flex';
    prioritiesTitle.style.display = count === 0 ? 'none' : 'block';

    const firstHalf = [
        document.querySelector("label[for='priceMassOne']"),
        document.querySelector("label[for='ascdescone']"),
        firstItemBox,
    ];

    const secondHalf = [
        document.querySelector("label[for='priceMassTwo']"),
        document.querySelector("label[for='ascdesctwo']"),
        preferenceInput,
        secondItemBox
    ];

    firstHalf.forEach(el => el.style.display = count >= 1 ? '' : 'none');
    secondHalf.forEach(el => el.style.display = count >= 2 ? '' : 'none');
}


// --- 2. Rūšiavimo logika ---
function sortProducts(data) { 
    if (!data || data.length === 0) return [];
    
    const n = data.length;
    for (let i = 0; i < n - 1; i++) {
        for (let j = 0; j < n - i - 1; j++) {
            let curFirstMacro = getMacro(data, 0, j, oneSortPrice);
            let curSecondMacro = getMacro(data, 1, j, twoSortPrice);
            let nextFirstMacro = getMacro(data, 0, j + 1, oneSortPrice);
            let nextSecondMacro = getMacro(data, 1, j + 1, twoSortPrice);

            // Užtikriname, kad NaN reikšmės netrukdytų rikiuoti
            if (isNaN(curFirstMacro)) curFirstMacro = 0;
            if (isNaN(nextFirstMacro)) nextFirstMacro = 0;
            if (isNaN(curSecondMacro)) curSecondMacro = 0;
            if (isNaN(nextSecondMacro)) nextSecondMacro = 0;

            if (curFirstMacro === 0 && nextFirstMacro > 0) {
                // Jei dabartinis neturi maistinių medžiagų, nustumiam į galą
                [data[j], data[j + 1]] = [data[j + 1], data[j]];
            } else if (curFirstMacro > 0 || nextFirstMacro > 0) {
                let a = oneSortAscending ? 1 : -1;
                let b = twoSortAscending ? 1 : -1;
                let first = 0;
                let second = 0;

                if (selectedMacros[1] == null) {
                    first = curFirstMacro * preferenceWeight * a;
                    second = nextFirstMacro * preferenceWeight * a;
                } else {
                    first = (curFirstMacro * preferenceWeight * a) + (curSecondMacro * (10 - preferenceWeight) * b);
                    second = (nextFirstMacro * preferenceWeight * a) + (nextSecondMacro * (10 - preferenceWeight) * b);
                }

                if (first > second) {
                    [data[j], data[j + 1]] = [data[j + 1], data[j]];
                }
            }
        }
    }
    return data;
}

function getMacro(data, i, j, byPrice) {
    if (selectedMacros[i] == null || !data[j]) return 0;
    
    let Macro = 0;   
    switch(selectedMacros[i].id) {
        case "protein":
            Macro = data[j].baltymai;
            break;
        case "carbs":
            Macro = data[j].angliavandeniai;
            break;
        case "fat":
            Macro = data[j].riebalai;
            break;
        case "calories":
            Macro = data[j].calories;
            break;
        default:
            Macro = 0;
    }

    if (byPrice) {
        Macro = data[j].price > 0 ? Macro / data[j].price : 0;
    } else {
        // Paverčiame svorį į skaičių (išfiltruojame raides g, kg, jei tokių yra)
        let rawWeight = data[j].weight;
        let numericWeight = parseFloat(rawWeight);

        // Jei svoris nurodytas kilogramais (pvz., 1kg), paverčiame į gramus
        if (typeof rawWeight === 'string' && rawWeight.toLowerCase().includes('kg')) {
            numericWeight *= 1000;
        }

        if (!isNaN(numericWeight) && numericWeight > 0) {
            Macro /= numericWeight;
        } else {
            Macro = 0; // Apsauga: jei svorio nėra, grąžiname 0, kad nesulaužytų algoritmo
        }
    }
    return Macro;
}

// --- 3. Puslapiavimo ir perbraižymo logika ---
function applySortingAndRender() {
    const sortedData = sortProducts(currentData);
    
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedData = sortedData.slice(startIndex, endIndex);

    renderList(paginatedData);
    renderPaginationControls(sortedData.length);
}

// --- 4. Produktų kortelių generavimas ---
function renderList(data) {
    list.innerHTML = ''; 
    if (data.length === 0) {
        list.innerHTML = '<p style="padding:20px; text-align:center;">No products found.</p>';
        return;
    }

    data.forEach(item => {
        const card = document.createElement('div');
        card.className = 'food-card';
        card.innerHTML = `
            <img src="${item.storeLogo}" alt="${item.store}" class="store-badge">
            <img src="${item.image}" alt="${item.name}" class="food-img">
            <div class="card-content">
                <h3>${item.name}</h3>
                <div class="price">€${item.price.toFixed(2)}</div>
                <div class="nutr-container">
                    <div class="nutr-badge prot">
                        <span class="nutr-label">PROTEIN</span>
                        <span class="nutr-value">${item.baltymai}g</span>
                    </div>
                    <div class="nutr-badge carb">
                        <span class="nutr-label">CARBS</span>
                        <span class="nutr-value">${item.angliavandeniai}g</span>
                    </div>
                    <div class="nutr-badge fat">
                        <span class="nutr-label">FAT</span>
                        <span class="nutr-value">${item.riebalai}g</span>
                    </div>
                </div>
            </div>
        `;
        list.appendChild(card);
    });
}

// --- 5. Puslapiavimo mygtukų valdymas (Sutvarkytas API integracijai) ---
function renderPaginationControls(totalItems) {
    const paginationContainer = document.getElementById('pagination');
    if (!paginationContainer) return;

    paginationContainer.innerHTML = '';
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    
    if (totalPages <= 1) {
        paginationContainer.style.display = 'none';
        return;
    } else {
        paginationContainer.style.display = 'flex';
    }

    // Pagalbinė funkcija mygtukų kūrimui
    function createPageButton(pageNumber, text = pageNumber, isActive = false) {
        const btn = document.createElement('button');
        btn.innerText = text;
        if (isActive) btn.className = 'active';
        
        // KRIZINIS PAKEITIMAS: Paspaudus siunčiame užklausą į serverį naujam puslapiui
        btn.onclick = () => {
            performSearch(null, pageNumber);
            list.scrollTo(0, 0); 
        };
        return btn;
    }

    function createEllipsis() {
        const span = document.createElement('span');
        span.innerText = '...';
        span.className = 'pagination-ellipsis';
        return span;
    }

    // ==========================================
    // REŽIMAS A: Mažai puslapių (iki 7)
    // ==========================================
    if (totalPages <= 7) {
        // "Atgal" mygtukas
        const prevBtn = document.createElement('button');
        prevBtn.innerHTML = '&laquo;';
        prevBtn.disabled = currentPage === 1;
        prevBtn.onclick = () => {
            performSearch(null, currentPage - 1);
            list.scrollTo(0, 0);
        };
        paginationContainer.appendChild(prevBtn);

        for (let i = 1; i <= totalPages; i++) {
            paginationContainer.appendChild(createPageButton(i, i, i === currentPage));
        }

        // "Pirmyn" mygtukas
        const nextBtn = document.createElement('button');
        nextBtn.innerHTML = '&raquo;';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.onclick = () => {
            performSearch(null, currentPage + 1);
            list.scrollTo(0, 0);
        };
        paginationContainer.appendChild(nextBtn);
        
        return;
    }

    // ==========================================
    // REŽIMAS B: Daug puslapių (Dinaminis langas)
    // ==========================================

    // "Atgal" mygtukas
    const prevBtn = document.createElement('button');
    prevBtn.innerHTML = '&laquo;';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => {
        performSearch(null, currentPage - 1);
        list.scrollTo(0, 0);
    };
    paginationContainer.appendChild(prevBtn);

    const maxVisibleButtons = 2; 

    // 1. Pirmasis puslapis
    paginationContainer.appendChild(createPageButton(1, 1, currentPage === 1));

    if (currentPage - maxVisibleButtons > 2) {
        paginationContainer.appendChild(createEllipsis());
    }

    let startPage = Math.max(2, currentPage - maxVisibleButtons);
    let endPage = Math.min(totalPages - 1, currentPage + maxVisibleButtons);

    // 2. Viduriniai mygtukai
    for (let i = startPage; i <= endPage; i++) {
        paginationContainer.appendChild(createPageButton(i, i, i === currentPage));
    }

    if (currentPage + maxVisibleButtons < totalPages - 1) {
        paginationContainer.appendChild(createEllipsis());
    }

    // 3. Paskutinis puslapis
    paginationContainer.appendChild(createPageButton(totalPages, totalPages, currentPage === totalPages));

    // "Pirmyn" mygtukas
    const nextBtn = document.createElement('button');
    nextBtn.innerHTML = '&raquo;';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => {
        performSearch(null, currentPage + 1);
        list.scrollTo(0, 0);
    };
    paginationContainer.appendChild(nextBtn);
}

// --- 6. Žemėlapio (Leaflet) logika ---
let map;
let storeMarkersGroup;
let latitude = 0;
let longitude = 0;
let searchRadius = 5;
let currentCircle;
let currentMarker;

function instantiateMap() {
    map = L.map('map', {
        doubleClickZoom: false,
        zoomControl: false,
        scrollWheelZoom: true,
        dragging: true,
    }).setView([54.9, 23.9], 10);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Dvilypis spustelėjimas nustato paieškos centrą
    map.on('dblclick', function(e) {
        latitude = e.latlng.lat;
        longitude = e.latlng.lng; 
        DrawCircle();    
    });

    storeMarkersGroup = L.layerGroup().addTo(map);
}

function DrawCircle() {
    if (currentMarker) currentMarker.remove();
    if (currentCircle) currentCircle.remove();

    const radiusLabel = document.getElementById('radiusLabel');
    if (radiusLabel) radiusLabel.textContent = searchRadius;

    currentMarker = L.marker([latitude, longitude]).addTo(map);
    currentCircle = L.circle([latitude, longitude], { radius: searchRadius * 1000 }).addTo(map);
}

// --- 7. Parduotuvių gavimas iš DB žemėlapyje ---
const rimiIcon = L.icon({ iconUrl: '/Backend/static\\Icons/rimi_logo.png', iconSize: [32, 16], iconAnchor: [16, 32] });
const maximaIcon = L.icon({ iconUrl: '/Backend/static\\Icons/maxima_logo.png', iconSize: [32, 8], iconAnchor: [16, 32] });
const ikiIcon = L.icon({ iconUrl: '/Backend/static\\Icons/iki_logo.png', iconSize: [32, 32], iconAnchor: [16, 32] });


async function GetStores() {
    if (!latitude || !longitude) {
        console.warn("Nenustatyta vieta žemėlapyje (dukart spustelėkite).");
        return { maxima: false, rimi: false, iki: false };
    }

    let foundBrands = { maxima: false, rimi: false, iki: false }; 
    storeMarkersGroup.clearLayers();
    const radiusInMeters = searchRadius * 1000;
    const url = `http://localhost:5000/api/stores?lat=${latitude}&lon=${longitude}&radius=${radiusInMeters}`;

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Klaida jungiantis prie DB API");
        
        const stores = await response.json();
        if (Array.isArray(stores)) {
            stores.forEach(store => {
                let icon = null;
                let webUrl = "";
                let nameLower = (store.name || "").toLowerCase();

                // Filtruojame tik 3 tinklus ir priskiriame nuorodas
                if (nameLower.includes("maxima")) { 
                    icon = maximaIcon;
                    webUrl = "https://www.maxima.lt";
                    foundBrands.maxima = true;
                } else if (nameLower.includes("rimi")) {
                    icon = rimiIcon;
                    webUrl = "https://www.rimi.lt";
                    foundBrands.rimi = true;
                } else if (nameLower.includes("iki")) {
                    icon = ikiIcon;
                    webUrl = "https://www.iki.lt";
                    foundBrands.iki = true;
                }

                // Jei tai viena iš trijų parduotuvių, dedame žymeklį
                if (icon != null) {
                    const popupContent = `
                        <div class="store-popup" style="min-width: 150px;">
                            <h3 style="margin-bottom: 8px;">${store.name}</h3>
                            <a href="${webUrl}" target="_blank" 
                               style="display: inline-block; color: #007bff; text-decoration: none; font-weight: bold; font-size: 13px;">
                               🌐 Apsilankyti svetainėje &rarr;
                            </a>
                        </div>
                    `;

                    L.marker([store.lat, store.lon], { icon: icon })
                        .addTo(storeMarkersGroup)
                        .bindPopup(popupContent);
                }
            });
        }
    } catch (error) {
        console.error("Map error:", error);
    }
    return foundBrands;
}


// --- 8. Event Listeners ---

// Rūšiavimo keitimas

// Spindulio keitimas
radiusInput.addEventListener("input", function() {
    searchRadius = radiusInput.value; 
    DrawCircle();
});

// Pagrindinis paieškos mygtukas
// Pagrindinis paieškos mygtukas
search_button.addEventListener("click", async function() {
    if (latitude === 0 && longitude === 0) {
        alert("Prašome pasirinkti vietą žemėlapyje dukart spustelint pelės klavišu!");
        return; 
    }

    const foundBrands = await GetStores(); // Suranda kokios parduotuvės patenka į spindulį
    performSearch(foundBrands, 1); // <--- Pradedame griežtai nuo 1 puslapio
});

// Sidebar uždarymas
sidebar_close_button.addEventListener("click", () => {
    sidebar.classList.remove('open');
});


// Žemėlapio inicializacija užsikrovus puslapiui
document.addEventListener("DOMContentLoaded", instantiateMap);

let oneSortPrice =true;
sort_Option_One.addEventListener('change',function(){
oneSortPrice = oneSortPrice ? false:true;
document.querySelector("label[for='priceMassOne']").textContent = oneSortPrice ? "Price" : "Mass";
});

let oneSortAscending = true;
sort_Method_One.addEventListener('change', function () {
    oneSortAscending = !oneSortAscending;
    document.querySelector("label[for='ascdescone']").textContent = oneSortAscending ? "Ascending" : "Descending";
});
let twoSortPrice =true;
sort_Option_Two.addEventListener('change', function () {
    twoSortPrice = !twoSortPrice;
    document.querySelector("label[for='priceMassTwo']").textContent = twoSortPrice ? "Price" : "Mass";
});
let twoSortAscending = true;
sort_Method_Two.addEventListener('change', function () {
    twoSortAscending = !twoSortAscending;
    document.querySelector("label[for='ascdesctwo']").textContent = twoSortAscending ? "Ascending" : "Descending";
});
let preferenceWeight = 5;
preferenceInput.addEventListener("input", function() {
    preferenceWeight = preferenceInput.value; 
});
document.addEventListener("DOMContentLoaded", updatePreferences);


// --- 9. Adresų Autocomplete Logika ---
const locationInput = document.getElementById('locationInput');
const autocompleteList = document.getElementById('autocomplete-list');

// Debounce timer — prevents firing a request on every single keystroke.
// The search only runs 300ms after the user stops typing, so you never
// see stale results from intermediate states like "bijunu g. 1".
let autocompleteTimeout = null;

locationInput.addEventListener('input', (e) => {
    const val = e.target.value;
    autocompleteList.innerHTML = '';

    if (val.length < 3) return;

    // Cancel any pending request from the previous keystroke
    clearTimeout(autocompleteTimeout);

    autocompleteTimeout = setTimeout(async () => {
        try {
            const res = await fetch(`http://localhost:5000/api/search-address?q=${encodeURIComponent(val)}`);
            const suggestions = await res.json();

            console.log("Gauti duomenys:", suggestions);

            suggestions.forEach(place => {
                const div = document.createElement('div');
                div.className = 'autocomplete-item';
                div.textContent = place.name;

                div.addEventListener('click', () => {
                    locationInput.value = place.name;
                    autocompleteList.innerHTML = '';

                    latitude  = parseFloat(place.lat);
                    longitude = parseFloat(place.lon);

                    map.setView([latitude, longitude], 15);
                    DrawCircle();
                });
                autocompleteList.appendChild(div);
            });
        } catch (err) {
            console.error("Klaida gaunant adresus:", err);
        }
    }, 300); // wait 300ms after last keystroke before searching
});

// Uždaryti sąrašą paspaudus bet kur kitur
document.addEventListener('click', (e) => {
    if (e.target !== locationInput && autocompleteList) {
        autocompleteList.innerHTML = '';
    }
});
