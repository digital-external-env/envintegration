from typing import Any

from .emotion import Emotion
from .toxic import BertPredict, count_mat_detect


def is_toxic(text: str) -> bool:
    """
    Identifies toxicity in a text
    Args:
        texr (str): text

    Returns:
        bool: True if is toxic text, False otherwise

    """
    toxic = BertPredict()
    return bool(toxic.predict(text))


def get_mat(text: str) -> tuple[int, int, list[Any]]:
    """
    Counting swear words
    Args:
        text: The text to be parsed is given as str. Can be any length

    Returns:
        tuple: Returns a tuple. The first cell of which contains the number of swear words,
                                in the second - the percentage of swear words in the text
                                and in the third - a lot of swear words.
    """
    return count_mat_detect(text)


def emotion(text: str) -> dict[Any, Any]:
    """
    Identifies emotions in text

    Args:
        text (str): text

    Returns:
        dict: dict of emotions and their confidence
    """
    emo = Emotion()
    return emo.predict(text)
