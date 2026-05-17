from ast import List
from calendar import c
from dataclasses import dataclass
from os import name
import os
from pickle import TRUE
import re
import json
from pydoc import pager
from re import U, RegexFlag
from sqlite3 import SQLITE_CREATE_INDEX
from time import thread_time_ns
from urllib import request, response
from xml.etree.ElementInclude import include
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

import psycopg2
from database import save_products_to_db

import tracemalloc

#auto scrape
import time
import urllib.request

import Product

import os
from dotenv import load_dotenv
load_dotenv()

DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "map_demo")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "password123")
DB_PORT = os.environ.get("DB_PORT", "5432")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "lt-LT,lt;q=0.9,en-US;q=0.8,en;q=0.7"
}

urls=[
    "https://www.rimi.lt/e-parduotuve/lt/produktai/mesa-ir-zuvis-/c/SH-9?currentPage=1&pageSize=80&query=%3Arelevance%3AallCategories%3ASH-9%3AassortmentStatus%3AinAssortment",
    "https://www.rimi.lt/e-parduotuve/lt/produktai/vaisiai-darzoves-ir-geles/c/SH-15?currentPage=1&pageSize=80&query=%3Arelevance%3AallCategories%3ASH-15%3AassortmentStatus%3AinAssortment",
    "https://www.rimi.lt/e-parduotuve/lt/produktai/augaliniai-produktai/c/SH-77",
    "https://www.rimi.lt/e-parduotuve/lt/produktai/pieno-produktai-ir-kiausiniai/c/SH-11",
    "https://www.rimi.lt/e-parduotuve/lt/produktai/duonos-gaminiai-/c/SH-3",
    "https://www.rimi.lt/e-parduotuve/lt/produktai/saldytas-maistas/c/SH-13",
    "https://www.rimi.lt/e-parduotuve/lt/produktai/bakaleja/c/SH-2",
    "https://www.rimi.lt/e-parduotuve/lt/produktai/rimi-konditerija-ir-kulinarija/c/SH-34?currentPage=1&pageSize=80&query=%3Arelevance%3AallCategories%3ASH-34%3AassortmentStatus%3AinAssortment",
    "https://www.rimi.lt/e-parduotuve/lt/produktai/vaiku-ir-kudikiu-prekes/c/SH-7?currentPage=1&pageSize=80&query=%3Arelevance%3AallCategories%3ASH-7%3AassortmentStatus%3AinAssortment",
    "https://www.rimi.lt/e-parduotuve/lt/produktai/saldumynai-ir-uzkandziai/c/SH-23?currentPage=1&pageSize=80&query=%3Arelevance%3AallCategories%3ASH-23%3AassortmentStatus%3AinAssortment",
    "https://www.rimi.lt/e-parduotuve/lt/produktai/gerimai/c/SH-4?currentPage=1&pageSize=80&query=%3Arelevance%3AallCategories%3ASH-4%3AassortmentStatus%3AinAssortment",
    "https://www.rimi.lt/e-parduotuve/lt/produktai/alkoholiniai-ir-nealkoholiniai-gerimai/c/SH-1"
]

def Rimi_crawler(url):
    response=requests.get(url,headers=headers)
    soup=BeautifulSoup((response.content),"html.parser")
    i=0
    checknextpage=0
    All_Products=[]
    while url!=None:
        for item in soup.find_all("li", class_="product-grid__item"):
            if len(All_Products) >= 10:
                return All_Products
            i=i+1
            weight=img_url=name=protein=fat=sugar=salt=carbs=calories="0"
            prod_ulr=item.find("a", class_="card__url js-gtm-eec-product-click")
            if not prod_ulr:
                continue
            print(str(i)+" https://www.rimi.lt"+str(prod_ulr.get("href")))
            img=item.find("img")
            if img:
                img_url=img.get("data-src")
            div_name=item.find("div", class_="js-product-container card -horizontal-for-mobile")
            if div_name:
                name=div_name.get("data-gtms-banner-title")
            conversion_measure=""
            if name:
                weight_re=re.search(r'(\d+[,.]?\d*)\s*(g|kg|l|ml)\b',str(name),re.IGNORECASE)
                if weight_re:
                    if weight_re.group(2) in ["kg", "l"]:
                        weight=weight_re.group(0).replace("kg","").replace("l","").replace(",",".")
                        weight=str(weight)
                        conversion_measure=str(weight_re.group(2))
                    elif weight_re.group(2) in ["g", "ml"]:
                         weight=float(weight_re.group(0).replace("g","").replace("ml","").replace(",","."))
                         weight=weight/1000
                         weight=str(weight)
                         conversion_measure=str(weight_re.group(2))
                else:
                    weight="1"
            response=requests.get("https://www.rimi.lt"+str(prod_ulr.get("href")),headers=headers)
            soup2=BeautifulSoup((response.content),"html.parser")
            actualprice=discountedprice="0"
            price_div = soup2.find_all('div')
            for p in price_div:
                   cents=p.find("span", class_="cents")
                   euros=p.find("span", class_="major")
                   price_class=p.get('class')
                   if cents and euros:
                        cents_re=re.search(r'\d+',str(cents))
                        euros_re=re.search(r'\d+',str(euros))
                        if cents_re and euros_re:
                            discountedprice=str(euros_re.group(0))+"."+str(cents_re.group(0))
                   if price_class and "price" in price_class:       
                       euro_re=re.search(r'\d+',str(p.find("span")))
                       cent_re=re.search(r'\d+',str(p.find("sup")))
                       if cent_re and euro_re:
                           actualprice=str(euro_re.group(0))+"."+str(cent_re.group(0))
                       oldprice=p.find("p", class_="price__old-price")
                       if oldprice:
                           discountedprice=actualprice
                           actualprice_re=re.search(r'\d+\.?\,?\d*',str(oldprice))
                           if actualprice_re:
                               actualprice=actualprice_re.group(0)
            scripts = soup2.find_all("script")
            for script in scripts:
                if script.string and "product__table" in script.string:
                    hidden_html = script.string.replace('\\u0022', '"').replace('\\/', '/')
                    inner_soup = BeautifulSoup(hidden_html, "html.parser")
                    table_div = inner_soup.find("div", class_="product__table")
                    if table_div:
                        rows = table_div.find_all("tr")
                        for row in rows:
                            cells = row.find_all("td")
                            if len(cells) == 2:
                                label=cells[0].text.strip().lower()
                                if re.search(r'energin.*?vert', label, re.IGNORECASE):
                                    value=re.search(r'(\d+\.?\d*)\s*kcal', cells[1].text.strip().lower())
                                    if value:
                                        calories=value.group(1)
                                if re.search(r'riebalai', label, re.IGNORECASE):
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        fat=value.group(1)
                                if re.search(r'angliavandeniai', label, re.IGNORECASE):
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        carbs=value.group(1)
                                if re.search(r'baltymai', label, re.IGNORECASE):
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        protein=value.group(1)
                                if re.search(r'druska', label, re.IGNORECASE):
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        salt=value.group(1)
                                if re.search(r'i.*?cukr', label, re.IGNORECASE):
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        sugar=value.group(1)
                    if(actualprice!="0" or discountedprice!="0"):                    
                        product_obj=Product.Product(str(name),str(weight),str(conversion_measure),str(protein),str(fat),str(sugar),str(salt),str(carbs),str(calories),"https://www.rimi.lt"+str(prod_ulr.get("href")),str(img_url),actualprice,discountedprice)
                        All_Products.append(product_obj)
        nextpage=soup.find_all("li", class_="pagination__item -chevron")
        if len(nextpage) > 1:
            nextpage=nextpage[1]
            anchor=nextpage.find("a")
            if anchor:
                checknextpage=checknextpage+1
                relative=anchor.get("href")
                url="https://www.rimi.lt"+str(relative)
                response=requests.get(url)
                soup=BeautifulSoup((response.content),"html.parser")
            else:
                url=None
        else:
            url=None
    return All_Products

# (IKI Crawler funkcijos categorie_grabber ir subcategorie_grabber lieka nepakeistos)
# [Čia tavo kodas tęsiasi iki IKI_crawler...]

headers2 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.lastmile.lt",
    "Referer": "https://www.lastmile.lt/",
    "Cookie": "__consent=%5B%22required%22%5D; __session=..." # Nukirpta dėl vietos, naudok savo originalų
}

slugs=[ "Vaisiai-ir-uogos", "Darzoves-ir-grybai", "Pienas", "Sviestas-margarinas-riebalai", "Suris", "Varskes-produktai", "Grietine-ir-grietinele", "Jogurtai-ir-desertai", "Kiausiniai", "Kefyras-rugpienis-pasukos", "Majonezas-ir-padazai", "Augaliniai-ir-be-laktozes-produktai", "Svieziai-kepti-duonos-gaminiai", "Duona", "Duonos-pakaitalai", "Dziuvesiai-meduoliai-riestainiai-ir-javinukai", "Bandeles-spurgos", "Konditerija", "Sviezia-mesa", "Sviezia-paukstiena", "Mesos-ir-paukstienos-gaminiai", "Marinuota-mesa-ir-paukstiena", "Sviezia-zuvis-ir-juru-gerybes", "Zuvies-gaminiai", "Kulinarija", "Augaliniai-mesos-pakaitalai", "Meksikos-virtuve", "Japonijos-virtuve", "Kinijos-virtuve", "Saldytos-darzoves-uogos-vaisiai-ir-grybai", "Ledai-ir-ledo-kubeliai", "Saldyti-kulinarijos-ir-konditerijos-gaminiai", "Saldyta-zuvis-ir-juru-gerybes", "Kava-kakava-kavos-gerimai", "Marinuotas-konservuotas-maistas", "Aliejus-ir-actas", "Cukrus-saldikliai-medus", "Arbata", "Makaronai", "Miltai", "Kruopos", "Ankstines-darzoves", "Padazai-ir-uztepeles", "Sausi-pusryciai-dribsniai-ir-javainiu-batoneliai", "Riesutai-seklos-dziovinti-vaisiai-uogos", "Greitai-paruosiamas-maistas", "Maisto-ruosimo-priedai", "Prieskoniai", "Gaivieji-gerimai", "Vanduo", "Sultys-nektarai-ir-sulciu-gerimai", "Energiniai-gerimai", "Saldumynai", "Sausainiai-ir-vafliai", "Uzkandziai", "Gerimu-gidas", "Alus", "Vynas-ir-sampanas", "Sidras-ir-kokteiliai", "Stiprieji-alkoholiniai-gerimai", "Nealkoholiniai-gerimai", "Kudikiu-maistas-maistas-vaikams", "Baltyminiai-batoneliai", "Vitaminai-ir-mineralai", "Kiti-papildai" ]

global_categorys=[]
IKI_url_categories="https://searchservice-952707942140.europe-north1.run.app/categories"

def categorie_grabber(url):
    for slug in slugs:
        payload_subcategorie={"isUsingCache": True, "params":{"chainIds": ["CvKfTzV4TN5U8BTMF1Hl"], "show": True, "slug": slug, "type": "categories", "slim": None}}
        response=requests.post(url, headers=headers2,json=payload_subcategorie)
        if response.status_code == 200:
            data=response.json()
            if "data" in data:
                node_list=data.get('data')
                if node_list:
                    node=node_list[0]
                    category=node.get('id')
                    if category:
                        global_categorys.append(category)
    print("category grabber done")

categoryIds=[]
def subcategorie_grabber(url):
    payload_cat_all={"isUsingCache": True, "params":{"chainIds": ["CvKfTzV4TN5U8BTMF1Hl"], "show": True, "type": "categories", "slim": None}}
    response=requests.post(url,headers=headers2, json=payload_cat_all)
    if response.status_code == 200:
        data=response.json()
        jsonfile_content = data.get('data')
        for category in jsonfile_content:
            parent_id=category.get('parentId')
            if parent_id!=0 and parent_id and parent_id in global_categorys:
                 categoryIds.append(category.get('id'))
    print("sub category grabber done")

IKI_url_API="https://searchservice-952707942140.europe-north1.run.app/v1/frontend-products"

def IKI_crawler(url):
    limit=60; fromIndex=0; All_Products=[]
    payload={"fromIndex":0, "limit":60, "chainIds": ["CvKfTzV4TN5U8BTMF1Hl"], "storeIds": ["CvKfTzV4TN5U8BTMF1Hl_700"], "params":{"categoryIds": categoryIds, "filter":{}, "hasLoyaltyCard":False, "isActive":True, "isApproved":True, "isUsingStock":True, "sort":"karma", "type": "view_products"}}
    while True:
        if len(All_Products) >= 10: return All_Products[:10]
        payload["fromIndex"]=fromIndex
        response=requests.post(url,headers=headers2, json=payload)
        if response.status_code == 200:
            data=response.json()
            if "products" in data:
                if len(data['products'])==0: return All_Products
                for item in data.get('products'):
                    if len(All_Products) >= 10: return All_Products
                    product=item.get("frontEndProduct", {})
                    if product.get("isInStock") and product.get("chainId")=="CvKfTzV4TN5U8BTMF1Hl":
                        name=str(product.get("name").get("lt"))
                        weight_kg=str(product.get('conversionValue',0))
                        conversion_measure=str(product.get('conversionMeasure',0))
                        protein=str(product.get('nutrition').get('protein',0))
                        fat=str(product.get('nutrition').get('fat',0))
                        sugar=str(product.get('nutrition').get('sugar',0))
                        salt=str(product.get('nutrition').get('salt',0))
                        carbs=str(product.get('nutrition').get('carbs',0))
                        calories=str(product.get('nutrition').get('energy',0))
                        calories_re=re.search(r'(\d+\.?\,?\d*)\s*kcal', calories.lower())
                        if calories_re: calories=calories_re.group(1)
                        img_url=str(product.get('photoUrl',0))
                        price=str(product.get('actualPrice',0))
                        price_discount=str(product.get('loyaltyPrice',0))
                        product_url=""
                        for slug in product.get('slugs',[]):
                            if re.search(r'\d+$',slug ):
                                product_url="https://www.lastmile.lt/chain/IKI/product/"+str(slug)
                                break
                        products_obj=Product.Product(name,weight_kg,conversion_measure,protein,fat,sugar,salt,carbs,calories,product_url,img_url,price,price_discount)
                        All_Products.append(products_obj)
        fromIndex=fromIndex+limit

# --- AUTOMATIZACIJOS LOGIKA ---

def start_scraping_job():
    tracemalloc.start()
    print(f"[{datetime.now()}] Skreipinimas pradedamas...")
    
    # RIMI dalis (per visus URL)
    all_rimi = []
    for url in urls:
        rimi_products = Rimi_crawler(url)
        all_rimi.extend(rimi_products)
        if len(all_rimi) >= 20: break # Apribojimas bandymui
    save_products_to_db(all_rimi, "Rimi")
    
    # IKI dalis
    categorie_grabber(IKI_url_categories)
    subcategorie_grabber(IKI_url_categories)
    all_iki = IKI_crawler(IKI_url_API)
    save_products_to_db(all_iki, "Iki")
    
    print(f"[{datetime.now()}] Visi duomenys sėkmingai atnaujinti.")

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    print("[Atminties naudojimo Top 10]")
    for stat in top_stats[:10]:
        print(stat)

if __name__ == "__main__":
    # Nustatome norimą laiką
    # Docker laikas atsilieka 3 valandom todel reikia
    TARGET_HOUR = 6
    TARGET_MINUTE = 30
     # Run once immediately on startup so the table/data exists right away
    print("=== Running initial scrape on startup... ===", flush=True)
    start_scraping_job()
    print(f"=== Skraperis paleistas. Laukiama {TARGET_HOUR}:{TARGET_MINUTE} ===", flush=True)
    
    while True:
        now = datetime.now()
        
        # Tikriname, ar dabartinė valanda ir minutė sutampa su nustatyta
        if now.hour == TARGET_HOUR and now.minute == TARGET_MINUTE:
            try:
                print(f"[{now}] Laikas pasiektas! Pradedamas skrapinimas...", flush=True)
                start_scraping_job()
                print(f"[{now}] Darbas baigtas sėkmingai.", flush=True)
                
                # Svarbu: pamiegame 60s, kad tą pačią minutę nepaleistų dar kartą
                time.sleep(60) 
            except Exception as e:
                print(f"[{now}] Klaida vykdant darbą: {e}", flush=True)
                time.sleep(60)
        
        # Tikriname laiką kas sekundę, kad nepraleistume minutės starto
        time.sleep(1)