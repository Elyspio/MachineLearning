import json
import os.path

from config import URL, images_path
from get_metadata import get_metadata
from util import download_img, ensure_dir, scrap


def get_images():
    """
    Point d'entrée de la récupération des données

     - Récupére les images à partir de l'url ci-dessus
     - Puis les tags à partir
         - de leur emplacement du site
         - de leur couleur 4 couleurs prédominantes
    """
    # Création du dossier images
    ensure_dir(images_path)

    soup = scrap(URL)
    galleries = soup.find_all("ul", {"class": "gallery"})

    data = []

    for gallery in galleries:

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

        gallery_title = gallery.previous_sibling
        while gallery_title.name not in ["h2", "h3"]:
            gallery_title = gallery_title.previous_sibling

        gallery_title_str = gallery_title.find("span", {"class": "mw-headline"}).getText()

        if len(categories_links) > 0:

            for i in range(len(categories_links)):
                image_link = images_links[i]
                img_name = image_link[image_link.rfind("/") + 1:]
                path = os.path.join(images_path, img_name)

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

    with open(os.path.join(images_path, "metadata.json", ), 'w') as outfile:
        json.dump(data, outfile, indent=4)
