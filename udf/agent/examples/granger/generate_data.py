import numpy as np
from time import sleep
import sys
sys.path.append("../lib")
from clients.influx import InfluxDatabaseClient, Datum, Data, Metadata, Record


def generate_data(N=2048, sigma=0.05):
    '''In this problem, X[1] drives X[0] for the first half and then independent of X[0] thereafter'''
    random_generator = np.random.RandomState(12235)
    n_spin = 1024 # this is length of spinoff period
    number_of_observations = N + n_spin
    number_of_variables = 2
    random_matrix = sigma*random_generator.randn(number_of_observations, number_of_variables)
    x = np.zeros((number_of_observations, number_of_variables))  # result matrix
    x[:5, :] = random_generator.randn(5, number_of_variables)  # initialize result matrix
    n_half = n_spin + int(0.5*N)
    for i in range(5, n_spin+N):
        if i < n_half:
            x[i, 0] = 0.8*x[i-1, 0]+0.5*x[i-3, 1]+0.15*x[i-4, 1]+random_matrix[i, 0]
            x[i, 1] = 0.6*x[i-1, 1]+0.10*x[i-2, 1]+0.25*x[i-3, 1]+0.01*x[i-4, 1]+random_matrix[i, 1]
        else:
            x[i, 0] = 0.8*x[i-1, 0]+random_matrix[i, 0]
            x[i, 1] = 0.6*x[i-1, 1]+0.10*x[i-2, 1]+0.25*x[i-3, 1]+0.01*x[i-4, 1]+random_matrix[i, 1]
    # remove spin off
    data = x[n_spin:, :]
    return data


def stream(data, client, interval=.1):
    """
    For each observations in a series of paired observations, send one observation to one measurement and another to
    another measurement in influxdb.
    :param:
           data: a numpy array consisting of N observations (rows) in two variables (columns)
           client: the InfluxDB client
           interval: interval (in secords) between sending observtions
    :return: None
    """
    stream1_index = 1
    stream2_index = 0
    for item in data:
        point1 = {"value": item[stream1_index], "measurement": "cause", "field": "causevalue"}
        point2 = {"value": item[stream2_index], "measurement": "effect", "field": "effectvalue"}
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
    client = InfluxDatabaseClient('129.114.111.79:8086')
    client.database = "granger"
    client.database.create()
    data = generate_data()
    while True:
    	stream(data, client)


# (.1 second interval between data points * 2048)/60  = 3.41 minutes to stream all the data
# 30 second windows of data = 292.5 data points
# at 15 second intervals = 150 dp overlap
