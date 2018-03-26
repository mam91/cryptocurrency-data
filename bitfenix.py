import requests
import json
import psycopg2
import time
import pyprogress.progress as pyprog
	
def loadConfig(filename):
	config = open(filename)
	data = json.load(config)
	return data
		
def getAssetsFromSymbol(con, symbol):
	cursor = con.cursor()
	#cursor.execute("select distinct lower(quote_asset) from public.crypto_markets where position(lower(quote_asset) in lower('" + symbol + "')) > 1")
	cursor.execute("select distinct lower(quote_asset) from public.crypto_markets where lower('" + symbol + "') like '%' || LOWER(quote_asset)")
	row = cursor.fetchone()
	cursor.close()
	quoteCurrency = row[0]
	baseCurrency = symbol[0:symbol.rindex(quoteCurrency)]
	return baseCurrency, quoteCurrency
	
def main():
	#bitfenix has a rate of 30 per minute so send 1 every 2 seconds to be safe.
	bitfenixRateSeconds = 3
	dbConfig = loadConfig(r'C:\AppCredentials\CoinTrackerPython\database.config')
	
	con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
	cursor = con.cursor()
	
	cursor.execute("SELECT id, name, endpoint, addl_endpoint FROM crypto_exchanges where name = 'bitfenix'")
	row = cursor.fetchone()
	
	if cursor.rowcount == 0:
		print("No bitfinex exchange data found")
		return
		
	print("Refreshing market data for " + str(row[1]) + ": ", end="", flush=True)
	response = requests.get(str(row[2])).content
	responseJson = json.loads(response.decode('utf-8'))
	
	responseLen = len(responseJson)
	progress = pyprog.progress(responseLen)
	
	for x in range(responseLen):
		time.sleep(bitfenixRateSeconds)
		progress.updatePercent(x+1)
		symbol = responseJson[x]

		#No base and quote currency, need to parse from symbol by checking database for quote currency
		baseCurrency, quoteCurrency = getAssetsFromSymbol(con, symbol)

		#Replace placeholder with symbol
		tickerEndpoint = row[3].replace("<symbol>", symbol)
		
		responseAddl = requests.get(tickerEndpoint).content
		responseAddlJson = json.loads(responseAddl.decode('utf-8'))

		params = (row[0], symbol, responseAddlJson["last_price"], responseAddlJson["volume"], baseCurrency, quoteCurrency)
		cursor.callproc('refreshMarketData', params)

	cursor.close()
	con.commit()
	con.close()
	
	progress.close()

main()