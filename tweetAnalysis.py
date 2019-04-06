import GetOldTweets3 as got3
import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plot 
from textblob import TextBlob
import numpy as np
import pandas as pd

def sentimentAnalysis(ticker):
	plot.figure()

	start  = datetime.datetime (2018,6,1)
	end = datetime.datetime(2019,1,1)
	df = web.DataReader(ticker,'yahoo',start,end)
	df = df['Adj Close']

	tweetCriteria = got3.manager.TweetCriteria().setQuerySearch(ticker).setSince("2018-06-01").setUntil("2019-01-01").setMaxTweets(2500).setTopTweets(True)
	tweet = got3.manager.TweetManager.getTweets(tweetCriteria)
	listOfTweets = []
	columns = ['date','cumulative_sentiment']
	cum_sentiment = 0

	for msg in tweet:
	    sentiment = TextBlob(msg.text).sentiment
	    if (sentiment.polarity < 0):
	    	cum_sentiment = cum_sentiment + sentiment.polarity
	    cum_sentiment = cum_sentiment + sentiment.polarity
	    listOfTweets.append([msg.date.replace(tzinfo=None),cum_sentiment])

	df2 = pd.DataFrame.from_records(listOfTweets,columns=columns)
	df2.dropna(how='any',inplace=True)


	frame = pd.read_csv(ticker+'.csv',parse_dates = True,index_col = 0)
	frame['50DMA'] = frame['Close'].ewm(com=0.33333333).mean()

	xAxis = plot.subplot2grid((6,1),(0,0),rowspan=5,colspan=1)
	plot.xlabel('Date')
	plot.ylabel('Close Price')
	plot.title(ticker)
	xAxis.xaxis_date()
	xAxis.plot(frame.index,frame['Close'])

	xAxis2 = xAxis.twinx()
	xAxis2.set_ylabel('Cumulative Sentiment', color="green")  # we already handled the x-label with ax1
	xAxis2.plot(df2.date.iloc[::-1], df2.cumulative_sentiment, color="green")
	xAxis2.tick_params(axis='y', labelcolor="orange")

def main(ticker):
	sentimentAnalysis(ticker)
	plot.show()
















