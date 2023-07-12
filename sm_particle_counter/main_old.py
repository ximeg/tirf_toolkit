import numpy as np
import pandas as pd
from dask.distributed import Client
import webbrowser
from dask_image import imread as dask_imread
from os.path import basename, splitext, exists
from time import sleep
from os import listdir
from pims.api import UnknownFormatError
import matplotlib
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter



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
    image_stack = dask_imread.imread(tiff_file)[1:]  # drop the first frame, it is usually bad

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


# %%


def estimate_rise_time(tiff_file):
    fname = splitext(basename(tiff_file))[0]
    image_stack = dask_imread.imread(tiff_file)[1:]  # drop the first frame, it is usually bad

    # FIXME dirty hack: truncate data. Skip first 100 frames, and use only following 400 frames
    image_stack = image_stack[100:500]

    channel_intensity = {}
    for channel, img in get_channels(image_stack).items():
        # Outputting channel intensity over time
        # FIXME dirty hack: analyze only Cy3
        if channel == 'Cy3':
            channel_intensity[channel] = img.mean(axis=(1, 2)).compute()

    df = pd.DataFrame(channel_intensity)
    df.to_csv(fname + "_Intensity.csv")

    # Rise time calculation
    for channel in df.columns:
        intensity_data_np = df[channel].to_numpy()

        front_edge = intensity_data_np  # most 400 points, see above

        half_max = 0.5 * (intensity_data_np.min() + intensity_data_np.max())
        peak_idx = np.where(intensity_data_np > half_max)[0]
        up_idx, down_idx = peak_idx[0], peak_idx[-1]
        # Should we just use mean instead??
        if (up_idx + down_idx) // 2 < 400:
            front_edge = front_edge[: (up_idx + down_idx) // 2]

        plt.plot(front_edge, alpha=0.5)
        N = len(front_edge)
        window_length = (2 * (N // 20) + 1) + 10
        front_edge_smooth = savgol_filter(
            front_edge, polyorder=3, window_length=window_length
        )
        plt.plot(front_edge_smooth)
        signal_l, signal_h = np.median(front_edge[: N // 4]), np.median(
            front_edge[-N // 4 :]
        )
        margin = 0.1 * (signal_h - signal_l)
        thresh_l, thresh_h = signal_l + margin, signal_h - margin
        plt.axhline(thresh_l, ls="--", c="k")
        plt.axhline(thresh_h, ls="--", c="k")

        t1, t2 = (
            np.argwhere(np.diff(np.sign(thresh_l - front_edge_smooth))).flatten()[0],
            np.argwhere(np.diff(np.sign(thresh_h - front_edge_smooth))).flatten()[0],
        )

        plt.plot([t1, t2], [front_edge_smooth[t1], front_edge_smooth[t2]], "ro")
        plt.xlabel("Frames")
        plt.ylabel("Intensity, photons")
        dt = t2 - t1
        plt.title(f"Rise time: {dt} frames")
        plt.savefig(fname + "_RiseTimeIntensity_" + channel + ".png", dpi=600)
        plt.close()

    # TODO: Analyze the falling edge of the signal as well!



# %%


def rise_time_main():
    matplotlib.use("Agg")
    client = Client()
    print(client)
    webbrowser.open(client.dashboard_link)

    while True:
        sleep(1)
        try:
            for f in listdir("."):
                name, ext = splitext(f)
                # TODO: change the logic. If CSV file is not there, create it.
                # If it is there but png is absent, create PNG based on data from CSV
                if ".tif" in ext.lower():
                    if not exists(f"{name}_Intensity.csv"):
                        print(f)
                        estimate_rise_time(f)
        except PermissionError:
            pass
        except UnknownFormatError:
            pass
        except KeyboardInterrupt:
            client.cancel()
            break


# %%
def particle_count_main():
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


# %%


def count_and_rise():
    matplotlib.use("Agg")
    client = Client()
    print(client)
    webbrowser.open(client.dashboard_link)

    while True:Village Creek State Park
        sleep(1)
        try:
            for f in listdir("."):
                name, ext = splitext(f)
                if ".tif" in ext.lower():
                    if not exists(f"{name}_N_particles.csv"):
                        print(f)
                        count_particles(f)
                    if not exists(f"{name}_Intensity.csv"):
                        print(f)
                        estimate_rise_time(f)
        except PermissionError:
            pass
        except UnknownFormatError:
            pass
        except KeyboardInterrupt:
            client.cancel()
            break


# %%
if __name__ == "__main__":
    particle_count_main()
    rise_time_main()
