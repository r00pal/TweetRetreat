#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 08:26:05 2017

@author: rjain11
"""

import datetime
import time
from slackclient import SlackClient
import tweepy
import MySQLdb

import query

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

HOST = "localhost"
USER = "root"
PASSWD = "roopal"
DATABASE = "hackathon"

def store_data(tweet_id, parent_id, created_at, text, product, user_id, fav_count, retweet_count, language, flag, score, screen_name, offers):
    db=MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE)
    cursor = db.cursor()
    insert_query = "INSERT INTO tweet_info (tweet_id, parent_id, created_at, text, product, user_id, fav_count, retweet_count, language, flag, score) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    insert_query_2 = "INSERT INTO user_info (user_id, screen_name, offers) VALUES (%s, %s, %s)"
    try:
        cursor.execute(insert_query, (tweet_id, parent_id, created_at, text, product, user_id, fav_count, retweet_count, language, flag, score))
        cursor.execute(insert_query_2, (user_id, screen_name, offers))
    except Exception as e:
        print (e)
    db.commit()
    cursor.close()
    db.close()

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
# s = u'Product: TurboTax\nTweet ID: 875434851721252865\nUser Handle: SkyeShepard\nSeverity Level: 1Text: RT @JJDJ1187: Gregg Jarrett: Trump should demand Mueller quit as special counsel <https://t.co/dzNLeqrZkz> via the @FoxNews Android app'
# str = s.splitlines()[0]
# print str.split(':')[1]
token = ''  # found at https://api.slack.com/web#authentication
sc = SlackClient(token)
if sc.rtm_connect():  # connect to a Slack RTM websocket
    while True:
        # print sc.rtm_read()  # read all data from the RTM websocket
        slack_data = sc.rtm_read()
        # slack_data = slack_data.replace("u'","")
        st = "Severity Level:"
        con = "See Conversation id"
        if(len(slack_data)==0):
             print ("No Response from Slack")
        elif(slack_data[0].get('text') is None):
            print ("No Response from Slack")
        elif(slack_data[0].get('username') == 'Slack API Tester'):
            print ("No Response from Slack")
        elif(con in slack_data[0].get('text')):
            tweetid = slack_data[0].get('text').split(':')[1].replace(' ','')
            convo = query.fetch_query(tweetid)
            for row in convo:
                sc.api_call(
                    "chat.postMessage",
                    channel="#general",
                    text=row
                    )
            # this is the user tweets
            print ("\n\n")
            print ("USER TWEET")
            # print slack_data[0].get('text').splitlines()[0].split(':')[1]
            # print slack_data[0].get('text').splitlines()[1].split(':')[1]
            # print slack_data[0].get('text').splitlines()[2].split(':')[1]
            # print slack_data[0].get('text').splitlines()[3].split(':')[1]
            # print slack_data[0].get('text').splitlines()[4].split(':')[1]
            print ("\n\n\n")
        else:
            print (slack_data[0])
            # print slack_data[0].get('text')
            # print type(slack_data[0].get('text'))
            print ("CUSTOMER RESPONSE TWEET")
            try:
                offers = 0
                replyid = 0
                userid = "0"
                pid = slack_data[0].get('text').split(';')[0].split(':')[1].replace(' ','')
                username = slack_data[0].get('text').split(';')[1].split(':')[1].replace(' ','')
                product =  slack_data[0].get('text').split(';')[2].split(':')[1].replace(' ','')
                response =  slack_data[0].get('text').split(';')[3].split(':')[1].replace('"','')
                time = datetime.datetime.utcnow()
                msg = '@{0} {1}'.format(username, response)
                # tweet = api.get_status(pid)
                # tweet = api.update_status(msg,pid)
                # replyid = tweet.id
                print (msg)
                store_data(str(replyid),pid,time,response,product,userid,0,0,"en",1,2,username,offers)
                #tweet_id, parent_id, created_at, text, product, user_id, fav_count, retweet_count, language, flag, score, screen_name, offers
            except Exception as e:
                sc.api_call(
                    "chat.postMessage",
                    channel="#general",
                    text="Give Proper Tweet Response"
                    )
            print ("\n\n\n\n\n")
        #time.sleep(1)
else:
    print ('Connection Failed, invalid token?')
