"""Roman's toolkit to analyze pTIRF datasets from FlashGordon.

This script monitors a given directory for new files that satisfy a
given pattern, processes them, and saves results. If the result
file already exists, the input file is skipped.

Supported operations include counting of particles in TIRF stack,
analysis of intensity, and analysis of rise/fall time of fluidic injections.

For TIFF images, it uses Dask for parallel computations.

Usage:
  tirf particles       [options] [<channels>]...
  tirf particles_plot  [options] [<channels>]...
  tirf intensity       [options] [<channels>]...
  tirf injection_plot  [options] [<channels>]...
  tirf injection_stats [options] [<channels>]...

You can specify spectral channels to process (one or more of Cy2, Cy3,
Cy5, and Cy7). By default, all spectral present channels are processed.

Options:
  -p --pattern=PTRN    Pattern for input file names, without extension [default: *]
  -n --n_frames=N      Maximum number of data points to process; zero means no limit [default: 0].
  -s --status          Open Dask dashboard to see the status of computing
  -a --align=T/F       For injection plot: align t=0 with the start of injection [default: true]
  -w --window=LENGH    Window length for Savitsky-Golay filter [default: 19]
  -h --help            Show this screen.
  -v --version         Show version.

Author: {author}, {email}
Version: {version}
"""

from daemon import start_daemon
from fluidics import analyze_csv, show_dataset
from intensity import tiff_analyze_intensity
from misc import parse_args, intersection, chop_filename
from particles import tiff_count_particles

from glob import glob
from matplotlib import pyplot as plt
from os.path import splitext, basename, dirname, join
import pandas as pd


def main():
    kwargs = parse_args(__doc__)

    if kwargs["particles"]:
        kwargs["pattern"] += ".tif"
        start_daemon("_N_particles.csv", tiff_count_particles, dask_cluster=True, **kwargs)

    if kwargs["particles_plot"]:

        kwargs["pattern"] += "_N_particles.csv"

        def plot_csv(fn, outfile, n_frames=0, **kwargs):
            df = pd.read_csv(fn, index_col='time')
            # First frame is usually garbage, drop it
            df = df.iloc[1:]

            if n_frames:
                df = df.iloc[:n_frames]

            # convert s to ms
            df.index *= 1000

            ch = intersection(kwargs["channels"], df.filter(regex="Cy?").columns)

            plt.figure(figsize=(7, 4))

            for channel in ch:
                plt.plot(df[channel], label=channel)

            plt.title(splitext(basename(fn))[0])
            plt.legend()
            plt.xlabel("time / ms")
            plt.ylabel("Number of particles")
            plt.savefig(outfile, dpi=200)
            plt.close()

        start_daemon(".png", plot_csv, **kwargs)

    if kwargs["intensity"]:
        kwargs["pattern"] += ".tif"
        start_daemon("_intensity.csv", tiff_analyze_intensity, dask_cluster=True, **kwargs)

    if kwargs["injection_plot"]:
        kwargs["pattern"] += "_intensity.csv"

        def plot_csv(fn, outfile, **kwargs):
            df, channel, front, back = analyze_csv(fn, **kwargs)
            ax = plt.figure(figsize=(7, 4)).gca()

            offset = front.a if front and kwargs["align"] else 0
            show_dataset(df, channel, front, back, ax, offset=offset)
            plt.title(chop_filename(fn))
            plt.savefig(outfile, dpi=200)
            plt.close()

        start_daemon(".png", plot_csv, **kwargs)

    if kwargs["injection_stats"]:
        kwargs["pattern"] += "_intensity.csv"

        data = []
        for fn in glob(kwargs["pattern"]):
            df, channel, front, back = analyze_csv(fn)
            data.append(dict(
                filename = chop_filename(fn),
                front_start = front.a,
                front_tau = front.tau,
                back_start = back.a,
                back_tau = back.tau,
                amp = front.ptp,
                duration = (back.a + back.tau / 2) - (front.a + front.tau / 2),
            ))

        pd.DataFrame.from_dict(data).to_csv(join(dirname(fn), "injection_stats.csv"), index=False, float_format='% 12.3f')


if __name__ == "__main__":
    main()