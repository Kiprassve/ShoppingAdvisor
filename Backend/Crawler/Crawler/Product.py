from os import name
from signal import default_int_handler


class Product(object):
    
   def __init__(self,name,weight_kg,conversion_measure,protein,fat,sugar,salt,carbohydrates,calories_kcal,url,image_url,price,price_discount):
         self.name=name
         self.weight_kg=weight_kg        
         self.conversion_measure=conversion_measure
         self.protein=protein
         self.fat=fat
         self.sugar=sugar
         self.salt=salt
         self.carbohydrates=carbohydrates
         self.calories_kcal=calories_kcal
         self.url=url
         self.image_url=image_url
         self.price=price
         self.price_discount=price_discount

   def __str__(self):
       return f"Name: {self.name}\nWeight: {self.weight_kg}\nProtein: {self.protein}\nFat: {self.fat}\nSugar: {self.sugar}\nSalt: {self.salt}\nCarbohydrates: {self.carbohydrates}\nCalories: {self.calories_kcal}"
    




