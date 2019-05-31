import unittest

import sentiment


class SentimentTest(unittest.TestCase):
    def test_sentiment(self):
        sent = sentiment.Sentiment()

        test_sentences = [
            "This film is terrible",
            "This film is great",
            "I’m very happy that my team won the world cup!",
            "I feel a bit sad today",
            "I feel much better",
            "Still feel sick",
            "I can't say I feel bad today",
            "It is far from bad today",
            "This is anything but good",
            "This is nothing close to good",
            "Pleasure is under question",
        ]

        r = sent(test_sentences[2])

        print(r)

        self.assertEqual(r, True)
