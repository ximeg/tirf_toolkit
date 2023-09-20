from misc import parse_args, cond_run, intersection
from tirf_image import TIRFimage
from flat_field import get_flat_frame

from scipy.ndimage import maximum_filter
import numpy as np
import pandas as pd


from time import time

def segment_particles(layer, threshold):
    """
    Threshold the image to select bright particles and apply maximum filter
    to erode background around them, leaving only a single white pixel per
    particle.
    """
    masked_layer = layer * (layer > threshold)
    return maximum_filter(layer, size=3) == masked_layer


def count_particles(tirf_image: TIRFimage, channels=None):
    """
    Count particles in each spectral channel of a TIFF stack. Each channel
    is segmented with an individual threshold computed based on the first five frames.
    Returns a pandas data frame with columns representing spectral channels
    """
    ch_n_particles = {}

    for channel in channels:
        # Compute an average frame from the first five frames
        stack = getattr(tirf_image, channel)

        # Calculate and subtract the flat frame. We add a constant bias (mean value of the flat frame)
        # to avoid getting negative numbers with uint16 data type.
        print("  ", time(), "Getting flat frame")
        flat_frame = get_flat_frame(stack)
        print("  ", time(), "Subtracting flat frame")
        stack = stack - flat_frame + flat_frame.mean()
        print("  ", time(), "Getting the subset for threshold calculation")

        # Create a small representative data subset to estimate the threshold
        n, h, w = stack.shape
        dh, dw = np.min([100, h // 2]), np.min([100, w // 2])
        subset = stack[
                 ::n // 10,                # 10 frames sampled across the stack
                 h // 2 - dh:h // 2 + dh,  # at most 200x200 pixels, from FOV center
                 w // 2 - dw:w // 2 + dw
                 ]

        # Threshold calculation
        print("  ", time(), "Computing quantiles")
        q25, q75, q90 = np.quantile(subset.compute(), [0.25, 0.75, 0.9])

        # Background occupies at least 90% of the area. On top of that,
        # we add 3x IQRs, which is a pretty conservative metric
        thresh = q90 + 10*(q75 - q25)

        print("  ", time(), "Segmenting stack with threshold =", thresh)
        # Create a stack containing one white pixel per each detected particle
        segmented_stack = stack.map_blocks(segment_particles, threshold=thresh)

        # Now count number of white pixels in each frame
        ch_n_particles[channel] = segmented_stack.sum(axis=(1, 2)).compute()

    return pd.DataFrame.from_dict(ch_n_particles)


def tiff_count_particles(tiff_file, csv_file, channels=None, n_frames=0, **kwargs):
    """
    Count particles in each spectral channel of a TIFF file.
    Saves result in a CSV file.
    """
    tirf_image = TIRFimage(tiff_file)

    if n_frames:
        tirf_image.data = tirf_image.data[:n_frames]

    ch = intersection(channels, tirf_image.channels)

    if ch:
        df = count_particles(tirf_image, channels=ch)
        df.insert(loc=0, column='time', value=df.index * tirf_image.frameTime)
        df.to_csv(csv_file, float_format='% 12.3f', index_label='frame')
