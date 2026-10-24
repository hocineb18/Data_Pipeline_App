"""Exploration hors ligne : inspecter le JSON intégré dans la page Trustpilot sauvegardée."""
import json
from bs4 import BeautifulSoup

with open("data/raw/page_test.html", encoding="utf-8") as file:
    soup = BeautifulSoup(file.read(), "html.parser")

data = json.loads(soup.find("script", id="__NEXT_DATA__").string)
page_props = data["props"]["pageProps"]
print("Clés disponibles :", list(page_props.keys()))

reviews = page_props["reviews"]
print("\nNombre d'avis sur la page :", len(reviews))
print("Clés d'un avis :", list(reviews[0].keys()))
print("\nPremier avis complet :")
print(json.dumps(reviews[0], indent=2, ensure_ascii=False))
