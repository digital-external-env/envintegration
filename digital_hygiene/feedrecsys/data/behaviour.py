import pandas as pd

from torch.utils.data import Dataset


class BehaviorsDataset(Dataset):
    def __init__(self, behaviors_path):
        super().__init__()

        self.behaviors = pd.read_table(
            behaviors_path,
            header=None,
            usecols=range(5),
            names=["impression_id", "user", "time", "clicked_news", "impressions"],
        )
        self.behaviors.clicked_news.fillna(" ", inplace=True)
        self.behaviors.impressions = self.behaviors.impressions.str.split()

    def __len__(self):
        return len(self.behaviors)

    def __getitem__(self, idx):
        row = self.behaviors.iloc[idx]
        item = {
            "impression_id": row.impression_id,
            "user": row.user,
            "time": row.time,
            "clicked_news_string": row.clicked_news,
            "impressions": row.impressions,
        }

        return item
