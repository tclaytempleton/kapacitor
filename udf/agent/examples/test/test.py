import pandas as pd
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri
from rpy2.robjects import r
from agent import Agent, Handler
import udf_pb2
import sys

r_base = rpackages.importr('base')
r('.libPaths("/usr/local/lib64/R/library")')
lmtest = rpackages.importr('lmtest')
pandas2ri.activate()


# The Agent calls the appropriate methods on the Handler as requests are read off STDIN.
#
# Throwing an exception will cause the Agent to stop and an ErrorResponse to be sent.
# Some *Response objects (like SnapshotResponse) allow for returning their own error within the object itself.
# These types of errors will not stop the Agent and Kapacitor will deal with them appropriately.
#
# The Handler is called from a single thread, meaning methods will not be called concurrently.
#
# To write Points/Batches back to the Agent/Kapacitor use the Agent.write_response method, which is thread safe.
class TestHandler(Handler):
    def __init__(self, agent):
        self._agent = agent
        self._logfile = open("/home/vagrant/var/test/handler_log.log", "a")
        self._order = 1

    def info(self):
        self._logfile.write("beginning info\n")
        response = udf_pb2.Response()
        response.info.wants = udf_pb2.BATCH
        response.info.provides = udf_pb2.STREAM
        response.info.options['field1'].valueTypes.append(udf_pb2.STRING)
        response.info.options['field2'].valueTypes.append(udf_pb2.STRING)
        response.info.options['order'].valueTypes.append(udf_pb2.INT)
        #response.info.options['some_int'].valueTypes.append(udf_pb2.INT)
        self._logfile.write("returning info\n\n")
        return response

    def init(self, init_req):
        self._logfile.write("beginning init\n")
        success = True
        msg = ''
        for opt in init_req.options:
            if opt.name == 'order':
                self._order = opt.values[0].intValue

        response = udf_pb2.Response()
        response.init.success = success
        response.init.error = msg
        self._logfile.write("returning init\n\n")
        return response

    def snapshot(self):
        response = udf_pb2.Response()
        response.snapshot.snapshot = ''
        return response

    def restore(self, restore_req):
        pass

    def begin_batch(self, begin_req):
        self._logfile.write("beginning batch\n")
        self._logfile.flush()
        self._x = {}
        self._y = {}

    def point(self, point):
        self._logfile.write("point")
        #self._logfile.write(point.name)
        self._logfile.write(str(point))
        if "stream1value" in point.fieldsDouble:
            self._logfile.write("1")
            self._x[point.time] = point.fieldsDouble["stream1value"]
        if "stream2value" in point.fieldsDouble:
            self._logfile.write("2")
            self._y[point.time] = point.fieldsDouble["stream2value"]
        self._logfile.flush()

    def end_batch(self, batch_meta):
        self._logfile.write("ONE")
        self._logfile.flush()
        x, y = self._align()
        self._logfile.write("TWO")
        self._logfile.flush()
        self._logfile.write("end\n")
        self._logfile.write(str(self._x) + '\n')
        self._logfile.write(str(self._y) + '\n')
        self._logfile.flush()

        #p1 = pandas2ri.py2ri(x)
        #self._logfile.write("THREE")
        #self._logfile.flush()
        #p2 = pandas2ri.py2ri(y)
        #self._logfile.write("FOUR")
        #self._logfile.flush()

        result = lmtest.grangertest(x, y, order=self._order)
        self._logfile.write("FIVE")
        self._logfile.flush()
        p_value = (float(result[3][1]))

        response = udf_pb2.Response()
        response.point.time = batch_meta.tmax
        response.point.fieldsDouble["testfield"] = p_value
        self._agent.write_response(response)

    def _align(self):
        x = pd.DataFrame({'x': self._x})
        y = pd.DataFrame({'y': self._y})
        x_y = pd.merge(x, y, left_index=True, right_index=True, how="outer") #all points from both streams
        x_y['y'] = x_y['y'].fillna(method='ffill') # forward-fill the y's to match the x indices
        x_y = x_y[pd.notnull(x_y['x'])] # delete the rows containing original y's s
        return x_y['x'], x_y['y']






if __name__ == '__main__':
        # Create an agent
        agent = Agent()
        h = TestHandler(agent)
        agent.handler = h

        # Anything printed to STDERR from a UDF process gets captured into the Kapacitor logs.
        print >> sys.stderr, "Starting agent for Test"
        agent.start()
        agent.wait()
        print >> sys.stderr, "Agent finished"