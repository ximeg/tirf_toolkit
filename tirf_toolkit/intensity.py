from misc import parse_args, cond_run, intersection
from tirf_image import TIRFimage
import pandas as pd


def analyze_intensity(tirf_image: TIRFimage, channels=None):
    """
    Count particles in each spectral channel of a TIFF stack. Each channel
    is segmented with an individual threshold computed based on the first frame.
    Returns a pandas data frame with columns representing spectral channels
    """

    ch_int = {}
    # Compute mean value across all the columns in a frame, per spectral channel
    for channel in channels:
        ch_int[channel] = getattr(tirf_image, channel).mean(axis=(-1, -2)).compute()

    return pd.DataFrame.from_dict(ch_int)


def tiff_analyze_intensity(tiff_file, csv_file, channels=None):
    """
    Measure average intensity of each frame in each spectral channel of a TIFF file.
    Saves result in a CSV file.
    """
    tirf_image = TIRFimage(tiff_file)
    ch = intersection(channels, tirf_image.channels)

    if ch:
        df = analyze_intensity(tirf_image, channels=ch)
        df.insert(loc=0, column='time', value=df.index*tirf_image.frameTime)
        df.to_csv(csv_file, float_format='% 12.3f', index_label='frame')
