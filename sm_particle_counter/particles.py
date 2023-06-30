from os.path import basename, splitext
from scipy.ndimage import maximum_filter
from dask_image import imread
from utils import get_channels
import numpy as np

def segment_particles(layer, threshold):
    """
    Threshold the image to select bright particles and apply maximum filter
    to erode background around them, leaving only a single white pixel per
    particle.
    """
    masked_layer = layer * (layer > threshold)
    return maximum_filter(layer, size=3) == masked_layer


def count_particles(tiff_file):
    """
    Count number of particles in each spectral channel of each
    frame of the TIFF stack and save the result into a CSV file
    """
    fname = splitext(basename(tiff_file))[0]
    image_stack = imread.imread(tiff_file)[1:]  # drop the first frame, it is usually bad

    N_particles = {}
    for channel, img in get_channels(image_stack).items():
        # Threshold calculation
        bg, q25, q75 = np.quantile(img[0].compute(), [0.05, 0.25, 0.75])
        iqr = q75 - q25
        thresh = bg + 5 * iqr

        # Segmentation of particles
        segmented_stack = img.map_blocks(segment_particles, threshold=thresh).compute()
        N_particles[channel] = segmented_stack.sum(axis=(1, 2))