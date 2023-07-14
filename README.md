# Roman's toolkit for single-molecule TIRF image processing

This script monitors a given directory for new files that satisfy a
given pattern, processes them, and saves the results. If the resulting
file already exists, the input file is skipped.

Supported operations include counting of particles in TIRF stack,
analysis of intensity, and analysis of rise/fall time of fluidic injections.

For TIFF images, it uses Dask for parallel computations.

Usage:
```
  tirf particles      [options] [<channel>]...
  tirf particles_plot [options] [<channel>]...
  tirf intensity      [options] [<channel>]...
  tirf injection_plot [options] [<channel>]...
  tirf injection_stat [options] [<channel>]...
```
You can specify spectral channels to process (one or more of Cy2, Cy3,
Cy5, and Cy7). By default, all spectral present channels are processed.

Options:
```
    -p --pattern=PTRN   Pattern of file names to process, by default everything in the current folder.
                        Depending on the command, it will process only TIF or CSV files, unless custom
                        pattern is provided.
    -s --status         Open Dask distributed dashboard to monitor status of the computations
    -h --help           Show help message
```


# Installation

Make sure you have Anaconda3 installed.

Clone this repository to a location of your choice. Open Anaconda3 command prompt,
go to the root folder of this package (the one with `setup.py`), and from there
create a new virtual environment...

```
conda create --name ttk -c conda-forge
conda activate ttk
```

and then install the package itself using `pip`

```
pip install .
```

# How to use

Open Anaconda terminal, navigate to the folder with your data (or specify pattern with wildcards using option `-p`),
and start `tirf <command>`. It will process all existing and any newly created TIF/CSV files in the current folder
as long as it is running.


