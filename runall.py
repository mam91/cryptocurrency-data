from subprocess import call
import json
import psycopg2
import time

def loadConfig(filename):
	config = open(filename)
	data = json.load(config)
	return data

def roundStr(numberToRound):
	return "{:.4f}".format(numberToRound) 

def main():
    dbConfig = loadConfig(r'C:\AppCredentials\CoinTrackerPython\database.config')
    con = psycopg2.connect(dbConfig[0]["postgresql_conn"])
    cursor = con.cursor()
        
    cursor.execute("SELECT name FROM crypto_exchanges order by name")
    rows = cursor.fetchall()

    if cursor.rowcount == 0:
        print("No exchange data found")
        return

    for row in rows:
        start = time.clock()
        filename = "c:/Users/mmill/Documents/GitHub/Cryptocurrency-Data/" + str(row[0]) + ".py"
        call(["python", filename])
        elapsed = time.clock() - start
        print(str(row[0]) + "  completed in " + roundStr(elapsed) + " seconds.")
main()