# coding=utf-8
import re
from typing import Any


def count_mat_detect(
    text: str, mat_dict_path: str = "pes_digenv/text_emotion/models/mats.txt"
) -> tuple[int, int, list[Any]]:
    """The module for counting swear words

    :param text: The text to be analyzed is set as str. Can be of any length
    :type text: str
    :return: Returns a tuple. The first cell of which contains the number
    of swear words, the second contains the percentage of swear words
    in the text and the third contains a lot of swear words.
    :rtype: tuple
    """

    with open(mat_dict_path, "r", encoding="utf-8") as inp:
        mats = set(map(lambda x: x[:-1], inp.readlines()))

    words = re.sub(r"[\W_0-9]", " ", text.lower()).split()
    words_ammount = len(words)
    count_duck = 0
    matwords = []
    for word in words:
        if word in mats:
            count_duck += 1
            matwords.append(word)

    return (
        count_duck,
        int(count_duck / words_ammount * 100),
        list(set(matwords)),
    )
