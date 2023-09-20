import webbrowser
from glob import glob
from os.path import splitext, exists
from time import sleep

from dask.distributed import Client
from pims import UnknownFormatError
from pandas.errors import EmptyDataError

from misc import cond_run


def start_daemon(output_suffix, func, dask_cluster=False, **kwargs):

    if dask_cluster:

        client = Client()
        print(client.dashboard_link)

        if kwargs['status']:
            webbrowser.open(client.dashboard_link)

    while True:
        sleep(1)

        for f in glob(kwargs["pattern"]):
            try:
                if not exists(f"{splitext(f)[0]}_{output_suffix}"):
                    cond_run(f, output_suffix, func, **kwargs)

            except PermissionError:
                print("Don't have permissions to open %f" % f)
            except UnknownFormatError:
                print("Unknown format of file %f" % f)
            except KeyboardInterrupt:
                break
            except EmptyDataError:
                print("No data found in %f" % f)
            except Exception as e:
                print(f"Could not process file {f}, error is {repr(e)}")
