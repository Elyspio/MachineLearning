import math

import numpy
from PIL import Image
from sklearn.cluster import KMeans

from util import scrap, get_img


def get_metadata(path: str, url: str):
    return {
        "colors": get_colors(path),
        "ratio": get_ratio(path),
        "categories": get_categories(url)
    }
    pass


def get_colors(path: str, nb_colors=4):
    imgfile = get_img(path)
    numarray = numpy.array(imgfile.getdata(), numpy.uint8)
    clusters = KMeans(n_clusters=nb_colors)
    clusters.fit(numarray)
    npbins = numpy.arange(0, nb_colors + 1)
    histogram = numpy.histogram(clusters.labels_, bins=npbins)

    indexes = []
    to_sort = list(histogram[0])

    for i in range(nb_colors):
        vMax = max(to_sort)
        indexes.append({'was': i, 'to': list(histogram[0]).index(vMax)})
        to_sort.remove(vMax)

    # indexes.sort(key=lambda xxx: xxx["to"])

    # HISTOGRAM

    # values = sorted(histogram[0], reverse=True)

    colors = []

    for i in range(nb_colors):
        centerIndex = next(x for x in indexes if x["to"] == i)["was"]
        center = clusters.cluster_centers_[centerIndex]
        color = '#%02x%02x%02x' % (math.ceil(center[0]), math.ceil(center[1]), math.ceil(center[2]))
        colors.append(color)

    # Liste de couleurs

    return colors


def get_ratio(path: str):
    img = get_img(path)
    width, height = img.size
    return {
        "width": width,
        "height": height,
        "value": width / height,
        "aspect": "landscape" if width > height else "portrait"
    }


def get_categories(url: str):
    soup = scrap(url)
    container = soup.find("div", {"id": "mw-normal-catlinks"})
    ul = container.find("ul")
    links = ul.find_all("a")
    return list(map(lambda link: link.getText(), links))
