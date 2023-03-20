import sys
from multiprocessing import Pool
from os import path

import numpy as np
import pandas as pd
import torch
from feedrecsys.data import BehaviorsDataset, NewsDataset, UserDataset
from feedrecsys.metrics import mrr_score, ndcg_score
from feedrecsys.models import NRMS
from feedrecsys.utils import latest_checkpoint
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader
from tqdm import tqdm


def value2rank(d):
    values = list(d.values())
    ranks = [sorted(values, reverse=True).index(x) for x in values]

    return {k: ranks[i] + 1 for i, k in enumerate(d.keys())}


def calculate_single_user_metric(pair):
    try:
        auc = roc_auc_score(*pair)
        mrr = mrr_score(*pair)
        ndcg5 = ndcg_score(*pair, 5)
        ndcg10 = ndcg_score(*pair, 10)

        return [auc, mrr, ndcg5, ndcg10]
    except ValueError:
        return [np.nan] * 4


@torch.no_grad()
def evaluate(
    model,
    directory,
    num_workers,
    batch_size: int = 1024,
    max_count=sys.maxsize,
    device: torch.device | None = None,
):
    device = device or torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    news_dataset = NewsDataset(path.join(directory, "news_parsed.tsv"), pd.read_csv("news_parsed.tsv").columns)
    news_dataloader = DataLoader(
        news_dataset,
        batch_size=batch_size * 16,
        shuffle=False,
        num_workers=num_workers,
        drop_last=False,
        pin_memory=True,
    )

    news2vector = {}
    for minibatch in tqdm(news_dataloader, desc="Calculating vectors for news"):
        news_ids = minibatch["id"]
        if any(id not in news2vector for id in news_ids):
            news_vector = model.get_news_vector(minibatch)
            for id, vector in zip(news_ids, news_vector):
                if id not in news2vector:
                    news2vector[id] = vector

    news2vector["PADDED_NEWS"] = torch.zeros(list(news2vector.values())[0].size())

    user_dataset = UserDataset(path.join(directory, "behaviors.tsv"), "data/train/user2int.tsv")
    user_dataloader = DataLoader(
        user_dataset,
        batch_size=batch_size * 16,
        shuffle=False,
        num_workers=num_workers,
        drop_last=False,
        pin_memory=True,
    )

    user2vector = {}
    for minibatch in tqdm(user_dataloader, desc="Calculating vectors for users"):
        user_strings = minibatch["clicked_news_string"]
        if any(user_string not in user2vector for user_string in user_strings):
            clicked_news_vector = torch.stack(
                [
                    torch.stack([news2vector[x].to(device) for x in news_list], dim=0)
                    for news_list in minibatch["clicked_news"]
                ],
                dim=0,
            ).transpose(0, 1)
            user_vector = model.get_user_vector(clicked_news_vector)
            for user, vector in zip(user_strings, user_vector):
                if user not in user2vector:
                    user2vector[user] = vector

    behaviors_dataset = BehaviorsDataset(path.join(directory, "behaviors.tsv"))
    behaviors_dataloader = DataLoader(behaviors_dataset, batch_size=1, shuffle=False, num_workers=num_workers)

    count = 0

    tasks = []
    for minibatch in tqdm(behaviors_dataloader):
        count += 1
        if count == max_count:
            break

        candidate_news_vector = torch.stack(
            [news2vector[news[0].split("-")[0]] for news in minibatch["impressions"]],
            dim=0,
        )
        user_vector = user2vector[minibatch["clicked_news_string"][0]]
        click_probability = model.get_prediction(candidate_news_vector, user_vector)

        y_pred = click_probability.tolist()
        y_true = [int(news[0].split("-")[1]) for news in minibatch["impressions"]]

        tasks.append((y_true, y_pred))

    with Pool(processes=num_workers) as pool:
        results = pool.map(calculate_single_user_metric, tasks)

    aucs, mrrs, ndcg5s, ndcg10s = np.array(results).T

    return np.nanmean(aucs), np.nanmean(mrrs), np.nanmean(ndcg5s), np.nanmean(ndcg10s)


if __name__ == "__main__":
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = NRMS().to(device)

    checkpoint_path = latest_checkpoint("./checkpoint/nrms")
    checkpoint = torch.load(checkpoint_path)
    model.load_state_dict(checkpoint["model_state_dict"])

    model.eval()
    auc, mrr, ndcg5, ndcg10 = evaluate(model, "./data/test")
