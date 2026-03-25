const search_button = document.getElementById("search-btn");
const sidebar_close_button = document.getElementById("close-btn");
const sidebar = document.getElementById('sidebar');
const list = document.getElementById('resultsList');

let currentData = []; // Čia saugosime gautus produktus

const sortSelect = document.getElementById("sortOptions");

async function performSearch() {
  list.innerHTML = '<p>Searching...</p>';
  sidebar.classList.add('open');

  // Imituojame duomenų gavimą
  const mockData = await new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { name: "Raudonos besėklės vynuogės", store: "Maxima", storeLogo: "Icons/maxima_logo.png", price: 12.99, image: "TestingImages/Grapes.jfif", baltymai: 0.7, angliavandeniai: 17, riebalai: 0.2, skaidulos: 0.9 },
        { name: "ŽEMAITIJOS sviestas, 82 % rieb.", store: "Lidl", storeLogo: "Icons/lidl_logo.png", price: 9.50, image: "TestingImages/Butter.jfif", baltymai: 0.6, angliavandeniai: 0.6, riebalai: 82, skaidulos: 0 },
        { name: "Bulvių traškučiai ESTRELLA", store: "Iki", storeLogo: "Icons/iki_logo.png", price: 8.75, image: "TestingImages/Chips.jfif", baltymai: 6, angliavandeniai: 50, riebalai: 32, skaidulos: 4 }
      ]);
    }, 1000);
  });

  currentData = mockData; // Išsaugojame duomenis
  applySortingAndRender(); // Iškviečiame rūšiavimą ir atvaizdavimą
}

// Funkcija, kuri atsakinga už sąrašo perbraižymą
function applySortingAndRender() {
  const sortBy = sortSelect.value;

  const sortedData = [...currentData].sort((a, b) => {
    if (sortBy === "price-asc") return a.price - b.price;
    if (sortBy === "price-desc") return b.price - a.price;
    if (sortBy === "protein-desc") return b.baltymai - a.baltymai;
    if (sortBy === "carbs-desc") return b.angliavandeniai - a.angliavandeniai;
    return 0;
  });

  renderList(sortedData);
}

// Funkcija, kuri tik piešia korteles
function renderList(data) {
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
  sidebar.classList.remove('open');
}

search_button.addEventListener("click", performSearch);
sidebar_close_button.addEventListener("click", closeSidebar);