import re
from typing import Any

import pymorphy2

from .porter_stem import Porter


class SmallTalk:
    def __init__(self) -> None:
        self.morph = pymorphy2.MorphAnalyzer()
        self.stemmer = Porter()

        self.AFFECT = re.compile(
            "(ик|ек|к|ец|иц|оск|ечк|оньк|еньк|ышк|инш|ушк|юшк)$"
        )

    def isAffect(self, sentence: str) -> tuple[bool, list[Any]]:
        """
        The sentence is passed and tuple(bool, list) is returned are there any diminutive words and a list of such words
        """
        words = sentence.split()
        words_affect = []
        affect = False

        for word in words:
            if self.isNoun(word):
                word_stem = self.word_stemming(word)
                word_affect = re.search(self.AFFECT, word_stem)
                if word_affect:
                    words_affect.append(word)
                    affect = True

        return affect, list(set(words_affect))

    def isNoun(self, word: str) -> bool:
        words_form = self.morph.parse(word)
        for word_form in words_form:
            if word_form.score >= 0.4 and "NOUN" in word_form.tag:
                return True

        return False

    def list_stemming(self, word_list: list[str]) -> list[str]:
        stem_list = []

        for word in word_list:
            stem_list.append(self.word_stemming(word))

        return stem_list

    def word_stemming(self, word: str) -> str:
        return self.stemmer.stem(word)
