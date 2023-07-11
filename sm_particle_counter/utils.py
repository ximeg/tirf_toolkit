import dask
import numpy as np

from PIL import Image
from PIL.TiffTags import TAGS



def n_channels(data):
    """
    Return number of channels in smTIRF. We assume that we always
    work with 2x2 binning
    """
    h, w = data.shape[-2:]

    if w >= 2 * h and w >= 2048:
        return 2
    return 1


def Cy3(data):
    # TODO Should it be TR(), TL(), BL(), BR() instead?
    return channel_slices(data)["Cy3"]

def Cy5(data):
    if n_channels(data) == 2:
        return channel_slices(data)["Cy5"]
    else:
        return None

def channel_slices(data):
    n = n_channels(data)
    if n == 1:
        return dict(Cy3=np.s_[...])
    elif n == 2:
        w = data.shape[-1]
        return dict(Cy3=np.s_[...,  :w//2], Cy5=np.s_[..., w//2:])
    else:
        raise NotImplementedError
def get_channels(data):
    """
    Extract channels from a smTIRF image and return them
    as a dict object. If width is twice the height, we have
    two channels, one otherwise.
    """
    n = n_channels(data)
    if n == 1:
        return dict(Cy3=data)
    elif n == 2:
        w = data.shape[-1]
        return dict(Cy3=data[..., : w // 2], Cy5=data[..., w // 2 :])
    else:
        raise NotImplementedError


def ensure_array(data, ndim=3):
    """
    Verify that data is numpy or dask array with correct number of
    dimensions, raise ValueError otherwise
    """
    if not is_array(data, ndim=[1, 2, 3]):
        raise ValueError("Provided data must be a dask or numpy array")

    if data.ndim != ndim:
        raise ValueError("Provided data have incorrect shape")


def is_array(data, ndim=[2, 3]):
    """
    Check if data is a numpy, zarr or dask image with two or three dimensions.
    """
    if not (dask.is_dask_collection(data) or isinstance(data, np.ndarray)):
        return False

    if data.ndim in ndim:
        return True

    return False
