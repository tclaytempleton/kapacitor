from subprocess import call, check_output
from collections import namedtuple
import json
import time
import pandas
import numpy as np
import os

class InfluxDatabaseClient(object):
    def __init__(self, host='http://localhost:8086'):
        self.host = host
        self._last_results = None
        # self._last_query

    class InfluxDatabase(object):
        def __init__(self, dbname, client):
            self.client = client
            self.dbname = dbname

        def create(self):
            # should check if database exists
            call(['curl', '-G', self.client.query_endpoint, '--data-urlencode', 'q=CREATE DATABASE ' + self.dbname])

    @property
    def database(self):
        return self._database

    @database.setter
    def database(self, dbname):
        self._database = self.InfluxDatabase(dbname, self)
        self.query_endpoint = self.host + '/query'
        self.write_endpoint = self.host + '/write?db=' + dbname

        # def create_database(self):

    #	call (['curl', '-G', self.query_endpoint, '--data-urlencode', 'q=CREATE DATABASE ' + self.dbname])

    def write(self, records, timestamp=None):
        #print " ".join(['curl', '-i', '-XPOST', self.write_endpoint, '--data-binary', str(records)])
        call(['curl', '-i', '-XPOST', self.write_endpoint, '--data-binary', str(records)])

    def write_from_file(self, filename):
        # assert filename begins with @; alternatively, add @ automatically
        call(['curl', '-i', '-XPOST', self.write_endpoint, '--data-binary', '@' + filename])

    def write_from_many_files(self, directory, pause=.01):  # pause in seconds
        filenames = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        counter = 0
        num_files = len(filenames)
        for f in filenames:
            counter += 1
            print "writing data to {} on {} from {}".format(self.database.dbname, self.host, f)
            print "file {} of {}".format(counter, num_files)
            self.write_from_file(os.path.join(directory, f))
            time.sleep(pause)


    def query(self, query):
        self.last_results = check_output(
            ['curl', '-G', self.query_endpoint, '--data-urlencode', 'db=' + self.database.dbname, '--data-urlencode',
             'q=' + query])
        return self.last_results

    def get_series_as_dataframe(self, query):
        results = self.query(query)
        json_results = json.loads(results)
        series = json_results["results"][0]["series"][0]
        columns = series['columns']
        data = series['values']
        df = pandas.DataFrame(data=data, columns=columns)
        return df

    @property
    def last_results(self):
        return self._last_results

    @last_results.setter
    def last_results(self, value):
        self._last_results = value

    def get_series_names(self):
        results = self.query("show measurements")
        json_results = json.loads(results)
        try:
            table_names = [name[0] for name in json_results["results"][0]["series"][0]["values"]]
        except Exception as e:
            table_names = []
        return table_names


##### influx_records should be a CLASS with a single nifty string method
##### or, alternatively, with injectable output methods
class Metadata():
    def __init__(self, measurement, tags=None):
        self.measurement = measurement
        self.tags = tags

    def __str__(self):
        string = ""
        string += self.measurement
        string += ','
        if self.tags:
            for tag in self.tags:
                string += tag.key + '=' + str(tag.value)
                string += ','
        return string[:-1]


class Data():
    def __init__(self, the_data):
        self.data = the_data

    def __str__(self):
        string = ""
        for datum in self.data:
            string += datum.key + '=' + str(datum.value)
        return string


class Record():
    def __init__(self, data, metadata, timestamp=None):
        self.data = data
        self.metadata = metadata
        self.timestamp = timestamp

    def __str__(self):
        string = ""
        string += str(self.metadata)
        string += " "
        string += str(self.data)
        if self.timestamp:
            string += " "
            string += self.timestamp
        return string


class Records():
    def __init__(self, records=[]):
        self.records = records

    def append(self, record):
        self.records.append(record)

    def __str__(self):
        string = ""
        for record in self.records:
            string += str(record)
            string += '\n'
        string = string[:-1]
        return string


Tag = namedtuple('Tag', 'key value')
Datum = namedtuple('Datum', 'key value')
Index = namedtuple('Index', 'result series')


if __name__ == '__main__':
    import os


    def write_cranfield(db, file_name):
        home = os.path.expanduser('~')
        client = InfluxDatabaseClient(db)
        client.create_database()
        client.write_from_file('@' + home + '/ims_web/data/' + file_name)


    def output():
        client = InfluxDatabaseClient('some_test_db')
        result = client.query('select * from cpu')
        return (result)


        # output()


    write_cranfield('CFU31_F2', 'f2_temperature.txt')
    write_cranfield('CFU31_F2', 'f2_pressure.txt')
    write_cranfield('CFU31_F3', 'f3_temperature.txt')
    write_cranfield('CFU31_F3', 'f3_pressure.txt')
