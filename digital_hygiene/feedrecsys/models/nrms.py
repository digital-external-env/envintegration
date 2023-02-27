import torch
import torch.nn as nn
import torch.nn.functional as F

from feedrecsys.models.common import AdditiveAttention, DotProductClickPredictor, MultiHeadSelfAttention


class UserEncoder(torch.nn.Module):
    def __init__(self, word_embedding_dim: int = 300, num_attention_heads: int = 15, query_vector_dim: int = 200):
        super().__init__()
        self.multihead_self_attention = MultiHeadSelfAttention(word_embedding_dim, num_attention_heads)
        self.additive_attention = AdditiveAttention(query_vector_dim, word_embedding_dim)

        self.word_embedding_dim = word_embedding_dim
        self.num_attention_heads = num_attention_heads

    def forward(self, user_vector):
        multihead_user_vector = self.multihead_self_attention(user_vector)
        final_user_vector = self.additive_attention(multihead_user_vector)

        return final_user_vector


class NewsEncoder(torch.nn.Module):
    def __init__(
        self,
        pretrained_word_embedding: torch.Tensor,
        num_words: int = 70976,
        word_embedding_dim: int = 300,
        num_attention_heads: int = 15,
        query_vector_dim: int = 200,
    ):
        super().__init__()
        if pretrained_word_embedding is None:
            self.word_embedding = nn.Embedding(num_words, word_embedding_dim, padding_idx=0)
        else:
            self.word_embedding = nn.Embedding.from_pretrained(pretrained_word_embedding, freeze=False, padding_idx=0)

        self.multihead_self_attention = MultiHeadSelfAttention(word_embedding_dim, num_attention_heads)
        self.additive_attention = AdditiveAttention(query_vector_dim, word_embedding_dim)

    def forward(self, news):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        news_vector = F.dropout(
            self.word_embedding(news["title"].to(device)),
            p=self.config.dropout_probability,
            training=self.training,
        )
        multihead_news_vector = self.multihead_self_attention(news_vector)
        multihead_news_vector = F.dropout(
            multihead_news_vector,
            p=self.config.dropout_probability,
            training=self.training,
        )
        final_news_vector = self.additive_attention(multihead_news_vector)

        return final_news_vector


class NRMS(torch.nn.Module):
    def __init__(
        self,
        num_words: int = 70976,
        word_embedding_dim: int = 300,
        num_attention_heads: int = 15,
        query_vector_dim: int = 200,
        pretrained_word_embedding=None,
    ):
        super().__init__()

        self.news_encoder = NewsEncoder(
            pretrained_word_embedding,
            num_words,
            word_embedding_dim,
            num_attention_heads,
            query_vector_dim,
        )
        self.user_encoder = UserEncoder(word_embedding_dim, num_attention_heads, query_vector_dim)
        self.click_predictor = DotProductClickPredictor()

    def forward(self, candidate_news, clicked_news):
        candidate_news_vector = torch.stack([self.news_encoder(x) for x in candidate_news], dim=1)
        clicked_news_vector = torch.stack([self.news_encoder(x) for x in clicked_news], dim=1)
        user_vector = self.user_encoder(clicked_news_vector)
        click_probability = self.click_predictor(candidate_news_vector, user_vector)

        return click_probability

    def get_news_vector(self, news):
        return self.news_encoder(news)

    def get_user_vector(self, clicked_news_vector):
        return self.user_encoder(clicked_news_vector)

    def get_prediction(self, news_vector, user_vector):
        return self.click_predictor(news_vector.unsqueeze(dim=0), user_vector.unsqueeze(dim=0)).squeeze(dim=0)
