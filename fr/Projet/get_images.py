import json
import os.path

from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve

URL = "https://commons.wikimedia.org/wiki/Commons:Featured_pictures/Astronomy"


def scrap(url: str):
    u = urlopen(url)
    try:
        print("scrapping: " + url)
        html = u.read().decode('utf-8')
    finally:
        u.close()
    return BeautifulSoup(html, "html.parser")


def main():

    os.mkdir()

    soup = scrap(URL)
    galleries = soup.find_all("ul", {"class": "gallery"})

    data = []

    for gallery in galleries:
        print("Gallery", gallery.name)

        categories_links = list()
        images_links = list()

        # Get categories HREF
        children = gallery.find_all("a")
        for child in children:
            href: str = child.attrs["href"]
            if href.endswith((".jpg", ".png")):
                categories_links.append("https://commons.wikimedia.org/{0}".format(href))

        # GET img url
        children = gallery.find_all("img")
        for child in children:
            src: str = child.attrs["src"]
            if src.endswith((".jpg", ".png")):
                images_links.append(src)

        print(len(categories_links), len(images_links))

        gallery_title = gallery.previous_sibling
        while gallery_title.name not in ["h2", "h3"]:
            gallery_title = gallery_title.previous_sibling

        gallery_title_str = gallery_title.find("span", {"class": "mw-headline"}).getText()

        if len(categories_links) > 0:

            for i in range(len(categories_links)):
                image_link = images_links[i]
                img_name = image_link[image_link.rfind("/") + 1:]
                path = os.path.join(os.path.dirname(__file__), "images", img_name)
                download_img(image_link, path)
                categories = get_categories(categories_links[i])
                categories.append(gallery_title_str),
                data.append({
                    "img_url": image_link,
                    "categories": categories,
                    "img_path": img_name
                })

    with open(os.path.join(os.path.dirname(__file__), "images", "metadata.json", ), 'w') as outfile:
        json.dump(data, outfile, indent=4)


def download_img(url: str, output: str) -> None:
    urlretrieve(url, output)


def get_categories(url: str):
    soup = scrap(url)
    container = soup.find("div", {"id": "mw-normal-catlinks"})
    ul = container.find("ul")
    links = ul.find_all("a")
    return list(map(lambda link: link.getText(), links))


if __name__ == '__main__':
    main()
