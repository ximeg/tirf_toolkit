"""
__version__.py
~~~~~~~~~~~~~~
Information about the current version of package
"""

__title__ = "sm_particle_counter"
__description__ = (
    "Counts number of particles in each frame of a TIFF stack from a pTIRF instrument"
)
__version__ = "0.0.1-refactor"
__author__ = "Roman Kiselev"
__author_email__ = "roman.kiselev@stjude.org"
__license__ = "BSD 2-Clause License"
__url__ = "https://git.stjude.org/users/rkiselev/repos/sm_particle_counter/browse"
__int_suffix__ = "_intensity"
__particles_suffix__ = "_N_particles"
__common_opts__ = '''\
  -s --status          Open Dask dashboard to see the status of computing
  -h --help            Show this screen.
  -v --version         Show version.
'''