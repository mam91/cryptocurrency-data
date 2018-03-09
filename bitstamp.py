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
	#Bitstamp has a rate of 1 requests per second.  For safety, send only 1 every 1.25 seconds
	bitstampRateSeconds = 1.25
	dbConfig = loadConfig(r'C:\AppCredentials\CoinTrackerPython\database.config')
	
	con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
	cursor = con.cursor()
	
	cursor.execute("SELECT id, name, endpoint, addl_endpoint FROM crypto_exchanges where name = 'bitstamp'")
	row = cursor.fetchone()
	
	if cursor.rowcount == 0:
		print("No bitstamp exchange data found")
		return
		
	print("Refreshing market data for " + str(row[1]))
	response = requests.get(str(row[2])).content
	responseJson = json.loads(response.decode('utf-8'))
	
	responseLen = len(responseJson)
	progress = ProgressOutput()
	
	for x in range(responseLen):
		time.sleep(bitstampRateSeconds)
		progress.updatePercent(x, responseLen)
		symbol = responseJson[x]["url_symbol"]
		name = responseJson[x]["name"]
		baseCurrency = name[0].strip()
		quoteCurrency = name[1].strip()

		#Replace placeholder with actual symbol
		tickerEndpoint = row[3].replace("<symbol>", symbol)
		
		responseAddl = requests.get(tickerEndpoint).content
		responseAddlJson = json.loads(responseAddl.decode('utf-8'))

		price = responseAddlJson["last"]
		volume = responseAddlJson["volume"]

		params = (row[0], symbol, price, volume, baseCurrency, quoteCurrency)
		cursor.callproc('refreshMarketData', params)

	cursor.close()
	con.commit()
	con.close()
			
	print("Done ")

main()