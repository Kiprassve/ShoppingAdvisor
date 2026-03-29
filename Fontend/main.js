const search_button = document.getElementById("search-btn");
const sidebar_close_button = document.getElementById("close-btn");
const sidebar = document.getElementById('sidebar');
const list = document.getElementById('resultsList');
let currentData = []; // Čia saugosime gautus produktus
const sortSelect = document.getElementById("sortOptions");
const radiusInput = document.getElementById('radiusInput');
async function performSearch() {

  list.innerHTML = '<p>Searching products in Rimi... (this may take a minute)</p>';
  sidebar.classList.add('open');

  try {
    // Kreipiamės į mūsų Python Flask serverį
    const response = await fetch('http://127.0.0.1:5000/api/scrape');
    const realData = await response.json();

    currentData = realData; 
    applySortingAndRender(); 
  } catch (error) {
    console.error("Klaida gaunant duomenis:", error);
    list.innerHTML = '<p style="color:red;">Failed to connect to the scraper server.</p>';
  }
}

function sortProducts(data, sortBy) {
  const sortSelect =document.getElementById("sortOptions"); // required for testing
   sortBy = sortSelect.value;
return [...data].sort((a, b) => {
if (sortBy === "price-asc") return a.price - b.price;
if (sortBy === "price-desc") return b.price - a.price;
// Funkcija, kuri atsakinga už sąrašo perbraižymą

  
  

        if (sortBy === "protein-asc") return a.baltymai - b.baltymai;
        if (sortBy === "protein-desc") return b.baltymai - a.baltymai;
        
        if (sortBy === "carbs-asc") return a.angliavandeniai - b.angliavandeniai;
        if (sortBy === "carbs-desc") return b.angliavandeniai - a.angliavandeniai;
        return 0;
    });
    
}

// Funkcija, kuri atsakinga už sąrašo perbraižymą
function applySortingAndRender() {
  const sortSelect =document.getElementById("sortOptions");
    sortBy = sortSelect.value;
    const sortedData = sortProducts(currentData, sortBy);
    renderList(sortedData);
}

// Funkcija, kuri tik piešia korteles
function renderList(data) {

const list = document.getElementById('resultsList');
  list.innerHTML = ''; 
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

// Klausomės, kada vartotojas pakeičia rūšiavimo parinktį
sortSelect.addEventListener("change", applySortingAndRender);

function closeSidebar() {
  const sidebar = document.getElementById('sidebar'); //required for functioning tests Reason
  sidebar.classList.remove('open');
}

let map;
function instantiateMap(){
   map = L.map('map',{
    doubleClickZoom: false,
    zoomControl:false,
  scrollWheelZoom: true,
  dragging: true,
}).setView([54.9,23.9],10);



   L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    map.on('dblclick', function(e){
      console.log("double");
    latitude= e.latlng.lat;
    longitude = e.latlng.lng; 
    DrawCircle();    
    });
}



let latitude=0;
let longitude=0;
let searchRadius =5;
let currentCircle;
let currentMarker;
 function DrawCircle(){
  if(currentMarker){
    currentMarker.remove();
  }
  if(currentCircle)
    {
  currentCircle.remove();
    }
  const radiusLabel = document.getElementById('radiusLabel');
  radiusLabel.textContent= searchRadius;
    currentMarker = L.marker([latitude,longitude]).addTo(map);
  currentCircle = L.circle([latitude, longitude], { radius: searchRadius * 1000}).addTo(map);
  
}

radiusInput.addEventListener("input",function(){searchRadius=radiusInput.value; DrawCircle();});
document.addEventListener("DOMContentLoaded",instantiateMap);
search_button.addEventListener("click", performSearch);
sidebar_close_button.addEventListener("click", closeSidebar);
