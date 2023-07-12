import pytest
from os.path import join
from sm_particle_counter.tirf_image import _parse_metadata
import numpy as np


@pytest.fixture(params=[
        # Single Cy3 channel
        ("meta_1ch.txt", dict(
            n_channels=1,
            fieldArrangement="[1]",
            width=1152,
            height=1008,
            channel_slices = dict(
                Cy2_slice = None,
                Cy3_slice = np.s_[..., 0:1008, 0:1152],
                Cy5_slice = None,
                Cy7_slice = None,
            )
        )),
        # Cy3 and Cy5
        ("meta_2ch.txt", dict(
            n_channels=2,
            fieldArrangement="[1,2]",
            width=2304,
            height=184,
            channel_slices = dict(
                Cy2_slice = None,
                Cy3_slice = np.s_[..., 0:184, 0:1152],
                Cy5_slice = np.s_[..., 0:184, 1152:2304],
                Cy7_slice = None,
            )
        )),
        # Cy3, Cy5, and Cy7
        ("meta_3ch.txt", dict(
            n_channels=3,
            fieldArrangement="[1,2;0,3]",
            width=2304,
            height=2304,
            channel_slices=dict(
                Cy2_slice = None,
                Cy3_slice = np.s_[..., 0:1152, 0:1152],
                Cy5_slice = np.s_[..., 0:1152, 1152:2304],
                Cy7_slice = np.s_[..., 1152:2304, 1152:2304],
            )
        )),
    ])
def parse_metadata_params(request):
    return request.param


def test_parse_metadata(parse_metadata_params):
    fn, result = parse_metadata_params
    meta_text = open(join("sm_particle_counter", "test", "data", fn)).read()

    metadata = _parse_metadata(meta_text)
    assert type(metadata) is dict
    assert metadata["fieldArrangement"] == result["fieldArrangement"]
    assert metadata["n_channels"] == result["n_channels"]
    for ch, s_ in result["channel_slices"].items():
        if s_:
            assert metadata[ch] == s_
        else:
            assert metadata.get(ch) is None


