const mockProducts = [
  {
    name: "Raudonos vynuogės",
    store: "Maxima",
    storeLogo: "Icons/maxima_logo.png",
    price: 12.99,
    image: "TestingImages/Grapes.jfif",
    baltymai: 0.7,
    angliavandeniai: 17,
    riebalai: 0.2,
    skaidulos: 0.9
  },
  {
    name: "Sviestas",
    store: "Lidl",
    storeLogo: "Icons/lidl_logo.png",
    price: 9.50,
    image: "TestingImages/Butter.jfif",
    baltymai: 0.6,
    angliavandeniai: 0.6,
    riebalai: 82,
    skaidulos: 0
  },
  {
    name: "Traškučiai",
    store: "Iki",
    storeLogo: "Icons/iki_logo.png",
    price: 8.75,
    image: "TestingImages/Chips.jfif",
    baltymai: 6,
    angliavandeniai: 50,
    riebalai: 32,
    skaidulos: 4
  }
];


QUnit.module("renderList()", function () {

  QUnit.test("card number", function (assert) {
    renderList(mockProducts);
    const cards = document.querySelectorAll(".food-card");
    assert.equal(cards.length, 3, "should render 3 cards");
  });

  QUnit.test("displays product name", function (assert) {
    renderList(mockProducts);
    const firstCard = document.querySelector(".food-card h3");
    assert.equal(firstCard.textContent, "Raudonos vynuogės");
  });

  QUnit.test("displays price", function (assert) {
    renderList(mockProducts);
    const price = document.querySelector(".food-card .price");
    assert.equal(price.textContent, "€12.99");
  });

  QUnit.test("All items contain images", function (assert) {
    renderList(mockProducts);
    const logos = document.querySelectorAll(".store-badge");
    assert.equal(logos.length, 3, "each card should have a store badge");
  });

});

QUnit.module("Sidebar", function () {

  QUnit.test("closeSidebar() removes 'open' class", function (assert) {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.add("open");             
    closeSidebar();
    assert.notOk(sidebar.classList.contains("open"), "sidebar should be closed");
  });


});
QUnit.module("Dropdown Sorting Integration", function () {

  QUnit.test("Sorts by price-asc: Cheapest should be first", function (assert) {
    currentData = mockProducts; 
    const select = document.getElementById("sortOptions");
    select.value = "price-asc";
    applySortingAndRender();
    const cards = document.querySelectorAll(".food-card h3");
    assert.equal(cards[0].textContent, "Traškučiai", "First should be Traškučiai");
    assert.equal(cards[2].textContent, "Raudonos vynuogės", "Last should be Raudonos vynuogės");
  });

  QUnit.test("Sorts by price-desc: Most expensive should be first", function (assert) {
    currentData = mockProducts;
    const select = document.getElementById("sortOptions");
    select.value = "price-desc";
    applySortingAndRender();
    const cards = document.querySelectorAll(".food-card h3");
    assert.equal(cards[0].textContent, "Raudonos vynuogės", "First should be Raudonos vynuogės");
    assert.equal(cards[2].textContent, "Traškučiai", "Last should be Traškučiai");
  });

  QUnit.test("Sorts by protein-desc: Highest protein should be first", function (assert) {
    currentData = mockProducts;
    const select = document.getElementById("sortOptions");
    select.value = "protein-desc";
    applySortingAndRender();
    const cards = document.querySelectorAll(".food-card h3");
    assert.equal(cards[0].textContent, "Traškučiai", "First should be Traškučiai (6g protein)");
    assert.equal(cards[2].textContent, "Sviestas", "Last should be Sviestas (0.6g protein)");
  });

  QUnit.test("Sorts by carbs-desc: Highest carbs should be first", function (assert) {
    currentData = mockProducts;
    const select = document.getElementById("sortOptions");
    select.value = "carbs-desc";
    applySortingAndRender();
    const cards = document.querySelectorAll(".food-card h3");
    assert.equal(cards[0].textContent, "Traškučiai", "First should be Traškučiai (50g carbs)");
    assert.equal(cards[2].textContent, "Sviestas", "Last should be Sviestas (0.6g carbs)");
  });

});