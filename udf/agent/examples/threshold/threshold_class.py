# Author: Alex Sun
# Date: 12042016
# Performs outlier detection using baseline data
#
import os
import readline #solves an R import issue
import sys
import time
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn.model_selection import cross_val_predict
import statsmodels.api as sm
from utility import index_by_date
from clients import InfluxDatabaseClient
import sklearn.preprocessing as skp
import pickle as pkl




if __name__ == '__main__':
    import sys
    import matplotlib.pyplot as plt
    from statsmodels.sandbox.regression.predstd import wls_prediction_std
    rgen = np.random.RandomState(12238)

    outfile = 'testdata.dump'
    PData = pkl.load(open(outfile, 'rb'))
    nTrain = 200
    Xtrain = np.c_[PData[4:nTrain-1], PData[3:nTrain-2], PData[2:nTrain-3], PData[1:nTrain-4], PData[0:nTrain-5]]
    ytrain = PData[5:nTrain]
    Xtest = np.c_[PData[nTrain-1:-1], PData[nTrain-2:-2], PData[nTrain-3:-3], PData[nTrain-4:-4], PData[nTrain-5:-5]]
    ytest = PData[nTrain:]
    print PData.shape

    res = ytrain

    model = sm.OLS(ytrain, Xtrain)
    #train an AR model
    model = model.fit()
    #The results from the following line will show that R^2 of the model is 0.993
    print model.summary()
    #print model.conf_int(0.05)   # 95% confidence interval of the trained model
    ##
    # do sequential testing on testing data
    nTest = Xtest.shape[0]
    # set up results array
    results = np.zeros((nTest, 5))
    outlierInd = []
    for i in xrange(nTest):
        #predict out of sample
        yhat = model.predict(Xtest[i,:])
        #get prediction interval
        #A prediction interval gives an interval in which one expects yhat to fall;
        #a good rule of thumb is to use Zi >= 3 as a proxy for the anomaly.
        #alpha is 0.9
        prstd, iv_l, iv_u = wls_prediction_std(model, exog= Xtest[i,:], alpha=0.9)
        results[i,:4] = [yhat, prstd, iv_l, iv_u]
        if (abs(yhat-ytest[i])>3*prstd):
            outlierInd.append(i)
'''
    fig, ax = plt.subplots()
    ax.hold(True)
    ax.plot(results[:,0])
    ax.fill_between(xrange(nTest), results[:,2], results[:,3], color='#888888', alpha=0.1)
    ax.plot(outlierInd, results[outlierInd,0], 'o')
    ax.plot(problem.ytest, 'r')
    plt.show()
'''