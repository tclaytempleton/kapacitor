from __future__ import print_function
from collections import namedtuple
from decimal import *
import xml.etree.ElementTree as ET
from pathbuilder import build_paths
from timestampers import Timestamp, channel4, influx_ts
from clients.influx import InfluxDatabaseClient, Datum, Data, Metadata, Record, Records, Tag
import time

Channel4Record = namedtuple('Channel4Record', 'depth temperature timestamp')


def get_root(infile):
    tree = ET.parse(infile)
    root = tree.getroot()
    return root


def obtain_timestamps(root, schema):
    min_time = root.find(schema + 'wellLog').find(schema + 'minDateTimeIndex').text
    max_time = root.find(schema + 'wellLog').find(schema + 'maxDateTimeIndex').text
    min_timestamp = Timestamp(min_time, channel4)
    min_timestamp.adjust(1, "microseconds")  # add one to avoid overlaps
    max_timestamp = Timestamp(max_time, channel4)
    max_timestamp.adjust(-1, "microseconds")  # subtract one to avoid overlaps
    return min_timestamp, max_timestamp


def obtain_records(root, schema, min_timestamp, max_timestamp):
    records = []
    for measurement in root.find(schema + 'wellLog').find(schema + 'logData').findall(schema + 'data'):
        measurement_data = measurement.text.split(',')
        depth = measurement_data[0]
        temperature = measurement_data[3]
        records.append(Channel4Record(depth, temperature, min_timestamp))
        #records.append(Channel4Record(depth, temperature, max_timestamp))
    return records

def downsample_records(records, sample_rate):
    records = sorted(records, key = lambda x: Decimal(x.depth))
    mask = range(0, len(records), sample_rate)
    records = [records[i] for i in mask]
    return records


def obtain_sleep_time(min_timestamp, prev_min_time):
    nanosecond_to_second_conversion_factor = 1000000000
    prev = prev_min_time.to(influx_ts)/nanosecond_to_second_conversion_factor
    min = min_timestamp.to(influx_ts)/nanosecond_to_second_conversion_factor
    sleep_time = min - prev
    return sleep_time


def write(client, records, log, database='spirit'):
    client.database = database
    client.database.create()
    influx_records = []
    for record in records:
        tag = Tag("depth", record.depth)
        datum = Datum("value", record.temperature)
        data = Data([datum])
        metadata = Metadata("dts", tags=[tag])
        influx_records.append(Record(data, metadata))
    print ("writing {} records (in write function)".format(len(influx_records)), file=log)
    print (len(influx_records))
    for i in range(len(records)/4000):
        client.write(Records(influx_records[4000*i:4000*(i+1)]))
    client.write(Records(influx_records[(len(records)/4000) * 4000:]))

    #client.write(Records(influx_records[:4000]))
    #client.write(Records(influx_records[4000:8000]))
    #client.write(Records(influx_records[8000:12000]))
    #client.write(Records(influx_records[12000:16000]))
    #client.write(Records(influx_records[16000:20000]))
    #client.write(Records(influx_records[20000:24000]))
    #client.write(Records(influx_records[24000:28000]))
    #client.write(Records(influx_records[28000:32000]))
    #client.write(Records(influx_records[32000:36000]))
    #client.write(Records(influx_records[36000:]))


if __name__ == '__main__':
    log = open('generate_data_log.out', 'a')
    dts_schema = '{http://www.witsml.org/schemas/1series}'
    paths = build_paths(["dts"])
    paths = sorted(paths)
    #for path in paths:
    #    print(path, file=log)
    client = InfluxDatabaseClient()
    prev_min_time = None
    sleep_time_scaler = 1200
    #sleep_time_scaler = 20
    for path in paths[28:]:
        log.flush()
        print(path, file=log)
        root = get_root(path)
        min_timestamp, max_timestamp = obtain_timestamps(root, dts_schema)
        records = obtain_records(root, dts_schema, min_timestamp, max_timestamp)
        records = downsample_records(records, sample_rate=100)
        print(len(records), file=log)
        if prev_min_time:
            sleep_time = obtain_sleep_time(min_timestamp, prev_min_time)
            print(str(sleep_time), file=log)
            print("sleeping for {} seconds\nsleep_time={}, sleep time scaler = {}".format(sleep_time/sleep_time_scaler, sleep_time, sleep_time_scaler))
            print("after sleep, will write {} records".format(len(records)))
            time.sleep(sleep_time/sleep_time_scaler)
        log.write("writing {} records".format(len(records)))
        write(client, records, log, database="spiritenergy")
        prev_min_time = min_timestamp


















class Reader(object):
    def __init__(self):
        pass

    def read(self, infile):
        '''overrride this method'''
        pass





class XMLReader(Reader):
    def read(self, infile):
        self._root = self._get_root(infile)
        records = self._obtain_records (self._root)
        return records

    def _get_root(self, infile):
        tree = ET.parse(infile)
        root = tree.getroot()
        return root

    def _obtain_records(self, root):
        '''override this method'''
        pass

class DTSXMLReader(XMLReader):
    def __init__(self):
        super(DTSXMLReader, self).__init__()
        self.schema = '{http://www.witsml.org/schemas/1series}'

    def _obtain_records(self, root):
        records = []
        min_time = root.find(self.schema + 'wellLog').find(self.schema + 'minDateTimeIndex').text
        max_time = root.find(self.schema + 'wellLog').find(self.schema + 'maxDateTimeIndex').text
        for measurement in root.find(self.schema + 'wellLog').find(self.schema + 'logData').findall(self.schema + 'data'):
            measurement_data = measurement.text.split(',')
            min_timestamp = Timestamp(min_time, channel4)
            min_timestamp.adjust(1, "microseconds") #add one to avoid overlaps
            max_timestamp = Timestamp(max_time, channel4)
            max_timestamp.adjust(-1, "microseconds") #subtract one to avoid overlaps
            depth = measurement_data[0]
            temperature = measurement_data[3]
            records.append(Channel4Record(depth, temperature, min_timestamp))
            records.append(Channel4Record(depth, temperature, max_timestamp))
        return records
