from __future__ import print_function
import tweepy
import json
import MySQLdb 
from dateutil import parser

from slacker import Slacker
import subprocess
import json
#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

#Variables that contains the user credentials to access Twitter API
consumer_key = 'OoDlic06gNPoweQZJ7YnO64F9'
consumer_secret = 'Cwr94rh8adYxKPTPLGp7DPERgGYm6t5nvpppQmAmCdxEx6vTA5'
access_token = '834249929128341505-NYcDFhQ8nqRITmczp4IhZgyIcbElPWR'
access_token_secret = 'dCXXBspFY83oUMt0X2jeRFlwOyB82ejC4F7QiaAYTbxd3'

HOST = "localhost"
USER = "root"
PASSWD = "roopal"
DATABASE = "hackathon"

POSITIVE = 0
NEGATIVE = 0

def store_data(tweet_id, parent_id, created_at, text, product, user_id, fav_count, retweet_count, language, flag, score, screen_name, offers):
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE, charset="utf8")
    cursor = db.cursor()
    insert_query = "INSERT INTO tweet_info (tweet_id, parent_id, created_at, text, product, user_id, fav_count, retweet_count, language, flag, score) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s)"
    cursor.execute(insert_query, (tweet_id, parent_id, created_at, text, product, user_id, fav_count, retweet_count, language, flag, score))
    insert_query_2 = "INSERT INTO user_info (user_id, screen_name, offers) VALUES (%s, %s, %s)"
    cursor.execute(insert_query_2, (user_id, screen_name, offers))
    cursor.close()
    db.commit()
    db.close()
    return

def getSeverity(x):
    if x > -0.6:
        return "1"
    elif x > -0.7:
        return "2"
    elif x > -0.8:
        return "3"
    elif x > -0.9:
        return "4"
    else:
        return "5"
    return "-1"

#set slack credentials
slack = Slacker('xoxp-86879456164-197794379475-198675153702-381ef567806dcc55be7283d27f1322cc')
def sendToSlack(product, tweet_id, parent_id, screen_name, score, text):
    msg = "Product: "+product+"\n"
    print (msg)
    pid = tweet_id
    if parent_id:
        pid = parent_id
    msg += "Tweet ID: " + str(pid)+"\n"
    msg += "User Handle: " + screen_name+"\n"
    msg+="Severity Level: " + getSeverity(score)+"\n"
    msg+="Text: "+ text
    print ("\tMessage:\n" + msg + "\n\n")
    slack.chat.post_message('#general', msg)
    return True

def getScore(jsonObj):
    #print (jsonObj)
    try:
        score = jsonObj['keywords'][0]['sentiment']['score']
    except:
        score = 0
    print (score)
    return score

def executeCurl(tweetRecevied):
    data = ""
    try:
        tweetTextRecevied = tweetRecevied['text']
        param1 = "{ \"text\": \""
        param3 = "\",\"features\": { \"keywords\": {\"emotion\": true,\"sentiment\": true,\"limit\": 1}}}"
        #udata = tweetTextRecevied.encode('utf-8')
        tweetTextRecevied = tweetTextRecevied.replace("\"","\\\"")
        tweetTextRecevied = tweetTextRecevied.replace("@"," ")
        tweetTextRecevied = tweetTextRecevied.replace("#"," ")
        param = param1 + tweetTextRecevied + param3
        text_file = open("parameters.json", "w")
        text_file.write(param)
        text_file.close()
        command = 'curl -X POST -H "Content-Type: application/json" -u "cb5f1d0c-cf33-4cae-b1c8-cf12c4a04eca":"G0qGrgAoRhjL" -d @parameters.json "https://gateway.watsonplatform.net/natural-language-understanding/api/v1/analyze?version=2017-02-27"'
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        #out = "{ \"language\": \"en\", \"keywords\": [ { \"text\": \"Good HEAVENS\", \"sentiment\": {        \"score\": -0.453591      },      \"relevance\": 0.900475,      \"emotion\": {        \"sadness\": 0.185634, \"joy\": 0.486092, \"fear\": 0.18237, \"disgust\": 0.040095, \"anger\": 0.215007      }    }  ]}"
        data = json.loads(out)
    except Exception as e:
        print ("Error" + str(e))

    return data

class StdOutListener(StreamListener):
    def on_data(self, data):
        global POSITIVE
        global NEGATIVE
        try:
            datajson = json.loads(data)
            jsonObj = executeCurl(datajson)
            tweet_id = datajson['id']
            parent_id = datajson['in_reply_to_status_id']
            created_at = parser.parse(datajson['created_at'])
            text = datajson['text']
            user_id = datajson['id_str']
            fav_count = datajson['favorite_count']
            retweet_count = datajson['retweet_count']
            language = datajson['lang']
            flag = 0
            score = getScore(jsonObj)
            screen_name = datajson['user']['screen_name']
            offers = 0
            print("Tweet collected at " + str(created_at))
            product = ""
            if "quickbook" in datajson['text'].lower():
                product = "quickbook"
            elif "turbotax" in datajson['text'].lower():
                product = "turbotax"
            elif "mint" in datajson['text'].lower():
                product = "mint"
            elif "trump" in datajson['text'].lower():
                product = "politics"

            if score < 0:
                NEGATIVE = NEGATIVE + 1
            else:
                POSITIVE = POSITIVE + 1
            print ("Count of positive tweets:", POSITIVE)
            print ("Count of negative tweets:", NEGATIVE)
            if score < -0.5:
                sendToSlack(product, tweet_id, parent_id, screen_name, score, text)
                store_data(tweet_id, parent_id, created_at, text, product, user_id, fav_count, retweet_count, language, flag, score, screen_name, offers)
        except Exception as e:
            print (str(e))

if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    #This line filter Twitter Streams to capture data by the keywords: 'inuit', '@mint', 'turbotax', 'quickbook'
    #Trump is included to keep it running as live tweets about Trump are high :D
    stream.filter(track=['Trump','intuit', '@mint', '@turbotax', '@quickbook'])