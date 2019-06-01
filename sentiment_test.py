import unittest

import sentiment


class SentimentTest(unittest.TestCase):

    def test_sentiment(self):
        sentiment_analyser = sentiment.Sentiment()

        test_sentences = [
            "I’m very happy that my team won the world cup!",
            "I feel a bit sad today",
            "I feel much better",
            "Still feel sick",
        ]

        expected_sentiments = [
            True,
            False,
            True,
            False,
        ]

        for sentence, expected_sentiment in zip(test_sentences, expected_sentiments):
            sentim = sentiment_analyser(sentence)
            self.assertEqual(sentim, expected_sentiment)
