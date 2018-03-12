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
    print(name + "  completed in " + roundStr(elapsed) + " seconds.")

class exchangePullThread(threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
   def run(self):
      print("Starting " + self.name)
      executeExchangeFile(self.name)
      print("Exiting " + self.name)

def main():
    dbConfig = loadConfig(r'C:\AppCredentials\CoinTrackerPython\database.config')
    con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
    con.autocommit = True
    cursor = con.cursor()
        
    cursor.execute("SELECT name FROM crypto_exchanges order by name")
    rows = cursor.fetchall()

    if cursor.rowcount == 0:
        print("No exchange data found")
        return
    totalStart = time.clock()

    exData = []
    for row in rows:
        exData.append(row[0])

    pool = ThreadPool(4) 
    pool.map(executeExchangeFile, exData)
    pool.close() 
    pool.join()     
   # for row in rows:
    #    executeExchangeFile(row[0])
    #    cursor.callproc("refreshCryptoMarket")
    
    cursor.close()
    con.close()
    print("Total runtime: " + str(time.clock() - totalStart))
main()