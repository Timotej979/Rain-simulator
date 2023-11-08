#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.INFO)

import matplotlib.pyplot as plt

import pyrealsense as pyrs


if __name__ == '__main__':
    with pyrs.Service():
        dev = pyrs.Device()

        dev.wait_for_frame()
        plt.imshow(dev.colour)
        plt.show()