import numpy as np
import pandas as pd
from scipy.ndimage import maximum_filter
from dask.distributed import Client
import webbrowser
from dask_image import imread as dask_imread
from os.path import basename, splitext, exists
from time import sleep
from os import listdir
from pims.api import UnknownFormatError
import matplotlib
import matplotlib.pyplot as plt


def segment_particles(layer, threshold):
    masked_layer = layer * (layer > threshold)
    return maximum_filter(layer, size=3) == masked_layer


def count_particles(tiff_file):
    image_stack = dask_imread.imread(tiff_file)

    # Threshold calculation
    N, H, W = image_stack.shape
    bg, q25, q75 = np.quantile(image_stack[0].compute(), [0.05, 0.25, 0.75])
    iqr = q75 - q25
    thresh = bg + 5 * iqr

    # Segmentation of particles
    segmented_stack = image_stack.map_blocks(
        segment_particles, threshold=thresh
    ).compute()

    return segmented_stack.sum(axis=(1, 2))


def plot_N_particles(tiff_file):
    fname = splitext(basename(tiff_file))[0]

    N_particles = count_particles(tiff_file)

    fig = plt.figure()
    plt.plot(N_particles, linewidth=0.75)
    plt.title(f"{fname}")
    plt.xlabel("Frame number")
    plt.ylabel("Number of particles")
    fig.patch.set_alpha(1.0)
    plt.savefig(fname + "_N_particles.png", dpi=600, transparent=False)
    plt.close()

    pd.DataFrame(dict(N=N_particles)).to_csv(fname + "_N_particles.csv")


def main():
    matplotlib.use("Agg")
    client = Client()
    print(client)
    webbrowser.open(client.dashboard_link)

    while True:
        sleep(0.1)
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
