import csv
import json
import random

import pandas as pd
from nltk.tokenize import word_tokenize
from tqdm import tqdm


def parse_behaviors(source: str, target: str, user2int_path: str, negative_sampling_ratio: int = 2):
    behaviors = pd.read_table(
        source,
        header=None,
        names=["impression_id", "user", "time", "clicked_news", "impressions"],
    )
    behaviors.clicked_news.fillna(" ", inplace=True)
    behaviors.impressions = behaviors.impressions.str.split()

    user2int: dict[str, int] = {}
    for row in behaviors.itertuples(index=False):
        if row.user not in user2int:
            user2int[row.user] = len(user2int) + 1

    pd.DataFrame(user2int.items(), columns=["user", "int"]).to_csv(user2int_path, sep="\t", index=False)

    for row in behaviors.itertuples():
        behaviors.at[row.Index, "user"] = user2int[row.user]

    for row in tqdm(behaviors.itertuples(), desc="Balancing data"):
        positive = iter([x for x in row.impressions if x.endswith("1")])
        negative = [x for x in row.impressions if x.endswith("0")]
        random.shuffle(negative)
        negative = iter(negative)
        pairs = []
        try:
            while True:
                pair = [next(positive)]
                for _ in range(negative_sampling_ratio):
                    pair.append(next(negative))
                pairs.append(pair)
        except StopIteration:
            pass
        behaviors.at[row.Index, "impressions"] = pairs

    behaviors = behaviors.explode("impressions").dropna(subset=["impressions"]).reset_index(drop=True)
    behaviors[["candidate_news", "clicked"]] = pd.DataFrame(
        behaviors.impressions.map(
            lambda x: (" ".join([e.split("-")[0] for e in x]), " ".join([e.split("-")[1] for e in x])),
        ).tolist(),
    )
    behaviors.to_csv(target, sep="\t", index=False, columns=["user", "clicked_news", "candidate_news", "clicked"])


def parse_news(
    source: str,
    target: str,
    category2int_path: str,
    word2int_path: str,
    entity2int_path: str,
    mode: str,
    num_words_title: int = 20,
    num_words_abstract: int = 50,
    entity_confidence_threshold: float = 0.5,
    word_freq_threshold: int = 1,
    entity_freq_threshold: int = 2,
):
    news = pd.read_table(
        source,
        header=None,
        usecols=[0, 1, 2, 3, 4, 6, 7],
        quoting=csv.QUOTE_NONE,
        names=["id", "category", "subcategory", "title", "abstract", "title_entities", "abstract_entities"],
    )
    news.title_entities.fillna("[]", inplace=True)
    news.abstract_entities.fillna("[]", inplace=True)
    news.fillna(" ", inplace=True)

    def parse_row(row):
        new_row = [
            row.id,
            category2int[row.category] if row.category in category2int else 0,
            category2int[row.subcategory] if row.subcategory in category2int else 0,
            [0] * num_words_title,
            [0] * num_words_abstract,
            [0] * num_words_title,
            [0] * num_words_abstract,
        ]

        local_entity_map = {}
        for e in json.loads(row.title_entities):
            if e["Confidence"] > entity_confidence_threshold and e["WikidataId"] in entity2int:
                for x in " ".join(e["SurfaceForms"]).lower().split():
                    local_entity_map[x] = entity2int[e["WikidataId"]]
        for e in json.loads(row.abstract_entities):
            if e["Confidence"] > entity_confidence_threshold and e["WikidataId"] in entity2int:
                for x in " ".join(e["SurfaceForms"]).lower().split():
                    local_entity_map[x] = entity2int[e["WikidataId"]]

        try:
            for i, w in enumerate(word_tokenize(row.title.lower())):
                if w in word2int:
                    new_row[3][i] = word2int[w]
                    if w in local_entity_map:
                        new_row[5][i] = local_entity_map[w]
        except IndexError:
            pass

        try:
            for i, w in enumerate(word_tokenize(row.abstract.lower())):
                if w in word2int:
                    new_row[4][i] = word2int[w]
                    if w in local_entity_map:
                        new_row[6][i] = local_entity_map[w]
        except IndexError:
            pass

        return pd.Series(
            new_row,
            index=["id", "category", "subcategory", "title", "abstract", "title_entities", "abstract_entities"],
        )

    if mode == "train":
        category2int = {}
        word2int = {}
        word2freq = {}
        entity2int = {}
        entity2freq = {}

        for row in news.itertuples(index=False):
            if row.category not in category2int:
                category2int[row.category] = len(category2int) + 1
            if row.subcategory not in category2int:
                category2int[row.subcategory] = len(category2int) + 1

            for w in word_tokenize(row.title.lower()):
                if w not in word2freq:
                    word2freq[w] = 1
                else:
                    word2freq[w] += 1
            for w in word_tokenize(row.abstract.lower()):
                if w not in word2freq:
                    word2freq[w] = 1
                else:
                    word2freq[w] += 1

            for e in json.loads(row.title_entities):
                times = len(e["OccurrenceOffsets"]) * e["Confidence"]
                if times > 0:
                    if e["WikidataId"] not in entity2freq:
                        entity2freq[e["WikidataId"]] = times
                    else:
                        entity2freq[e["WikidataId"]] += times

            for e in json.loads(row.abstract_entities):
                times = len(e["OccurrenceOffsets"]) * e["Confidence"]
                if times > 0:
                    if e["WikidataId"] not in entity2freq:
                        entity2freq[e["WikidataId"]] = times
                    else:
                        entity2freq[e["WikidataId"]] += times

        for k, v in word2freq.items():
            if v >= word_freq_threshold:
                word2int[k] = len(word2int) + 1

        for k, v in entity2freq.items():
            if v >= entity_freq_threshold:
                entity2int[k] = len(entity2int) + 1

        parsed_news = news.swifter.apply(parse_row, axis=1)
        parsed_news.to_csv(target, sep="\t", index=False)

        pd.DataFrame(category2int.items(), columns=["category", "int"]).to_csv(category2int_path, sep="\t", index=False)
        pd.DataFrame(word2int.items(), columns=["word", "int"]).to_csv(word2int_path, sep="\t", index=False)
        pd.DataFrame(entity2int.items(), columns=["entity", "int"]).to_csv(entity2int_path, sep="\t", index=False)
    else:
        category2int = dict(pd.read_table(category2int_path).values.tolist())
        word2int = dict(pd.read_table(word2int_path, na_filter=False).values.tolist())
        entity2int = dict(pd.read_table(entity2int_path).values.tolist())

        parsed_news = news.swifter.apply(parse_row, axis=1)
        parsed_news.to_csv(target, sep="\t", index=False)
