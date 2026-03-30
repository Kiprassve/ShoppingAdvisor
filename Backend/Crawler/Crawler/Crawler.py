from ast import List
from calendar import c
from dataclasses import dataclass
from os import name
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

from . import Product

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
            if i >= 10:
                break
            
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
                        print("Successfully found the hidden table!")
                        rows = table_div.find_all("tr")
                        for row in rows:
                            cells = row.find_all("td")
                            if len(cells) == 2:
                                label=cells[0].text.strip().lower()
                                if re.search(r'energin.*?vert', label, re.IGNORECASE):#calories
                                    
                                    value=re.search(r'(\d+\.?\d*)\s*kcal', cells[1].text.strip().lower())
                                    if value:
                                        print(f"{cells[0].text}: {value.group(1)}")
                                        calories=value.group(1)
                                if re.search(r'riebalai', label, re.IGNORECASE):#fats
                                   
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        print(f"{cells[0].text}: {value.group(1)}")
                                        fat=value.group(1)
                                if re.search(r'angliavandeniai', label, re.IGNORECASE):#carbohydrates
                                   
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        print(f"{cells[0].text}: {value.group(1)}")
                                        carbs=value.group(1)
                                if re.search(r'baltymai', label, re.IGNORECASE):#proteins
                                   
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        print(f"{cells[0].text}: {value.group(1)}")
                                        protein=value.group(1)
                                if re.search(r'druska', label, re.IGNORECASE):#salt
                                   
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        print(f"{cells[0].text}: {value.group(1)}")
                                        salt=value.group(1)
                                if re.search(r'i.*?cukr', label, re.IGNORECASE):#sugar
                                    
                                    value=re.search(r'(\d+\.?\d*)\s*g', cells[1].text.strip().lower())
                                    if value:
                                        print(f"{cells[0].text}: {value.group(1)}")
                                        sugar=value.group(1)
                    product_obj=Product.Product(str(name),str(weight),str(conversion_measure),str(protein),str(fat),str(sugar),str(salt),str(carbs),str(calories),"https://www.rimi.lt"+str(prod_ulr.get("href")),str(img_url),actualprice,discountedprice)
                    All_Products.append(product_obj)
                    
        if i >= 10:
            break
        
        nextpage=soup.find_all("li", class_="pagination__item -chevron")
        nextpage=nextpage[1]#finds the next page button, if it exists
        if nextpage:
            
            anchor=nextpage.find("a")
    
            if anchor:
                checknextpage=checknextpage+1
                relative=anchor.get("href")
                url="https://www.rimi.lt"+str(relative)#creates full link to the next page
                print(str(checknextpage)+url)
                response=requests.get(url)
                soup=BeautifulSoup((response.content),"html.parser")
                
            else:
                url=None

        else:
            url=None
            
    return All_Products
# All_Products=[]

# for url in urls:
#     All_Products=All_Products+Rimi_crawler(url)
#     break


# data_to_json=[product.__dict__ for product in All_Products]

# with open("products.json", "w", encoding="utf-8") as f:
#     json.dump(data_to_json, f, ensure_ascii=False, indent=4)



# Sviestas="https://www.rimi.lt/e-parduotuve/lt/produktai/bakaleja/cukrus-ir-saldikliai/baltasis-cukrus-/cukrus-panevezio-plius-1-kg/p/148646"
# response=requests.get(Sviestas,headers=headers)
# soup2=BeautifulSoup((response.content),"html.parser")
# actualprice=discountedprice="0"
# price_div = soup2.find_all('div')

# for p in price_div:
#        cents=p.find("span", class_="cents")
#        euros=p.find("span", class_="major")
#        price_class=p.get('class')
#        if cents and euros:
#             cents_re=re.search(r'\d+',str(cents))
#             euros_re=re.search(r'\d+',str(euros))
#             #print(str(euros)+" "+str(cents))
#             if cents_re and euros_re:
#                 discountedprice=str(euros_re.group(0))+"."+str(cents_re.group(0))
#        if price_class and "price" in price_class:       
#            euro_re=re.search(r'\d+',str(p.find("span")))
#            cent_re=re.search(r'\d+',str(p.find("sup")))
#            if cent_re and euro_re:
#                actualprice=str(euro_re.group(0))+"."+str(cent_re.group(0))
           
#            oldprice=p.find("p", class_="price__old-price")
#            #print(oldprice)
#            if oldprice:
              
#                discountedprice=actualprice
#                actualprice_re=re.search(r'\d+\.?\,?\d*',str(oldprice))
#                if actualprice_re:
#                    actualprice=actualprice_re.group(0)
               
# if actualprice!="0" or discountedprice!="0":
#       print("Actual price:"+ str(actualprice))
#       print("Discounted price:"+str(discountedprice))
  
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
    limit=60;
    fromIndex=0;
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
                        # print(str(i)+" "+str(product.get("name").get("lt")))
                        # print(f"\nBaltymai: {product.get('nutrition').get('protein')} \nRiebalai: {product.get('nutrition').get('fat')} \nEnergetine verte: {product.get('nutrition').get('energy')} \nCukrus: {product.get('nutrition').get('sugar')}")
                        # print(f"Angliavandeniai: {product.get('nutrition').get('carbs')} \nDruska: {product.get('nutrition').get('salt')} \n")
                        name=str(product.get("name").get("lt"))                  
                        weight_kg=str(product.get('conversionValue',0))#-------------------------------------------pasiziureti kaip konvertonasi svoris nes jis pre json faila atrodo netikslus
                       
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

# All_Products2=[]
# All_Products2=IKI_crawler(IKI_url_API)
# #Writes products into a file
# if All_Products2:
#     data_to_json2=[product.__dict__ for product in All_Products2]
#     with open("IKI_products.json", "w", encoding="utf-8") as f:
#         json.dump(data_to_json2, f, ensure_ascii=False, indent=4)