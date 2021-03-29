import os
import random

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from config import images_path
from util import get_metadata_for_img

nb_colors = 4


def get_user_preferences(nb_images=100):
    """

    :param nb_images:
    :return:
    """
    all_images = os.listdir(images_path)
    all_images = list((x for x in all_images if not x == "metadata.json"))

    choices = []
    imgs = random.sample(all_images, nb_images)

    for i in range(nb_images):
        choices.append(random.choice(("Favorite", "NotFavorite")))

    return imgs, choices


def map_datum_to_tuple(datum):
    values = []

    for i in range(nb_colors):
        for j in "rgb":
            values.append(datum["colors"][i][j])
    values.append(datum["ratio"]["aspect"])
    values.append(datum["categories"][-1])
    return values


def get_estimator(train_data: tuple[list[str], list[str]], test_dataset: list[str]) -> (RandomForestClassifier, list[LabelEncoder]):
    """
    :param train_data: liste des images qui on été évaluées par l'utilisateur TODO
    :param test_dataset: liste du choix de l'utilisateur pour chaque images "Favorite" ou "NotFavorite" TODO
    :return: Renvoie un classifieur d'un utilisateur en fonction des images qu'il a appréciées ou non TODO
    """

    labels = []

    for i in range(nb_colors):
        for j in range(3):
            labels.append(f"color-{i}-{'rgb'[j]}")
    labels.append("aspect")
    labels.append("category")

    # test

    metadata = list(map(lambda x: get_metadata_for_img(x), test_dataset))
    test_data = list(map(map_datum_to_tuple, metadata))

    # train
    (imgs, results) = train_data

    metadata = list(map(lambda x: get_metadata_for_img(x), imgs))
    data = list(map(map_datum_to_tuple, metadata))

    dataframe = pd.DataFrame(data, columns=labels)
    test_dataframe = pd.DataFrame(test_data, columns=labels)
    resultframe = pd.DataFrame(results, columns=['favorite'])

    # generating numerical labels
    les = []
    for i in range(nb_colors):
        for j in range(3):
            key = f"color-{i}-{'rgb'[j]}"
            encoder = LabelEncoder()
            dataframe[key] = encoder.fit_transform(dataframe[key])
            test_dataframe[key] = encoder.fit_transform(test_dataframe[key])
            les.append(encoder)

    aspect_encoder = LabelEncoder()
    dataframe['aspect'] = aspect_encoder.fit_transform(dataframe['aspect'])
    test_dataframe['aspect'] = aspect_encoder.fit_transform(test_dataframe['aspect'])
    les.append(aspect_encoder)

    category_encoder = LabelEncoder()
    dataframe['category'] = category_encoder.fit_transform(dataframe['category'])
    test_dataframe['category'] = category_encoder.fit_transform(test_dataframe['category'])
    les.append(category_encoder)

    le5 = LabelEncoder()
    resultframe['favorite'] = le5.fit_transform(resultframe['favorite'])
    les.append(le5)

    # Use of decision tree classifiers

    # n_estimators = 10
    # rfc = DecisionTreeClassifier(max_depth=10, n_estimators=n_estimators, random_state=0)
    rfc = RandomForestClassifier()
    rfc = rfc.fit(dataframe, resultframe.values.ravel())
    #
    # for i in range(n_estimators):
    #     dot_data = tree.export_graphviz(rfc.estimators_[i], out_file=None,
    #                                     feature_names=dataframe.columns,
    #                                     filled=True, rounded=True,
    #                                     class_names=
    #                                     le5.inverse_transform(
    #                                         resultframe.favorite.unique())
    #                                     )
    #     graph = graphviz.Source(dot_data)
    #     pydot_graph = pydotplus.graph_from_dot_data(dot_data)
    #     img = Image(pydot_graph.create_png())
    #     display(img)

    return rfc, les


def get_prediction(rfc: RandomForestClassifier, les: list[LabelEncoder], img: str) -> bool:
    """

    :param rfc:
    :param les:
    :param img:
    :return: Si l'utilisateur va aimer l'image passer en paramètre
    """
    metadata = get_metadata_for_img(img)
    values = map_datum_to_tuple(metadata)

    classifiers = []
    for index, le in enumerate(les[:-1]):
        classifiers.append(le.transform([values[index]])[0])

    prediction = rfc.predict([classifiers])

    favorite_value = les[-1].inverse_transform(prediction)[0]
    return (favorite_value == "Favorite")
