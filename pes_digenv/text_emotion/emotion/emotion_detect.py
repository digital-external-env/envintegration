from typing import Any

import torch
from transformers import BertForSequenceClassification, BertTokenizer


class EmotionModels:
    """Static, in order for the model to load only once"""

    tokenizer = BertTokenizer.from_pretrained(
        "pes_digenv/text_emotion/models/emotion-detection"
    )
    model = BertForSequenceClassification.from_pretrained(
        "pes_digenv/text_emotion/models/emotion-detection",
        problem_type="multi_label_classification",
    )


class Emotion:
    """Classification of emotions by text"""

    def predict(self, text: str) -> dict[Any, Any]:
        """A method for determining emotions from a text

        Args:
            text (str): _description_

        Returns:
            tuple: (emotion id, emotion title)
        """
        inputs = EmotionModels.tokenizer(text, return_tensors="pt")

        with torch.no_grad():
            logits = EmotionModels.model(**inputs).logits

        emotion_dict = {}

        for i, confidence in enumerate(
            torch.softmax(logits, -1).cpu().numpy()[0]
        ):
            emotion_dict[EmotionModels.model.config.id2label[i]] = confidence

        return emotion_dict
