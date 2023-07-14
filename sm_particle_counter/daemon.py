"""Roman's toolkit to analyze pTIRF data sets from FlashGordon.

This script monitors a given directory for new files that satisfy a
given pattern, processes them, and saves results. If the result
file already exists, the input file is skipped.

Supported operations include counting of particles in TIRF stack,
analysis of intensity, and analysis of rise/fall time of fluidic injections.

For TIFF images, it uses Dask for parallel computations.

Usage:
  tirf particles      [options] [<channel>]...
  tirf particles_plot [options] [<channel>]...
  tirf intensity      [options] [<channel>]...
  tirf injection_plot [options] [<channel>]...
  tirf injection_stat [options] [<channel>]...

You can specify spectral channels to process (one or more of Cy2, Cy3,
Cy5, and Cy7). By default, all spectral present channels are processed.

Options:
  -p --pattern=PTRN   Pattern of file names to process, by default everything in the current folder.
{common_opts}

Author: {author}, {email}
Version: {version}
"""

from glob import glob
from os.path import splitext, exists, basename, dirname, join
from time import sleep
from pims import UnknownFormatError
from misc import cond_run, parse_args, intersection, chop_filename
from dask.distributed import Client
from matplotlib import pyplot as plt
import webbrowser
import pandas as pd

from particles import tiff_count_particles
from intensity import tiff_analyze_intensity
from fluidics import analyze_csv, show_dataset


def start_daemon(output_suffix, func, arguments, dask_cluster=False):
    if dask_cluster:

        client = Client()
        print(client.dashboard_link)

        if arguments['--status']:
            webbrowser.open(client.dashboard_link)

    while True:
        sleep(1)

        for f in glob(arguments["--pattern"]):
            try:
                if not exists(f"{splitext(f)[0]}_{output_suffix}"):
                    cond_run(f, output_suffix, func, channels=arguments["<channel>"])

            except PermissionError:
                pass
            except UnknownFormatError:
                pass
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Could not process file {f}, error is {repr(e)}")


def main():
    arguments = parse_args(__doc__)
    if arguments["particles"]:
        if not arguments["--pattern"]:
            arguments["--pattern"] = "./*.tif"
        start_daemon("_N_particles.csv", tiff_count_particles, arguments=arguments, dask_cluster=True)

    if arguments["particles_plot"]:
        if not arguments["--pattern"]:
            arguments["--pattern"] = "./*_N_particles.csv"

        def plot_csv(fn, *args, **kwargs):
            df = pd.read_csv(fn, index_col='time')
            # First frame is usually garbage, drop it
            df = df.iloc[1:]

            # convert s to ms
            df.index *= 1000

            ch = intersection(arguments["<channel>"], df.filter(regex=("Cy?")).columns)

            ax = plt.figure(figsize=(7, 4)).gca()

            for channel in ch:
                plt.plot(df[channel], label=channel)

            plt.title(splitext(basename(fn))[0])
            plt.legend()
            plt.savefig(splitext(fn)[0] + ".png", dpi=200)

        start_daemon(".png", plot_csv, arguments=arguments, dask_cluster=False)

    if arguments["intensity"]:
        if not arguments["--pattern"]:
            arguments["--pattern"] = "./*.tif"
        start_daemon("_intensity.csv", tiff_analyze_intensity, arguments=arguments, dask_cluster=True)

    if arguments["injection_plot"]:
        if not arguments["--pattern"]:
            arguments["--pattern"] = "./*_intensity.csv"

        def plot_csv(fn, *args, **kwargs):
            df, channel, front, back = analyze_csv(fn)
            ax = plt.figure(figsize=(7, 4)).gca()
            show_dataset(df, channel, front, back, ax, offset=front.a)
            plt.savefig(splitext(fn)[0] + ".png", dpi=200)

        start_daemon(".png", plot_csv, arguments=arguments, dask_cluster=False)

    if arguments["injection_stat"]:
        if not arguments["--pattern"]:
            arguments["--pattern"] = "./*_intensity.csv"

        data = []
        for fn in glob(arguments["--pattern"]):
            df, channel, front, back = analyze_csv(fn)
            data.append(dict(
                filename = chop_filename(fn),
                front_start = front.a,
                front_tau = front.tau,
                back_start = back.a,
                back_tau = back.tau,
                amp = front.ptp,
            ))

        pd.DataFrame.from_dict(data).to_csv(join(dirname(fn), "injection_stats.csv"), index=False, float_format='% 12.3f')


if __name__ == "__main__":
    main()