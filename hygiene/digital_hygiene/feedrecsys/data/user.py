import pandas as pd
from torch.utils.data import Dataset


class UserDataset(Dataset):
    def __init__(self, behaviors_path: str, user2int_path: str, num_clicked_news_a_user: int = 50):
        super().__init__()

        self.num_clicked_news_a_user = num_clicked_news_a_user

        self.behaviors = pd.read_table(behaviors_path, header=None, usecols=[1, 3], names=["user", "clicked_news"])
        self.behaviors.clicked_news.fillna(" ", inplace=True)
        self.behaviors.drop_duplicates(inplace=True)
        user2int = dict(pd.read_table(user2int_path).values.tolist())
        user_total = 0
        user_missed = 0
        for row in self.behaviors.itertuples():
            user_total += 1
            if row.user in user2int:
                self.behaviors.at[row.Index, "user"] = user2int[row.user]
            else:
                user_missed += 1
                self.behaviors.at[row.Index, "user"] = 0

    def __len__(self):
        return len(self.behaviors)

    def __getitem__(self, idx):
        row = self.behaviors.iloc[idx]
        item = {
            "user": row.user,
            "clicked_news_string": row.clicked_news,
            "clicked_news": row.clicked_news.split()[: self.num_clicked_news_a_user],
        }
        item["clicked_news_length"] = len(item["clicked_news"])
        repeated_times = self.num_clicked_news_a_user - len(item["clicked_news"])
        item["clicked_news"] = ["PADDED_NEWS"] * repeated_times + item["clicked_news"]

        return item
