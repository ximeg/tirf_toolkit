"""Quantification of fluorescence intensity in a TIRF image stack

This script monitors a given directory for new TIFF files
created by Flash Gordon and calculates average signal intensity
in each frame per each spectral channel. It uses Dask for
parallel computations. The results are written in CSV format.
A TIFF file is being processed only if a corresponding CSV file
with the result is missing. The CSV file name is formed by replacing
the extension of the input TIFF file with "{int_suffix}.csv".

Usage:
  tirf_intensity [options] [<channel>]...

You can specify spectral channels to process (one or more of Cy2, Cy3,
Cy5, and Cy7). By default, all spectral present channels are processed.

Options:
  -d --directory=DIR   Directory to monitor [default: .].
{common_opts}

Author: {author}, {email}
Version: {version}
"""
from dask.distributed import Client
from misc import parse_args, cond_run, intersection
from time import sleep
from pims.api import UnknownFormatError
from os import listdir
from os.path import splitext, exists, join, basename
import pandas as pd
import webbrowser
from tirf_image import TIRFimage


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
        # TODO: add time axis to the data
        df.to_csv(csv_file)
    else:
        print(f"Requested spectral channels {channels} not found. {basename(tiff_file)} contains {tirf_image.channels}\n")
        with open(csv_file, 'w') as fp:
            pass

def main():
    """
    Main function for automated analysis that does everything.
    """
    arguments = parse_args(__doc__)

    client = Client()
    print(client.dashboard_link)

    if arguments['--status']:
        webbrowser.open(client.dashboard_link)

    folder = arguments["--directory"]

    while True:
        sleep(1)
        try:
            for f in listdir(folder):
                # include path to the selected file
                f = join(folder, f)
                name, ext = splitext(f)
                if ".tif" in ext.lower():
                    suffix = arguments['int_suffix'] + ".csv"
                    if not exists(f"{name}_{suffix}"):
                        cond_run(f, suffix, tiff_analyze_intensity, channels=arguments["<channel>"])

        except PermissionError:
            pass
        except UnknownFormatError:
            pass
        except KeyboardInterrupt:
            client.cancel()
            break


if __name__ == '__main__':
    main()
