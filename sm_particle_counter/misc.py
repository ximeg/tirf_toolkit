from docopt import docopt
from os.path import splitext, exists, basename
import sm_particle_counter.__version__ as meta

def parse_args(doc):
    """
    Fill in common placeholdes in the docstring for docopt
    based on the information from the package metadata,
    and invoke `docopt` to parse the arguments based on
    the docstring.
    """
    pkg_info = dict(
        version=meta.__version__,
        author=meta.__author__,
        email=meta.__author_email__,
        common_opts=meta.__common_opts__,
    )
    arguments = docopt(
            version=meta.__version__,
            doc=doc.format(**pkg_info)
    )

    return arguments | pkg_info


def intersection(requested, available):
    if requested:
        return list(set(requested) & set(available))
    else:
        return available


def cond_run(infile, suffix, action, *args, **kwargs):
    """
    Run `action` on input file `infile`. `action` creates an output file.
    The output file name is created by dropping extension of `infile` and adding `suffix`.
    Skip `action` if output file exists. Essentially, it caches the `action` result.
    """
    outfile = splitext(infile)[0] + suffix
    if not exists(outfile):
        print(f"Processing {infile}")
        return action(infile, outfile, *args, **kwargs)

def chop_filename(fn):
    _ = splitext(basename(fn))[0]
    return _[:_.find("_intensity")]