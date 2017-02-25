from clients import InfluxDatabaseClient
import pickle as pkl

def generate_data():
    outfile = 'causalitydataP.dump'
    PData = pkl.load(open(outfile, 'rb'))
    N = PData.shape[0]
    print PData


def stream(data, client, interval=1):
    """
    For each observations in a series of paired observations, send one observation to one measurement and another to
    another measurement in influxdb.
    :param:
           data: a numpy array consisting of N observations (rows) in two variables (columns)
           client: the InfluxDB client
           interval: interval (in secords) between sending observtions
    :return: None
    """
    stream1_index = 0
    stream2_index = 1
    for item in data:
        point1 = {"value": item[stream1_index], "measurement": "stream1", "field": "stream1value"}
        point2 = {"value": item[stream2_index], "measurement": "stream2", "field": "stream2value"}
        write_point(point1, client)
        write_point(point2, client)
        sleep(interval)


def write_point(point, client):
    """Send a batch of points to influx
    :param: batch: a pair of observations
            client: an influx database client that implements write method for a batch of records
    :return: None

    """
    datum = Datum(point["field"], point["value"])
    data = Data([datum])
    metadata = Metadata(point["measurement"])
    record = Record(data, metadata)
    client.write(record)


if __name__ == "__main__":
    client = InfluxDatabaseClient()
    client.database = "granger"
    client.database.create()
    data = generate_data()
    stream(data, client)



