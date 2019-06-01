import os
import sys
import json
import emoji
import numpy as np
from typing import List

# torchMoji is an external git-subtree dependency, so
# let's "link" it with "system path" method.

TORCHMOJI_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "torchMoji")
sys.path.insert(0, TORCHMOJI_PATH)

from torchMoji.torchmoji.global_variables import (
    PRETRAINED_PATH,
    VOCAB_PATH,
    ROOT_PATH
    )
from torchMoji.torchmoji.model_def import torchmoji_emojis
from torchMoji.torchmoji.sentence_tokenizer import SentenceTokenizer


def top_elements(array: np.ndarray, k: int) -> np.ndarray:
    """ Determine top-K classes. """
    ind = np.argpartition(array, -k)[-k:]
    return ind[np.argsort(array[ind])][::-1]


def majority_vote(votes: List[bool]) -> bool:
    return sum(votes) > len(votes) // 2


class Sentiment:
    """
    Wrapper class for torchMoji.
    Repo:
    https://github.com/huggingface/torchMoji
    Original DeepMoji paper:
    "Using millions of emoji occurrences to learn any-domain
    representations for detecting sentiment, emotion and sarcasm"
    https://arxiv.org/pdf/1708.00524.pdf
    """

    # Maximal lenght of a sentense in words
    _max_message_len_words = 30
    # Top K smiley predictions to derive sentiment from
    _top_k_predictions = 5

    def __init__(self):
        """
        Ctor.
        """

        # Automatically download weights
        if not os.path.isfile(PRETRAINED_PATH):
            os.system("(cd torchMoji && python scripts/download_weights_yes.py)")

        # Instanciate a pytorch model
        self._model = torchmoji_emojis(weight_path=PRETRAINED_PATH)

        # Load vocabulary
        with open(VOCAB_PATH, 'r') as f:
            vocabulary = json.load(f)

        # Create tokenizer to split a sentence into words
        self._st = SentenceTokenizer(vocabulary, self._max_message_len_words)

        # Load a mapping in neural network prediction to smileys
        emoji_codes_path = os.path.join(ROOT_PATH, "data", "emoji_codes.json")
        with open(emoji_codes_path, 'r') as f:
            self._emoji_codes = json.load(f)

        # This is a reduction of 64 smileys into there "happiness" bool flag
        with open("sentiment.json", 'r') as f:
            self._sentiments = json.load(f)

        pass

    def __call__(self, message: str) -> bool:
        """
        Perform inference.
        :param message: text sentense
        :return: True if a sentence has positive sentiment, False - if negative
        """

        assert isinstance(message, str)

        # Tokenize sentence
        tokens, _, _ = self._st.tokenize_sentences([message])

        # Neural network inference
        prob, *_ = self._model(tokens)

        # Analyse only top K predictions out of 64
        top = top_elements(prob, self._top_k_predictions)

        if False:
            # See original top-K smileys before reduction
            top_emoji = [self._emoji_codes[str(i)] for i in top]
            print(" ".join([emoji.emojize(e, use_aliases=True) for e in top_emoji]))

        # Reduce to "happiness" flag
        votes = [self._sentiments[str(e)] for e in top]
        result = majority_vote(votes)

        return result
