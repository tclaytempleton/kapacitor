from agent import Agent, Handler
import udf_pb2
import sys

# The Agent calls the appropriate methods on the Handler as requests are read off STDIN.
#
# Throwing an exception will cause the Agent to stop and an ErrorResponse to be sent.
# Some *Response objects (like SnapshotResponse) allow for returning their own error within the object itself.
# These types of errors will not stop the Agent and Kapacitor will deal with them appropriately.
#
# The Handler is called from a single thread, meaning methods will not be called concurrently.
#
# To write Points/Batches back to the Agent/Kapacitor use the Agent.write_response method, which is thread safe.

# The Granger Handler just runs the granger algorithm every time a data point comes in. To do this, it keeps a moving
# window that is updated each time before the granger algorithm is rerun. The window is either initialized or *waits until
# there are sufficient data points to run the algorithm*
# parameters: window size
#             order
#             (increment: run granger only at increments of n; is this implementable in kapacitor)
#
# private state variables:
#       window.size
#
# update window:
#     add to window
#
#     add granger to the window
#     if window.size == self.size:
#          call granger on the window
#          drop the first-in value from the window
#


class GrangerHandler(object):
    def __init__(self, agent):
        self._agent = agent
        #self._size = 0
        self._order = 1 #defaults #to order = 1
        self._window = []
        self._field1 = ''
        self._field2 = ''
        self._logfile = open("/home/vagrant/var/granger/test_log.log", "a")

    def info(self):
        self._logfile.write("getting info\n")
        response = udf_pb2.Response()
        response.info.wants = udf_pb2.STREAM
        response.info.provides = udf_pb2.STREAM
        response.info.options['order'].valueTypes.append(udf_pb2.INT)
        #response.info.options['size'].valueTypes.append(udf_pb2.INT)
        response.info.options['field1'].valueTypes.append(udf_pb2.STRING)
        response.info.options['field2'].valueTypes.append(udf_pb2.STRING)
        self._logfile.write("returning response\n\n")
        return response

    def init(self, init_req):
        self._logfile.write("initting\n")
        msg = ''
        for opt in init_req.options:
             if opt.name == 'order':
                self._order = opt.values[0].intValue
             #elif opt.name == 'size':
             #   self._size = opt.values[0].intValue
             elif opt.name == 'field1':
                self._field1 = opt.values[0].stringValue
             elif opt.name == 'field2':
                self._field2 = opt.values[0].stringValue
        #if self._size <= 1:
        #    success = False
        #    msg += ' must supply window size > 1'

        success = True

        # Do some action to intitialize the statistical code
        # In this case we initialize the historical window
        # e.g. self._history = MovingStats(size)

        response = udf_pb2.Response()
        response.init.success = success
        response.init.error = msg
        #response.init.error = msg[1:]
        self._logfile.write("returning response\n\n")
        return response


    def begin_batch(self, begin_req):
        self._logfile.write("beginning the batch\n\n")
        self._x = []
        self._y = []


    def point(self, point):
        with open("whatsthedealwiththepoints.txt", 'a') as of:
            print point
        #point.fieldsDouble[self._field]
        # sort the points by field and place the points in correct bins

    def end_batch(self, end_req):
        pass
        # align points
        # see ipython notebook

        # calculate the Granger score
        # send the granger score back to Kapacitor (and thence to InfluxDB, per the tick script)


def seqGranger(self, params):
    '''
    This is the sequential version of the granger test
    '''
    order = params['order']
    t0 = params['t0']
    t1 = params['t1']
    dt = params['dt']
    Fstat = []
    Prob = []

    tarr = []  # use this array to track analyzed data [maybe should be real timestamp?]
    cause = self.data[:, 1]
    effect = self.data[:, 0]
    ndata = len(self.data[:, 1])
    while t1 < ndata:
        # R implementation
        x = r_base.as_numeric(cause[t0:t1])
        y = r_base.as_numeric(effect[t0:t1])
        result = lmtest.grangertest(x, y, order=order)
        Prob.append(float(result[3][1]))
        Fstat.append(float(result[2][1]))
        tarr.append(t1)
        t0 += dt
        t1 += dt

    return Prob, tarr


# params={'order':4, 't0':0, 't1':200, 'dt':10}


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
