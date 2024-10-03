import requests
from bs4 import BeautifulSoup

result= requests.get("https://www.diyetkolik.com/kac-kalori/arama/karniyarik")

html = result.content
soup=soup = BeautifulSoup(html, "html.parser")


food_list=soup.find("div",attrs={'class':'p15 kurumsalBorder backgroundWhite'})
food=food_list.find_all("span",attrs={'class':'d-block'})

x=food[0]
print(x.text)
