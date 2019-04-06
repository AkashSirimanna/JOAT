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
import tkinter as tk
from tkinter import simpledialog

def visualAnalysis(ticker):
	plot.figure()
	style.use('ggplot')

	start  = datetime.datetime (2010,1,1)
	end = datetime.datetime(2018,12,31)

	frame = web.DataReader(ticker,'yahoo',start,end)
	fileName = ticker+ 'main' + '.csv'
	frame.to_csv(fileName)

	frame = pd.read_csv(fileName,parse_dates = True,index_col = 0)
	frame['100DMA'] = frame['Close'].rolling(window=200,min_periods = 0).mean()
	frame['50DMA'] = frame['Close'].rolling(window=50,min_periods = 0).mean()
	framePrice = frame['Close'].resample('10D').ohlc()
	frameVolume = frame['Volume'].resample('10D').sum() 

	framePrice.reset_index(inplace=True)

	framePrice['Date'] = framePrice['Date'].map(matplotlib.dates.date2num)

	xAxis = plot.subplot2grid((6,1),(0,0),rowspan=5,colspan=1)
	plot.xlabel('Date')
	plot.ylabel('Close Price')
	plot.title(ticker)
	xAxis.xaxis_date()
	xAxis.plot(frame.index,frame['100DMA'])
	xAxis.plot(frame.index,frame['50DMA'])
	candlestick_ohlc(xAxis,framePrice.values,width=3,colorup='g',colordown='r')
	plot.show(block=False)

application_window = tk.Tk()

ticker = simpledialog.askstring("Jack Of All Trades", "Enter A Ticker With Atleast 5 Years of Price Action",
                                parent=application_window)

try:
	visualAnalysis(ticker)
except:
	print('An error has occured while plotting price action of stock')

try:
	import dcf as intrinsicValuation
	intrinsicValuation.main(ticker)
except:
	print('An error has occured while modelling discounted cash flows')
	try:
		import technicalAnalysis as techAnalysis
		techAnalysis.main(ticker)
	except:
		print('An error has occured while analysing support and resistance levels')
		try:
			import tweetAnalysis as tweetAnalysis
			tweetAnalysis.main(ticker)
		except:
			print('An error has occured while analysing sentiment of stock')





