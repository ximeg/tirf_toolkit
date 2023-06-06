import numpy as np
import pandas as pd
from scipy.ndimage import maximum_filter
from dask.distributed import Client
import webbrowser
import dask
from dask_image import imread as dask_imread
from os.path import basename, splitext, exists
from time import sleep
from os import listdir
from pims.api import UnknownFormatError
import matplotlib
import matplotlib.pyplot as plt


def get_num_channels(data):
    """
    Return number of channels in smTIRF. If width
    is twice the height, we have two channels.
    """
    ensure_array(data)
    h, w = data.shape[-2:]

    if 2 * h == w:
        return 2
    return 1


def get_channels(data):
    """
    Extract channels from a smTIRF image and return them
    as a dict object. If width is twice the height, we have
    two channels, one otherwise.
    """
    N = get_num_channels(data)
    if N == 1:
        return dict(Cy3=data)
    elif N == 2:
        w = data.shape[-1]
        return dict(Cy3=data[:, :, : w // 2], Cy5=data[:, :, w // 2 :])
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


def segment_particles(layer, threshold):
    """
    Threshold the image to select bright particles and apply maximum filter
    to erode background around them, leaving only a single white pixel per
    particle.
    """
    masked_layer = layer * (layer > threshold)
    return maximum_filter(layer, size=3) == masked_layer


def count_particles(tiff_file):
    fname = splitext(basename(tiff_file))[0]
    image_stack = dask_imread.imread(tiff_file)

    fig = plt.figure()

    N_particles = {}
    for channel, img in get_channels(image_stack).items():
        # Threshold calculation
        bg, q25, q75 = np.quantile(img[0].compute(), [0.05, 0.25, 0.75])
        iqr = q75 - q25
        thresh = bg + 5 * iqr

        # Segmentation of particles
        segmented_stack = img.map_blocks(segment_particles, threshold=thresh).compute()
        N_particles[channel] = segmented_stack.sum(axis=(1, 2))

        # Plot the results
        plt.plot(N_particles[channel], linewidth=0.75, label=channel)

    plt.legend()
    plt.title(f"{fname}")
    plt.xlabel("Frame number")
    plt.ylabel("Number of particles")
    fig.patch.set_alpha(1.0)
    plt.savefig(fname + "_N_particles.png", dpi=600, transparent=False)
    plt.close()

    pd.DataFrame(N_particles).to_csv(fname + "_N_particles.csv")


def main():
    matplotlib.use("Agg")
    client = Client()
    print(client)
    webbrowser.open(client.dashboard_link)

    while True:
        sleep(1)
        try:
            for f in listdir("."):
                name, ext = splitext(f)
                if ".tif" in ext.lower():
                    if not exists(f"{name}_N_particles.csv"):
                        print(f)
                        count_particles(f)
        except PermissionError:
            pass
        except UnknownFormatError:
            pass
        except KeyboardInterrupt:
            client.cancel()
            break


if __name__ == "__main__":
    main()
