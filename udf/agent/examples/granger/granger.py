import pandas as pd
import readline
import rpy2.robjects.packages as rpackages
from rpy2.robjects import pandas2ri
from rpy2.robjects import r
import sys
sys.path.append('../lib')
from udf.agent import Agent, Handler
import udf.udf_pb2 as udf_pb2

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
class GrangerHandler(Handler):
    def __init__(self, agent):
        self._agent = agent
        self._order = 1

    def info(self):
        response = udf_pb2.Response()
        response.info.wants = udf_pb2.BATCH
        response.info.provides = udf_pb2.STREAM
        response.info.options['field1'].valueTypes.append(udf_pb2.STRING)
        response.info.options['field2'].valueTypes.append(udf_pb2.STRING)
        response.info.options['order'].valueTypes.append(udf_pb2.INT)
        return response

    def init(self, init_req):
        success = True
        msg = ''
        for opt in init_req.options:
            if opt.name == 'order':
                self._order = opt.values[0].intValue

        response = udf_pb2.Response()
        response.init.success = success
        response.init.error = msg
        return response

    def snapshot(self):
        response = udf_pb2.Response()
        response.snapshot.snapshot = ''
        return response

    def restore(self, restore_req):
        pass

    def begin_batch(self, begin_req):
        self._x = {}
        self._y = {}

    def point(self, point):
        if "causevalue" in point.fieldsDouble:
            self._x[point.time] = point.fieldsDouble["causevalue"]
        if "effectvalue" in point.fieldsDouble:
            self._y[point.time] = point.fieldsDouble["effectvalue"]

    def end_batch(self, batch_meta):
        x, y = self._align()
        result = lmtest.grangertest(x, y, order=self._order)
        p_value = (float(result[3][1]))
        response = udf_pb2.Response()
        response.point.time = batch_meta.tmax
        response.point.fieldsDouble["grangervalue"] = p_value
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
        h = GrangerHandler(agent)
        agent.handler = h

        # Anything printed to STDERR from a UDF process gets captured into the Kapacitor logs.
        print >> sys.stderr, "Starting agent for Granger"
        agent.start()
        agent.wait()
        print >> sys.stderr, "Agent finished"