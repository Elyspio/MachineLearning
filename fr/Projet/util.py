import json
import os
from urllib.request import urlopen, urlretrieve
from PIL import Image

from bs4 import BeautifulSoup


# Télécharge une image
def download_img(url: str, output: str) -> None:
    urlretrieve(url, output)


# Scrap une page web (Soup)
def scrap(url: str):
    u = urlopen(url)
    try:
        print("scrapping: " + url)
        html = u.read().decode('utf-8')
    finally:
        u.close()
    return BeautifulSoup(html, "html.parser")


# Lit une image (Numpy) à partir de son path en la convertissant au format RGB
def get_img(path: str) -> Image:
    return Image.open(path).convert("RGB")


# Lit les metadata d'une image à partir de son chemin sur le disque
def get_metadata_for_img(img: str):
    with open(os.path.join(os.path.dirname(__file__), "images", "metadata.json"), "r") as metadata:
        data = list(json.load(metadata))
        return list(x for x in data if x["img"]["path"] == img)[0]["metadata"]

