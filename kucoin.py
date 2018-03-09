import requests
import json
import psycopg2
	
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
    dbConfig = loadConfig(r'C:\AppCredentials\CoinTrackerPython\database.config')
	
    con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
    cursor = con.cursor()
	
    cursor.execute("SELECT id, name, endpoint, addl_endpoint FROM crypto_exchanges where name = 'kucoin'")
    row = cursor.fetchone()
	
    if cursor.rowcount == 0:
        print("No kucoin exchange data found")
        return
    
    print("Refreshing market data for " + str(row[1]))
    response = requests.get(str(row[2])).content
    responseJson = json.loads(response.decode('utf-8'))['data']

    responseLen = len(responseJson)

    progress = ProgressOutput()
	
    for x in range(responseLen):
        progress.updatePercent(x, responseLen)
        coinType = responseJson[x]['coinType']
        lastDealPrice = responseJson[x]['lastDealPrice']
        vol = responseJson[x]['vol']
        coinTypePair = responseJson[x]['coinTypePair']
        symbol = coinType + coinTypePair

        params = (row[0], symbol, lastDealPrice, vol, coinType, coinTypePair)
        cursor.callproc('refreshMarketData', params)

    cursor.close()
    con.commit()
    con.close()
    
    print("Done ")

main()