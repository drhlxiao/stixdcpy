#!/usr/bin/python
'''
    This module provides APIs to retrieve Housekeeping data from STIX data center  ,and some tools to display the data
    Author: Hualin Xiao (hualin.xiao@fhnw.ch)
    Date: Sep. 1, 2021

'''
import requests
from matplotlib import pyplot as plt
import datetime
from astropy.io import fits
from stixdcpy.net import FitsProduct as freq
from stixdcpy import io as sio

class Housekeeping(sio.IO):
    def __init__(self, filename):
        self.data = fits.open(filename)

    @classmethod
    def fetch(cls, start_utc:str, end_utc:str):
        filename=freq.fetch_continuous_data(start_utc, end_utc, 'hkmax') 
        return cls(filename)

    @classmethod
    def from_fits(cls, filename):
        return cls(filename)


    def __getattr__(self, name):
        if name == 'data':
            return self.data
    def get_data(self):
        return self.data
    def peek(self, ax=None, legend_loc='upper right'):
        if not ax:
            _, ax=plt.subplots()
        return ax