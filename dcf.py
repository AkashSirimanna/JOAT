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

def technicalAnalysis(ticker,url,figureToGet):
	site = urlopen(url+ticker)
	soup = BeautifulSoup(site,"html.parser")
	file = open(ticker+".txt","w")
	file.write(soup.find('pre').text.lower())
	file.close()
	file = open(ticker+".txt","r")
	text = json.load(file)
	file.close()
	data = []
	for item in text[ticker][figureToGet]:
		data.append(text[ticker][figureToGet][item])
	return data

def getKeyData(url,figureToGet):
	site = urlopen(url)
	soup = BeautifulSoup(site,"html.parser")
	for row in soup.find_all('ul',{'class':'list list--kv list--col50'}):
		for item in row.find_all('small'):
			if(item.text == figureToGet):
				figure = item.find_next().text
				if(figureToGet == "Market Cap"):
					figure = item.find_next().text.replace("$","")
				if(figure[-1] == 'B'):
					return float(figure.replace('B',""))*1000000000
				elif(figure[-1] == 'M'):
					return float(figure.replace('M',""))*1000000
				else:
					return figure

def DCF(ticker):
	# Collection and forecast of Free Cash Flow
	data = technicalAnalysis(ticker,"https://financialmodelingprep.com/api/financials/cash-flow-statement/",'free cash flow')
	fcfGrowth = ((float(data[-1])/float(data[0]))-1) / 5
	earningsData = technicalAnalysis(ticker,"https://financialmodelingprep.com/api/financials/income-sheet-statement/",'revenue')
	earningsGrowth = ((float(earningsData[-1])/float(earningsData[0]))-1) / 5
	cumGrowth = 0
	for i in range(len(data)-1,1,-1):
		cumGrowth += (float(data[i])/float(data[i-1])) - 1

	cumGrowth /= 5
	if (cumGrowth > 0):
		earningsGrowth = cumGrowth
	elif (earningsGrowth < 0):
		print("We do not valuate companies with decreasing revenue")
		sys.exit()

	data[0] = data[-1]
	for i in range(0,len(data)-1):
		data[i] = float(data[i])*(1+fcfGrowth)
		data[i+1] = float(data[i])

	# Calculation of WACC
	liabilities = technicalAnalysis(ticker,"https://financialmodelingprep.com/api/financials/balance-sheet-statement/","total non-current liabilities")[-1]
	interest = technicalAnalysis(ticker,"https://financialmodelingprep.com/api/financials/income-sheet-statement/","interest expense")[-1]
	marketCap = getKeyData("https://www.marketwatch.com/investing/stock/" + ticker,"Market Cap")
	sharesOSTD = getKeyData("https://www.marketwatch.com/investing/stock/" + ticker,"Shares Outstanding")
	beta = getKeyData("https://www.marketwatch.com/investing/stock/" + ticker,"Beta")
	marketPrice = getKeyData("https://www.marketwatch.com/investing/stock/" + ticker ,"Open")
	eps = getKeyData("https://www.marketwatch.com/investing/stock/" + ticker ,"EPS").replace('$',"")
	MRP = 0.07
	RFR = 0.05
	corpTax = 0.2
	woE = float(marketCap) / (float(marketCap) + float(liabilities)*1000000)
	woD = (float(liabilities)*1000000) / (float(marketCap) + float(liabilities)*1000000)
	coE = RFR + float(beta)*MRP
	coD = float(interest)/float(liabilities)
	WACC = coE*woE + coD*woD*(1-corpTax)
	sumPV = 0
	for i in range(1,len(data)):
		sumPV += data[i]/pow((1+WACC),i)

	TV = data[i]*(1+0.0402)/(WACC-0.0402) #4% is the 20-Y A Corporate Bond Yield In the US
	NPV = sumPV + TV/pow(1+WACC,len(data)) 
	print("Intrinsic Valuation Per Discounted Cash Flow")
	fairPrice = NPV*1000000 / sharesOSTD
	if (fairPrice <= 0):
		print("The company's does not have sufficient cash flow to maintain operations and realize capital gain, intrinsic value is negative...")
	print("Fair Market Price: $" + str(round(fairPrice,2)))
	print("Market Price: " + marketPrice)
	#Prices will be off due to using LFCF instead of UFCF, not forecasting Revenues, expenses etc...
	#WACC is low

	fairPrice = (4.4*float(eps)*(8.5 + 2*earningsGrowth))/3.9
	print("\n" +"Intrinsic Valuation Per Graham Formula")
	if (fairPrice <= 0):
		print("The company's does not have sufficient cash flow to maintain operations and realize capital gain, intrinsic value is negative...")
	print("Fair Market Price: $" + str(round(fairPrice,2)))
	print("Market Price: " + marketPrice)
	#Prices will be off due to EPS being a poor indicator since it can be manipulated easily

def main(ticker):
	DCF(ticker)
	import technicalAnalysis as techAnalysis
	techAnalysis.main(ticker)

