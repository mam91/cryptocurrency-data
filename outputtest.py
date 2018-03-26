import requests
import json
import psycopg2
import time
import pyprogress.progress as pyprog
	
def loadConfig(filename):
	config = open(filename)
	data = json.load(config)
	return data
	
def main():
	'''
	print("Refreshing market data for test: ", end="", flush=True)
	responseLen = 3
	progress = pyprog.progress(responseLen)
	
	for x in range(responseLen):
		progress.updatePercent(x+1)
		time.sleep(1)
	
	progress.close()
	'''
	symbol = 'btcausd'
	quoteCurrency = 'usd'
	rIn = symbol.rindex(quoteCurrency)
	print(str(rIn))
	baseCurrency = symbol[0:4]
	print(baseCurrency)
main()