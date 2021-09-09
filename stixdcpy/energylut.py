#!/usr/bin/python
"""
    This script provides APIs to retrieve energy  calibration data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

"""

from pprint import pprint

import numpy as np

from stixdcpy import io as sio
from stixdcpy.net import JSONRequest as jreq
from stixdcpy.transmission import Transmission


class EnergyLUT(sio.IO):
    def __init__(self, data):
        self.data = data

    @classmethod
    def request(cls, utc):
        data = jreq.fetch_onboard_and_true_eluts(utc)
        '''
        data structure
        {'data':{
                    'onboard':self.onboard_elut, 
                    'calibration':self.calibration_run_elut,
                    'true_energy_bin_edges':self.true_energy_bin_edges,
                    'energy_bin_edges':NOMINAL_EBIN_EDGES,
                },
                'info': self.info(),
                }
                '''
        return cls(data)

    @classmethod
    def from_npy(cls, filename):
        with np.load(filename, allow_picke=True) as data:
            elut_data = data.item()['elut']
            cls(elut_data)

    def save_npy(self, filename):
        np.save(filename, {'elut': self.data})

    def info(self):
        try:
            pprint(self.data['info'])
            # pprint('Pixel 0 true energy bin  edges: ')
            # pprint(self.get_pixel_true_ebins(0))
            # pprint('...')

        except KeyError as e:
            print(e)

    def __getattr__(self, name):
        if name == 'data':
            return self.data['data']

    def get_data(self):
        return self.data['data']

    def get_calibration_data(self):
        try:
            return self.data['data']['calibration']
        except Exception as e:
            print(e)
            return None

    def get_onboard_elut(self):
        try:
            return self.data['data']['onboard']
        except Exception as e:
            print(e)

    def get_true_energy_bin_edges(self):
        try:
            return np.array(self.data['data']['true_energy_bin_edges'])
        except Exception as e:
            print(e)
            return None

    def get_pixel_true_ebins(self, pixel):
        try:

            true_ebins = np.array(self.data['data']['true_energy_bin_edges'])
            pixel_ebins = true_ebins[:, pixel]  # 33 x 384 retrieve the column
            ebins = np.column_stack((pixel_ebins[:-1], pixel_ebins[1:]))
            return ebins
        except Exception as e:
            print(e)
            return None

    def get_pixel_ebins_transmissions(self):
        """
        Get transmission for pixels at a given time
        Arguments
            None
        Returns:
            A numpy array with a shape of 32 x12 x 32.  The three dimensions indicate detector, pixel, and transmission for 32 energy channels.
            The transmission for the last energy bin set to 0
            """
        tr = Transmission()
        try:
            true_ebins = np.array(self.data['data']['true_energy_bin_edges'])  # an 2d array: 33 x 384

            trans = np.zeros((32, 12, 32))
            for i in range(32):
                for j in range(12):
                    ipix = i * 12 + j
                    pixel_ebins = true_ebins[:, ipix]  # retrieve the column
                    ebins = np.column_stack((pixel_ebins[:-1], pixel_ebins[1:]))
                    ebins[0][0] = np.finfo(float).eps
                    ebins[31][1] = 300

                    trans[i][j] = tr.get_detector_transmission(i, ebins, attenuator=False)
            trans[:, :, 31] = 0  # set the transmission for the last energy bin to 0
            # trans[:,:,0]=0 # set the transmission for the first energy bin to 0
            return trans
        except Exception as e:
            return None
