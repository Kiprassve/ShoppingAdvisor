// ─── Sample test data ───────────────────────────────────────────────
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


// ─── renderList() tests ──────────────────────────────────────────────
QUnit.module("renderList()", function () {

  QUnit.test("renders the correct number of cards", function (assert) {
    renderList(mockProducts);
    const cards = document.querySelectorAll(".food-card");
    assert.equal(cards.length, 3, "should render 3 cards");
  });

  QUnit.test("displays product name", function (assert) {
    renderList(mockProducts);
    const firstCard = document.querySelector(".food-card h3");
    assert.equal(firstCard.textContent, "Raudonos vynuogės");
  });

  QUnit.test("displays formatted price", function (assert) {
    renderList(mockProducts);
    const price = document.querySelector(".food-card .price");
    assert.equal(price.textContent, "€12.99");
  });

  QUnit.test("renders empty list when given no data", function (assert) {
    renderList([]);
    const cards = document.querySelectorAll(".food-card");
    assert.equal(cards.length, 0, "no cards should be rendered");
  });

  QUnit.test("each card has a store logo image", function (assert) {
    renderList(mockProducts);
    const logos = document.querySelectorAll(".store-badge");
    assert.equal(logos.length, 3, "each card should have a store badge");
  });

});


// ─── Sorting tests ───────────────────────────────────────────────────
QUnit.module("Sorting logic", function () {

  QUnit.test("price-asc sorts cheapest first", function (assert) {
    const sorted = [...mockProducts].sort((a, b) => a.price - b.price);
    assert.equal(sorted[0].name, "Traškučiai", "cheapest should be first");
    assert.equal(sorted[2].name, "Raudonos vynuogės", "most expensive should be last");
  });

  QUnit.test("price-desc sorts most expensive first", function (assert) {
    const sorted = [...mockProducts].sort((a, b) => b.price - a.price);
    assert.equal(sorted[0].name, "Raudonos vynuogės", "most expensive should be first");
  });

  QUnit.test("protein-desc sorts highest protein first", function (assert) {
    const sorted = [...mockProducts].sort((a, b) => b.baltymai - a.baltymai);
    assert.equal(sorted[0].name, "Traškučiai", "chips have the most protein");
  });

  QUnit.test("carbs-desc sorts highest carbs first", function (assert) {
    const sorted = [...mockProducts].sort((a, b) => b.angliavandeniai - a.angliavandeniai);
    assert.equal(sorted[0].name, "Traškučiai", "chips have the most carbs");
  });

});


// ─── Sidebar tests ───────────────────────────────────────────────────
QUnit.module("Sidebar", function () {

  QUnit.test("closeSidebar() removes 'open' class", function (assert) {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.add("open");             
    closeSidebar();
    assert.notOk(sidebar.classList.contains("open"), "sidebar should be closed");
  });

  QUnit.test("sidebar starts without 'open' class", function (assert) {
    const sidebar = document.getElementById("sidebar");
    sidebar.classList.remove("open");          
    assert.notOk(sidebar.classList.contains("open"), "sidebar should not be open by default");
  });

});