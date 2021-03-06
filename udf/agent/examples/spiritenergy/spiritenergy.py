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
        #self._k = None
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
            #if opt.name == 'k':
            #    self._k = opt.values[0].intValue
            if opt.name == 'n':
                self._n = opt.values[0].intValue
        if self._n:
            self._se = SPIRITEnergy(self._n)
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
        value = point.fieldsDouble["value"]
        tag = point.tags["depth"]
        self._point[tag] = float(value)
        self._count += 1
        if self._count == self._n:
            print ("CALCULATING SPIRIT", file=sys.stderr)
            x = np.array([[i[1] for i in sorted(self._point.items(), key=lambda ii: ii[0])]]).T
            x_df = pd.DataFrame(x)
            ff = x_df.fillna(method='ffill')
            x = ff.as_matrix()
            y, oldp = self._se.update(x)
            y = -y
            self._count = 0
            self._point = {tag.strip(): None for tag in self._tags}
            response = udf_pb2.Response()
            response.point.time = point.time
            fields = ["hv1value", "hv2value", "hv3value", "hv4value", "hv5value"]
            for ii in range(len(y)):
                print ("SENDING {}".format(fields[ii]), file=sys.stderr)
                response.point.fieldsDouble[fields[ii]] = y[0, ii]
            #response.point.fieldsDouble["hv1value"] = y[0,0]
            #response.point.fieldsDouble["hv2value"] = y[0,1]
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
        # initialize the eigen vectors
        self.W = np.matrix(np.zeros((m, m)))

        for i in range(self.m):
            self.W[i,i]=1
        self.dvec = np.zeros((m)) + 1e-2
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
            y = np.array(np.dot(self.W[:, i].T, x))
            y = y[0][0]
            self.dvec[i] = self.lamb*self.dvec[i] + y*y
            err = x - y*(self.W[:, i])
            self.W[:, i] = self.W[:, i] + y*err/self.dvec[i]
            x = x - y*(self.W[:, i])
            #normalize w
            self.W[:, i] = self.W[:, i]/np.linalg.norm(self.W[:, i])

        self.W[:, :self.p] = self.grams(self.W[:, :self.p])
        #compute low-D projection, aka hidden variables
        yvec = np.dot(self.W[:, :self.p].T, x0)

        xr = np.dot(self.W[:, :self.p], yvec)
        xorth = x0 - xr
        relError = np.array(np.dot(xorth.T,xorth)/np.dot(x0.T, x0))
        relError = relError[0][0]

        return yvec.T, xr.T, relError

class SPIRITEnergy(object):
    """
    Loop for selecting an appropriate k
    """
    def __init__(self, m):
        self.m = m
        self.initial_p = 1
        self.E = 0.0 #sumXsq
        self.E1 = 0.0 #sumYsq
        self.t = 0
        self.lo = 0.999999
        self.hi = 1.00
        self.holdOffTime = 10
        self.lastChangeAt = 1
        self.spirit = SPIRIT(self.m, self.initial_p) #change

    def update(self, x):
        self.t += 1

        yvec, xr, relError = self.spirit.update(x)
        oldp = self.spirit.p
        E = self.spirit.lamb*self.E + np.dot(x.T,x)[0][0]  # change
        E1 = self.spirit.lamb*self.E1 + np.dot(yvec,yvec.T)[0][0]  # change
        print ("COEF = {}".format(str(self.lo*E/E1)), file=sys.stderr)
        if E1 > self.hi*E and self.spirit.p > 1 and self.lastChangeAt < self.t-self.holdOffTime:
            self.spirit.p -= 1
            self.lastChangeAt = self.t
            # print self.t, 'decrease p', self.spirit.p, E1, E
        elif E1 < self.lo*E and self.lastChangeAt < self.t-self.holdOffTime and self.spirit.p < self.m:
            self.spirit.p += 1
            self.lastChangeAt = self.t
            # print self.t, 'increase p', self.spirit.p, E1, E
        self.E = E
        self.E1 = E1
        return yvec, oldp


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