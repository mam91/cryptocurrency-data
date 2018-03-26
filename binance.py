import requests
import json
import psycopg2
import pyprogress.progress as pyprog
	
def loadConfig(filename):
	config = open(filename)
	data = json.load(config)
	return data
	
def main():
	dbConfig = loadConfig(r'C:\AppCredentials\CoinTrackerPython\database.config')
	
	con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
	cursor = con.cursor()
	
	cursor.execute("SELECT id, name, endpoint, addl_endpoint FROM crypto_exchanges where name = 'binance'")
	row = cursor.fetchone()
	
	if cursor.rowcount == 0:
		print("No binance exchange data found")
		return
		
	print("Refreshing market data for " + str(row[1]) + ": ", end="", flush=True)
	response = requests.get(str(row[2])).content
	responseJson = json.loads(response.decode('utf-8'))['symbols']
	responseAddl = requests.get(str(row[3])).content
	responseAddlJson = json.loads(responseAddl.decode('utf-8'))
	
	responseLen = len(responseJson)
	responseAddlLen = len(responseAddlJson)
	
	progress = pyprog.progress(responseAddlLen)
		
	for x in range(responseAddlLen):
		symbolAddl = responseAddlJson[x]['symbol']
		lastPrice = responseAddlJson[x]['lastPrice']
		volume = responseAddlJson[x]['volume']
		
		progress.updatePercent(x+1)
		
		for y in range(responseLen):
			symbol = responseJson[y]['symbol']
			baseAsset = responseJson[y]['baseAsset']
			quoteAsset = responseJson[y]['quoteAsset']
			if symbol == symbolAddl:
				params = (row[0], symbol, lastPrice, volume, baseAsset, quoteAsset)
				cursor.callproc('refreshMarketData', params)
				
	cursor.close()
	con.commit()
	con.close()
			
	progress.close()

main()