import mysql.connector
from mysql.connector import Error
import tweepy
import json
from dateutil import parser
import time
import os
import credentials


def connect(username, created_at, tweet, place):
	"""
	connect to MySQL database and insert twitter data
	"""
	try:
		con = mysql.connector.connect(host = 'localhost',
		database='#######', user='root', password = '######', charset = 'utf8')


		if con.is_connected():
			"""
			Insert twitter data
			"""
			cursor = con.cursor()
			# twitter, Covid-19
			query = "INSERT INTO tweets2 (username, created_at, tweet, place) VALUES (%s, %s, %s, %s)"
			cursor.execute(query, (username, created_at, tweet, place))
			con.commit()


	except Error as e:
		print(e)

	cursor.close()
	con.close()

	return


# Tweepy class to access Twitter API
class Streamlistener(tweepy.StreamListener):

	def on_connect(self):
		print("You are connected to the Twitter API")

	def on_error(self):
		if status_code != 200:
			print("error found")
			# returning false disconnects the stream
			return False

	"""
	This method reads in tweet data as JSON
	"""
	def on_data(self,data):

		try:
			raw_data = json.loads(data)

			if 'text' in raw_data:

				username = raw_data['user']['screen_name']
				created_at = parser.parse(raw_data['created_at'])
				tweet = raw_data['text']

				if raw_data['place'] is not None:
					place = raw_data['place']['country']
					print(place)
				else:
					place = None


				# insert data collected into MySQL database
				connect(username, created_at, tweet, place)
				print("Tweet colleted at: {} ".format(str(created_at)))
		except Error as e:
			print(e)


if __name__== '__main__':


	# authentificate to access twitter API
	auth = tweepy.OAuthHandler(credentials.API_KEY, credentials.API_SECRET_KEY)
	auth.set_access_token(credentials.ACCESS_TOKEN, credentials.ACCESS_TOKEN_SECRET)
	api =tweepy.API(auth, wait_on_rate_limit=True)

	# create instance of Streamlistener
	listener = Streamlistener(api = api)
	stream = tweepy.Stream(auth, listener = listener)

	# track words
	track = ['#coronavirus', '#covid19', "#covid"]

	stream.filter(track = track, languages = ['en'])
