from subprocess import call
import json
import psycopg2
import time
import threading
from multiprocessing.dummy import Pool as ThreadPool 

def loadConfig(filename):
	config = open(filename)
	data = json.load(config)
	return data

def roundStr(numberToRound):
	return "{:.4f}".format(numberToRound) 

def executeExchangeFile(name):
    start = time.clock()
    filename = "c:/Users/mmill/Documents/GitHub/Cryptocurrency-Data/" +name + ".py"
    call(["python", filename])
    elapsed = time.clock() - start
    print(name + " completed in " + roundStr(elapsed) + " seconds.")

class exchangePullThread(threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
   def run(self):
      executeExchangeFile(self.name)

def main():
    dbConfig = loadConfig(r'C:\AppCredentials\CoinTrackerPython\database.config')
    con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
    con.autocommit = True
    cursor = con.cursor()

    totalStart = time.clock()

    #Do fiat exchanges first
    cursor.execute("SELECT name FROM crypto_exchanges where active_flag = 'Y' and fiat_exchange = true order by name")
    rows = cursor.fetchall()

    if cursor.rowcount == 0:
        print("No exchange data found")
        return

    for row in rows:
        executeExchangeFile(row[0])

    #Do non-fiat exchanges second
    cursor.execute("SELECT name FROM crypto_exchanges where active_flag = 'Y' and fiat_exchange = false order by name")
    rows = cursor.fetchall()

    for row in rows:
        executeExchangeFile(row[0])


    #exData = []
    #for row in rows:
    #    exData.append(row[0])

    #pool = ThreadPool(2) 
    #pool.map(executeExchangeFile, exData)
    #pool.close() 
    #pool.join() 

    cursor.callproc("refreshCryptoMarket")
    cursor.close()
    con.close()
    print("Total runtime: " + str(time.clock() - totalStart))
main()