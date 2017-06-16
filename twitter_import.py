import tweepy
import jsonpickle
import os.path

total_tweets = 1000
limit_fetch = 100
query = '@mint'

output_file = 'mint.json'

consumer_key="pla3KEF20rFSKijgygVJEib07"
consumer_secret="YW0D5GmweDmX7TzthMCA821C3xmt3Zutf70G64fPmHgsfbh5lZ" 

auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

sinceId = None

current_count = 0
with open(output_file, 'w') as f:
    while current_count < total_tweets:
        try:
            if (not sinceId):
                result = api.search(q=query, count=limit_fetch)
            else:
                result = api.search(q=query, count=limit_fetch, since_id=sinceId)

            if not result:
                print("No more tweets found")
                break

            for tweet in result:
                f.write(jsonpickle.encode(tweet._json, unpicklable=True) +'\n')

            current_count += len(result)

            print("Downloaded {0} tweets".format(current_count))

            sinceId = result[-1].id

        except tweepy.TweepError as e:
            print("Error : " + str(e))
            break