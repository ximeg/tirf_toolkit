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


def get_channel_slices(data):
    """
    Return slices of channels in smTIRF.
    If width is twice the height, we have two channels,
    and two slices will be returned. Otherwise one slice
    will be returned that contains the whole image
    """
    ensure_array(data)

    w = data.shape[-1]
    n_ch = get_num_channels(data)
    for ch_index in range(n_ch):
        x_min = int(ch_index * w / n_ch)
        x_max = int((ch_index + 1) * w / n_ch)
        yield np.s_[:, :, x_min:x_max]


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
    masked_layer = layer * (layer > threshold)
    return maximum_filter(layer, size=3) == masked_layer


def count_particles(tiff_file):
    image_stack = dask_imread.imread(tiff_file)

    N = image_stack.shape[0]
    N_particles = dict(Cy3=np.zeros(N), Cy5=np.zeros(N))
    Cy3 = True
    for slice in get_channel_slices(image_stack):
        img = image_stack[slice]

        # Threshold calculation
        H, W = img.shape[-2:]
        bg, q25, q75 = np.quantile(img[0].compute(), [0.05, 0.25, 0.75])
        iqr = q75 - q25
        thresh = bg + 5 * iqr

        # Segmentation of particles
        segmented_stack = img.map_blocks(segment_particles, threshold=thresh).compute()

        channel = "Cy3" if Cy3 else "Cy5"
        Cy3 = False

        N_particles[channel] = segmented_stack.sum(axis=(1, 2))

    return N_particles


def plot_N_particles(tiff_file):
    fname = splitext(basename(tiff_file))[0]

    N_particles = count_particles(tiff_file)

    fig = plt.figure()
    plt.plot(N_particles["Cy3"], color="darkred", linewidth=0.75)
    plt.plot(N_particles["Cy5"], color="navy", linewidth=0.75)
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
                        plot_N_particles(f)
                        print(f)
        except PermissionError:
            pass
        except UnknownFormatError:
            pass
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
