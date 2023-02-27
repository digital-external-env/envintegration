import datetime
import os
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from feedrecsys.data.base import BaseDataset
from feedrecsys.models import NRMS
from feedrecsys.utils import EarlyStopping, latest_checkpoint
from test import evaluate


def train(
    batch_size: int = 128,
    num_batches_validate: int = 1024,
    learning_rate: float = 1e-4,
    num_epochs: int = 100,
    num_workers: int = -1,
    device: torch.device | None = None,
):
    device = device or torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    writer = SummaryWriter(
        log_dir=f"./runs/nrms/{datetime.datetime.now().replace(microsecond=0).isoformat()}{'-' + os.environ['REMARK'] if 'REMARK' in os.environ else ''}"
    )

    if not os.path.exists("checkpoint"):
        os.makedirs("checkpoint")

    pretrained_word_embedding = torch.from_numpy(np.load("./data/train/pretrained_word_embedding.npy")).float()

    model = NRMS(pretrained_word_embedding=pretrained_word_embedding).to(device)

    dataset = BaseDataset(
        "data/train/behaviors_parsed.tsv",
        "data/train/news_parsed.tsv",
        pd.read_csv("data/train/news_parsed.tsv").columns,
    )

    dataloader = iter(
        DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            drop_last=True,
            pin_memory=True,
        ),
    )
    criterion = nn.NLLLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_full = []
    exhaustion_count = 0
    step = 0
    early_stopping = EarlyStopping()

    checkpoint_dir = "./checkpoint/nrms"
    Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)

    checkpoint_path = latest_checkpoint(checkpoint_dir)
    if checkpoint_path is not None:
        checkpoint = torch.load(checkpoint_path)
        early_stopping(checkpoint["early_stop_value"])
        step = checkpoint["step"]
        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        model.train()

    for i in tqdm(range(1, num_epochs * len(dataset) // batch_size + 1)):
        try:
            minibatch = next(dataloader)
        except StopIteration:
            exhaustion_count += 1
            dataloader = iter(
                DataLoader(
                    dataset,
                    batch_size=batch_size,
                    shuffle=True,
                    num_workers=num_workers,
                    drop_last=True,
                    pin_memory=True,
                ),
            )
            minibatch = next(dataloader)

        step += 1
        y_pred = model(minibatch["candidate_news"], minibatch["clicked_news"])

        y = torch.zeros(len(y_pred)).long().to(device)
        loss = criterion(y_pred, y)

        loss_full.append(loss.item())
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if i % 10 == 0:
            writer.add_scalar("Train/Loss", loss.item(), step)

        if i % num_batches_validate == 0:
            model.eval()
            val_auc, val_mrr, val_ndcg5, val_ndcg10 = evaluate(model, "./data/val", num_workers, 200000)
            model.train()
            writer.add_scalar("Validation/AUC", val_auc, step)
            writer.add_scalar("Validation/MRR", val_mrr, step)
            writer.add_scalar("Validation/nDCG@5", val_ndcg5, step)
            writer.add_scalar("Validation/nDCG@10", val_ndcg10, step)

            early_stop, get_better = early_stopping(-val_auc)
            if early_stop:
                tqdm.write("Early stop.")
                break
            elif get_better:
                torch.save(
                    {
                        "model_state_dict": model.state_dict(),
                        "optimizer_state_dict": optimizer.state_dict(),
                        "step": step,
                        "early_stop_value": -val_auc,
                    },
                    f"./checkpoint/nrms/ckpt-{step}.pth",
                )


if __name__ == "__main__":
    train()
