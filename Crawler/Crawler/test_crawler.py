import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 1. Kelio nustatymas, kad rastų Crawler.py ir Product.py
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 2. Importuojame funkciją tiesiogiai iš modulio
try:
    import Crawler as CrawlerModule
    print("✅ Sėkmingai importuotas Crawler modulis!")
except ImportError as e:
    print(f"❌ Klaida: nepavyko rasti Crawler.py")
    raise e

class TestCrawlerMocks(unittest.TestCase):

    # 3 UŽDUOTIS: Mock'as (Imitacija)
    # Mes "užlopome" requests.get, kad testas nevykdytų realių užklausų į Rimi
    @patch('requests.get')
    def test_rimi_crawler_with_mock(self, mock_get):
        # --- STUB DALIS ---
        # Sukuriame netikrą atsakymą su minimaliu HTML karkasu
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Simuliuojame Rimi puslapio struktūrą, kurią tavo funkcija supranta
        mock_response.content = b"""
        <html>
            <li class="product-grid__item">
                <a class="card__url js-gtm-eec-product-click" href="/p/test-preke"></a>
                <div class="js-product-container" data-gtms-banner-title="Testinis Produktas 500g"></div>
                <img src="test.jpg">
            </li>
        </html>
        """
        mock_get.return_value = mock_response

        # --- TESTAVIMAS ---
        # Kviečiame tavo funkciją. max_pages=1, item_limit=1, kad neužsiloopintų
        # Kadangi funkcija viduje vėl kviečia requests.get produkto puslapiui,
        # mūsų mock'as suveiks abu kartus.
        try:
            results = CrawlerModule.Rimi_crawler("https://www.rimi.lt/test", max_pages=1, item_limit=1)
            
            # Patikriname rezultatus
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].name, "Testinis Produktas 500g")
            print(f"✅ Mock testas pavyko! Gautas produktas: {results[0].name}")
            
        except Exception as e:
            self.fail(f"Testas nepavyko dėl klaidos: {e}")

if __name__ == '__main__':
    unittest.main()