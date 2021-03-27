import os
import random

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from util import get_metadata_for_img

nb_colors = 4


def get_user_preferences(nb_images=100):
    all_images = os.listdir(os.path.join(os.path.dirname(__file__), "images"))
    all_images = list((x for x in all_images if not x == "metadata.json"))
    choices = []
    imgs = random.sample(all_images, nb_images)

    for i in range(nb_images):
        choices.append(random.choice(("Favorite", "NotFavorite")))

    return imgs, choices


def map_datum_to_tuple(datum):
    values = []

    for i in range(nb_colors):
        values.append(datum["colors"][i])
    values.append(datum["ratio"]["aspect"])
    values.append(datum["categories"][-1])
    return values


def get_estimator(imgs, results):
    metadata = list(map(lambda x: get_metadata_for_img(x), imgs))
    data = list(map(map_datum_to_tuple, metadata))


    labels = []

    for i in range(nb_colors):
        labels.append(f"color-{str(i)}")
    labels.append("aspect")
    labels.append("category")

    dataframe = pd.DataFrame(data, columns=labels)
    resultframe = pd.DataFrame(results, columns=['favorite'])

    # generating numerical labels
    for i in range(nb_colors):
        key = f"color-{str(i)}"
        dataframe[key] = LabelEncoder().fit_transform(dataframe[key])
    dataframe['aspect'] = LabelEncoder().fit_transform(dataframe['aspect'])
    dataframe['category'] = LabelEncoder().fit_transform(dataframe['category'])

    le5 = LabelEncoder()
    resultframe['favorite'] = le5.fit_transform(resultframe['favorite'])

    # Use of decision tree classifiers
    n_estimators = 10
    rfc = RandomForestClassifier(n_estimators=n_estimators, max_depth=2,
                                 random_state=0, )
    rfc = rfc.fit(dataframe, resultframe.values.ravel())
    return rfc, le5


imgs, results = get_user_preferences()


def get_prediction(rfc, le5, img: str):
    metadata = get_metadata_for_img(img)
    values = map_datum_to_tuple(metadata)
    classifiers = []

    for index, val in enumerate(values):
        classifiers.append(LabelEncoder().fit_transform([val])[0])

    prediction = rfc.predict([classifiers])

    print(le5.inverse_transform(prediction))
    print(rfc.feature_importances_)


estimator, le5 = get_estimator(imgs, results)

get_prediction(estimator, le5, "lossy-page1-534px-Jovian_Tempest.tif.jpg")

