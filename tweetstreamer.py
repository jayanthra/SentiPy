from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob import TextBlob

import credentials
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import json


class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(credentials.CONSUMER_KEY,
                            credentials.CONSUMER_SECRET)
        auth.set_access_token(credentials.ACCESS_TOKEN,
                              credentials.ACCESS_TOKEN_SECRET)
        return auth


class TwitterStreamer():
    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, json_file, hash_tag_list):
        listener = TwitterListener(json_file)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # filter data by the keywords:
        stream.filter(track=hash_tag_list)


class TwitterListener(StreamListener):
    def __init__(self, json_file):
        self.json_file = json_file

    def on_data(self, data):
        try:
            print(data)
            with open(self.json_file, 'a') as jsonfile:
                jsonfile.write(data+',')
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            return False
        print(status)


class TweetAnalyzer():

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(
            data=[tweet.text for tweet in tweets], columns=['text'])

       # df['id'] = np.array([tweet.id for tweet in tweets])
       # df['len'] = np.array([len(tweet.text) for tweet in tweets])
       # df['date'] = np.array([tweet.created_at for tweet in tweets])
       # df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
       # df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        return analysis.sentiment.polarity

if __name__ == '__main__':

    # To get streamed tweets 
    # hash_tag_list = ["donald trump"]
    # json_file = "tweets.json"

    # twitter_client = TwitterClient('jayanthracharya')

    # tweet = twitter_client.get_user_timeline_tweets(1)
    # print(tweet)
    # with open("self.json", "w") as text_file:
    #     print(str(tweet), file=text_file)

    # twitter_streamer = TwitterStreamer()
    # twitter_streamer.stream_tweets(json_file, hash_tag_list)

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name="realDonaldTrump", count=200)

    # print(dir(tweets[0]))
    # print(tweets[0].retweet_count)

    df = tweet_analyzer.tweets_to_data_frame(tweets)
    df['sentiment'] = np.array(
        [tweet_analyzer.analyze_sentiment(tweet) for tweet in df['text']])

    # print(df.head(10))
    with open('sentimetalanalysis.json', 'w') as f:
        f.write(json.dumps(json.loads(df.reset_index().to_json(orient='records')), indent=2))   

    # Graph plot
    # time_likes = pd.Series(data=df['likes'].values, index=df['date'])
    # time_likes.plot(figsize=(16, 4), label="likes", legend=True)
    # time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
    # time_retweets.plot(figsize=(16, 4), label="retweets", legend=True)
    # plt.show()
