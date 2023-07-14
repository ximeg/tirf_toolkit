from PIL import Image
from dask_image import imread
import numpy as np
import re


class TIRFimage:
    def __init__(self, tiff_file):
        self.metadata = _parse_metadata(read_metadata(tiff_file))
        self.channels = self.metadata["channels"]

        self.data = imread.imread(tiff_file)
        self.frameTime = float(self.metadata["frameTime"])

    def __repr__(self):
        return self.data.__repr__() + "\n" + \
            "\n".join([f"{k}={v}" for k, v in self.metadata.items()])

    @property
    def Cy2(self):
        if "Cy2" in self.metadata["channels"]:
            return self.data[self.metadata["Cy2_slice"]]

    @property
    def Cy3(self):
        if "Cy3" in self.metadata["channels"]:
            return self.data[self.metadata["Cy3_slice"]]

    @property
    def Cy5(self):
        if "Cy5" in self.metadata["channels"]:
            return self.data[self.metadata["Cy5_slice"]]

    @property
    def Cy7(self):
        if "Cy7" in self.metadata["channels"]:
            return self.data[self.metadata["Cy7_slice"]]


def get_metadata(tiff_file):
    return _parse_metadata(read_metadata(tiff_file))


def read_metadata(tiff_file):
    """
    Read ImageDescription metadata from the tiff file as a block of text
    """
    image_desc = 270   # Magic EXIF tag numbers
    image_width = 256
    image_length = 257
    with Image.open(tiff_file) as img:
        d = {k: v for (k, v) in img.tag.items()}
        txt = d[image_desc][0]
        txt += f"\nwidth={d[image_width][0]}"
        txt += f"\nheight={d[image_length][0]}"
    return txt


def _parse_metadata(meta_text):
    """
    Parse text block containing metadata in <key>=<value> format
    """
    meta = dict(u.strip().replace('\x00', '').split('=', 1) for u in meta_text.splitlines())
    meta["width"] = int(meta["width"])
    meta["height"] = int(meta["height"])
    meta = _get_channel_info(meta)
    return meta


def _get_channel_info(metadata):
    """
    Extract information about arrangement of spectral channels from the metadata dict
    """
    fields = metadata["fieldArrangement"]
    N = len(re.findall("[1-4]", fields))
    metadata["n_channels"] = N

    f = re.findall(r'[\d|;]', fields)

    W, H = metadata['width'], metadata['height']
    if N >= 2:
        W = W//2
    if N >= 3:
        H = H//2

    metadata["channels"] = []
    for m in range(1, N+1):
        ch = metadata[f"channel{m}.name"]
        metadata["channels"].append(ch)
        x, y, = 0, 0

        for token in f:
            if str(m) == token:
                metadata[f"{ch}_slice"] = np.s_[..., H*y:H*(y + 1), W*x:W*(x + 1)]
            x += 1
            if token == ';':
                y += 1
                x = 0

    return metadata
