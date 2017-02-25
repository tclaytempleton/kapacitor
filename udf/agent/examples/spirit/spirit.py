from __future__ import print_function

from udf.agent import Agent, Handler
import udf.udf_pb2 as udf_pb2
import sys
import numpy as np
import pandas as pd

class SpiritHandler(Handler):
    def __init__(self, agent):
        self._tags = open("/vagrant/udf/agent/examples/spirit/tags.txt", "rb").read().split('\n')
        mask = range(0, 36210, 100)
        self._tags = [self._tags[i] for i in mask]
        self._agent = agent
        self._logfile = open("/vagrant/udf/agent/examples/spirit/handler_log.out", 'a')
        self._n = None
        self._k = None
        self._count = 0

    def info(self):
        print ("Info for Spirit", file=sys.stderr)
        print ("Info for Spirit", file=self._logfile)
        self._logfile.flush()
        response = udf_pb2.Response()
        response.info.wants = udf_pb2.STREAM
        response.info.provides = udf_pb2.STREAM
        #response.info.options['field'].valueTypes.append(udf_pb2.STRING)
        response.info.options['n'].valueTypes.append(udf_pb2.INT)  # the number of components (raw data)
        response.info.options['k'].valueTypes.append(udf_pb2.INT)  # the number of components (projection)
        return response

    def init(self, init_req):
        print("INIT", file=sys.stderr)
        print("initializing", file=self._logfile)
        self._logfile.flush()
        success = True
        msg = ''
        for opt in init_req.options:
            if opt.name == 'k':
                self._k = opt.values[0].intValue
            if opt.name == 'n':
                self._n = opt.values[0].intValue
        if self._n and self._k:
            self._se = SPIRIT(self._n, self._k)
            self._point = {tag.strip(): None for tag in self._tags}
        response = udf_pb2.Response()
        response.init.success = success
        response.init.error = msg
        return response

    def restore(self, restore_req):
        print("RESTORE", file=sys.err)
        pass

    def begin_batch(self, begin_req):
        print("BEGIN_BATCH", file=sys.err)
        pass

    def snapshot(self):
        print("SNAPSHOT", file=sys.stderr)
        response = udf_pb2.Response()
        response.snapshot.snapshot = ''
        return response

    def point(self, point):
        #print("POINT", file=sys.stderr)
        value = point.fieldsDouble["value"]
        tag = point.tags["depth"]
        #print ("{} {} {} {}".format("Point:", value, tag, self._count), file=self._logfile)
        self._point[tag] = float(value)
        #print ("Got a point", file=self._logfile)
        #print (value, file=self._logfile)
        #print (tag, file=self._logfile)
        #print (self._count, file=self._logfile)
        self._count += 1
        #self._logfile.flush()
        if self._count == self._n:
            print ("CALCULATING SPIRIT", file=sys.stderr)
            #print ("self._count == {}".format(self._count), file=self._logfile)
            #print ("length of items list = {}".format(len(self._point.items()), file=self._logfile))
            x = np.array([[i[1] for i in sorted(self._point.items(), key=lambda ii: ii[0])]]).T
            x_df = pd.DataFrame(x)
            ff = x_df.fillna(method='ffill')
            x = ff.as_matrix()
            #print("count = {}".format(self._count), file=self._logfile)
            #print("shape of update {}".format(x.shape), file=self._logfile)
            y, xr, rel_err = self._se.update(x)
            y = -y
            #print("y = {}".format(y), file=self._logfile)
            #print("y[0,0] = {}".format(y), file=self._logfile)
            self._count = 0
            self._point = {tag.strip(): None for tag in self._tags}
            response = udf_pb2.Response()
            #print ("type of point.time = {}".format(type(point.time)), file=self._logfile)
            #print ("point.time = {}".format(point.time), file=self._logfile)
            #self._logfile.flush()
            #print ("response.point.time before = {}".format(response.point.time, file=self._logfile))
            response.point.time = point.time
            #print ("point.time assigned to response.point.time is {}".format(response.point.time), file=self._logfile)
            #self._logfile.flush()
            #print ("response.point.time after = {}".format(response.point.time, file=self._logfile))
            response.point.fieldsDouble["hv1value"] = y[0,0]

            #response.point.fieldsDouble["hv2value"] = y[0,1]

            #print ("WRITING SPIRIT RESPONSE", file=sys.stderr)
            self._agent.write_response(response, True)

    def end_batch(self, batch_meta):
        print("END_BATCH", file=sys.err)
        pass


class SPIRIT(object):
    def __init__(self, m, p):
        """
        @param m, number of variables
        @param p, number of hidden variables to keep
        """
        self.m = m
        self.p = p
        #initialize the eigen vectors
        self.W = np.matrix(np.zeros((m, p)))

        for i in range(self.p):
            self.W[i,i]=1
        self.dvec = np.zeros((p)) + 1e-2
        self.lamb = 1.0

    def grams(self, A):
        """
        Grams-Schmidt orthogonalization of the columns of a matrix A
        Q = grams(A) returns an m by n matrix Q whose columns are
        an orthonormal basis for the column space of A.
        """
        Q, R = np.linalg.qr(A)
        return Q

    def update(self, x):
        """
        Update for one step
        """
        #x is column vector
        assert x.shape == (self.m, 1)
        x0 = x.copy()
        #do projection onto w
        for i in range(self.p):
            y = np.array(np.dot(self.W[:,i].T, x))
            y = y[0][0]
            self.dvec[i] = self.lamb*self.dvec[i] + y*y
            err = x - y*(self.W[:,i])
            self.W[:,i] = self.W[:,i] + y*err/self.dvec[i]
            x = x - y*(self.W[:,i])
            #normalize w
            self.W[:,i] = self.W[:,i]/np.linalg.norm(self.W[:,i])

        self.W = self.grams(self.W)
        #compute low-D projection, aka hidden variables
        yvec = np.dot(self.W.T, x0)

        xr = np.dot(self.W, yvec)
        xorth = x0 - xr
        relError = np.array(np.dot(xorth.T,xorth)/np.dot(x0.T, x0))
        relError = relError[0][0]

        return yvec.T, xr.T, relError


if __name__ == '__main__':
    # Create an agent
    agent = Agent()
    h = SpiritHandler(agent)
    agent.handler = h

    # Anything printed to STDERR from a UDF process gets captured into the Kapacitor logs.
    #print >> sys.stderr, "Starting agent for Spirit"
    print ("Starting agent for Spirit", file=sys.stderr)
    agent.start()
    agent.wait()
    #print >> sys.stderr, "Agent finished"
    print ("Agent finished", file=sys.stderr)
