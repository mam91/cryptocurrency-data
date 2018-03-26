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
	#okex has a rate of ~10 requests per second.
	okexSendRateSeconds = 0.1
	dbConfig = loadConfig(r'C:\AppCredentials\CoinTrackerPython\database.config')
	
	con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
	cursor = con.cursor()
	
	cursor.execute("SELECT id, name, endpoint, addl_endpoint FROM crypto_exchanges where name = 'okex'")
	row = cursor.fetchone()
	
	if cursor.rowcount == 0:
		print("No okex exchange data found")
		return
		
	print("Refreshing market data for " + str(row[1]) + ":  ", end="", flush=True)
	response = requests.get(str(row[2])).content
	responseJson = json.loads(response.decode('utf-8'))["data"]
	
	responseLen = len(responseJson)
	progress = pyprog.progress(responseLen)
	
	for x in range(responseLen):
		time.sleep(okexSendRateSeconds)
		progress.updatePercent(x+1)
		symbol = responseJson[x]["symbol"]
		
		#No base and quote currency, need to parse from symbol by splitting on underscore _
		symbols = symbol.split('_')
		baseCurrency = symbols[0]
		quoteCurrency = symbols[1]

		#Replace placeholder with symbol
		tickerEndpoint = row[3].replace("<symbol>", symbol)
		
		responseAddl = requests.get(tickerEndpoint).content
		responseAddlJson = json.loads(responseAddl.decode('utf-8'))["ticker"]
		
		params = (row[0], symbol, responseAddlJson["last"], responseAddlJson["vol"], baseCurrency, quoteCurrency)
		cursor.callproc('refreshMarketData', params)

	cursor.close()
	con.commit()
	con.close()
	
	progress.close()

main()