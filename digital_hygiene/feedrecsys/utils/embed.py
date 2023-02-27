import numpy as np
import pandas as pd


def generate_word_embedding(source, target, word2int_path, word_embedding_dim):
    word2int = pd.read_table(word2int_path, na_filter=False, index_col="word")
    source_embedding = pd.read_table(source, index_col=0, sep=" ", header=None, names=range(word_embedding_dim))
    source_embedding.index.rename("word", inplace=True)
    merged = word2int.merge(source_embedding, how="inner", left_index=True, right_index=True)
    merged.set_index("int", inplace=True)

    missed_index = np.setdiff1d(np.arange(len(word2int) + 1), merged.index.values)
    missed_embedding = pd.DataFrame(data=np.random.normal(size=(len(missed_index), word_embedding_dim)))
    missed_embedding["int"] = missed_index
    missed_embedding.set_index("int", inplace=True)

    final_embedding = pd.concat([merged, missed_embedding]).sort_index()
    np.save(target, final_embedding.values)
