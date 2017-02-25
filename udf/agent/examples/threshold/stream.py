import pickle as pkl
import time
from clients import InfluxDatabaseClient, Record, Metadata, Data, Datum

nTrain = 200
outfile = 'testdata.dump'

PData = pkl.load(open(outfile, 'rb'))
xTest = PData[nTrain:]

client = InfluxDatabaseClient()
client.database = "threshold"
client.database.create()

sleep_time = .25
for i in xrange(xTest.shape[0]):
    datum = Datum("value", xTest[i][0])
    data = Data([datum])
    metadata = Metadata("input")
    record = Record(data, metadata)
    client.write(record)
    time.sleep(sleep_time)





