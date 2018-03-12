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
	#Gdax has a rate of 3 requests per second.  For safety, send only 2 a second or once ever 0.5 seconds
	gdaxSendRateSeconds = 0.5
	dbConfig = loadConfig(r'C:\AppCredentials\CoinTrackerPython\database.config')
	
	con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
	cursor = con.cursor()
	
	cursor.execute("SELECT id, name, endpoint, addl_endpoint FROM crypto_exchanges where name = 'gdax'")
	row = cursor.fetchone()
	
	if cursor.rowcount == 0:
		print("No gdax exchange data found")
		return
		
	print("Refreshing market data for " + str(row[1]) + ":  ", end="", flush=True)
	response = requests.get(str(row[2])).content
	responseJson = json.loads(response.decode('utf-8'))
	
	responseLen = len(responseJson)
	progress = pyprog.progress(responseLen)
	
	for x in range(responseLen):
		time.sleep(gdaxSendRateSeconds)
		progress.updatePercent(x)
		id = responseJson[x]["id"]
		baseCurrency = responseJson[x]["base_currency"]
		quoteCurrency = responseJson[x]["quote_currency"]

		#Replace placeholder with actual product id
		tickerEndpoint = row[3].replace("<product-id>", id)
		
		responseAddl = requests.get(tickerEndpoint).content
		responseAddlJson = json.loads(responseAddl.decode('utf-8'))

		params = (row[0], id, responseAddlJson["price"], responseAddlJson["volume"], baseCurrency, quoteCurrency)
		cursor.callproc('refreshMarketData', params)

	cursor.close()
	con.commit()
	con.close()
			
	progress.close()

main()