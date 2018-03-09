import requests
import json
import psycopg2
import time
	
def loadConfig(filename):
	config = open(filename)
	data = json.load(config)
	return data
	
class ProgressOutput(object):
	def __init__(self):
		self.percent = -1
 
	def updatePercent(self, current, total):
		newPercent = int(current / total * 100)
		if newPercent > self.percent:
			self.percent = newPercent
			self.printPercent()
			
	def printPercent(self):
		print(" " + str(self.percent) + "%\r", end="", flush=True)
	
def getAssetsFromSymbol(con, symbol):
	cursor = con.cursor()
	cursor.execute("select distinct lower(quote_asset) from public.crypto_markets where position(lower(quote_asset) in lower('" + symbol + "')) > 2")
	row = cursor.fetchone()
	cursor.close()
	quoteCurrency = row[0]
	baseCurrency = symbol[0:-symbol.index(quoteCurrency)]
	return baseCurrency, quoteCurrency
	
def main():
	#Gdax has a rate of 3 requests per second.  For safety, send only 2 a second or once ever 0.5 seconds
	gemeniRateSeconds = 1
	dbConfig = loadConfig(r'C:\AppCredentials\CoinTrackerPython\database.config')
	
	con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
	cursor = con.cursor()
	
	cursor.execute("SELECT id, name, endpoint, addl_endpoint FROM crypto_exchanges where name = 'gemeni'")
	row = cursor.fetchone()
	
	if cursor.rowcount == 0:
		print("No gemeni exchange data found")
		return
		
	print("Refreshing market data for " + str(row[1]))
	response = requests.get(str(row[2])).content
	responseJson = json.loads(response.decode('utf-8'))
	
	responseLen = len(responseJson)
	progress = ProgressOutput()
	
	for x in range(responseLen):
		time.sleep(gemeniRateSeconds)
		progress.updatePercent(x, responseLen)
		symbol = responseJson[x]

		#Replace placeholder with actual symbol
		tickerEndpoint = row[3].replace("<symbol>", symbol)
		
		responseAddl = requests.get(tickerEndpoint).content
		responseAddlJson = json.loads(responseAddl.decode('utf-8'))
		
		#baseCurrency, quoteCurrency = getAssetsFromSymbol(con, symbol)
		volumeJson = responseAddlJson["volume"]
		
		i = 0
		for key, value in volumeJson.items():
			i = i + 1
			if i == 1:
				baseCurrency = key
			if i == 2:
				volume = value
				quoteCurrency = key
				
		
		params = (row[0], symbol, responseAddlJson["last"], volume, baseCurrency, quoteCurrency)
		cursor.callproc('refreshMarketData', params)

	cursor.close()
	con.commit()
	con.close()
	
	print("Done ")

main()