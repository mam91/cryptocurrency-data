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
	
	
def main():
	#Kraken has a rate of 1 requests per second.  For safety, send only 1 every 1.25 seconds
	bitstampRateSeconds = 1.25
	dbConfig = loadConfig(r'C:\AppCredentials\CoinTrackerPython\database.config')
	
	con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
	cursor = con.cursor()
	
	cursor.execute("SELECT id, name, endpoint, addl_endpoint FROM crypto_exchanges where name = 'kraken'")
	row = cursor.fetchone()
	
	if cursor.rowcount == 0:
		print("No kraken exchange data found")
		return
		
	print("Refreshing market data for " + str(row[1]))
	response = requests.get(str(row[2])).content
	responseJson = json.loads(response.decode('utf-8'))["result"]

	responseLen = len(responseJson)
	progress = ProgressOutput()
	x = 0

	for key, value in responseJson.items():
		x = x + 1
		time.sleep(bitstampRateSeconds)
		progress.updatePercent(x, responseLen)
		symbol = key
		if '.' in symbol:
			continue

		baseCurrency = value["base"]
		quoteCurrency = value["quote"]

		tickerEndpoint = row[3].replace("<symbol>", symbol)
		responseAddl = requests.get(tickerEndpoint).content
		responseAddlJson = json.loads(responseAddl.decode('utf-8'))["result"][symbol]
		price = responseAddlJson["p"][0]
		volume = responseAddlJson["v"][1]

		params = (row[0], symbol, price, volume, baseCurrency, quoteCurrency)
		cursor.callproc('refreshMarketData', params)
		
	cursor.close()
	con.commit()
	con.close()
			
	print("Done ")

main()