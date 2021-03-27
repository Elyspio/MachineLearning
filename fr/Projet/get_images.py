import json
import os.path
import re
import urllib

from get_metadata import  get_metadata
from util import download_img, scrap


URL = "https://commons.wikimedia.org/wiki/Commons:Featured_pictures/Astronomy"


def main():
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

                if not os.path.exists(path):
                    download_img(image_link, path)

                metadata = get_metadata(path, categories_links[i])
                metadata["categories"].append(gallery_title_str)

                data.append({
                    "img": {
                        "path": img_name,
                        "url": image_link
                    },
                    "metadata": metadata,
                })

    with open(os.path.join(os.path.dirname(__file__), "images", "metadata.json", ), 'w') as outfile:
        json.dump(data, outfile, indent=4)


if __name__ == '__main__':
    main()

