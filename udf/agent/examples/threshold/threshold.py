import numpy as np
import pickle as pkl
import sys
import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
from agent import Agent, Handler
import udf_pb2

# The Agent calls the appropriate methods on the Handler as requests are read off STDIN.
#
# Throwing an exception will cause the Agent to stop and an ErrorResponse to be sent.
# Some *Response objects (like SnapshotResponse) allow for returning their own error within the object itself.
# These types of errors will not stop the Agent and Kapacitor will deal with them appropriately.
#
# The Handler is called from a single thread, meaning methods will not be called concurrently.
#
# To write Points/Batches back to the Agent/Kapacitor use the Agent.write_response method, which is thread safe.
class ThresholdHandler(object):
    def __init__(self, agent):
        self._agent = agent
        self._model = None
        self._lag0 = None
        self._lag1 = None
        self._lag2 = None
        self._lag3 = None
        self._lag4 = None
        self._lag5 = None
        self._count = 0


    def info(self):
        response = udf_pb2.Response()
        response.info.wants = udf_pb2.STREAM
        response.info.provides = udf_pb2.STREAM
        #response.info.options['some_string'].valueTypes.append(udf_pb2.STRING)
        #response.info.options['some_int'].valueTypes.append(udf_pb2.INT)
        return response

    def init(self, init_req):
        success = True
        msg = ''
        for opt in init_req.options:
            pass
        outfile = '/vagrant/udf/agent/examples/threshold/testdata.dump'
        PData = pkl.load(open(outfile, 'rb'))
        nTrain = 200
        Xtrain = np.c_[PData[4:nTrain-1], PData[3:nTrain-2], PData[2:nTrain-3], PData[1:nTrain-4], PData[0:nTrain-5]]
        ytrain = PData[5:nTrain]
        self._model = sm.OLS(ytrain, Xtrain)
        self._model = self._model.fit()
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
        pass

    def point(self, point):
        self._lag5 = self._lag4
        self._lag4 = self._lag3
        self._lag3 = self._lag2
        self._lag2 = self._lag1
        self._lag1 = self._lag0
        self._lag0 =  (point.fieldsDouble["value"])
        predictor_vector = [self._lag1, self._lag2, self._lag3, self._lag4, self._lag5]
        if all(predictor_vector):
            self._count += 1
            yhat = self._model.predict(predictor_vector)
            prstd, iv_l, iv_u = wls_prediction_std(self._model, exog=[predictor_vector], alpha=0.9)
            if (abs(yhat-self._lag0)>3*prstd) and self._count > 20:
                response = udf_pb2.Response()
                response.point.time = point.time
                response.point.fieldsString["title"] = "Anomaly"
                response.point.fieldsInt["time"] = response.point.time
                response.point.fieldsDouble["value"] = self._lag0
                #print ("WRITING SPIRIT RESPONSE", file=sys.stderr)
                self._agent.write_response(response, True)

    def end_batch(self, end_req):
        pass


if __name__ == '__main__':
        # Create an agent
        agent = Agent()
        h = ThresholdHandler(agent)
        agent.handler = h

        # Anything printed to STDERR from a UDF process gets captured into the Kapacitor logs.
        print >> sys.stderr, "Starting agent for Threshold"
        agent.start()
        agent.wait()
        print >> sys.stderr, "Agent finished"