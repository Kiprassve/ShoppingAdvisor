// --- Globalūs kintamieji ---
const search_button = document.getElementById("search-btn");
const sidebar_close_button = document.getElementById("close-btn");
const sidebar = document.getElementById('sidebar');
const list = document.getElementById('resultsList');
const sortSelect = document.getElementById("sortOptions");
const radiusInput = document.getElementById('radiusInput');

let currentData = [];      // Čia saugome visus gautus produktus iš Flask
let currentPage = 1;       // Dabartinis puslapis
const itemsPerPage = 5;   // Kiek produktų rodyti viename puslapyje

// --- 1. Pagrindinė paieškos funkcija ---
async function performSearch() {
    list.innerHTML = '<p style="padding:20px;">Searching products in Rimi... (this may take a minute)</p>';
    sidebar.classList.add('open');
    currentPage = 1; // Grįžtame į pirmą puslapį naujai paieškai

    try {
        // Kreipiamės į Flask serverį skreipinimui
        const response = await fetch('http://127.0.0.1:5000/api/scrape');
        
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

// --- 2. Rūšiavimo logika ---
function sortProducts(data, sortBy) {
    return [...data].sort((a, b) => {
        if (sortBy === "price-asc") return a.price - b.price;
        if (sortBy === "price-desc") return b.price - a.price;
        if (sortBy === "protein-asc") return a.baltymai - b.baltymai;
        if (sortBy === "protein-desc") return b.baltymai - a.baltymai;
        if (sortBy === "carbs-asc") return a.angliavandeniai - b.angliavandeniai;
        if (sortBy === "carbs-desc") return b.angliavandeniai - a.angliavandeniai;
        if (sortBy === "fat-asc") return a.riebalai - b.riebalai;
        if (sortBy === "fat-desc") return b.riebalai - a.riebalai;
        return 0;
    });
}

// --- 3. Puslapiavimo ir perbraižymo logika ---
function applySortingAndRender() {
    const sortBy = sortSelect.value;
    const sortedData = sortProducts(currentData, sortBy);
    
    // Paskaičiuojame, kurią dalį masyvo rodyti (pvz., 0-10, 10-20...)
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

// --- 5. Puslapiavimo mygtukų valdymas ---
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

    // "Atgal" mygtukas
    const prevBtn = document.createElement('button');
    prevBtn.innerHTML = '&laquo;';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => {
        currentPage--;
        applySortingAndRender();
        list.scrollTo(0, 0); // Grįžtame į sąrašo viršų
    };
    paginationContainer.appendChild(prevBtn);

    // Puslapių numeriai
    for (let i = 1; i <= totalPages; i++) {
        const btn = document.createElement('button');
        btn.innerText = i;
        if (i === currentPage) btn.className = 'active';
        btn.onclick = () => {
            currentPage = i;
            applySortingAndRender();
            list.scrollTo(0, 0);
        };
        paginationContainer.appendChild(btn);
    }

    // "Pirmyn" mygtukas
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
const rimiIcon = L.icon({ iconUrl: '/Backend/static\\Icons/rimi_logo.png', iconSize: [32, 32], iconAnchor: [16, 32] });
const maximaIcon = L.icon({ iconUrl: '/Backend/static\\Icons/maxima_logo.png', iconSize: [32, 15], iconAnchor: [16, 32] });
const ikiIcon = L.icon({ iconUrl: '/Backend/static\\Icons/iki_logo.png', iconSize: [32, 32], iconAnchor: [16, 32] });

async function GetStores() {
    if (!latitude || !longitude) {
        console.warn("Nenustatyta vieta žemėlapyje (dukart spustelėkite).");
        return;
    }

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
                if (/Maxima.*/i.test(store.name)) icon = maximaIcon;
                else if (/Rimi.*/i.test(store.name)) icon = rimiIcon;
                else if (/Iki.*/i.test(store.name)) icon = ikiIcon;

                if(icon !=null){
                L.marker([store.lat, store.lon], { icon: icon })
                    .addTo(storeMarkersGroup)
                    .bindPopup(`<b>${store.name}</b>`);
                }
            });
        }
    } catch (error) {
        console.error("Map error:", error);
    }
}

// --- 8. Event Listeners ---

// Rūšiavimo keitimas
sortSelect.addEventListener("change", () => {
    currentPage = 1; // Grįžtame į pradžią pakeitus rūšiavimą
    applySortingAndRender();
});

// Spindulio keitimas
radiusInput.addEventListener("input", function() {
    searchRadius = radiusInput.value; 
    DrawCircle();
});

// Pagrindinis paieškos mygtukas
search_button.addEventListener("click", function() {
    performSearch(); // Skreipinam prekes
    GetStores();     // Ieškom parduotuvių aplink
});

// Sidebar uždarymas
sidebar_close_button.addEventListener("click", () => {
    sidebar.classList.remove('open');
});

// Žemėlapio inicializacija užsikrovus puslapiui
document.addEventListener("DOMContentLoaded", instantiateMap);