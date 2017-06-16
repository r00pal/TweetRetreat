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

#set slack credentials
slack = Slacker('xoxp-86879456164-197794379475-198675153702-381ef567806dcc55be7283d27f1322cc')

# def sendToSlack(tweetRecevied, jsonObj):
# 	msg = ""
# 	if "quickbook" in tweetRecevied['text'].lower():
# 		msg = "Product: QuickBooks\n"
# 	elif "turbotax" in tweetRecevied['text'].lower():
# 		msg = "Product: TurboTax\n"
# 	elif "mint" in tweetRecevied['text'].lower():
# 		msg = "Product: Mint\n"
# 	else:
# 		return False
# 	msg+="ID: "+tweetRecevied['id_str']+"\n"
# 	msg+="Link: "+"\n"
# 	msg+="User: "+"\n"
# 	msg+="Text: "+tweetRecevied['text']
# 	print "\n\n\n\tMessage:\n\t\t"+msg+"\n\n"
# 	slack.chat.post_message('#general', msg)
# 	return True

def getScore(jsonObj):
	print (jsonObj)
	try:
		score = jsonObj['keywords'][0]['sentiment']['score']
	except:
		score = 0
	return score

def executeCurl(tweetRecevied):
	data = ""
	try:
		tweetTextRecevied = tweetRecevied['text']
		param1 = "{ \"text\": \""
		param3 = "\",\"features\": { \"keywords\": {\"emotion\": true,\"sentiment\": true,\"limit\": 1}}}"
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
		tweetRecevied = json.loads(data)
		jsonObj = executeCurl(tweetRecevied)
		print ("\n\n\t")
		print (getScore(jsonObj))
		print ("\n\n")
		#if getScore(jsonObj) < -0.30:
		#	sendToSlack(tweetRecevied,jsonObj)
		#print data
		print (tweetRecevied['text'].encode('utf-8'))
		return True
	def on_error(self, status):
		print (status)

if __name__ == '__main__':
	#This handles Twitter authetification and the connection to Twitter Streaming API
	l = StdOutListener()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	stream = Stream(auth, l)
	#This line filter Twitter Streams to capture data by the keywords: 'trump', 'inuit', '@mint', 'turbotax', 'quickbook'
	stream.filter(track=['trump', 'inuit', '@mint', 'turbotax', 'quickbook'])
