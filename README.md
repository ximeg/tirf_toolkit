# Single-molecule particle counting

This is a Python script that counts number of particles in a given TIFF image stack.

The script correctly handles data with one or two spectral channels.

# Work in progress


# Installation

Make sure you have Anaconda3 installed.

Clone this repository to a location of your choice. Open Anaconda3 command prompt,
go to the root folder of this package (the one with `setup.py`), and from there
create a new virtual environment...

```
conda create --name counter -c conda-forge
conda activate counter
```

and then install the package itself using `pip`

```
pip install .
```

# How to use

Open Anaconda terminal, navigate to the folder with your data, and start `sm_particle_counter`. It will process all existing and any newly created TIFF files in the current folder as long as it is running.


# Known problems

Currently, it treats the entire image as one spectral channel. If you have Cy3 and Cy5 channels side by side, it will report the total number of particles in both channels, combined.
