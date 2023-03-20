import torch


class DotProductClickPredictor(torch.nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, candidate_news_vector, user_vector):
        probability = torch.bmm(candidate_news_vector, user_vector.unsqueeze(dim=-1)).squeeze(dim=-1)

        return probability
