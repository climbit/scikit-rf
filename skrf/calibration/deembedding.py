'''
.. module:: skrf.calibration.deembedding
================================================================
calibration (:mod:`skrf.calibration.deembedding`)
================================================================


This module  provides objects to perform de-embedding.

'''


import numpy as npy

import skrf as rf
from .calibration import Calibration



class Deembedding(Calibration):
    def __init__(self, measured, *args, **kwargs):
        Calibration.__init__(self, measured, [], self_calibration=True, *args, **kwargs)

        self.error_matrix = None


class OpenDeembedding(Deembedding):
    def __init__(self, measured, *args, **kwargs):
        Deembedding.__init__(self, measured, *args, **kwargs)

    def run(self):
        nports = self.measured[0].nports
        print(nports)
        nfreq = len(self.measured[0].f)
        # filter_matrix = npy.diag(npy.ones(nports))
        filter = npy.zeros((nfreq, nports, nports))
        #print(filter)
        for port in range(nports):
            filter[:,port,port] = 1
        #print(filter)
        self.error_matrix = [meas.y * filter for meas in self.measured]
        #print(self.error_matrix[0])

        return None

    def apply_cal(self, ntwk):
        deembedded = ntwk.copy()
        print(npy.shape(deembedded.y))
        print(npy.shape(self.error_matrix[0]))
        deembedded.y = deembedded.y - self.error_matrix[0]

        return deembedded



class OpenShortDeembedding(Deembedding):
    def __init__(self, measured, *args, **kwargs):
        Deembedding.__init__(self, measured, [], *args, **kwargs)
