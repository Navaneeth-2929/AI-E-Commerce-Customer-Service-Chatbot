from textblob import TextBlob


class SentimentAnalyzer:
    def classify(self, text: str) -> str:
        polarity = TextBlob(text).sentiment.polarity
        if polarity > 0.2:
            return "positive"
        if polarity < -0.2:
            return "negative"
        return "neutral"
