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


#gets all the products form the Rimi store page
def Rimi_crawler(url):
    response=requests.get(url,headers=headers)
    #print(response.text)
    soup=BeautifulSoup((response.content),"html.parser")
    i=0
    checknextpage=0
    All_Products=[]
    while url!=None: #goes throught each page of the site
    
    
        for item in soup.find_all("li", class_="product-grid__item"):# goes through each product on the page
            
            
            #writes produkt url
            i=i+1
            weight=img_url=name=protein=fat=sugar=salt=carbs=calories="0"
            prod_ulr=item.find("a", class_="card__url js-gtm-eec-product-click")
            if not prod_ulr:
                continue
            print(str(i)+" https://www.rimi.lt"+str(prod_ulr.get("href")))

            #finds image url
            img=item.find("img")
            if img:
                img_url=img.get("data-src")
                #print(img_url)
            #find name
            div_name=item.find("div", class_="js-product-container card -horizontal-for-mobile")
            if div_name:
                name=div_name.get("data-gtms-banner-title")
                #print(name)
            #find weight
            conversion_measure="" #unite of measure like kg,l,g,ml
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
                   

            response=requests.get("https://www.rimi.lt"+str(prod_ulr.get("href")),headers=headers)# creates product link
           
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
                        #print(str(euros)+" "+str(cents))
                        if cents_re and euros_re:
                            discountedprice=str(euros_re.group(0))+"."+str(cents_re.group(0))
                   if price_class and "price" in price_class:       
                       euro_re=re.search(r'\d+',str(p.find("span")))
                       cent_re=re.search(r'\d+',str(p.find("sup")))
                       if cent_re and euro_re:
                           actualprice=str(euro_re.group(0))+"."+str(cent_re.group(0))
           
                       oldprice=p.find("p", class_="price__old-price")
                       #print(oldprice)
                       if oldprice:
              
                           discountedprice=actualprice
                           actualprice_re=re.search(r'\d+\.?\,?\d*',str(oldprice))
                           if actualprice_re:
                               actualprice=actualprice_re.group(0)
        

            # Finds tables that are turned into scrips 
            scripts = soup2.find_all("script")
            
            for script in scripts:
                if script.string and "product__table" in script.string:
                    # 2. We found the hidden data! 
                    # We need to clean the "escaped" characters so it looks like real HTML
                    # \u0022 is " and \/ is /
                    hidden_html = script.string.replace('\\u0022', '"').replace('\\/', '/')
        
                    # 3. Create a NEW soup just for this hidden chunk
                    inner_soup = BeautifulSoup(hidden_html, "html.parser")
                   
                    # 4. Now search for your table inside the inner_soup
                    table_div = inner_soup.find("div", class_="product__table")
                    
                    if table_div:
                        #print("Successfully found the hidden table!")
                        rows = table_div.find_all("tr")
                        for row in rows:
                            cells = row.find_all("td")
                            if len(cells) == 2:
                                label=cells[0].text.strip().lower()
                                if re.search(r'energin.*?vert', label, re.IGNORECASE):#calories
                                    
                                    value=re.search(r'(\d+\.?\d*)\s*kcal', cells[1].text.strip().lower())
                                    if value:
                                        #print(f"{cells[0].text}: {value.group(1)}")
                                        calories=value.group(1)
                                if re.search(r'riebalai', label, re.IGNORECASE):#fats
                                   
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        #print(f"{cells[0].text}: {value.group(1)}")
                                        fat=value.group(1)
                                if re.search(r'angliavandeniai', label, re.IGNORECASE):#carbohydrates
                                   
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        #print(f"{cells[0].text}: {value.group(1)}")
                                        carbs=value.group(1)
                                if re.search(r'baltymai', label, re.IGNORECASE):#proteins
                                   
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        #print(f"{cells[0].text}: {value.group(1)}")
                                        protein=value.group(1)
                                if re.search(r'druska', label, re.IGNORECASE):#salt
                                   
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        #print(f"{cells[0].text}: {value.group(1)}")
                                        salt=value.group(1)
                                if re.search(r'i.*?cukr', label, re.IGNORECASE):#sugar
                                    
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        #print(f"{cells[0].text}: {value.group(1)}")
                                        sugar=value.group(1)
                    if(actualprice!="0" or discountedprice!="0"):                    
                        product_obj=Product.Product(str(name),str(weight),str(conversion_measure),str(protein),str(fat),str(sugar),str(salt),str(carbs),str(calories),"https://www.rimi.lt"+str(prod_ulr.get("href")),str(img_url),actualprice,discountedprice)
                        All_Products.append(product_obj)
                    
      
        
        nextpage=soup.find_all("li", class_="pagination__item -chevron")
        nextpage=nextpage[1]#finds the next page button, if it exists
        if nextpage:
            
            anchor=nextpage.find("a")
    
            if anchor:
                checknextpage=checknextpage+1
                relative=anchor.get("href")
                url="https://www.rimi.lt"+str(relative)#creates full link to the next page
                #print(str(checknextpage)+url)
                response=requests.get(url)
                soup=BeautifulSoup((response.content),"html.parser")
                
            else:
                url=None

        else:
            url=None
            
    return All_Products
""" if __name__ == "__main__":
    # 1. Gauname aplanką, kuriame yra šis Crawler.py failas
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 2. Sujungiame tą aplanką su failo pavadinimu
    file_path = os.path.join(current_dir, "products.json")
    All_Products=[]

    for url in urls:
        All_Products=All_Products+Rimi_crawler(url)
        break
    data_to_json=[product.__dict__ for product in All_Products]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data_to_json, f, ensure_ascii=False, indent=4) """



  
#------------------------------IKI CRAWLER---------------------------------
headers2 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.lastmile.lt",
    "Referer": "https://www.lastmile.lt/",
    "Cookie": "__consent=%5B%22required%22%5D; __session=eyJhbGciOiJSUzI1NiIsImtpZCI6ImEyZGZiOGEzOGI1MmQ5ZjA5ZWRjYWE1MDcwYTBlOGYwYTllMDk4YmEiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiUGlqdXNzdmVudCIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NKZU5RVm9keUowUEtMV3FDVG94SGwzWG9xcE56TXlQLVE2S3ljZDEwbHJWUlNZeW5vPXM5Ni1jIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2xhc3RtaWxlLWRlbGl2ZXJ5IiwiYXVkIjoibGFzdG1pbGUtZGVsaXZlcnkiLCJhdXRoX3RpbWUiOjE3NzIyOTI5NzksInVzZXJfaWQiOiJUWm9EcUdCNWROVXdneWpnRGdicUdDd0l1M3kxIiwic3ViIjoiVFpvRHFHQjVkTlV3Z3lqZ0RnYnFHQ3dJdTN5MSIsImlhdCI6MTc3MzU3NzU4MiwiZXhwIjoxNzczNTgxMTgyLCJlbWFpbCI6InBpanVzc3ZlbnRAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZ29vZ2xlLmNvbSI6WyIxMTAwMjk5NTU2NTIxODI3NzExOTYiXSwiZW1haWwiOlsicGlqdXNzdmVudEBnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJnb29nbGUuY29tIn19.KuAaukcnhvzzJFFck4FjuEg9OFe2CvYK_LsuuoAeDt2njoIuHLhJIyZ1GVM0IYOk61aoNfTYphtXT5_CXWswFmbxzHAHgRUJSsS7vTLC5Vzp_cRJoIL3ihUibxpJLYvI4xCv1o0mv1e6H1z2TPLJhSvtvOPGKLoANZJiet5qIX1TaMSfZTQ8Kya1KRVGxgiFRgAihI9qg7YhjWV0FGDqhcd3B6hh1jClvwYf7KTYrJJeOKISbMgFu21lmv2dFaDAl-YXp6gviN98eNJJeNP8lITA3Bg-2XrywuVQvC3iC_6KLNVoJozGh-95oxElx9-38rC_9IguGVypF7b12EuYrQ"
}

slugs=[
    "Vaisiai-ir-uogos",
    "Darzoves-ir-grybai",
    "Pienas",
    "Sviestas-margarinas-riebalai",
    "Suris",
    "Varskes-produktai",
    "Grietine-ir-grietinele",
    "Jogurtai-ir-desertai",
    "Kiausiniai",
    "Kefyras-rugpienis-pasukos",
    "Majonezas-ir-padazai",
    "Augaliniai-ir-be-laktozes-produktai",
    "Svieziai-kepti-duonos-gaminiai",
    "Duona",
    "Duonos-pakaitalai",
    "Dziuvesiai-meduoliai-riestainiai-ir-javinukai",
    "Bandeles-spurgos",
    "Konditerija",
    "Sviezia-mesa",
    "Sviezia-paukstiena",
    "Mesos-ir-paukstienos-gaminiai",
    "Marinuota-mesa-ir-paukstiena",
    "Sviezia-zuvis-ir-juru-gerybes"
    "Zuvies-gaminiai",
    "Kulinarija",
    "Augaliniai-mesos-pakaitalai",
    "Meksikos-virtuve",
    "Japonijos-virtuve",
    "Kinijos-virtuve",
    "Saldytos-darzoves-uogos-vaisiai-ir-grybai",
    "Ledai-ir-ledo-kubeliai",
    "Saldyti-kulinarijos-ir-konditerijos-gaminiai",
    "Saldyta-zuvis-ir-juru-gerybes",
    "Kava-kakava-kavos-gerimai",
    "Marinuotas-konservuotas-maistas",
    "Aliejus-ir-actas",
    "Cukrus-saldikliai-medus",
    "Arbata",
    "Makaronai",
    "Miltai",
    "Kruopos",
    "Ankstines-darzoves",
    "Padazai-ir-uztepeles",
    "Sausi-pusryciai-dribsniai-ir-javainiu-batoneliai",
    "Riesutai-seklos-dziovinti-vaisiai-uogos",
    "Greitai-paruosiamas-maistas",
    "Maisto-ruosimo-priedai",
    "Prieskoniai",
    "Gaivieji-gerimai",
    "Vanduo",
    "Sultys-nektarai-ir-sulciu-gerimai",
    "Energiniai-gerimai",
    "Saldumynai",
    "Sausainiai-ir-vafliai",
    "Uzkandziai",
    "Gerimu-gidas",   
    "Alus",
    "Vynas-ir-sampanas",
    "Sidras-ir-kokteiliai",
    "Stiprieji-alkoholiniai-gerimai",
    "Nealkoholiniai-gerimai",
    "Kudikiu-maistas-maistas-vaikams",
    "Baltyminiai-batoneliai",
    "Vitaminai-ir-mineralai",
    "Kiti-papildai"
    ]
#this is a payload of a file which contains all subcategorys
payload_categories_all={
    "isUsingCache": True,
    "params":{
        "chainIds": ["CvKfTzV4TN5U8BTMF1Hl"],
        "show": True,
        "type": "categories",
        "slim": None
    }
}



global_categorys=[]
IKI_url_categories="https://searchservice-952707942140.europe-north1.run.app/categories"
#Gets categorys of products like "Milk products"
def categorie_grabber(url):
    for slug in slugs:
        #print(slug)
        payload_subcategorie={
            "isUsingCache": True,
            "params":{
                "chainIds": ["CvKfTzV4TN5U8BTMF1Hl"],
                "show": True,
                "slug": slug,
                "type": "categories",
                "slim": None
            }
        }
        response=requests.post(url, headers=headers2,json=payload_subcategorie)
        if response.status_code == 200:
            data=response.json()
            #print(data)
            if "data" in data:
                node_list=data.get('data')
                if node_list:
                    node=node_list[0]
                    category=node.get('id')
                    if category:
                        #print(category)
                        global_categorys.append(category)
    # for g_category in global_categorys:
    #         print(g_category)
    print("category grabber done")
                                        
#categorie_grabber(IKI_url_categories)

categoryIds=[]
#Gets subcategorys of products. "Milk procducts" -> "Milk", "Cheeses", "Ice cream" ...
def subcategorie_grabber(url):
    response=requests.post(url,headers=headers2, json=payload_categories_all)
    
    if response.status_code == 200:
        data=response.json()
        jsonfile_content = data.get('data')

   
        for category in jsonfile_content:
            #print(category)
            
            parent_id=category.get('parentId')
            #print(parent_id)
            if parent_id!=0 and parent_id and parent_id in global_categorys:
                 categoryIds.append(category.get('id'))
                # print(category.get('id'))
    print("sub category grabber done")
    
#subcategorie_grabber(IKI_url_categories)

payload={
    "fromIndex":0,
    "limit":60,
    "chainIds": ["CvKfTzV4TN5U8BTMF1Hl"],
    "storeIds": ["CvKfTzV4TN5U8BTMF1Hl_700"],
    "params":{
        
        "categoryIds": categoryIds,
        "filter":{},
        "hasLoyaltyCard":False,
        "isActive":True,
        "isApproved":True,
        "isUsingStock":True,
        "sort":"karma",
        "type": "view_products"
    }
    
    
}


IKI_url_API="https://searchservice-952707942140.europe-north1.run.app/v1/frontend-products"

#Gets the products from the IKI website
def IKI_crawler(url):
   
    #print(response.text)
    i=0
    limit=60
    fromIndex=0
    All_Products=[]
  
    while True:
        payload["fromIndex"]=fromIndex
        payload["limit"]=limit
        response=requests.post(url,headers=headers2, json=payload)
        
        if response.status_code == 200:
      
            # with open("python_pamatytas_skriptas.txt", "w", encoding="utf-8")as f:
            #     f.writelines(response.text)

            data=response.json()

            if "products" in data:
                print(len(data['products']))
                if len(data['products'])==0:
                      return All_Products                 
                i=0
                for item in data.get('products'):
                    if i > 15:
                        break

                    weight_kg="1"
                    protein=fat=sugar=salt=carbs=calories=conversion_measure=price=price_discount="0"
                    product=item.get("frontEndProduct", {})
                    if product.get("isInStock") and product.get("chainId")=="CvKfTzV4TN5U8BTMF1Hl":
                        #print(str(i)+" "+str(product.get("name").get("lt")))
                        # print(f"\nBaltymai: {product.get('nutrition').get('protein')} \nRiebalai: {product.get('nutrition').get('fat')} \nEnergetine verte: {product.get('nutrition').get('energy')} \nCukrus: {product.get('nutrition').get('sugar')}")
                        # print(f"Angliavandeniai: {product.get('nutrition').get('carbs')} \nDruska: {product.get('nutrition').get('salt')} \n")
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
                        if calories_re:
                             calories=calories_re.group(1)

                        img_url=str(product.get('photoUrl',0)) 
                        price=str(product.get('actualPrice',0))
                        price_discount=str(product.get('loyaltyPrice',0))
                        #gets product url
                        for slug in product.get('slugs',[]):
                            correct_slug=re.search(r'\d+$',slug )
                   
                            if correct_slug:
                                product_url="https://www.lastmile.lt/chain/IKI/product/"+str(slug)
                                print(product_url)
                                break

                    
                        print(f"\n Svoris KG: {weight_kg}")
                        print(f"\n Nuotraukos nuoroda: {product.get('photoUrl')}")
                        print('-'*50)
                        
                        products_obj=Product.Product(name,weight_kg,conversion_measure,protein,fat,sugar,salt,carbs,calories,product_url,img_url,price,price_discount)

                        All_Products.append(products_obj)
        
      
        fromIndex=fromIndex+limit


""" if __name__ == "__main__":
    # 1. Gauname aplanką, kuriame yra šis Crawler.py failas
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 2. Sujungiame tą aplanką su failo pavadinimu
    file_path = os.path.join(current_dir, "IKI_products.json")

    All_Products2=[]
    All_Products2=IKI_crawler(IKI_url_API)
    #Writes products into a file
    if All_Products2:
        data_to_json2=[product.__dict__ for product in All_Products2]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_json2, f, ensure_ascii=False, indent=4) """
            

#----------------Maxima crawler-----------------
url_maxima=[
    "https://barbora.lt/pieno-gaminiai-kiausiniai-ir-majonezas",
    "https://barbora.lt/darzoves-ir-vaisiai",
    "https://barbora.lt/duonos-gaminiai-ir-konditerija",
    "https://barbora.lt/mesa-zuvis-ir-kulinarija",
    "https://barbora.lt/bakaleja",
    "https://barbora.lt/saldytas-maistas",
    "https://barbora.lt/gerimai"

]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def Maxima_html_crawler(base_url):
    All_Products = []
    page_number = 1
    
    # SAUGIKLIS: Sekame šioje kategorijoje jau matytų produktų URL adresus
    seen_product_urls = set()
    
    print(f"\n=========================================")
    print(f"STARTING CATEGORY: {base_url}")
    print(f"=========================================")

    while True:
        # 1. Sukuriamas dinaminis puslapio URL adresas
        paginated_url = f"{base_url}?page={page_number}"
        print(f"\n--- Scraping Page {page_number} ---")
        print(f"URL: {paginated_url}")
        
        response = requests.get(paginated_url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch the HTML view. Status code: {response.status_code}")
            break # Sustabdomas ciklas, jei puslapis neatsidaro
            
        html_content = response.text
        
        # Ištraukiame JSON masyvą iš puslapio kodo
        match = re.search(r'window\.b_productList\s*=\s*(\[[\s\S]*?\]);', html_content)
        if not match:
            print("Could not locate metadata variable inside the page HTML scripts. Ending category loop.")
            break 
            
        try:
            json_data_string = match.group(1)
            products_data = json.loads(json_data_string)
            
            # 1-asis SAUGIKLIS: Jeigu masyvas visiškai tuščias, baigėme puslapius
            if not products_data:
                print(f"No more products found (Empty Array). Finished crawling at page {page_number - 1}.")
                break
                
            print(f"Successfully extracted {len(products_data)} products from page {page_number}.")
            
            # Kintamasis, kuris stebės, ar šiame puslapyje radome nors vieną NAUJĄ prekę
            has_new_items_on_page = False
            
            for item in products_data:
                # Produkto URL generavimas
                slug = item.get("Url", "")
                product_url = f"https://barbora.lt/produktai/{slug}" if slug else ""
                
                # 2-asis SAUGIKLIS (Svarbiausias): Jei šį produktą jau matėme ankstesniuose puslapiuose, praleidžiame jį
                if product_url in seen_product_urls:
                    continue
                
                # Jei produktas naujas – pažymime jį kaip matytą ir leidžiame puslapio ciklui tęstis
                seen_product_urls.add(product_url)
                has_new_items_on_page = True
                
                # Basic Metadata Extraction
                name = str(item.get("title", ""))
                print(f"Parsing product: {name}")
                
                weight_kg = "1"
                conversion_measure = "vnt"
                
                if name:
                    weight_re = re.search(r'(\d+[,.]?\d*)\s*(g|kg|l|ml|vnt\.?)\b', name, re.IGNORECASE)
                    if weight_re:
                        unit = weight_re.group(2).lower()
                        value_str = weight_re.group(1).replace(",", ".")
                        
                        if unit in ["kg", "l"]:
                            weight_kg = value_str
                            conversion_measure = unit
                        elif unit in ["g", "ml"]:
                            weight_kg = str(float(value_str) / 1000)
                            conversion_measure = unit
                        elif "vnt" in unit:
                            weight_kg = value_str
                            conversion_measure = "vnt"
                
                image_url = item.get("big_image", "") 
                
                # Price & Discount Logic
                item_price = item.get("price", 0.0)
                item_retail_price = item.get("retail_price")
                
                if item_retail_price is not None:
                    price = str(item_retail_price)
                    price_discount = str(item_price)
                else:
                    price = str(item_price)
                    price_discount = "0"

                # Initialize default macronutrients values
                protein = "0"
                fat = "0"
                sugar = "0"
                salt = "0"
                carbohydrates = "0"
                calories_kcal = "0"
                
                # Request Product Page & Extract Nutrition Facts
                if product_url:
                    try:
                        time.sleep(0.2) # Saugus tarpas prieš atidarant detalų puslapį
                        
                        detail_response = requests.get(product_url, headers=headers,timeout=10)
                        if detail_response.status_code == 200:
                            product_match = re.search(r'window\.product\s*=\s*(\{[\s\S]*?\});\s*</script>', detail_response.text)
                            
                            if product_match:
                                product_json_str = product_match.group(1)
                                product_info = json.loads(product_json_str)
                                
                                # STRATEGY A: Target structured 'nutrients' block
                                nutrient_list = product_info.get("nutrients", [])
                                
                                if nutrient_list:
                                    for nutrient in nutrient_list:
                                        nutrient_name = str(nutrient.get("Name", "")).strip().lower()
                                        amounts = nutrient.get("Amounts", [])
                                        
                                        if not amounts:
                                            continue
                                            
                                        if "energin" in nutrient_name:
                                            for amt in amounts:
                                                if amt.get("UnitName") == "Kcal":
                                                    calories_kcal = str(amt.get("Amount", "0"))
                                        elif "riebal" in nutrient_name:
                                            fat = str(amounts[0].get("Amount", "0"))
                                        elif "angliavanden" in nutrient_name:
                                            carbohydrates = str(amounts[0].get("Amount", "0"))
                                        elif "cukr" in nutrient_name:
                                            sugar = str(amounts[0].get("Amount", "0"))
                                        elif "baltym" in nutrient_name:
                                            protein = str(amounts[0].get("Amount", "0"))
                                        elif "drusk" in nutrient_name:
                                            salt = str(amounts[0].get("Amount", "0"))
                                
                                # STRATEGY B: Fallback to plain text attributes for raw produce
                                else:
                                    attributes_obj = product_info.get("attributes", {})
                                    attr_list = attributes_obj.get("list", []) if isinstance(attributes_obj, dict) else []
                                    
                                    for attr in attr_list:
                                        attr_id = str(attr.get("id", "")).strip().lower()
                                        attr_val = str(attr.get("value", "")).strip()
                                        
                                        if not attr_id or not attr_val: 
                                            continue
                                        
                                        num_match = re.search(r'(\d+[,.]?\d*)', attr_val)
                                        extracted_val = num_match.group(1).replace(",", ".") if num_match else "0"
                                        
                                        if "energin" in attr_id:
                                            kcal_match = re.search(r'(\d+[,.]?\d*)\s*Kcal', attr_val, re.IGNORECASE)
                                            if kcal_match:
                                                calories_kcal = kcal_match.group(1).replace(",", ".")
                                        elif "riebal" in attr_id and "sočiosios" not in attr_id:
                                            fat = extracted_val
                                        elif "angliavanden" in attr_id:
                                            carbohydrates = extracted_val
                                        elif "cukr" in attr_id:
                                            sugar = extracted_val
                                        elif "baltym" in attr_id:
                                            protein = extracted_val
                                        elif "drusk" in attr_id:
                                            salt = extracted_val
                                            
                                print(f"-> Macros found - Cal: {calories_kcal}, P: {protein}, F: {fat}, C: {carbohydrates}")
                            else:
                                print("-> Warning: Could not locate window.product object.")
                        else:
                            print(f"-> Warning: Failed loading detail view. Status code: {detail_response.status_code}")
                            time.sleep(5)
                    except Exception as detail_err:
                        print(f"-> Error crawling individual product detail page: {detail_err}")

                # Instantiation
                product_obj = Product.Product(
                    name, weight_kg, conversion_measure, protein, fat, 
                    sugar, salt, carbohydrates, calories_kcal, 
                    product_url, image_url, price, price_discount
                )
                All_Products.append(product_obj)
            
            # BEGALINIO CIKLO STABDYS: Jeigu visos prekės šiame puslapyje jau buvo nuskaitytos anksčiau,
            # tai reiškia, kad puslapis mus nukreipė atgal į pradžią arba nebėra naujo turinio.
            if not has_new_items_on_page:
                print(f"Detected duplicate page content/wrap-around redirect. Safely stopping at page {page_number}.")
                break

        except Exception as e:
            print("Regex matched, but failed parsing to clean object:", e)
            break 

        # Einame į sekantį puslapį
        page_number += 1
        time.sleep(1) # Saugus tarpas tarp puslapių užklausų
        
    return All_Products



""" if __name__ == "__main__":
    # 1. Gauname aplanką, kuriame yra šis Crawler.py failas
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 2. Sujungiame tą aplanką su failo pavadinimu
    file_path = os.path.join(current_dir, "Maxima_products.json")

    All_Products2=[]
    for url in url_maxima:
        All_Products2=All_Products2+Maxima_html_crawler(url)
        break
    #Writes products into a file
    if All_Products2:
        data_to_json2=[product.__dict__ for product in All_Products2]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_json2, f, ensure_ascii=False, indent=4) """

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
        break
    save_products_to_db(all_rimi, "Rimi")
    
    # IKI dalis
    categorie_grabber(IKI_url_categories)
    subcategorie_grabber(IKI_url_categories)
    all_iki = IKI_crawler(IKI_url_API)
    save_products_to_db(all_iki, "Iki")
    
   

    #Maximos dalis (per visus URL)
    all_maxima = []
    for url in url_maxima:
        maxima_products = Maxima_html_crawler(url)
        all_maxima.extend(maxima_products)
        break
    save_products_to_db(all_maxima, "Maxima")

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