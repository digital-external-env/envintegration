from ast import literal_eval

import pandas as pd
import torch
from torch.utils.data import Dataset


class NewsDataset(Dataset):
    def __init__(self, news_path, cols: str):
        super(NewsDataset, self).__init__()
        self.news_parsed = pd.read_table(
            news_path,
            usecols=["id"] + cols,
            converters={
                attribute: literal_eval
                for attribute in set(cols) & {"title", "abstract", "title_entities", "abstract_entities"}
            },
        )
        self.news2dict = self.news_parsed.to_dict("index")
        for key1 in self.news2dict.keys():
            for key2 in self.news2dict[key1].keys():
                if type(self.news2dict[key1][key2]) != str:
                    self.news2dict[key1][key2] = torch.tensor(self.news2dict[key1][key2])

    def __len__(self):
        return len(self.news_parsed)

    def __getitem__(self, idx):
        item = self.news2dict[idx]

        return item
