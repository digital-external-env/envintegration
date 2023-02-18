import pymorphy2


class Imperative:
    def __init__(self) -> None:
        self.morph = pymorphy2.MorphAnalyzer()

    def isPovel(self, sentence: str, excl: bool = False) -> bool:
        """
        The input line is
        If there is a word in the imperative mood, returns True
        If excel = True, it will return True only if the speakers are not included in the action (go), if we go, it will be False
        """
        sentence_words = sentence.split()

        for word in sentence_words:
            if self.isWordPovel(word, excl):
                return True

        return False

    def isWordPovel(self, word: str, excl: bool = False) -> bool:
        """
        If the word is in the imperative mood, returns True
        If excel = True, it will return True only if the speakers are not included in the action (go, go), if we go, it will be False
        """
        word_morph = self.morph.parse(word)
        for w_morph in word_morph:
            if w_morph.score >= 0.4:
                if "impr" in w_morph.tag:
                    if excl:
                        if "excl" in w_morph.tag:
                            return True
                        else:
                            continue

                    return True

                return False

        return False
