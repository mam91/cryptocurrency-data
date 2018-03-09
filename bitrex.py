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
	#bitrex has a rate of ~10 requests per second.
	bitrexSendRateSeconds = 0.1
	dbConfig = loadConfig(r'C:\AppCredentials\CoinTrackerPython\database.config')
	
	con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
	cursor = con.cursor()
	
	cursor.execute("SELECT id, name, endpoint, addl_endpoint FROM crypto_exchanges where name = 'bitrex'")
	row = cursor.fetchone()
	
	if cursor.rowcount == 0:
		print("No bitrex exchange data found")
		return
		
	print("Refreshing market data for " + str(row[1]))
	response = requests.get(str(row[2])).content
	responseJson = json.loads(response.decode('utf-8'))["result"]
	
	responseLen = len(responseJson)
	progress = ProgressOutput()
	
	for x in range(responseLen):
		time.sleep(bitrexSendRateSeconds)
		progress.updatePercent(x, responseLen)
		
		symbol = responseJson[x]["MarketName"]
		#No base and quote currency, need to parse from symbol by splitting on hyphen - 
		symbols = symbol.split('-')
		price = responseJson[x]["Last"]
		volume = responseJson[x]["Volume"]
		baseCurrency = symbols[1]
		quoteCurrency = symbols[0]
		#reverse symbol because bitrex is stupid
		symbol = baseCurrency + "-" + quoteCurrency
		
		params = (row[0], symbol, price, volume, baseCurrency, quoteCurrency)
		cursor.callproc('refreshMarketData', params)

	cursor.close()
	con.commit()
	con.close()
	
	print("Done ")

main()