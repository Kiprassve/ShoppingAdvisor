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

// --- 1. Pagrindinė paieškos funkcija ---
async function performSearch(brands = { maxima: true, rimi: true, iki: true }) {
    list.innerHTML = '<p style="padding:20px;">Searching products in Rimi... (this may take a minute)</p>';
    sidebar.classList.add('open');
    currentPage = 1; // Grįžtame į pirmą puslapį naujai paieškai

    try {
        // Kreipiamės į Flask serverį skreipinimui
        //klaustukas (?) po scrape rodo kad parametrai neprivalomi
        const url = `http://127.0.0.1:5000/api/scrape?maxima=${brands.maxima}&rimi=${brands.rimi}&iki=${brands.iki}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error("Serverio klaida");
        
        const realData = await response.json();
        currentData = realData; 
        
        // Atvaizduojame rezultatus
        applySortingAndRender(); 
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

     const n = data.length;
  for (let i = 0; i < n - 1; i++) {
    for (let j = 0; j < n - i - 1; j++) {
        
let curFirstMacro = getMacro(data,0,j,oneSortPrice);
let curSecondMacro = getMacro(data,1,j,twoSortPrice);
let nextFirstMacro = getMacro(data,0,j+1,oneSortPrice);
let nextSecondMacro = getMacro(data,1,j+1,twoSortPrice);
if(curFirstMacro==0)
{
        [data[j], data[j + 1]] = [data[j + 1], data[j]];
}
else{
let a = oneSortAscending? 1:-1;
let b = twoSortAscending? 1:-1;
let first =0;
let second = 0;
if(selectedMacros[1]==null)
    {
             first = (curFirstMacro * preferenceWeight * a);
             second = (nextFirstMacro * preferenceWeight * a);
    }
    else
        {
             first = (curFirstMacro * preferenceWeight * a) + (curSecondMacro * (10-preferenceWeight) * b);
             second = (nextFirstMacro * preferenceWeight * a) + (nextSecondMacro * (10-preferenceWeight) * b);
        }

      if (first > second) {
        [data[j], data[j + 1]] = [data[j + 1], data[j]];
      }
    }
    }
  }
    
    return data;
}

function getMacro(data, i ,j,byPrice){

        let Macro;   
        if(selectedMacros[i]==null){return 0;}
        switch(selectedMacros[i].id){
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
                Macro=0;
        }
       if(byPrice)
        {Macro/=data[j].price} 
       else
        {
           if(data[j].weight!=0)
            {
                Macro/=data[j].weight
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

// --- 5. Puslapiavimo mygtukų valdymas (Suvaldyta mygtukų gausa) ---
function renderPaginationControls(totalItems) {
    const paginationContainer = document.getElementById('pagination');
    if (!paginationContainer) return;

    paginationContainer.innerHTML = '';
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    
    // Jei puslapių nėra arba yra tik 1, paslepiame konteinerį ir baigiame darbą
    if (totalPages <= 1) {
        paginationContainer.style.display = 'none';
        return;
    } else {
        paginationContainer.style.display = 'flex';
    }

    // Pagalbinė funkcija vienodo mygtuko sukūrimui, kad kodas nesidubliuotų
    function createPageButton(pageNumber, text = pageNumber, isActive = false) {
        const btn = document.createElement('button');
        btn.innerText = text;
        if (isActive) btn.className = 'active';
        btn.onclick = () => {
            currentPage = pageNumber;
            applySortingAndRender();
            list.scrollTo(0, 0); // Atstato sąrašą į viršų persijungus puslapiui
        };
        return btn;
    }

    // Pagalbinė funkcija daugtaškio (...) sukūrimui su specialia klase stiliams
    function createEllipsis() {
        const span = document.createElement('span');
        span.innerText = '...';
        span.className = 'pagination-ellipsis';
        return span;
    }

    // ==========================================
    // REŽIMAS A: Mažai puslapių (iki 7 puslapių)
    // Tiesiog išvedame visus skaičius iš eilės be jokių daugtaškių
    // ==========================================
    if (totalPages <= 7) {
        // "Atgal" mygtukas («)
        const prevBtn = document.createElement('button');
        prevBtn.innerHTML = '&laquo;';
        prevBtn.disabled = currentPage === 1;
        prevBtn.onclick = () => {
            currentPage--;
            applySortingAndRender();
            list.scrollTo(0, 0);
        };
        paginationContainer.appendChild(prevBtn);

        // Sugeneruojame visus mygtukus iš eilės
        for (let i = 1; i <= totalPages; i++) {
            paginationContainer.appendChild(createPageButton(i, i, i === currentPage));
        }

        // "Pirmyn" mygtukas (»)
        const nextBtn = document.createElement('button');
        nextBtn.innerHTML = '&raquo;';
        nextBtn.disabled = currentPage === totalPages;
        nextBtn.onclick = () => {
            currentPage++;
            applySortingAndRender();
            list.scrollTo(0, 0);
        };
        paginationContainer.appendChild(nextBtn);
        
        return; // Baigiame funkciją, žemesnis kodas nebus vykdomas
    }

    // ==========================================
    // REŽIMAS B: Daug puslapių (virš 7 puslapių)
    // Įjungiamas dinaminis langas ir daugtaškiai
    // ==========================================

    // "Atgal" mygtukas («)
    const prevBtn = document.createElement('button');
    prevBtn.innerHTML = '&laquo;';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => {
        currentPage--;
        applySortingAndRender();
        list.scrollTo(0, 0);
    };
    paginationContainer.appendChild(prevBtn);

    const maxVisibleButtons = 2; // Kiek skaičių rodyti į kairę ir dešinę nuo dabartinio

    // 1. Visada pridedame pirmąjį puslapį
    paginationContainer.appendChild(createPageButton(1, 1, currentPage === 1));

    // Kairysis daugtaškis: jei tarp 1-o puslapio ir matomo lango pradžios yra tarpas
    if (currentPage - maxVisibleButtons > 2) {
        paginationContainer.appendChild(createEllipsis());
    }

    // Paskaičiuojame dinaminio lango pradžią ir pabaigą aplink dabartinį puslapį
    let startPage = Math.max(2, currentPage - maxVisibleButtons);
    let endPage = Math.min(totalPages - 1, currentPage + maxVisibleButtons);

    // 2. Sugeneruojame vidurinius puslapius aplink dabartinį
    for (let i = startPage; i <= endPage; i++) {
        paginationContainer.appendChild(createPageButton(i, i, i === currentPage));
    }

    // Dešinysis daugtaškis: jei tarp matomo lango pabaigos ir paskutinio puslapio yra tarpas
    if (currentPage + maxVisibleButtons < totalPages - 1) {
        paginationContainer.appendChild(createEllipsis());
    }

    // 3. Visada pridedame paskutinį puslapį
    paginationContainer.appendChild(createPageButton(totalPages, totalPages, currentPage === totalPages));

    // "Pirmyn" mygtukas (»)
    const nextBtn = document.createElement('button');
    nextBtn.innerHTML = '&raquo;';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => {
        currentPage++;
        applySortingAndRender();
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
//app.py metodo iskvetimas get_data(iki,rimi,maxima)

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
    // Patikriname, ar koordinatės vis dar yra pradinėje 0 būsenoje
    if (latitude === 0 && longitude === 0) {
        alert("Prašome pasirinkti vietą žemėlapyje dukart spustelint pelės klavišu!");
        return; // Sustabdo funkcijos vykdymą, kad toliau neieškotų duomenų
    }

    const foundBrands = await GetStores(); // Ieškom parduotuvių aplink
    performSearch(foundBrands); // Skreipinam prekes
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