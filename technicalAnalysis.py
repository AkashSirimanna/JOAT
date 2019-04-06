from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import json
import requests
from math import pow
import datetime
import matplotlib.pyplot as plot
import matplotlib.dates
from mpl_finance import candlestick_ohlc
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web
import webbrowser
import sys
from sklearn import linear_model
import numpy as np 

def visualAnalysis(ticker):
	plot.figure()
	style.use('ggplot')

	start  = datetime.datetime (2018,6,1)
	end = datetime.datetime(2019,1,1)

	frame = web.DataReader(ticker,'yahoo',start,end)
	fileName = ticker + '.csv'
	frame.to_csv(fileName)



	frame = pd.read_csv(ticker+'.csv',parse_dates = True,index_col = 0)
	frame['50DMA'] = frame['Close'].ewm(com=0.33333333).mean()


	xAxis = plot.subplot2grid((6,1),(0,0),rowspan=5,colspan=1)
	plot.xlabel('Date')
	plot.ylabel('Close Price')
	plot.title(ticker)
	xAxis.xaxis_date()
	# xAxis.plot(frame.index,frame['50DMA'])
	xAxis.plot(frame.index,frame['Close'])

	wWidth = int(len(frame.index)/10)
	cumWidth = wWidth
	maxWindow = 0
	minWindow = 1000000
	maxIndex = frame.index[0]
	minIndex = frame.index[0]
	mayBePeak = False
	mayBeTrough = False
	peakList = []
	troughList = []

	for i in range(len(frame['50DMA'])-1):
		if (cumWidth < 0):
			cumWidth = wWidth
			if (maxWindow != 0):
				xAxis.plot(maxIndex,maxWindow,'bo')
				peakList.append([maxIndex,maxWindow])
			if (minWindow != 1000000):
				xAxis.plot(minIndex,minWindow,'go')
				troughList.append([minIndex,minWindow])
			maxWindow = 0
			minWindow = 1000000

		if (frame.iloc[i]['50DMA'] < frame.iloc[i+1]['50DMA']): #Find peaks
			mayBePeak = True

		if (frame.iloc[i]['50DMA'] > frame.iloc[i+1]['50DMA'] and mayBePeak == True):
			mayBePeak = False
			if (frame['50DMA'][i] > maxWindow):
				maxWindow = frame['50DMA'][i]
				maxIndex = frame.index[i]

		if (frame.iloc[i]['50DMA'] > frame.iloc[i+1]['50DMA']): #Find troughs
			mayBeTrough = True

		if (frame.iloc[i]['50DMA'] < frame.iloc[i+1]['50DMA'] and mayBeTrough == True):
			mayBeTrough= False
			if (frame['50DMA'][i] < minWindow):
				minWindow = frame['50DMA'][i]
				minIndex = frame.index[i]		

		cumWidth = cumWidth - 1

	minimums = [[0,1000000],[0,1000000]]
	for row in troughList:
		current = row[1]
		if (current < minimums[0][1]):
			minimums[1] = minimums[0]
			minimums[0] = [row[0],current]
		elif(current < minimums[1][1]):
			minimums[1] = [row[0],current]

	maximums = [[0,0],[0,0]]
	for row in peakList:
		current = row[1]
		if (current > maximums[0][1]):
			maximums[1] = maximums[0]
			maximums[0] = [row[0],current]
		elif(current > maximums[1][1]):
			maximums[1] = [row[0],current]	

	xAxis.fill_between(frame.index,minimums[0][1],minimums[1][1],color='green',label='Support',interpolate= True,alpha=.6)
	xAxis.fill_between(frame.index,maximums[0][1],maximums[1][1],color='orange',label='Resistance',interpolate= True,alpha=.6)
	# Consider plotting a region of the graph in which the support/resistance lies
	plot.legend()


def main(ticker):
	visualAnalysis(ticker)
	plot.show(block=False)
	import tweetAnalysis as tweetAnalysis
	tweetAnalysis.main(ticker)


