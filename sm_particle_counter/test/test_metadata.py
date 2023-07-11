import pytest
from os.path import join
from sm_particle_counter.TIRF_image import _parse_metadata


@pytest.fixture(params=[
        # Single Cy3 channel
        ("meta_1ch.txt", dict(
            n_channels=1,
            fieldArrangement="[1]",
            width=1152,
            height=1008,
        )),
        # Cy3 and Cy5
        ("meta_2ch.txt", dict(
            n_channels=2,
            fieldArrangement="[1,2]",
            width=2304,
            height=184,
         )),
        # Cy3, Cy5, and Cy7
        ("meta_3ch.txt", dict(
            n_channels=3,
            fieldArrangement="[1,2;0,3]",
            width=2304,
            height=2304,
        )),
    ])
def parse_metadata_params(request):
    return request.param


def test_parse_metadata(parse_metadata_params):
    fn, result = parse_metadata_params
    meta_text = open(join("sm_particle_counter", "test", "data", fn)).read()
    assert _parse_metadata(meta_text)["fieldArrangement"] == result["fieldArrangement"]
    assert _parse_metadata(meta_text)["n_channels"] == result["n_channels"]


