import os
import sys
import json
import time
import emoji
from typing import List
import numpy as np

TORCHMOJI_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "torchMoji")
sys.path.insert(0, TORCHMOJI_PATH)

from torchMoji.torchmoji.global_variables import (
    PRETRAINED_PATH,
    NB_TOKENS,
    VOCAB_PATH,
    ROOT_PATH
    )
from torchMoji.torchmoji.model_def import torchmoji_emojis
from torchMoji.torchmoji.sentence_tokenizer import SentenceTokenizer


def top_elements(array, k):
    ind = np.argpartition(array, -k)[-k:]
    return ind[np.argsort(array[ind])][::-1]


def majority_vote(votes: List[bool]) -> bool:
    return sum(votes) > len(votes) // 2


class Sentiment:

    _max_message_len_words = 30
    _top_n_predictions = 5

    def __init__(self):

        if not os.path.isfile(PRETRAINED_PATH):
            os.system("(cd torchMoji && python scripts/download_weights_yes.py)")

        self._model = torchmoji_emojis(weight_path=PRETRAINED_PATH)

        # Initialize by loading dictionary and tokenize texts
        with open(VOCAB_PATH, 'r') as f:
            vocabulary = json.load(f)

        self._st = SentenceTokenizer(vocabulary, self._max_message_len_words)

        emoji_codes_path = os.path.join(ROOT_PATH, "data", "emoji_codes.json")
        with open(emoji_codes_path, 'r') as f:
            self._emoji_codes = json.load(f)

        with open("sentiment.json", 'r') as f:
            self._sentiments = json.load(f)

        pass

    def __call__(self, message: str):
        assert isinstance(message, str)

        tokens, _, _ = self._st.tokenize_sentences([message])

        prob, *_ = self._model(tokens)

        top = top_elements(prob, self._top_n_predictions)

        top_emoji = [self._emoji_codes[str(i)] for i in top]

        print(message)
        print(top_emoji)
        print(" ".join([emoji.emojize(e, use_aliases=True) for e in top_emoji]))
        votes = [self._sentiments[str(e)] for e in top]
        votes_str = [str(v) for v in votes]
        print(" ".join(votes_str))
        result = majority_vote(votes)
        print(result)

        return result
