const search_button = document.getElementById("search-btn");
const sidebar_close_button = document.getElementById("close-btn");
const sidebar = document.getElementById('sidebar');
const list = document.getElementById('resultsList');

async function performSearch() {
  list.innerHTML = '<p>Searching...</p>';
  sidebar.classList.add('open');

  // Atnaujinti mock duomenys su maistine verte
  const mockData = await new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { 
          name: "Raudonos besėklės vynuogės", store: "Maxima", price: 12.99, image: "TestingImages/Grapes.jfif",
          baltymai: 0.7, angliavandeniai: 17, riebalai: 0.2, skaidulos: 0.9 
        },
        { 
          name: "ŽEMAITIJOS sviestas, 82 % rieb.", store: "Lidl", price: 9.50, image: "TestingImages/Butter.jfif",
          baltymai: 0.6, angliavandeniai: 0.6, riebalai: 82, skaidulos: 0 
        },
        { 
          name: "Bulvių traškučiai ESTRELLA", store: "Iki", price: 8.75, image: "TestingImages/Chips.jfif",
          baltymai: 6, angliavandeniai: 50, riebalai: 32, skaidulos: 4 
        }
      ]);
    }, 1500);
  });

  list.innerHTML = ''; 
  mockData.forEach(item => {
    const card = document.createElement('div');
    card.className = 'food-card';
    
    // Pridedame naują sekciją maistinėms vertėms
    card.innerHTML = `
      <img src="${item.image}" alt="${item.name}" class="food-img">
      <div class="card-content">
        <h3>${item.name}</h3>
        <p><strong>Parduotuvė:</strong> ${item.store}</p>
        <div class="price">€${item.price}</div>
        
        <div class="nutritional-info">
          <p>B: ${item.baltymai}g | A: ${item.angliavandeniai}g | R: ${item.riebalai}g | S: ${item.skaidulos}g</p>
        </div>
      </div>
    `;
    list.appendChild(card);
  });
}

function closeSidebar() {
  sidebar.classList.remove('open');
}

search_button.addEventListener("click", performSearch);
sidebar_close_button.addEventListener("click", closeSidebar);