from ast import literal_eval

import pandas as pd
import torch
from torch.utils.data import Dataset


class BaseDataset(Dataset):
    def __init__(
        self,
        behaviors_path: str,
        news_path: str,
        cols: list[str],
        num_words_title: int = 20,
        num_words_abstract: int = 50,
        num_clicked_news_a_user: int = 50,
    ):
        super().__init__()

        self.num_clicked_news_a_user = num_clicked_news_a_user

        self.behaviors_parsed = pd.read_table(behaviors_path)
        self.news_parsed = pd.read_table(
            news_path,
            index_col="id",
            usecols=["id"] + cols,
            converters={
                attribute: literal_eval
                for attribute in set(cols) & {"title", "abstract", "title_entities", "abstract_entities"}
            },
        )
        self.news_id2int = {x: i for i, x in enumerate(self.news_parsed.index)}
        self.news2dict = self.news_parsed.to_dict("index")
        for key1 in self.news2dict.keys():
            for key2 in self.news2dict[key1].keys():
                self.news2dict[key1][key2] = torch.tensor(self.news2dict[key1][key2])
        padding_all = {
            "category": 0,
            "subcategory": 0,
            "title": [0] * num_words_title,
            "abstract": [0] * num_words_abstract,
            "title_entities": [0] * num_words_title,
            "abstract_entities": [0] * num_words_abstract,
        }
        for key in padding_all.keys():
            padding_all[key] = torch.tensor(padding_all[key])

        self.padding = {k: v for k, v in padding_all.items() if k in cols}

    def __len__(self):
        return len(self.behaviors_parsed)

    def __getitem__(self, idx):
        item = {}
        row = self.behaviors_parsed.iloc[idx]
        item["user"] = row.user
        item["clicked"] = list(map(int, row.clicked.split()))
        item["candidate_news"] = [self.news2dict[x] for x in row.candidate_news.split()]
        item["clicked_news"] = [self.news2dict[x] for x in row.clicked_news.split()[: self.num_clicked_news_a_user]]
        item["clicked_news_length"] = len(item["clicked_news"])
        repeated_times = self.num_clicked_news_a_user - len(item["clicked_news"])
        item["clicked_news"] = [self.padding] * repeated_times + item["clicked_news"]

        return item
