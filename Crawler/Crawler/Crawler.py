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
from tkinter import N
from urllib import request, response
from xml.etree.ElementInclude import include
import requests
from bs4 import BeautifulSoup
import time

import Product

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
            if name:
                weight_re=re.search(r'(\d+[,.]?\d*)\s*(g|kg)\b',str(name),re.IGNORECASE)
                if weight_re:
                    if ("kg" or "l") in str(weight_re):
                        weight=weight_re.group(0).replace("kg","").replace("l","").replace(",",".")
                        weight=str(weight)
                    elif ("g" or "ml") in str(weight_re):
                         weight=float(weight_re.group(0).replace("g","").replace("ml","").replace(",","."))
                         weight=weight/1000
                         weight=str(weight)
                    
                
            

            response=requests.get("https://www.rimi.lt"+str(prod_ulr.get("href")),headers=headers)# creates product link
           
            soup2=BeautifulSoup((response.content),"html.parser")
           
            
        

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
                                    
                                    value=re.search(r'(\d+)\s*kcal', cells[1].text.strip().lower())
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
                    product_obj=Product.Product(str(name),str(weight),str(protein),str(fat),str(sugar),str(salt),str(carbs),str(calories),"https://www.rimi.lt"+str(prod_ulr.get("href")),str(img_url))
                    All_Products.append(product_obj)
                    
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


# data_to_json=[product.__dict__ for product in All_Products]

# with open("products.json", "w", encoding="utf-8") as f:
#     json.dump(data_to_json, f, ensure_ascii=False, indent=4)


#------------------------------IKI CRAWLER---------------------------------
headers2 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://www.lastmile.lt",
    "Referer": "https://www.lastmile.lt/",
    "Cookie": "__consent=%5B%22required%22%5D; __session=eyJhbGciOiJSUzI1NiIsImtpZCI6ImEyZGZiOGEzOGI1MmQ5ZjA5ZWRjYWE1MDcwYTBlOGYwYTllMDk4YmEiLCJ0eXAiOiJKV1QifQ.eyJuYW1lIjoiUGlqdXNzdmVudCIsInBpY3R1cmUiOiJodHRwczovL2xoMy5nb29nbGV1c2VyY29udGVudC5jb20vYS9BQ2c4b2NKZU5RVm9keUowUEtMV3FDVG94SGwzWG9xcE56TXlQLVE2S3ljZDEwbHJWUlNZeW5vPXM5Ni1jIiwiaXNzIjoiaHR0cHM6Ly9zZWN1cmV0b2tlbi5nb29nbGUuY29tL2xhc3RtaWxlLWRlbGl2ZXJ5IiwiYXVkIjoibGFzdG1pbGUtZGVsaXZlcnkiLCJhdXRoX3RpbWUiOjE3NzIyOTI5NzksInVzZXJfaWQiOiJUWm9EcUdCNWROVXdneWpnRGdicUdDd0l1M3kxIiwic3ViIjoiVFpvRHFHQjVkTlV3Z3lqZ0RnYnFHQ3dJdTN5MSIsImlhdCI6MTc3MzU3NzU4MiwiZXhwIjoxNzczNTgxMTgyLCJlbWFpbCI6InBpanVzc3ZlbnRAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImZpcmViYXNlIjp7ImlkZW50aXRpZXMiOnsiZ29vZ2xlLmNvbSI6WyIxMTAwMjk5NTU2NTIxODI3NzExOTYiXSwiZW1haWwiOlsicGlqdXNzdmVudEBnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJnb29nbGUuY29tIn19.KuAaukcnhvzzJFFck4FjuEg9OFe2CvYK_LsuuoAeDt2njoIuHLhJIyZ1GVM0IYOk61aoNfTYphtXT5_CXWswFmbxzHAHgRUJSsS7vTLC5Vzp_cRJoIL3ihUibxpJLYvI4xCv1o0mv1e6H1z2TPLJhSvtvOPGKLoANZJiet5qIX1TaMSfZTQ8Kya1KRVGxgiFRgAihI9qg7YhjWV0FGDqhcd3B6hh1jClvwYf7KTYrJJeOKISbMgFu21lmv2dFaDAl-YXp6gviN98eNJJeNP8lITA3Bg-2XrywuVQvC3iC_6KLNVoJozGh-95oxElx9-38rC_9IguGVypF7b12EuYrQ"
}
categoryIds= [
    "dXm2I2xsSMKPb34maRSX",
    "vDZoX4YoRHKJp2fiFp0d",
    "WcAZLXz93Js0Jti4IRo7",
    "lK7sODURO01CWsoaBEVe",
    "jKUM60P3woQgmfwI7EdR",
    "Gl7ZGnHk3b4dlw5nP2XE",
    "r6e4ozyqi48AyYVh6yPW",
    "P7xyuwbRtRE5FVFe1xr8",
    "1Z8mB9eITHSGo6S7Vz01",
    "ofL9nIXiarQ8oBAJeczM",
    "sJtx16jajsoTtamdixwy",
    "tUtPGLkqEjpQnMGRp4hI",
    "VX72LbxC8cV0A1Kh40k6",
    "iiZ8IdTP183Y2H5Mieyj",
    "G6cUl6GygNjWqvJnj1Rw",
    "gRRCe4XqwSfhKY9c3ygl",
    "rOtgAIampSoxg3lfxWX7",
    "AxUgDJHupD2BhqgTSuGv",
    "LRMkYuph2eNqPqVTDnac",
    "lMoQcXaqfDgPv0rllcyE",
    "M9G1xLe4Y6CWYWnjrT2t",
    "DFu7WwowDc7NeJNRIHmw",
    "BAUzlFdi73V44CgWeQ9T",
    "zf0UdfDZI7oGlDmMoe0N",
    "nj0qcjYDdDDcecG2qcQ7",
    "fUNsQqE3Rt95dL3IWgdw",
    "fiSeUG72B9JQMiphZC06",
    "7yB88JyhZw1hxNXhZG32",
    "QAoU95vgfvZPF7BLLSh4",
    "9YsMrrQpuJe56SPiP0Zd",
    "TQpiDVQhWL0dpEEzgV0t",
    "15b1Snd0TdfNIwE9P5XV",
    "PafltvJILZpo501sQbEC",
    "dZL8wt1mOjHNOZkqh5DC",
    "OkDgUGHMR4j8wG7fVKeO",
    "dDHn0eZM6k4CPMC47rLk",
    "iQgmASToRohvgevtcBQq",
    "usXF4Ah2lKqKGDg3M0Ny",
    "pbaSCswzsoLororHCKTj",
    "MG3ys0lt7bRcpQQDeOLv",
    "RhGsMC0pBD5Lag2p367t",
    "j7PaQxVpAojXjcP2aubj",
    "4HCgzg4zyGq2uYl40e4X",
    "DiDbnMeQyQq9Km6jIHM1",
    "fWfYEE7RlTxVdhU7pmjI",
    "lzRORVBpbndxRriEhlSf",
    "MvcqcuztAKFgQfSfWweB",
    "abJpUl28jW0TIHnmWN0N",
    "l2hN9yW3veWXDyX5dWIK",
    "DWDGJLEUeALikCN2z1hO",
    "pdSBzTsUbRlCJ4rq4HOQ",
    "G6UHTxJYYt3PsSP0zLUx",
    "HEBxisvA6rnSgaxXPHiV",
    "FiSrK34utqVQGwUF3mZ5",
    "ewKKA6euD2QXtN8OpYnu",
    "AI5QZEjMZPkhZZhyq7LT",
    "EszaJ78TDbl1N5amF8EQ",
    "QlCPgewLGjxXiKgK618k",
    "8CWlkbOIFYo55nSTKvkY",
    "rxe2ctZNWkaIIOOEz4dD",
    "zslp6wFZXMBnbs3z5gJm",
    "3A5KhxEeYVkri42HjSNY",
    "VYwJEmXLnnl1mCl8koWw",
    "S2DFsmzfkQYf26V8LA6e",
    "kz5nAWUAF3YcKxAJ4e0p",
    "Gxng8GF6GFlXkD5shnH4",
    "vOOf760CqLJjmqY3yTSN",
    "5WNlJkLLvdjHJqMITUSW",
    "HB3sSoAwMaM9g4YoGuN6",
    "czBwsUuHDAP9YpAkh4Ju",
    "3pRNrY5AYIZLm1qY1arO",
    "JnKjnc2RHoRVcFOTEoGy",
    "T3rFPOk8kBDYTFUg7XYu",
    "xg9OD77BU8UsFrogPAM5",
    "xYy4BmLDKRMbWCzXgVbn",
    "ChXkwTIkGyHsd0ZL7EaR",
    "cFkxXrf3DahHriNXY7lB",
    "tIKbONJT3Mt4lMwgHxyA",
    "Xzp8Ot3GTgNpkij7JI8E",
    "ki9n6JAMQHHAlZ8WMP4g",
    "WobGXsYgGfIgZySgEsEI",
    "IzfVHk828lkBXfYmLPgu",
    "EAfPrnueM0PWPYMK6XLg",
    "sjSCoKEcOdOfwny2FNCB",
    "VLR9MVzh4yl9T64R8CJW",
    "g7wncpIvXNer6M2tJR7g",
    "GwrtH4nMhpxJpPz55Tw8",
    "KVsrkwqXdpWAxjImI6Y5",
    "2s5zS71RUOLDzbmVwKuI",
    "f2rZx6Axh1Z8HzSPxT8W",
    "GU3MSN3YNMySX2LYqyjm",
    "ZHGCKTttlhWjOjXcrzIH",
    "CXmRw5Eqxzb8RvbLiRZE",
    "sZHTlenViMRnpDoTQsic",
    "H0DimxZcVzsqUtCMsVqR",
    "goimKMKmoFomTyxkl80U",
    "umtMTLSM7sexyc8W5UWM",
    "hU8jDhL2nJ2uzbRJWWqF",
    "FCzlIAjs7YRuwZ7Dndml",
    "0OTXNo0V1nkZEm4mxFKK",
    "KvVXIixA52dLzS2MDp3R",
    "ZuAF5wIp4TyuCAej5h08",
    "vLzKOwpPwPKSJP9ClWGR",
    "Yy8mBh2jhGbq7BKYM0RD",
    "4aYUZZggSGLBt5Q9ZZCO",
    "ZtQoUHk3GvqQJwO1aIOF",
    "K7gxcxORNBLcXnZ2QwdM",
    "kauBJx9e7XkdMrMDA8AX",
    "00cEfTUXdxst47m9XDcQ",
    "jg9uuNF49ImzvVIYXaDN",
    "jyhhntliQQJFIriJ9N7y",
    "bHPvWNaEJZ2hUyT5nURU",
    "XZIDR6SRgzhIB4R6cGWK",
    "yNobk8Iq0oUmYo88MItC",
    "SXrWFE6bRhLo5Mz5NAwx",
    "gxAXJ6Wfpsl2SPy99fCE",
    "9eMbjBClutLDgl6HlcD3",
    "pofnfxHblavBrHCBl5xR",
    "HBDXwli0mBhugo0iqhVR",
    "metp9W7tZC2vE6lQiSMQ",
    "gGLQTDyJw670zGBHKJx8",
    "t1Qk8MDRhhiAehFpEDYx",
    "IGu2c03QCiw5dLOqG0tG",
    "U3X18JkONqIqg1U9CTzR",
    "qFUpgotRsXiYNuVVAHtG",
    "xHBgbvXrEupivailDAS8",
    "12HR5jPkVk2sxRLQJtyz",
    "KtsFQYBmEbLxBVi0Utd6",
    "1Tnlo2jTrx0pnALhSfeI",
    "uwiJL8WFait2Z2RWTRbc",
    "AlvsSnkvmfD3mfkuksuB",
    "eDiIc605Da6q1NoCzH5P",
    "35A76I0uvpOk2Msdmlqq",
    "0X1KclEEiN8OcQIuvSHt",
    "LWKZIR9ZntRQaa78eRIg",
    "qnesDQ4GOIqVXEMkDpqT",
    "mzOQT6NlrdiJDgurC7uR",
    "fAqWT3XB2TR3J0dMuCY5",
    "ZRe8fXU0o4xcGPrxcQD1",
    "lcA7sr4g4v7O4KBWFd75",
    "ddUO6o0AQNPVwsedA5Fp",
    "DnmHLwg3yVQxSVg9e8JA",
    "AaSERD7AYE6Aq9Q8Pli7",
    "u0QNthmAA69JQyT1CVyr",
    "0JBbRCn9fGkuZsccjmJe",
    "WLIWmXfoLhL2VSqNH5LU",
    "FoWTh4XlUWcayAhRjRRQ",
    "bw8jiaKoR549jNw3Yotk",
    "X33yp6VcdtaXAj4EMHaF",
    "oiZVuY2ZYGYSYky3QQvM",
    "fqkYrITfJN1o3OZzcABg",
    "6m2zhl6S6mdyfjhY8QIB",
    "5ecrCdRmt6cKhzM65yiw",
    "qaMf8oQ7FIp8qVgdtqq9",
    "aqpMF35rXjYFj7zOjLah",
    "9xmM52dqf9dWlD9nVHgv",
    "fcRo5J3PUI3JGLrAkGxY",
    "JXSIM3nElfwWLsxQcHtT",
    "OkBlhPBtMWXam7SdN86F",
    "T4xrBTOoGbaZtNL0Uehj",
    "45fDarUmJFiPtzaM42Bk",
    "zZiTY0fTi7IUcrf5dGHY",
    "pflWcvsWP0faJSWswudF",
    "50Kj9XaLSMyFLLqFKx0G",
    "nZUNr4dlYOBrpUtU4jfg",
    "4OU3qOjDTRwNfec1jIRA",
    "m9StS6yJmyjIy8RaaJGy",
    "dasNaei6hfLHNFLqRhp1",
    "9eGlrFL3UnFCqwF1qSVj",
    "6XgWu0arqlVMS6VMh9cC",
    "7evk43L6gkOrBwea7wv9",
    "joyY6CESpfIZqiPScZp7",
    "m3GU0mN4RZD7eMrNtk3T",
    "k9CicJLIZl23n1p7MYe5",
    "veSoMKiO9vpfefYCw4Ic",
    "2475rDHqwvigHoL3BfTS",
    "SI7YT5BEz5CFfn4dLApR",
    "6Yq8XKcVO1RcpEYc9FTE",
    "7LCPfabShbishbjNGoYA",
    "agecidqfgGzhYC2MjidM",
    "MPge5RgrQMmu1K3fnPpJ",
    "yFwyZvlMSJHT5WhVGP2V",
    "kcumy7OvgBxVUwwvS8rt",
    "NXwF9xJE5mY1t1Kd09Cd",
    "LRTIoVS6mTnaPuVeIlpm",
    "cvvdl5PJo1afOTQS3VlA",
    "YzrYkGLRd1dhDrZJscpt",
    "nMLzCoWeHbTHTFd5jVZk",
    "otvbp76rJHPNMFzG1TTA",
    "fGqzQJFvAc6O3ZkCVI0L",
    "hOU1k964TB49FGSptIgb",
    "DpGpZutpr8IYfJTMTtuw",
    "3d1RHiS9rY6ZMrqMKSBX",
    "LO7mES0TwcZVu26aDafX",
    "E7UEY1PH6WwMID2x0zTO",
    "VF3H0gteL4sJFCAmZCOc",
    "gwHnzHERBCIJcxplMitZ",
    "Ovsjo2iLeN3RS7kM763e",
    "l4Dwnkoc6fJRliCAg4Bv",
    "DCtcllctH7sOHGPPHlZH",
    "ZpqncpazPLwyX5Tk9PKe",
    "OTxKvmFLf91Iyyrp59mU",
    "NOecl3LQv5lo4drjDFfZ",
    "yFnSVLUARDUScQEzrFYL",
    "UzU9MEJdkq7vSWZbIBKv",
    "CVSZlirb1SoMf6fL2nVf",
    "OXduVvOIReh8nV49hN8C",
    "jlveYIMLJmuR0E3aix8i",
    "zd9Z5an102Jb0gJpUXYU",
    "pjdcZIwKKCSskzSFQYHJ",
    "kOhxWa9Wg09kABuAeF5B",
    "XuadqNgz0E2VddDxPUfe",
    "3NuhKU2Io2RgT8MhIaHN",
    "qV4hqYJ5D8ob0nGpBExh",
    "ryyM4c1zXLBhzhjoxLJc",
    "PwIRpgODrJLMSTAEHWBp",
    "JPkV4xpdAcY0xb2nFXsS",
    "Y7DWgGRMehGYjAr6Dqzv",
    "xcbcG7I0D2ZR05ssNOQX",
    "k9mevjO8s6WGOxGxCKgz",
    "MmbrPDe0lmCV0CwdmbNx",
    "GYGAOrDFZLzHZBjpVf7a",
    "d89cM1dJRu6gpF5JPlkP",
    "Udmh5Xsk7LccKPe0GLm9",
    "dVbwNtdZySobGZfEhk6H",
    "YlosfpWrJ5LIzmpuHhGM",
    "sGirQEsnvHp9dWJGYB8c",
    "nTNvKCEYJSD3HL9pclsF",
    "WyittPk96b2FkjJSo3lh",
    "2CulyMgqoFPtTk8caMeV",
    "3WuWanfbW89hLTWQdm0o",
    "FsGZTDOuKqL6mqAybBk9",
    "fhVwJ6bmqDZa4kKfhQQz",
    "Xo2vq3zYpRRxrtL45BxK",
    "zXfqzjVTwBKITEKWBKhn",
    "Pk7IljdY3DXvgUo6VnMY",
    "mlf71NSW5gmXzUHc0HlJ",
    "YazZYt7kP15AhhvyW3YN",
    "OXyVHsqMmu4xMjaGkpv3",
    "Xu7o43Hd4ZKTNxhNKQ4L",
    "qwFG4stL5VDkNOLzxtRe",
    "loetQGiXMDMJbUJVftiO",
    "tuqQFHCGPZKEm55a0ajL",
    "knAY8u0PUuno6zUSeYqG",
    "qYsK9NXiCLOFMg34YYbi",
    "eIbDONqUVwiXPkRWQ9ID",
    "4TiZAUvHGbL9OCGRlFPf",
    "jeV5LwZBgZvXCnOtQWOO",
    "YGDoPYihNOAxXtNFiKot",
    "pDFlic9FZ14Q02v1vqgY",
    "CbMDVQxeMtQpe6BgNgug",
    "g1vHI06GcZMmshJIagwS",
    "giBjgbHVdJlwFqo8RhWF",
    "85KuDz0ZQLiubIpTn3KA",
    "f3qkRhCbw2gc0X6oIfxQ",
    "skZUkqvHjfmlydimxctn",
    "nn40YsAgPlRguDG5omSq",
    "hYnRf53zXfpWHwN7zYVV",
    "0k1XaixZ0CtzqNz5UqV3",
    "swjZ9L0Gx376BWJ3YyWw",
    "xihRs4qg8wNEBLy0CZiI",
    "YpXb4jtjSnq3QBu7Jf2X",
    "ZT8wyLKbsDtvsz2A4NHZ",
    "1uJaUHgATqSy6ZWd2avN",
    "b7BxPdxe9GeLxoYmeqcJ",
    "lxEu3583QF4FLAK7w2h4",
    "6DJHiP8ImURnCkdcEuaO",
    "iofKyCfqWB3CpIRhWY4z",
    "3eqhrraRav5E5GcbR2iz",
    "Zqttzm93fbSLGsbR0z5v",
    "KSWj0ZQ3Owlg2FmXKFhm",
    "oZo4lboJKkNrfsQ3QnIj",
    "62sSORrLC12Vcf1o8N7O",
    "kFJdQnSMwVO9c86Xl4Fq",
    "Nx3L6Zo3JmS44q9zZtae",
    "VDcnZZfZSsRJsmlY7GRh",
    "nn6YYvUvHzFV4uGDhxaN",
    "ozxonKqK6aqggpkPFawk",
    "v1b2Pzj6T1ihDZyYozlg",
    "sGg32dOnbClSESIGWhJU",
    "xJf1MMmWY3pNu6KQgB1c",
    "i25Vl3cqbbzUsC4ZnJK7",
    "7x4KzW0YZLcjzztZwfNJ",
    "VzsiChfSycJZEyT2IAKa",
    "od6yYoX4EIJuqS2IhZXc",
    "dyiJla5HqciIOx8adoN1",
    "JEIN9mPaCbpf2zP81hC6",
    "VhfIOWo4qcfhEJxeDdjw",
    "63WI9PwoP1lszbx5JdTW",
    "HdtKSeF23ygkk08VzZXn",
    "7x4KzW0YZLcjzztZwfNJ",
    "VzsiChfSycJZEyT2IAKa",
    "od6yYoX4EIJuqS2IhZXc",
    "dyiJla5HqciIOx8adoN1",
    "JEIN9mPaCbpf2zP81hC6",
    "VhfIOWo4qcfhEJxeDdjw",
    "63WI9PwoP1lszbx5JdTW",
    "HdtKSeF23ygkk08VzZXn",
    "xskOXgxkwA8RRoFlspi5",
    "HDfKUO495ipCS0c8GA4B",
    "8JswN1hMt4XB6BXtbam3",
    "EtzcUIg0imAsvOKTfmW5",
    "6c1SaUzR2rRdimFck9aS",
    "FKJFtFwJ605vrKAzagpU",
    "AjKyXlSr5l0rWugRdHOk",
    "oPeaGHyPeOdFXx0SpHgl",
    "6JD6ye2KULnyM8Jyx9WP",
    "v1K3xrXL77LOrH4dlZIg",
    "IIk8FPKSn5XiDIZnUtnB",
    "QqVct75UCrfTKdo93vQn",
    "8dtkfUj256Pbwh5EGKyd",
    "LWH0PkqIUc4XaibVwl33",
    "4y3xrhP557EMbPLyI5k6",
    "mVjH3msZjoKN0p7Jzqlw",
    "73RvPfPPbUwsFdjg6a92",
    "yL1Tacc76TSAfQd90r1v",
    "eGGfzyJVcqHlcxuyUECG",
    "declwC8nYMieUfO1LGaW",
    "Xp09Lc6JKjIVq2WaFZtp",
    "Oq9sRT64sxtVyuGpEa49",
    "tjag3qLCkvYLC6d2gvmE",
    "05kzerSKaHjeVKBWroIC",
    "TxCnuZUlY3g4FdzAProp",
    "einWsAsqU0cUdWpOL3H9",
    "H3iLrtDjkR6AbT8Iuc27",
    "zRfwlHX9EQ2Sisx6Vi1V",
    "khKc3oxJ1uA5wDxHUwiY",
    "0ANpirdIGoSM9c7giFz2",
    "bBHNnWLiWqLheX3JgzCE",
    "QavSiMHlc4pbGhOmp2JU",
    "ekkRARBkmE1lpqLtY3BQ",
    "Es347Ztg0rbqSF69ause",
    "60zYa81BCMQxBQ06s5Qk",
    "mdnNh0VZc9WHDeEGEZNC",
    "8QLl82ZKa4kuqaxRX3di",
    "wM9iXooMvyzm1rxCXaCQ",
    "ASsLydsc71FS8dHZTmRN",
    "bCjd9e8yIoNT9P73gwPO",
    "gmW4LjzT4swPI1XKca8G",
    "XAhnO3deWMM6QMcMcvSF",
    "yYFRO07tdx7IIf7ZYQXa",
    "P3po021q0aIlLoaI1mfZ",
    "uQ6VFSMk9I3HtMf7m4VS",
    "qRXFhVeyc6wCpY0RKnnY",
    "Cn6gdP21z65n0x52c57q",
    "6MVtVfuABBUT11mgXP60",
    "mBClYjWNoIg4jjIOFKmb",
    "MHes0WzIiv2z8ZfMwrEa",
    "vT9Hytk37r5df3E7jUr2",
    "WDxOhLjw1mxsHjgmoBBE",
    "zCndSD7iyGlOd9DUNNft",
    "qAxHwaVSRoG4BlYByrkJ",
    "jYdxDr81yZ3VYYwjBil1",
    "cU3Ec8OehFe0KD6p4VkQ",
    "kAr0lwTY3JY4RYAbKXNr",
    "bgQAtRAknQkvcSM3F4fx",
    "1FzTBT2F1XxGqSXkM5hB",
    "gYO5UnlpWVoCYdO2NNww",
    "zaV0e0IPox0rdzvak8dW",
    "KaRYKtGwDbSMD5G1lawe",
    "EQHzC5duRl5KeZDDn79S",
    "StIajaHnHDq1tCcnBsda",
    "igsDElqcJ0e1LpArRUox",
    "qKOgvAC6Ph3gujAvpinY"

    ]#dabaigti pyldyti, einant per inscpect -> network (pasirinkti fetchxhr) parasyti products ir ieskoti fronted-products
payload={
    "fromIndex":0,
    "limit":1000,
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

def IKI_crawler(url):
   
    #print(response.text)
    i=0
    limit=8000;
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

                i=0
                for item in data.get('products'):
                    
                    weight=protein=fat=sugar=salt=carbs=calories="0"
                    product=item.get("frontEndProduct", {})
                    if product.get("isInStock") and product.get("chainId")=="CvKfTzV4TN5U8BTMF1Hl":
                        # print(str(i)+" "+str(product.get("name").get("lt")))
                        # print(f"\nBaltymai: {product.get('nutrition').get('protein')} \nRiebalai: {product.get('nutrition').get('fat')} \nEnergetine verte: {product.get('nutrition').get('energy')} \nCukrus: {product.get('nutrition').get('sugar')}")
                        # print(f"Angliavandeniai: {product.get('nutrition').get('carbs')} \nDruska: {product.get('nutrition').get('salt')} \n")
                        name=str(product.get("name").get("lt"))
                        weight=str(product.get('conversionValue'))#-------------------------------------------pasiziureti kaip konvertonasi svoris nes jis pre json faila atrodo netikslus
                        protein=str(product.get('nutrition').get('protein'))
                        fat=str(product.get('nutrition').get('fat'))
                        sugar=str(product.get('nutrition').get('sugar'))
                        salt=str(product.get('nutrition').get('salt'))
                        carbs=str(product.get('nutrition').get('carbs'))
                        calories=str(product.get('nutrition').get('energy'))
                        img_url=str(product.get('photoUrl')) 

                        #gets product url
                        for slug in product.get('slugs',[]):
                            correct_slug=re.search(r'\d+$',slug )
                   
                            if correct_slug:
                                product_url="https://www.lastmile.lt/chain/IKI/product/"+str(slug)
                                print(product_url)
                                break
            
                    
                        print(f"\n Svoris KG: {product.get('conversionValue')}")
                        print(f"\n Nuotraukos nuoroda: {product.get('photoUrl')}")
                        print('-'*50)
                        if weight=="0":
                            i=i+1
                        if i==20:
                            break;
                        products_obj=Product.Product(name,weight,protein,fat,sugar,salt,carbs,calories,product_url,img_url)
                        All_Products.append(products_obj)
                fromIndex=fromIndex+limit
        elif fromIndex==16000:
           return All_Products    

All_Products2=[]
All_Products2=IKI_crawler(IKI_url_API)

if All_Products2:
    data_to_json2=[product.__dict__ for product in All_Products2]
    with open("IKI_products.json", "w", encoding="utf-8") as f:
        json.dump(data_to_json2, f, ensure_ascii=False, indent=4)





    

      