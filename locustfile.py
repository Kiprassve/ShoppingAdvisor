from locust import HttpUser, task, between

class ShoppingAdvisorUser(HttpUser):
    wait_time = between(1, 3)

    # Simulates a user browsing products (your main endpoint)
    @task(5)
    def scrape_products(self):
        self.client.get("/api/scrape?rimi=true&iki=true")

    @task(3)
    def scrape_rimi_only(self):
        self.client.get("/api/scrape?rimi=true")

    @task(2)
    def scrape_iki_only(self):
        self.client.get("/api/scrape?iki=true")

    # Simulates a user checking nearby stores (Kaunas city center coords)
    @task(4)
    def get_stores_nearby(self):
        self.client.get("/api/stores?lat=54.8985&lon=23.9036&radius=1000")

    @task(2)
    def get_stores_wide(self):
        self.client.get("/api/stores?lat=54.8985&lon=23.9036&radius=3000")