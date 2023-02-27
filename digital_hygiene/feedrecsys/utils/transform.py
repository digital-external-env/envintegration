import numpy as np
import pandas as pd


def transform_entity_embedding(source, target, entity2int_path, entity_embedding_dim):
    entity_embedding = pd.read_table(source, header=None)
    entity_embedding["vector"] = entity_embedding.iloc[:, 1:101].values.tolist()
    entity_embedding = entity_embedding[[0, "vector"]].rename(columns={0: "entity"})

    entity2int = pd.read_table(entity2int_path)
    merged_df = pd.merge(entity_embedding, entity2int, on="entity").sort_values("int")
    entity_embedding_transformed = np.random.normal(size=(len(entity2int) + 1, entity_embedding_dim))
    for row in merged_df.itertuples(index=False):
        entity_embedding_transformed[row.int] = row.vector
    np.save(target, entity_embedding_transformed)
