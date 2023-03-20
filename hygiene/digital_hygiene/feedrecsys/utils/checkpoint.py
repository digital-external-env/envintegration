import os

import numpy as np


class EarlyStopping:
    def __init__(self, patience=5):
        self.patience = patience
        self.counter = 0
        self.best_loss = np.Inf

    def __call__(self, val_loss):
        if val_loss < self.best_loss:
            early_stop = False
            self.counter = 0
            self.best_loss = val_loss
        else:
            self.counter += 1
            if self.counter >= self.patience:
                early_stop = True
            else:
                early_stop = False

        return (early_stop,)


def latest_checkpoint(directory):
    if not os.path.exists(directory):
        return None

    all_checkpoints = {int(x.split(".")[-2].split("-")[-1]): x for x in os.listdir(directory)}
    if not all_checkpoints:
        return None

    return os.path.join(directory, all_checkpoints[max(all_checkpoints.keys())])
