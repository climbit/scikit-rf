import unittest
import os
import skrf as rf
import numpy as npy

from skrf.calibration.deembedding import OpenDeembedding, OpenShortDeembedding


class DeembeddingTest(object):
    '''
    '''
    def __init__(self):
        # dut
        self.dut = None
        # dut with errors
        self.dut_measured = None
        # dut after deembedding
        self.dut_deembeded = None
        # list of error networks
        # one per port
        self.errors = []
        # ideals
        self.ideals = []
        # ideals with error networks
        self.ideals_measured = []
        # how many ports should the dut have?
        self.nports = 2
        # frequency range of the dut
        self.freq = rf.Frequency(10, 10e3, 1001, 'mhz')
        # the medium in which everything is implemented
        self.medium = None

    def setup(self):
        # setup dut
        self.medium = rf.media.CPW(self.freq, w=0.6e-3, s=0.25e-3, ep_r=10.6)
        self.dut = self.medium.line(90, 'deg')
        # setup error network and measurement data
        self.dut_measured = self.dut.copy()
        for port_idx in range(self.nports):
            self.errors.append(self.medium.random(2, True))
            self.dut_measured = rf.connect(self.errors[port_idx], 1, self.dut_measured, port_idx)

    def measure(self, ntwk_left, ntwk_right):
        out = ntwk_left ** ntwk_right
        out.name = ntwk_right.name
        return out

    def measure_oneport_ideal(self, ideal, errors):
        meas_list = []
        measured = rf.Network(f=ideal.f, z0=ideal.z0)
        for port in range(self.nports):
            meas_list.append(errors[port] ** ideal)
        measured = rf.network.n_oneports_2_nport(meas_list)

        return measured

    def measure_twoport_ideal(self, ideal, errors):
        meas_list = []
        for outport in range(self.nports):
            for inport in range(outport+1, self.nports):
                meas_list.append(errors[outport] ** ideal ** errors[inport])

        return rf.network.n_twoports_2_nport(meas_list, self.nports)

    def test_dut(self):
        for f in range(len(self.dut.f)):
            for outport in range(self.nports):
                for inport in range(self.nports):
                    self.assertAlmostEqual(
                        self.dut.s[f, outport, inport],
                        self.dut_deembeded.s[f, outport, inport]
                    )

    def test_accuracy_of_directivity(self):
        for port in range(self.nports):
            self.assertEqual(
                self.errors[port].s11,
                self.errors[port].s11
                )

    def test_accuracy_of_source_match(self):
        self.assertEqual(
            self.E.s22,
            self.cal.coefs_ntwks['source match'],
            )

    def test_accuracy_of_reflection_tracking(self):
        self.assertEqual(
            self.E.s21*self.E.s12,
            self.cal.coefs_ntwks['reflection tracking'],
            )



class OpenDeembeddingTest(unittest.TestCase, DeembeddingTest):
    '''
    Test for open deembedding.
    '''
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)
        DeembeddingTest.__init__(self)

    def setUp(self):
        DeembeddingTest.setup(self)

        # create ideals
        self.ideals.append(self.medium.open())
        self.ideals_measured.append(self.measure_oneport_ideal(self.ideals[0], self.errors))

        # deembed
        de = OpenDeembedding(self.ideals_measured)
        de.run()
        self.dut_deembeded = de.apply_cal(self.dut_measured)


if __name__ == "__main__":
    unittest.main()
