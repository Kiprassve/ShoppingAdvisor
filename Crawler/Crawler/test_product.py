import sys
import os
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from Product import Product
    print("✅ Sėkmingai importuota Product klasė!")
except ImportError as e:
    print(f"❌ Klaida: nepavyko rasti Product.py aplanke {current_dir}")
    raise e

class TestProductClass(unittest.TestCase):

    # 5 UŽDUOTIS: Set-up fazė (vykdoma prieš KIEKVIENĄ testą)
    def setUp(self):
        self.sample_name = "Vištienos krūtinėlė"
        self.sample_protein = "22,5"
        self.sample_carbs = "0,5"
        # Sukuriame objektą, kurį naudosime testuose
        self.product = Product(
            name=self.sample_name,
            weight_kg="0.5",
            protein=self.sample_protein,
            fat="1,2",
            sugar="0,1",
            salt="0,5",
            carbohydrates=self.sample_carbs,
            calories_kcal="110",
            url="http://rimi.lt/vistsiena",
            image_url="http://rimi.lt/img.jpg"
        )

    # 5 UŽDUOTIS: Tear-down fazė (vykdoma po KIEKVIENO testo)
    def tearDown(self):
        del self.product

    # 6 UŽDUOTIS: Unit testas (tikriname ar duomenys teisingai priskirti)
    def test_product_initialization(self):
        self.assertEqual(self.product.name, self.sample_name)
        self.assertEqual(self.product.protein, self.sample_protein)

    # Papildomas testas: patikriname __str__ metodą
    def test_string_representation(self):
        expected_string = f"Name: {self.sample_name}\nWeight: 0.5\nProtein: {self.sample_protein}\nFat: 1,2\nSugar: 0,1\nSalt: 0,5\nCarbohydrates: {self.sample_carbs}\nCalories: 110"
        self.assertEqual(str(self.product), expected_string)

        # TEST CASE: Tikriname, kaip klasė elgiasi su tuščiomis reikšmėmis
    def test_product_with_empty_fields(self):
        empty_product = Product("", "", "", "", "", "", "", "", "", "")
        self.assertEqual(empty_product.name, "")
        self.assertEqual(empty_product.protein, "")

    # TEST CASE: Tikriname kainos skaičiavimo logiką (jei tavo klasė ją turi)
    # Arba tiesiog patikriname, ar svoris teisingai išsaugotas
    def test_weight_parsing(self):
        self.product.weight_kg = "1.25"
        self.assertEqual(self.product.weight_kg, "1.25")


    # 4 UŽDUOTIS: Parametrizuotas testas (tikriname skirtingas maistines medžiagas)
    def test_nutrient_variations(self):
        test_data = [("10,0", "5,5", "1,2"), ("0", "0", "0")]
        for protein, carbs, fat in test_data:
            with self.subTest(p=protein, c=carbs, f=fat):
                p = Product("Test", "1", protein, fat, "0", "0", carbs, "100", "url", "img")
                self.assertEqual(p.protein, protein)

if __name__ == '__main__':
    unittest.main()